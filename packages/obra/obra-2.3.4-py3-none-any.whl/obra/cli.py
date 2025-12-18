"""CLI commands for the Obra hybrid orchestration package.

This module provides all CLI commands for the unified obra package:
- derive: Main workflow command to start orchestrated tasks
- status: Check session status
- resume: Resume an interrupted session
- login/logout/whoami: Authentication commands
- config: Configuration management
- version: Version information and server compatibility check
- validate-plan: Validate YAML syntax of MACHINE_PLAN.yaml files
- upload-plan: Upload plan files to Obra SaaS
- plans: Manage uploaded plans (list, delete)

Usage:
    $ obra derive "Add user authentication"
    $ obra derive --plan-id abc123 "Execute uploaded plan"
    $ obra derive --plan-file plan.yaml "Upload and execute plan"
    $ obra status
    $ obra resume --session-id <id>
    $ obra login
    $ obra logout
    $ obra whoami
    $ obra config
    $ obra version
    $ obra validate-plan path/to/plan.yaml
    $ obra upload-plan path/to/plan.yaml
    $ obra plans list
    $ obra plans delete <plan_id>

Reference: EPIC-HYBRID-001 Story S10: CLI Commands
          FEAT-PLAN-IMPORT-OBRA-001: Plan File Import
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from obra import __version__
from obra.config import (
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    DEFAULT_THINKING_LEVEL,
    THINKING_LEVELS,
    get_thinking_level_notes,
    infer_provider_from_model,
)
from obra.display import (
    ObservabilityConfig,
    ProgressEmitter,
    console,
    handle_encoding_errors,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from obra.display.errors import display_error, display_obra_error
from obra.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    ObraError,
)
from obra.cli_commands import UploadPlanCommand, ValidatePlanCommand

logger = logging.getLogger(__name__)

# Enforce UTF-8 mode for consistent cross-platform behavior
os.environ.setdefault("PYTHONUTF8", "1")

# Create Typer app
app = typer.Typer(
    name="obra",
    help="Obra - Cloud-native AI orchestration platform",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for CLI commands.

    Args:
        verbose: Enable debug-level logging
    """
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# =============================================================================
# Main Workflow Commands
# =============================================================================


@app.command()
@handle_encoding_errors
def derive(
    objective: str = typer.Argument(..., help="The objective to accomplish"),
    working_dir: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Working directory (defaults to current directory)",
    ),
    resume_session: Optional[str] = typer.Option(
        None,
        "--resume",
        "-r",
        help="Resume an existing session by ID",
    ),
    plan_id: Optional[str] = typer.Option(
        None,
        "--plan-id",
        help="Use an uploaded plan by ID (from 'obra upload-plan')",
    ),
    plan_file: Optional[Path] = typer.Option(
        None,
        "--plan-file",
        help="Upload and use a plan file in one step",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Implementation model (e.g., opus, gpt-5.2, gemini-2.5-flash)",
    ),
    impl_model: Optional[str] = typer.Option(
        None,
        "--impl-model",
        help="Alias for --model",
        hidden=True,
    ),
    impl_provider: Optional[str] = typer.Option(
        None,
        "--impl-provider",
        "-p",
        help="Implementation provider (anthropic, openai, google). Requires provider CLI (claude/codex/gemini).",
    ),
    thinking_level: Optional[str] = typer.Option(
        None,
        "--thinking-level",
        "-t",
        help="Thinking/reasoning level (off, low, medium, high, maximum)",
    ),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        max=3,
        help="Verbosity level (0-3, use -v/-vv/-vvv)",
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        "-s",
        help="Enable real-time LLM output streaming",
    ),
) -> None:
    """Start or resume an orchestrated derivation workflow.

    This is the main workflow command. It:
    1. Connects to the Obra server
    2. Creates or resumes a session
    3. Orchestrates the derivation, examination, revision, and execution loop
    4. Deploys review agents and handles fixes
    5. Completes when quality gates pass

    Examples:
        $ obra derive "Add user authentication"
        $ obra derive "Refactor the payment module" --dir /path/to/project
        $ obra derive --resume abc123 "Continue authentication work"
        $ obra derive "Fix the bug" --model opus --thinking-level high
        $ obra derive "Add tests" --impl-provider openai --model gpt-5.2
        $ obra derive "Add logging" -vv  # Level 2 verbosity
        $ obra derive --plan-id abc123 "Implement from uploaded plan"
        $ obra derive --plan-file plan.yaml "Execute plan file"
    """
    setup_logging(verbose > 0)

    # Validate plan-related arguments
    if plan_id and plan_file:
        print_error("Cannot specify both --plan-id and --plan-file")
        console.print("\nUse one or the other:")
        console.print("  --plan-id: Reference an already uploaded plan")
        console.print("  --plan-file: Upload and use a plan in one step")
        raise typer.Exit(2)

    # Resolve model from --model or --impl-model (--model takes precedence)
    effective_model = model or impl_model

    # S2.T2: Validate thinking level against THINKING_LEVELS constant
    if thinking_level is not None and thinking_level not in THINKING_LEVELS:
        print_error(f"Invalid thinking level: '{thinking_level}'")
        console.print(f"\nValid levels: {', '.join(THINKING_LEVELS)}")
        raise typer.Exit(2)  # Exit code 2 for config errors

    # S2.T3 & S2.T4: Auto-detect provider from model, warn if unknown
    effective_provider = impl_provider
    if effective_model and not effective_provider:
        detected = infer_provider_from_model(effective_model)
        if detected:
            effective_provider = detected
            if verbose > 0:
                console.print(f"[dim]Detected provider: {detected}[/dim]")
        else:
            # S2.T4: Unknown model warning with default fallback
            print_warning(f"Unknown model '{effective_model}', using default provider: {DEFAULT_PROVIDER}")
            effective_provider = DEFAULT_PROVIDER

    try:
        from obra.auth import ensure_valid_token, get_current_auth
        from obra.config import validate_provider_ready
        from obra.hybrid import HybridOrchestrator

        # Set working directory
        work_dir = working_dir or Path.cwd()
        if not work_dir.exists():
            print_error(f"Working directory does not exist: {work_dir}")
            raise typer.Exit(1)

        # Resolve effective config values with defaults
        display_provider = effective_provider or DEFAULT_PROVIDER
        display_model = effective_model or DEFAULT_MODEL
        display_thinking = thinking_level or DEFAULT_THINKING_LEVEL

        # S3.T1: Fail-fast provider health check before any session output/auth
        validate_provider_ready(display_provider)

        # Ensure authenticated
        auth = get_current_auth()
        if not auth:
            print_error("Not logged in")
            console.print("\nRun 'obra login' to authenticate.")
            raise typer.Exit(1)

        # Ensure valid token
        try:
            ensure_valid_token()
        except AuthenticationError as e:
            display_obra_error(e, console)
            raise typer.Exit(1)

        # Handle --plan-file: upload plan before starting session
        effective_plan_id = plan_id
        if plan_file:
            console.print()
            console.print(f"[dim]Uploading plan file: {plan_file}[/dim]")
            try:
                import yaml
                from obra.api import APIClient

                # Parse YAML file (basic syntax check)
                with open(plan_file, encoding="utf-8") as f:
                    plan_data = yaml.safe_load(f)

                # Extract plan name
                plan_name = plan_data.get("work_id", plan_file.stem)

                # Upload to server for full validation and storage
                client = APIClient.from_config()
                upload_response = client.upload_plan(plan_name, plan_data)
                effective_plan_id = upload_response.get("plan_id")

                console.print(f"[dim]Plan uploaded: {effective_plan_id}[/dim]")

            except ObraError as e:
                display_obra_error(e, console)
                raise typer.Exit(1)
            except Exception as e:
                print_error(f"Failed to upload plan file: {e}")
                logger.exception("Error uploading plan file")
                raise typer.Exit(1)

        console.print()
        console.print(f"[bold]Obra Derive[/bold]", style="cyan")
        console.print(f"Objective: {objective}")
        console.print(f"Directory: {work_dir}")
        if resume_session:
            console.print(f"Resuming session: {resume_session}")
        if effective_plan_id:
            console.print(f"Plan ID: {effective_plan_id}")

        # S2.T5: Display LLM config line before session starts
        console.print(f"LLM: {display_provider} ({display_model}) | thinking: {display_thinking}")

        # S2.T6: Display thinking level notes if applicable
        notes = get_thinking_level_notes(display_provider, display_thinking, display_model)
        if notes:
            console.print(f"[dim]{notes}[/dim]")

        console.print()

        # Create observability configuration from CLI flags
        obs_config = ObservabilityConfig(
            verbosity=verbose,
            stream=stream,
            timestamps=True,
        )

        # Create progress emitter for observability
        progress_emitter = ProgressEmitter(obs_config, console)

        # Create orchestrator with progress callback
        def on_progress(action: str, payload: dict) -> None:
            """Progress callback that routes events to ProgressEmitter.

            Args:
                action: Event type (e.g., 'phase_started', 'llm_streaming')
                payload: Event data dict
            """
            # Route events to appropriate ProgressEmitter methods
            if action == "phase_started":
                phase = payload.get("phase", "UNKNOWN")
                progress_emitter.phase_started(phase, payload.get("context"))
            elif action == "phase_completed":
                phase = payload.get("phase", "UNKNOWN")
                duration_ms = payload.get("duration_ms", 0)
                progress_emitter.phase_completed(phase, payload.get("result"), duration_ms)
            elif action == "llm_started":
                purpose = payload.get("purpose", "LLM invocation")
                progress_emitter.llm_started(purpose)
            elif action == "llm_streaming":
                chunk = payload.get("chunk", "")
                progress_emitter.llm_streaming(chunk)
            elif action == "llm_completed":
                summary = payload.get("summary", "")
                tokens = payload.get("tokens", 0)
                progress_emitter.llm_completed(summary, tokens)
            elif action == "item_started":
                item = payload.get("item", {})
                progress_emitter.item_started(item)
            elif action == "item_completed":
                item = payload.get("item", {})
                result = payload.get("result")
                progress_emitter.item_completed(item, result)
            elif action == "error":
                # Error event with verbosity-appropriate detail
                message = payload.get("message", "Unknown error")
                hint = payload.get("hint")
                phase = payload.get("phase")
                affected_items = payload.get("affected_items")
                stack_trace = payload.get("stack_trace")
                raw_response = payload.get("raw_response")
                progress_emitter.error(
                    message, hint, phase, affected_items, stack_trace, raw_response
                )
            elif verbose > 0:
                # Fallback for unknown events at verbose mode
                console.print(f"[dim]{action}[/dim]")

        # S5.T1/T2: Pass LLM overrides to orchestrator
        orchestrator = HybridOrchestrator.from_config(
            working_dir=work_dir,
            on_progress=on_progress,
            impl_provider=effective_provider,
            impl_model=effective_model,
            thinking_level=thinking_level,
        )

        # Run derive workflow
        if resume_session:
            result = orchestrator.resume(resume_session)
        else:
            result = orchestrator.derive(objective, plan_id=effective_plan_id)

        # Display result
        console.print()
        if result.action == "complete":
            print_success("Derivation completed successfully!")
            if hasattr(result, "session_summary"):
                summary = result.session_summary
                console.print(f"\nItems completed: {summary.get('items_completed', 'N/A')}")
                console.print(f"Iterations: {summary.get('total_iterations', 'N/A')}")
                console.print(f"Quality score: {summary.get('quality_score', 'N/A')}")
        elif result.action == "escalate":
            print_warning("Session requires user decision")
            console.print("\nRun 'obra status' to see details and respond.")
        else:
            console.print(f"Session state: {result.action}")

    # S3.T3: Consistent exit codes - config=2, connection=3, execution=1
    except ConfigurationError as e:
        display_obra_error(e, console)
        raise typer.Exit(2)
    except ConnectionError as e:
        display_obra_error(e, console)
        raise typer.Exit(3)
    except ObraError as e:
        display_obra_error(e, console)
        raise typer.Exit(1)
    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in derive command")
        raise typer.Exit(1)


@app.command()
@handle_encoding_errors
def status(
    session_id: Optional[str] = typer.Option(
        None,
        "--session-id",
        "-s",
        help="Session ID to check (defaults to most recent)",
    ),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        max=3,
        help="Verbosity level (0-3, use -v/-vv/-vvv)",
    ),
) -> None:
    """Check the status of a derivation session.

    Shows the current state of the session including:
    - Session phase (derive, examine, revise, execute, review)
    - Iteration count
    - Quality metrics
    - Any pending user decisions

    Examples:
        $ obra status
        $ obra status --session-id abc123
        $ obra status -v
        $ obra status -vv  # More detail
    """
    setup_logging(verbose > 0)

    try:
        from obra.api import APIClient
        from obra.auth import ensure_valid_token, get_current_auth
        from obra.config import load_config

        # Ensure authenticated
        auth = get_current_auth()
        if not auth:
            print_error("Not logged in")
            console.print("\nRun 'obra login' to authenticate.")
            raise typer.Exit(1)

        ensure_valid_token()

        # Get API client
        client = APIClient.from_config()

        # Get session status
        if session_id:
            session = client.get_session(session_id)
        else:
            # Get most recent session
            sessions = client.list_sessions(limit=1)
            if not sessions:
                print_info("No active sessions found")
                console.print("\nRun 'obra derive \"objective\"' to start a new session.")
                return
            session = sessions[0]

        # Display session status
        console.print()
        console.print("[bold]Session Status[/bold]", style="cyan")
        console.print()

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="dim")
        table.add_column("Value")

        table.add_row("Session ID", session.get("session_id", "N/A"))
        table.add_row("Objective", session.get("objective", "N/A"))
        table.add_row("State", session.get("state", "N/A"))
        table.add_row("Phase", session.get("current_phase", "N/A"))
        table.add_row("Iteration", str(session.get("iteration", 0)))
        table.add_row("Created", session.get("created_at", "N/A"))
        table.add_row("Updated", session.get("updated_at", "N/A"))

        console.print(table)

        # Show quality metrics if available
        if verbose > 0 and "quality_scorecard" in session:
            scorecard = session["quality_scorecard"]
            console.print()
            console.print("[bold]Quality Scorecard[/bold]", style="cyan")

            score_table = Table()
            score_table.add_column("Dimension", style="cyan")
            score_table.add_column("Score")

            for dim, score in scorecard.items():
                score_table.add_row(dim, f"{score:.2f}" if isinstance(score, float) else str(score))

            console.print(score_table)

        # Show pending escalation if any
        if session.get("pending_escalation"):
            console.print()
            print_warning("Pending escalation requires your decision")
            escalation = session["pending_escalation"]
            console.print(f"Reason: {escalation.get('reason', 'N/A')}")
            console.print("\nOptions:")
            for opt in escalation.get("options", []):
                console.print(f"  - {opt.get('id')}: {opt.get('label')} - {opt.get('description', '')}")

    except ObraError as e:
        display_obra_error(e, console)
        raise typer.Exit(1)
    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in status command")
        raise typer.Exit(1)


@app.command()
@handle_encoding_errors
def resume(
    session_id: str = typer.Argument(..., help="Session ID to resume"),
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        max=3,
        help="Verbosity level (0-3, use -v/-vv/-vvv)",
    ),
    stream: bool = typer.Option(
        False,
        "--stream",
        "-s",
        help="Enable real-time LLM output streaming",
    ),
) -> None:
    """Resume an interrupted session.

    Continues a session from where it left off. Useful after:
    - Network disconnection
    - Client crash
    - Manual interruption

    Examples:
        $ obra resume abc123
        $ obra resume abc123 -v
        $ obra resume abc123 -vv --stream
    """
    setup_logging(verbose > 0)

    try:
        from obra.auth import ensure_valid_token, get_current_auth
        from obra.hybrid import HybridOrchestrator

        # Ensure authenticated
        auth = get_current_auth()
        if not auth:
            print_error("Not logged in")
            console.print("\nRun 'obra login' to authenticate.")
            raise typer.Exit(1)

        ensure_valid_token()

        console.print()
        console.print(f"[bold]Resuming Session[/bold]", style="cyan")
        console.print(f"Session ID: {session_id}")
        console.print()

        # Create observability configuration from CLI flags
        obs_config = ObservabilityConfig(
            verbosity=verbose,
            stream=stream,
            timestamps=True,
        )

        # Create progress emitter for observability
        progress_emitter = ProgressEmitter(obs_config, console)

        # Create orchestrator and resume with progress callback
        def on_progress(action: str, payload: dict) -> None:
            """Progress callback that routes events to ProgressEmitter."""
            # Route events to appropriate ProgressEmitter methods
            if action == "phase_started":
                phase = payload.get("phase", "UNKNOWN")
                progress_emitter.phase_started(phase, payload.get("context"))
            elif action == "phase_completed":
                phase = payload.get("phase", "UNKNOWN")
                duration_ms = payload.get("duration_ms", 0)
                progress_emitter.phase_completed(phase, payload.get("result"), duration_ms)
            elif action == "llm_started":
                purpose = payload.get("purpose", "LLM invocation")
                progress_emitter.llm_started(purpose)
            elif action == "llm_streaming":
                chunk = payload.get("chunk", "")
                progress_emitter.llm_streaming(chunk)
            elif action == "llm_completed":
                summary = payload.get("summary", "")
                tokens = payload.get("tokens", 0)
                progress_emitter.llm_completed(summary, tokens)
            elif action == "item_started":
                item = payload.get("item", {})
                progress_emitter.item_started(item)
            elif action == "item_completed":
                item = payload.get("item", {})
                result = payload.get("result")
                progress_emitter.item_completed(item, result)
            elif action == "error":
                # Error event with verbosity-appropriate detail
                message = payload.get("message", "Unknown error")
                hint = payload.get("hint")
                phase = payload.get("phase")
                affected_items = payload.get("affected_items")
                stack_trace = payload.get("stack_trace")
                raw_response = payload.get("raw_response")
                progress_emitter.error(
                    message, hint, phase, affected_items, stack_trace, raw_response
                )
            elif verbose > 0:
                # Fallback for unknown events at verbose mode
                console.print(f"[dim]{action}[/dim]")

        orchestrator = HybridOrchestrator.from_config(on_progress=on_progress)
        result = orchestrator.resume(session_id)

        # Display result
        console.print()
        if result.action == "complete":
            print_success("Session completed successfully!")
        elif result.action == "escalate":
            print_warning("Session requires user decision")
            console.print("\nRun 'obra status' to see details.")
        else:
            console.print(f"Session state: {result.action}")

    except ObraError as e:
        display_obra_error(e, console)
        raise typer.Exit(1)
    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in resume command")
        raise typer.Exit(1)


# =============================================================================
# Authentication Commands
# =============================================================================


@app.command()
@handle_encoding_errors
def login(
    timeout: int = typer.Option(
        300,
        "--timeout",
        "-t",
        help="Timeout in seconds for browser authentication",
    ),
    no_browser: bool = typer.Option(
        False,
        "--no-browser",
        help="Don't open browser, just print URL",
    ),
) -> None:
    """Authenticate with Obra.

    Opens your browser to sign in with Google or GitHub.
    After successful authentication, your session is saved locally.

    Examples:
        $ obra login
        $ obra login --no-browser
        $ obra login --timeout 600
    """
    try:
        from obra.auth import login_with_browser, save_auth

        console.print()
        console.print("[bold]Obra Login[/bold]", style="cyan")
        console.print()

        if no_browser:
            console.print("Opening authentication URL...")
            console.print("Copy the URL below and open it in your browser:")
        else:
            console.print("Opening browser for authentication...")

        result = login_with_browser(timeout=timeout, auto_open=not no_browser)

        # Save the authentication
        save_auth(result)

        console.print()
        print_success(f"Logged in as: {result.email}")
        if result.display_name:
            console.print(f"Name: {result.display_name}")

    except AuthenticationError as e:
        display_obra_error(e, console)
        raise typer.Exit(1)
    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in login command")
        raise typer.Exit(1)


@app.command()
@handle_encoding_errors
def logout() -> None:
    """Log out and clear stored credentials.

    Removes your authentication token from the local config.
    You'll need to run 'obra login' again to use Obra.

    Example:
        $ obra logout
    """
    try:
        from obra.auth import clear_auth, get_current_auth

        auth = get_current_auth()
        if not auth:
            print_info("Not currently logged in")
            return

        email = auth.email
        clear_auth()

        console.print()
        print_success(f"Logged out: {email}")
        console.print("\nRun 'obra login' to sign in again.")

    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in logout command")
        raise typer.Exit(1)


@app.command()
@handle_encoding_errors
def whoami() -> None:
    """Show current authentication status.

    Displays the currently authenticated user and token status.

    Example:
        $ obra whoami
    """
    try:
        from obra.auth import get_current_auth
        from obra.config import load_config

        auth = get_current_auth()

        console.print()
        if not auth:
            print_info("Not logged in")
            console.print("\nRun 'obra login' to authenticate.")
            return

        console.print("[bold]Current User[/bold]", style="cyan")
        console.print()

        table = Table(show_header=False, box=None)
        table.add_column("Field", style="dim")
        table.add_column("Value")

        table.add_row("Email", auth.email)
        if auth.display_name:
            table.add_row("Name", auth.display_name)
        table.add_row("Provider", auth.auth_provider)
        table.add_row("User ID", auth.firebase_uid[:16] + "...")

        console.print(table)

        # Check token status
        config = load_config()
        token_expires = config.get("token_expires_at")
        if token_expires:
            from datetime import datetime, timezone

            try:
                expires_dt = datetime.fromisoformat(token_expires.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                if expires_dt > now:
                    remaining = expires_dt - now
                    minutes = int(remaining.total_seconds() / 60)
                    console.print(f"\n[dim]Token expires in {minutes} minutes[/dim]")
                else:
                    console.print("\n[yellow]Token expired - will auto-refresh on next request[/yellow]")
            except ValueError:
                pass

    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in whoami command")
        raise typer.Exit(1)


# =============================================================================
# Configuration Commands
# =============================================================================


def _run_config_validation(json_output: bool = False) -> None:
    """Run configuration validation and display results.

    S4.T2: Validates provider CLIs and configuration settings.

    Args:
        json_output: If True, output JSON instead of human-readable format
    """
    import json
    from obra.config import (
        CONFIG_PATH,
        LLM_PROVIDERS,
        check_provider_status,
        load_config,
    )

    # Check all providers
    provider_results = {}
    for provider_key in LLM_PROVIDERS:
        status = check_provider_status(provider_key)
        provider_results[provider_key] = {
            "name": LLM_PROVIDERS[provider_key].get("name", provider_key),
            "installed": status.installed,
            "cli_command": status.cli_command,
            "install_hint": status.install_hint,
            "docs_url": status.docs_url,
        }

    # Load configuration
    config_data = load_config()
    config_exists = bool(config_data)

    # Overall status
    all_installed = all(p["installed"] for p in provider_results.values())

    if json_output:
        # S4.T4: JSON output structure
        output = {
            "status": "valid" if (all_installed and config_exists) else "issues_found",
            "providers": provider_results,
            "configuration": {
                "path": str(CONFIG_PATH),
                "exists": config_exists,
                "keys_present": list(config_data.keys()) if config_data else [],
            },
        }
        console.print(json.dumps(output, indent=2))
    else:
        # S4.T3: Human-readable output with colors and icons
        _display_validation_human(provider_results, config_exists, str(CONFIG_PATH))


def _display_validation_human(
    provider_results: dict,
    config_exists: bool,
    config_path: str,
) -> None:
    """Display validation results in human-readable format with colors and icons.

    S4.T3: Display validation with ✓/✗ icons and colored output.

    Args:
        provider_results: Provider validation results
        config_exists: Whether config file exists
        config_path: Path to config file
    """
    console.print()
    console.print("[bold]Configuration Validation[/bold]", style="cyan")
    console.print()

    # Provider CLI checks
    console.print("[bold]Provider CLIs:[/bold]")
    for provider_key, result in provider_results.items():
        if result["installed"]:
            icon = "[green]✓[/green]"
            status_text = f"[green]{result['cli_command']} installed[/green]"
        else:
            icon = "[red]✗[/red]"
            status_text = f"[red]{result['cli_command']} not found[/red]"
            if result["install_hint"]:
                status_text += f"\n    [dim]{result['install_hint']}[/dim]"

        console.print(f"  {icon} {result['name']}: {status_text}")

    console.print()

    # Configuration file check
    console.print("[bold]Configuration:[/bold]")
    if config_exists:
        icon = "[green]✓[/green]"
        status_text = f"[green]Config found at {config_path}[/green]"
    else:
        icon = "[yellow]⚠[/yellow]"
        status_text = f"[yellow]No config file (using defaults)[/yellow]"

    console.print(f"  {icon} {status_text}")
    console.print()

    # Overall status
    all_installed = all(p["installed"] for p in provider_results.values())
    if all_installed and config_exists:
        print_success("All checks passed!")
    elif all_installed:
        print_warning("Providers installed but no config file found (using defaults)")
    else:
        print_warning("Some provider CLIs are not installed")
        console.print("\n[dim]Tip: Install the providers you plan to use with obra derive --impl-provider[/dim]")


@app.command()
@handle_encoding_errors
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    reset: bool = typer.Option(False, "--reset", help="Reset configuration to defaults"),
    validate: bool = typer.Option(False, "--validate", help="Validate provider CLIs and configuration"),
    json_output: bool = typer.Option(False, "--json", help="Output validation results as JSON"),
) -> None:
    """Manage Obra configuration.

    Without options, launches the interactive configuration TUI.
    Use --show to display current configuration.
    Use --reset to reset to default values.
    Use --validate to check provider CLIs and configuration.
    Use --json with --validate for machine-readable output.

    Examples:
        $ obra config
        $ obra config --show
        $ obra config --reset
        $ obra config --validate
        $ obra config --validate --json
    """
    try:
        from obra.config import CONFIG_PATH, load_config, save_config

        # S4.T1: Handle --validate flag
        if validate:
            _run_config_validation(json_output=json_output)
            return

        if reset:
            # Confirm reset
            confirm = typer.confirm("Reset configuration to defaults?")
            if not confirm:
                console.print("Cancelled")
                return

            # Reset by saving minimal config
            save_config({})
            print_success("Configuration reset to defaults")
            return

        if show:
            # Show current configuration
            config_data = load_config()

            console.print()
            console.print("[bold]Current Configuration[/bold]", style="cyan")
            console.print(f"[dim]Location: {CONFIG_PATH}[/dim]")
            console.print()

            if not config_data:
                print_info("No configuration set")
                return

            table = Table(show_header=False, box=None)
            table.add_column("Key", style="cyan")
            table.add_column("Value")

            # Show non-sensitive config
            for key, value in sorted(config_data.items()):
                # Mask sensitive values
                if key in ("auth_token", "refresh_token", "firebase_uid"):
                    if value:
                        display_val = str(value)[:16] + "..."
                    else:
                        display_val = "[dim]not set[/dim]"
                else:
                    display_val = str(value) if value else "[dim]not set[/dim]"

                table.add_row(key, display_val)

            console.print(table)
            return

        # Launch config explorer TUI
        try:
            from obra.config.explorer import run_explorer

            # Load local config to pass to explorer
            local_config = load_config()

            # Try to get server config if authenticated
            server_config: dict = {}
            api_client = None
            try:
                from obra.api_client import APIClient

                api_client = APIClient.from_config()
                config_data = api_client.get_user_config()
                server_config = config_data.get("resolved", {})
                server_config["_preset"] = config_data.get("preset", "unknown")
            except Exception:
                # Server unavailable or not authenticated - offline mode
                pass

            run_explorer(
                local_config=local_config,
                server_config=server_config,
                api_client=api_client,
            )
        except ImportError:
            print_error("Config explorer not available")
            console.print("\nUse 'obra config --show' to view current configuration.")
            console.print("Edit ~/.obra/client-config.yaml directly to make changes.")
            raise typer.Exit(1)

    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in config command")
        raise typer.Exit(1)


# =============================================================================
# Version Command
# =============================================================================


@app.command()
@handle_encoding_errors
def version(
    check_server: bool = typer.Option(
        False,
        "--check",
        "-c",
        help="Check server version compatibility",
    ),
) -> None:
    """Show version information.

    Displays the client version and optionally checks server compatibility.

    Examples:
        $ obra version
        $ obra version --check
    """
    console.print()
    console.print(f"[bold]Obra[/bold] v{__version__}")
    console.print()

    # Show Python version
    console.print(f"Python: {sys.version.split()[0]}")

    # Show platform
    import platform

    console.print(f"Platform: {platform.system()} {platform.release()}")

    if check_server:
        console.print()
        console.print("Checking server compatibility...")

        try:
            from obra.api import APIClient
            from obra.config import get_api_base_url

            # Create unauthenticated client for version check
            client = APIClient(base_url=get_api_base_url())

            try:
                server_info = client.get_version()

                console.print()
                console.print("[bold]Server Information[/bold]", style="cyan")

                table = Table(show_header=False, box=None)
                table.add_column("Field", style="dim")
                table.add_column("Value")

                table.add_row("Server Version", server_info.get("version", "N/A"))
                table.add_row("API Version", server_info.get("api_version", "N/A"))
                table.add_row("Status", server_info.get("status", "N/A"))

                console.print(table)

                # Check compatibility
                compatible = server_info.get("compatible", True)
                min_client = server_info.get("min_client_version", "0.0.0")

                console.print()
                if compatible:
                    print_success("Client is compatible with server")
                else:
                    print_warning(f"Client update required (minimum: {min_client})")
                    console.print("\nRun: pip install --upgrade obra")

            except APIError as e:
                if e.status_code == 0:
                    print_error("Cannot connect to server")
                    console.print("\nCheck your network connection.")
                else:
                    print_error(f"Server error: {e}")

        except Exception as e:
            print_error(f"Version check failed: {e}")
            logger.exception("Error checking server version")


# =============================================================================
# Plan Management Commands
# =============================================================================


@app.command("upload-plan")
@handle_encoding_errors
def upload_plan(
    file_path: Path = typer.Argument(..., help="Path to MACHINE_PLAN.yaml file to upload"),
    validate_only: bool = typer.Option(
        False,
        "--validate-only",
        help="Only validate the plan file without uploading",
    ),
) -> None:
    """Upload MACHINE_PLAN.yaml file to Obra SaaS.

    Validates and uploads a plan file to Firestore for later use.
    After upload, use the returned plan_id with 'obra derive --plan-id'.

    Examples:
        $ obra upload-plan docs/development/MY_PLAN.yaml
        $ obra upload-plan --validate-only plan.yaml

    Exit Codes:
        0: Upload successful or validation passed
        1: Upload failed or validation failed
    """
    try:
        command = UploadPlanCommand()
        exit_code = command.execute(str(file_path), validate_only)

        if exit_code != 0:
            raise typer.Exit(exit_code)

    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in upload-plan command")
        raise typer.Exit(1)


# Create plans subcommand group
plans_app = typer.Typer(
    name="plans",
    help="Manage uploaded plan files",
    no_args_is_help=True,
)
app.add_typer(plans_app, name="plans")


@plans_app.command("list")
@handle_encoding_errors
def plans_list(
    limit: int = typer.Option(
        50,
        "--limit",
        "-n",
        help="Maximum number of plans to list (max: 100)",
    ),
) -> None:
    """List uploaded plan files.

    Displays all plans uploaded by the current user, ordered by
    creation time (most recent first).

    Examples:
        $ obra plans list
        $ obra plans list --limit 10
    """
    try:
        from obra.api import APIClient
        from obra.auth import ensure_valid_token, get_current_auth

        # Ensure authenticated
        auth = get_current_auth()
        if not auth:
            print_error("Not logged in")
            console.print("\nRun 'obra login' to authenticate.")
            raise typer.Exit(1)

        ensure_valid_token()

        # Get plans from server
        client = APIClient.from_config()
        plans = client.list_plans(limit=limit)

        console.print()
        if not plans:
            print_info("No plans uploaded")
            console.print("\nUpload a plan with: [cyan]obra upload-plan path/to/plan.yaml[/cyan]")
            return

        console.print(f"[bold]Uploaded Plans[/bold] ({len(plans)} total)", style="cyan")
        console.print()

        table = Table()
        table.add_column("Plan ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Stories", justify="right")
        table.add_column("Uploaded", style="dim")

        for plan in plans:
            plan_id_short = plan.get("plan_id", "")[:8] + "..."
            name = plan.get("name", "N/A")
            story_count = str(plan.get("story_count", 0))
            created_at = plan.get("created_at", "N/A")

            # Format timestamp if it's ISO format
            if "T" in created_at:
                from datetime import datetime

                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    created_at = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass

            table.add_row(plan_id_short, name, story_count, created_at)

        console.print(table)
        console.print()
        console.print("[dim]Use with:[/dim] [cyan]obra derive --plan-id <plan_id> \"objective\"[/cyan]")

    except ObraError as e:
        display_obra_error(e, console)
        raise typer.Exit(1)
    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in plans list command")
        raise typer.Exit(1)


@plans_app.command("delete")
@handle_encoding_errors
def plans_delete(
    plan_id: str = typer.Argument(..., help="Plan ID to delete"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Delete an uploaded plan file.

    Permanently removes the plan from the server. This cannot be undone.
    Existing sessions using this plan are not affected.

    Examples:
        $ obra plans delete abc123-uuid
        $ obra plans delete abc123-uuid --force
    """
    try:
        from obra.api import APIClient
        from obra.auth import ensure_valid_token, get_current_auth

        # Ensure authenticated
        auth = get_current_auth()
        if not auth:
            print_error("Not logged in")
            console.print("\nRun 'obra login' to authenticate.")
            raise typer.Exit(1)

        ensure_valid_token()

        # Get plan details first
        client = APIClient.from_config()

        console.print()
        console.print(f"[dim]Fetching plan details...[/dim]")

        try:
            plan = client.get_plan(plan_id)
            plan_name = plan.get("name", "Unknown")
            story_count = plan.get("story_count", 0)

            console.print()
            console.print(f"[bold]Plan Details[/bold]", style="yellow")
            console.print(f"ID: {plan_id}")
            console.print(f"Name: {plan_name}")
            console.print(f"Stories: {story_count}")
            console.print()

        except ObraError:
            # Plan not found or error fetching - proceed with deletion anyway
            plan_name = "Unknown"

        # Confirm deletion
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to delete plan '{plan_name}'?",
                default=False,
            )
            if not confirm:
                console.print("Cancelled")
                return

        # Delete plan
        console.print(f"[dim]Deleting plan...[/dim]")
        result = client.delete_plan(plan_id)

        if result.get("success"):
            console.print()
            print_success(f"Plan deleted: {plan_name}")
        else:
            print_error("Failed to delete plan")
            raise typer.Exit(1)

    except ObraError as e:
        display_obra_error(e, console)
        raise typer.Exit(1)
    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in plans delete command")
        raise typer.Exit(1)


# =============================================================================
# Validation Commands
# =============================================================================


@app.command("validate-plan")
@handle_encoding_errors
def validate_plan(
    file_path: Path = typer.Argument(..., help="Path to MACHINE_PLAN.yaml file to validate"),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with additional details",
    ),
) -> None:
    """Validate YAML syntax of a MACHINE_PLAN.yaml file.

    Validates the specified plan file for YAML syntax errors and schema
    compliance. Displays detailed error messages with line/column numbers
    and helpful suggestions for fixing common issues.

    Examples:
        $ obra validate-plan docs/development/MY_PLAN.yaml
        $ obra validate-plan --verbose plan.yaml

    Exit Codes:
        0: Validation passed - file is valid
        1: Validation failed - file has errors
    """
    try:
        # Validate that file exists
        if not file_path.exists():
            print_error(f"File not found: {file_path}")
            raise typer.Exit(1)

        # Execute validation
        command = ValidatePlanCommand()
        exit_code = command.execute(str(file_path), verbose)

        # Exit with appropriate code
        if exit_code != 0:
            raise typer.Exit(exit_code)

    except Exception as e:
        display_error(e, console)
        logger.exception("Unexpected error in validate-plan command")
        raise typer.Exit(1)


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
