"""API client for Obra Firebase Cloud Functions with retry logic and error handling.

Provides HTTP client wrapper for communicating with Cloud Functions endpoints,
implementing retry logic, timeout handling, and optional compression.
"""

import time
from datetime import datetime, timedelta, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
import yaml

from obra.exceptions import APIError, ConfigurationError, TermsNotAcceptedError


class APIClient:
    """HTTP client for Obra Cloud Functions API.

    Implements:
    - Automatic retry with exponential backoff
    - Timeout handling
    - Auth token management
    - Optional gzip compression for large payloads
    - Standardized error handling

    Example:
        client = APIClient(
            base_url="https://us-central1-obra-205b0.cloudfunctions.net",
            auth_token="your-firebase-token"
        )
        response = client.orchestrate(
            user_id="user123",
            project_id="proj456",
            working_dir="/home/user/project",
            objective="Add user authentication"
        )
    """

    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # seconds (exponential backoff)
    TOKEN_REFRESH_THRESHOLD = timedelta(minutes=5)  # Refresh if <5 minutes until expiration

    # Firebase Token Refresh API endpoint
    FIREBASE_TOKEN_URL = "https://securetoken.googleapis.com/v1/token"

    @staticmethod
    def _get_client_version() -> str:
        """Get the installed obra package version.

        Returns:
            Version string from package metadata, or "0.0.0-dev" if not installed.
        """
        try:
            return version("obra")
        except PackageNotFoundError:
            try:
                return version("obra-client")
            except PackageNotFoundError:
                return "0.0.0-dev"

    def __init__(
        self,
        base_url: str,
        auth_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        firebase_api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        enable_compression: bool = True,
        auto_refresh: bool = True,
    ) -> None:
        """Initialize APIClient.

        Args:
            base_url: Base URL for Cloud Functions (e.g., https://us-central1-obra-205b0.cloudfunctions.net)
            auth_token: Firebase ID token for authentication
            refresh_token: Firebase refresh token for token renewal
            firebase_api_key: Firebase Web API key (required for token refresh)
            timeout: Request timeout in seconds (default: 30)
            enable_compression: Enable gzip compression for requests >5KB
            auto_refresh: Automatically refresh token when close to expiration

        Raises:
            ConfigurationError: If base_url is invalid
        """
        if not base_url or not base_url.startswith("http"):
            raise ConfigurationError(f"Invalid base_url: {base_url}")

        # Ensure base_url ends with / for proper urljoin() behavior
        self.base_url = base_url.rstrip("/") + "/"
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        self.firebase_api_key = firebase_api_key
        self.timeout = timeout
        self.enable_compression = enable_compression
        self.auto_refresh = auto_refresh

        # Token expiration tracking
        self.token_expires_at: Optional[datetime] = None

        self.session = requests.Session()

        # Get client version for headers
        client_version = self._get_client_version()

        # Set default headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": f"obra/{client_version}",
                "X-Obra-Client-Version": client_version,
            }
        )

        # Add auth header if token provided
        if self.auth_token:
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})

    def refresh_auth_token(self) -> bool:
        """Refresh authentication token using Firebase refresh token.

        Uses Firebase Auth REST API to exchange refresh token for new ID token.

        Returns:
            True if refresh succeeded, False otherwise

        Note:
            This is called automatically if auto_refresh is enabled and
            token is close to expiration.
        """
        if not self.refresh_token or not self.firebase_api_key:
            return False

        try:
            # Firebase Token Refresh API endpoint
            url = f"https://securetoken.googleapis.com/v1/token?key={self.firebase_api_key}"

            # Use requests.post directly instead of self.session.post to avoid
            # the session's Content-Type: application/json header conflicting
            # with form-encoded data that Firebase expects
            response = requests.post(
                url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                new_id_token = data.get("id_token")
                new_refresh_token = data.get("refresh_token")

                if new_id_token:
                    self.set_auth_token(new_id_token)
                    if new_refresh_token:
                        self.refresh_token = new_refresh_token

                    # Firebase ID tokens expire in 1 hour
                    self.token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

                    # Save updated tokens to config
                    self._save_token_to_config(new_id_token, self.token_expires_at, new_refresh_token)
                    return True

            return False

        except Exception:
            return False

    def _check_token_expiration(self) -> None:
        """Check if token needs refresh and refresh if necessary.

        Called before authenticated requests if auto_refresh is enabled.
        """
        if not self.auto_refresh or not self.refresh_token:
            return

        if not self.token_expires_at:
            return

        # Check if token is close to expiration
        time_until_expiry = self.token_expires_at - datetime.now(timezone.utc)

        if time_until_expiry < self.TOKEN_REFRESH_THRESHOLD:
            # Token is close to expiration, refresh it
            try:
                self.refresh_auth_token()
            except Exception:
                # Refresh failed, continue with existing token
                pass

    def _save_token_to_config(
        self,
        token: str,
        expires_at: Optional[datetime] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        """Save auth token to config file for persistence.

        Args:
            token: Firebase ID token
            expires_at: Token expiration datetime
            refresh_token: Firebase refresh token (optional)
        """
        config_path = Path.home() / ".obra" / "client-config.yaml"

        if not config_path.exists():
            return  # No config file to update

        try:
            # Load existing config
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

            # Update token fields
            config["auth_token"] = token

            if expires_at:
                config["token_expires_at"] = expires_at.isoformat()

            if refresh_token:
                config["refresh_token"] = refresh_token

            # Save updated config
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

        except Exception:
            # Failed to save token, but continue (token is still in memory)
            pass

    @classmethod
    def from_config(cls, config_path: Optional[Path] = None) -> "APIClient":
        """Create APIClient from configuration file.

        Args:
            config_path: Path to config file (default: ~/.obra/client-config.yaml)

        Returns:
            Configured APIClient instance

        Raises:
            ConfigurationError: If config file doesn't exist or is invalid
        """
        if config_path is None:
            config_path = Path.home() / ".obra" / "client-config.yaml"

        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}\n"
                "Run 'obra login' to authenticate."
            )

        try:
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigurationError(f"Failed to load config: {e}") from e

        # Extract fields
        base_url = config.get("api_base_url")
        if not base_url:
            # Use default API URL
            base_url = "https://us-central1-obra-205b0.cloudfunctions.net"

        auth_token = config.get("auth_token")
        refresh_token = config.get("refresh_token")
        firebase_api_key = config.get("firebase_api_key")

        # Check for authentication
        if not auth_token:
            raise ConfigurationError(
                "Not authenticated.\n"
                "Run 'obra login' to sign in."
            )

        # Parse token expiration
        token_expires_at = None
        expires_at_str = config.get("token_expires_at")
        if expires_at_str:
            try:
                token_expires_at = datetime.fromisoformat(expires_at_str)
                # Ensure timezone-aware for comparison with datetime.now(timezone.utc)
                if token_expires_at.tzinfo is None:
                    token_expires_at = token_expires_at.replace(tzinfo=timezone.utc)
            except Exception:
                pass

        # Create client
        client = cls(
            base_url=base_url,
            auth_token=auth_token,
            refresh_token=refresh_token,
            firebase_api_key=firebase_api_key,
            auto_refresh=True,
        )

        client.token_expires_at = token_expires_at

        # Refresh token if expired (or close to expiration)
        if token_expires_at and token_expires_at < datetime.now(timezone.utc):
            if refresh_token and firebase_api_key:
                if not client.refresh_auth_token():
                    raise ConfigurationError(
                        "Authentication token expired and refresh failed.\n"
                        "Run 'obra login' to sign in again."
                    )
            else:
                raise ConfigurationError(
                    "Authentication token expired.\n"
                    "Run 'obra login' to sign in again."
                )

        return client

    def health_check(self) -> Dict[str, Any]:
        """Check API health.

        Returns:
            Health status dictionary

        Raises:
            APIError: If health check fails
        """
        return self._request("GET", "health", skip_auth_check=True)

    def get_version(self) -> Dict[str, Any]:
        """Get API version and client compatibility info.

        Returns:
            Version info dictionary with fields:
            - api_version: Server API version
            - min_client_version: Minimum compatible client version
            - features: List of enabled features

        Raises:
            APIError: If version check fails
        """
        return self._request("GET", "version", skip_auth_check=True)

    def orchestrate(
        self,
        user_id: str,
        project_id: str,
        working_dir: str,
        objective: str,
        task_type: str = "feature",
        requirements: Optional[list[str]] = None,
        constraints: Optional[list[str]] = None,
        validation_rules: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Start orchestration session.

        Args:
            user_id: User ID
            project_id: Project ID
            working_dir: Project working directory path
            objective: Task objective/goal
            task_type: Type of task (feature, bug_fix, refactor, etc.)
            requirements: List of requirements
            constraints: List of constraints
            validation_rules: List of validation rules

        Returns:
            Response dictionary with fields:
            - session_id: Session ID for subsequent calls
            - base_prompt: Base prompt (Tier 1 strategic context)
            - metadata: Additional metadata
            - status: Session status
            - iteration: Current iteration number

        Raises:
            APIError: If orchestration request fails
        """
        payload = {
            "user_id": user_id,
            "project_id": project_id,
            "working_dir": working_dir,
            "objective": objective,
            "task_type": task_type,
            "requirements": requirements or [],
            "constraints": constraints or [],
            "validation_rules": validation_rules or [],
        }

        return self._request("POST", "orchestrate", json=payload)

    def llm_result(
        self,
        session_id: str,
        result: str,
        status: str = "success",
        validation_errors: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        """Submit LLM execution result.

        Args:
            session_id: Session ID from /orchestrate
            result: LLM output/result
            status: Result status (success, partial, failure)
            validation_errors: List of validation errors (if any)

        Returns:
            Response dictionary with fields:
            - action: Next action (continue, complete, error)
            - base_prompt: Next iteration prompt (if action="continue")
            - iteration: Current iteration number
            - feedback: Feedback from server (if any)
            - message: Completion message (if action="complete")

        Raises:
            APIError: If result submission fails
        """
        payload = {
            "session_id": session_id,
            "result": result,
            "status": status,
            "validation_errors": validation_errors or [],
        }

        return self._request("POST", "llm_result", json=payload)

    def get_status(self, session_id: str) -> Dict[str, Any]:
        """Query session status.

        Args:
            session_id: Session ID to query

        Returns:
            Status dictionary with fields:
            - session_id: Session ID
            - status: Current status (active, completed, expired, failed)
            - current_iteration: Current iteration number
            - objective: Task objective
            - task_type: Task type

        Raises:
            APIError: If status query fails
        """
        return self._request("GET", f"get_status?session_id={session_id}")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session details with resume context.

        This is the enhanced session endpoint per PRD Pre-Implementation #2.

        Args:
            session_id: Session ID to query

        Returns:
            Session dictionary with fields:
            - session_id: Session ID
            - objective: Task objective
            - state: Current state
            - current_phase: Current orchestration phase
            - iteration: Current iteration number
            - resume_context: Context for resuming (if applicable)
            - quality_scorecard: Quality metrics (if available)
            - pending_escalation: Pending escalation notice (if any)
            - created_at: Session creation timestamp
            - updated_at: Last update timestamp

        Raises:
            APIError: If session query fails
        """
        return self._request("GET", f"session/{session_id}")

    def list_sessions(
        self, limit: int = 10, status: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """List recent sessions for the current user.

        Args:
            limit: Maximum number of sessions to return (default: 10)
            status: Filter by session status (active, completed, expired)

        Returns:
            List of session dictionaries with summary info

        Raises:
            APIError: If list request fails
        """
        params = [f"limit={limit}"]
        if status:
            params.append(f"status={status}")

        query_string = "&".join(params)
        response = self._request("GET", f"sessions?{query_string}")
        return response.get("sessions", [])

    def resume(self, session_id: str) -> Dict[str, Any]:
        """Resume an interrupted orchestration session.

        Args:
            session_id: Session ID to resume

        Returns:
            Response dictionary with fields:
            - session_id: Session ID
            - base_prompt: Continuation prompt
            - metadata: Prompt metadata
            - status: Session status ("active")
            - iteration: Current iteration number

        Raises:
            APIError: If resume request fails
        """
        payload = {"session_id": session_id}
        return self._request("POST", "resume", json=payload)

    def get_session_events(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query event history for a session.

        Args:
            session_id: Session ID to query events for
            limit: Maximum number of events to return (default 100, max 1000)
            offset: Number of events to skip for pagination
            event_type: Filter by event type
            severity: Filter by severity level (INFO, WARNING, ERROR)

        Returns:
            Response dictionary with fields:
            - session_id: Session ID
            - events: List of event dicts
            - count: Number of events returned
            - has_more: Whether more events exist

        Raises:
            APIError: If request fails
        """
        params = [f"session_id={session_id}", f"limit={limit}", f"offset={offset}"]
        if event_type:
            params.append(f"event_type={event_type}")
        if severity:
            params.append(f"severity={severity}")

        query_string = "&".join(params)
        return self._request("GET", f"get_session_events?{query_string}")

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        retry: bool = True,
        skip_auth_check: bool = False,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/orchestrate")
            json: JSON payload for POST/PUT
            retry: Enable retry logic (default: True)
            skip_auth_check: Skip token expiration check

        Returns:
            Response JSON as dictionary

        Raises:
            APIError: If request fails after retries
        """
        # Check token expiration and refresh if needed (unless skipped)
        if not skip_auth_check:
            self._check_token_expiration()

        url = urljoin(self.base_url, endpoint)

        # Determine retry attempts
        max_attempts = self.MAX_RETRIES if retry else 1

        last_error: Optional[Exception] = None

        for attempt in range(max_attempts):
            try:
                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json,
                    timeout=self.timeout,
                )

                # Handle response
                if response.status_code == 200:
                    return response.json()

                # Handle error status codes
                error_body = response.text
                error_json = {}
                try:
                    error_json = response.json()
                    error_message = error_json.get("error", error_body)
                except Exception:
                    error_message = error_body

                # Don't retry client errors (4xx), except 401 which gets token refresh
                if 400 <= response.status_code < 500:
                    # Check for specific terms_not_accepted error (403)
                    if (
                        response.status_code == 403
                        and error_json.get("error") == "terms_not_accepted"
                    ):
                        raise TermsNotAcceptedError(
                            message=error_json.get(
                                "message",
                                "You must accept the Obra Beta Software Agreement.",
                            ),
                            required_version=error_json.get("required_version", ""),
                            terms_url=error_json.get("terms_url", "https://obra.dev/terms"),
                            action=error_json.get(
                                "action", "Run 'obra setup' to accept terms."
                            ),
                        )

                    # Handle 401 Unauthorized - attempt token refresh and retry once
                    if response.status_code == 401 and not skip_auth_check:
                        if self.refresh_token and self.firebase_api_key:
                            # Try to refresh the token
                            if self.refresh_auth_token():
                                # Token refreshed, retry the request
                                return self._request(
                                    method=method,
                                    endpoint=endpoint,
                                    json=json,
                                    retry=False,
                                    skip_auth_check=True,
                                )

                        # Refresh failed or not possible
                        raise APIError(
                            message="Authentication token expired. Run 'obra login' to sign in again.",
                            status_code=401,
                            response_body=error_body,
                        )

                    raise APIError(
                        message=f"API error {response.status_code}: {error_message}",
                        status_code=response.status_code,
                        response_body=error_body,
                    )

                # Retry server errors (5xx)
                last_error = APIError(
                    message=f"API error {response.status_code}: {error_message}",
                    status_code=response.status_code,
                    response_body=error_body,
                )

            except requests.exceptions.Timeout as e:
                last_error = APIError(
                    message=f"Request timed out after {self.timeout}s",
                    status_code=0,
                    response_body=str(e),
                )

            except requests.exceptions.ConnectionError as e:
                last_error = APIError(
                    message=f"Connection error: {e}",
                    status_code=0,
                    response_body=str(e),
                )

            except (APIError, TermsNotAcceptedError):
                # Re-raise API errors and terms errors
                raise

            except Exception as e:
                last_error = APIError(
                    message=f"Request failed: {e}",
                    status_code=0,
                    response_body=str(e),
                )

            # Retry with exponential backoff
            if attempt < max_attempts - 1:
                delay = self.RETRY_DELAYS[attempt]
                time.sleep(delay)
            else:
                break

        # All retries exhausted
        if last_error:
            raise last_error

        raise APIError("Request failed with unknown error")

    def set_auth_token(self, token: str) -> None:
        """Update authentication token.

        Args:
            token: New Firebase custom token
        """
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def log_terms_acceptance(
        self,
        terms_version: str,
        privacy_version: str,
        client_version: str,
        source: str = "cli_setup",
        user_id: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        """Log terms acceptance to server for legal compliance audit trail.

        Args:
            terms_version: Version of terms accepted (e.g., "2.1")
            privacy_version: Version of privacy policy (e.g., "1.3")
            client_version: obra package version
            source: Where acceptance occurred (default: "cli_setup")
            user_id: Firebase UID (preferred identifier)
            email: User email address (fallback identifier)

        Returns:
            True if server logging succeeded, False otherwise
        """
        payload: Dict[str, Any] = {
            "terms_version": terms_version,
            "privacy_version": privacy_version,
            "client_version": client_version,
            "source": source,
        }

        if user_id:
            payload["user_id"] = user_id
        if email:
            payload["email"] = email

        try:
            response = self._request(
                method="POST",
                endpoint="terms_accept",
                json=payload,
                retry=True,
                skip_auth_check=False,
            )

            return response.get("success", False)

        except Exception:
            # Graceful degradation: don't raise, just return False
            return False

    def close(self) -> None:
        """Close HTTP session and cleanup resources."""
        self.session.close()

    # =========================================================================
    # User Configuration Methods
    # =========================================================================

    def get_user_config(self) -> Dict[str, Any]:
        """Get user's configuration (preset + overrides + resolved).

        Returns:
            Dictionary with fields:
            - preset: str - Current preset name
            - overrides: dict - User's custom overrides
            - resolved: dict - Full merged configuration
            - created_at: str - When config was created
            - updated_at: str - When config was last updated

        Raises:
            APIError: If request fails
        """
        return self._request("GET", "get_user_config")

    def update_user_config(
        self,
        preset: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
        clear_overrides: bool = False,
    ) -> Dict[str, Any]:
        """Update user's configuration.

        Args:
            preset: New preset name (optional)
            overrides: Dict of dot-notation path overrides to merge
            clear_overrides: If True, clear all existing overrides

        Returns:
            Dictionary with updated config

        Raises:
            APIError: If request fails
        """
        payload: Dict[str, Any] = {}

        if preset is not None:
            payload["preset"] = preset

        if overrides is not None:
            payload["overrides"] = overrides

        if clear_overrides:
            payload["clear_overrides"] = True

        if not payload:
            return self.get_user_config()

        return self._request("POST", "update_user_config", json=payload)

    def list_presets(self) -> Dict[str, Any]:
        """List available configuration presets.

        Returns:
            Dictionary with fields:
            - presets: list of preset info dicts

        Raises:
            APIError: If request fails
        """
        return self._request("GET", "list_presets")

    # =========================================================================
    # Plan Management Methods
    # =========================================================================

    def upload_plan(self, name: str, plan_data: dict) -> Dict[str, Any]:
        """Upload a MACHINE_PLAN.yaml to the server.

        Uploads a parsed plan structure to Firestore for later use.
        The plan is stored in users/{uid}/plans/{plan_id} and can be
        referenced in subsequent derive commands via --plan-id.

        Args:
            name: Plan name (typically work_id from YAML)
            plan_data: Parsed YAML structure (dict representation)

        Returns:
            Dictionary with fields:
            - plan_id: UUID for the uploaded plan
            - name: Plan name
            - story_count: Number of stories in the plan
            - created_at: Timestamp when plan was uploaded

        Raises:
            APIError: If upload fails or validation fails

        Example:
            >>> client = APIClient.from_config()
            >>> with open("plan.yaml") as f:
            ...     plan_data = yaml.safe_load(f)
            >>> result = client.upload_plan("FEAT-AUTH-001", plan_data)
            >>> print(f"Plan ID: {result['plan_id']}")
        """
        payload = {
            "name": name,
            "plan_data": plan_data,
        }
        return self._request("POST", "upload_plan", json=payload)

    def list_plans(self, limit: int = 50) -> list[Dict[str, Any]]:
        """List user's uploaded plans.

        Returns a list of plans uploaded by the current user, ordered
        by creation time (most recent first).

        Args:
            limit: Maximum number of plans to return (default: 50, max: 100)

        Returns:
            List of plan dictionaries with fields:
            - plan_id: UUID for the plan
            - name: Plan name
            - story_count: Number of stories
            - created_at: Upload timestamp
            - used_count: How many times plan was used (optional)

        Raises:
            APIError: If list request fails

        Example:
            >>> client = APIClient.from_config()
            >>> plans = client.list_plans(limit=10)
            >>> for plan in plans:
            ...     print(f"{plan['name']}: {plan['story_count']} stories")
        """
        params = f"limit={min(limit, 100)}"
        response = self._request("GET", f"plans?{params}")
        return response.get("plans", [])

    def get_plan(self, plan_id: str) -> Dict[str, Any]:
        """Get details of a specific plan.

        Args:
            plan_id: UUID of the plan to retrieve

        Returns:
            Dictionary with fields:
            - plan_id: UUID
            - name: Plan name
            - plan_data: Full plan structure
            - story_count: Number of stories
            - created_at: Upload timestamp

        Raises:
            APIError: If plan not found or request fails

        Example:
            >>> client = APIClient.from_config()
            >>> plan = client.get_plan("abc123-uuid")
            >>> print(f"Plan: {plan['name']}")
        """
        return self._request("GET", f"plans/{plan_id}")

    def delete_plan(self, plan_id: str) -> Dict[str, Any]:
        """Delete a plan from the server.

        Permanently removes the plan from Firestore. This cannot be undone.
        Sessions using this plan are not affected (they have their own copy).

        Args:
            plan_id: UUID of the plan to delete

        Returns:
            Dictionary with fields:
            - success: True if deletion succeeded
            - plan_id: UUID of deleted plan

        Raises:
            APIError: If plan not found or deletion fails

        Example:
            >>> client = APIClient.from_config()
            >>> result = client.delete_plan("abc123-uuid")
            >>> print("Plan deleted" if result['success'] else "Failed")
        """
        return self._request("DELETE", f"plans/{plan_id}")
