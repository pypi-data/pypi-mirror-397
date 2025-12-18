"""Examine handler for Hybrid Orchestrator.

This module handles the EXAMINE action from the server. It examines the current
plan using LLM to identify issues that need to be addressed.

The examination process:
    1. Receive ExamineRequest with plan to examine
    2. Build examination prompt with IP-protected criteria from server
    3. Invoke LLM with extended thinking if required
    4. Parse structured issues from response
    5. Return ExaminationReport to report to server

Related:
    - docs/design/prds/UNIFIED_HYBRID_ARCHITECTURE_PRD.md Section 1
    - obra/api/protocol.py
    - obra/hybrid/orchestrator.py
"""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from obra.api.protocol import ExamineRequest
from obra.display import console, print_info
from obra.hybrid.prompt_enricher import PromptEnricher
from obra.llm.cli_runner import invoke_llm_via_cli

logger = logging.getLogger(__name__)


class ExamineHandler:
    """Handler for EXAMINE action.

    Examines the current plan using LLM to identify issues.
    Issues are categorized and assigned severity levels.

    ## Architecture Context (ADR-027)

    This handler implements the two-tier prompting architecture where:
    - **Server (Tier 1)**: Generates strategic base prompts with examination criteria
    - **Client (Tier 2)**: Enriches base prompts with local tactical context

    **Implementation Flow**:
    1. Server sends ExamineRequest with base_prompt containing examination criteria
    2. Client enriches base_prompt via PromptEnricher (adds file structure, git log)
    3. Client invokes LLM with enriched prompt locally
    4. Client reports issues back to server for validation

    ## IP Protection

    Strategic examination criteria (quality standards, issue patterns) stay on server.
    This protects Obra's proprietary quality assessment IP from client-side inspection.

    ## Privacy Protection

    Tactical context (file contents, git messages, errors) never sent to server.
    Only LLM examination results (issues summary) is transmitted.

    See: docs/decisions/ADR-027-two-tier-prompting-architecture.md

    Example:
        >>> handler = ExamineHandler(Path("/path/to/project"))
        >>> request = ExamineRequest(
        ...     plan_version_id="v1",
        ...     plan_items=[{"id": "T1", "title": "Task 1", ...}]
        ... )
        >>> result = handler.handle(request)
        >>> print(result["issues"])
    """

    def __init__(
        self,
        working_dir: Path,
        on_stream: Optional[Callable[[str, str], None]] = None,
        llm_config: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize ExamineHandler.

        Args:
            working_dir: Working directory for file access
            on_stream: Optional callback for LLM streaming chunks (S3.T6)
            llm_config: Optional LLM configuration (S4.T3)
        """
        self._working_dir = working_dir
        self._on_stream = on_stream
        self._llm_config = llm_config or {}

    def handle(self, request: ExamineRequest) -> Dict[str, Any]:
        """Handle EXAMINE action.

        Args:
            request: ExamineRequest from server with base_prompt

        Returns:
            Dict with issues, thinking_budget_used, and raw_response

        Raises:
            ValueError: If request.base_prompt is None (server must provide base_prompt)
        """
        logger.info(f"Examining plan version: {request.plan_version_id}")
        print_info(f"Examining plan ({len(request.plan_items)} items)...")

        # Validate base_prompt (server-side prompting required)
        if request.base_prompt is None:
            error_msg = "ExamineRequest.base_prompt is None. Server must provide base prompt (ADR-027)."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Enrich base prompt with local tactical context
        enricher = PromptEnricher(self._working_dir)
        enriched_prompt = enricher.enrich(request.base_prompt)

        # Invoke LLM with thinking if required
        raw_response, thinking_used, thinking_fallback = self._invoke_llm(
            enriched_prompt,
            request.thinking_required,
            request.thinking_level,
        )

        # Parse issues from response
        issues = self._parse_issues(raw_response)

        logger.info(f"Found {len(issues)} issues")
        print_info(f"Found {len(issues)} issues")

        # Log blocking issues
        blocking = [i for i in issues if i.get("severity") in ("P0", "P1", "critical", "high")]
        if blocking:
            logger.info(f"  Blocking issues: {len(blocking)}")
            print_info(f"  Blocking issues: {len(blocking)}")

        return {
            "issues": issues,
            "thinking_budget_used": thinking_used,
            "thinking_fallback": thinking_fallback,
            "raw_response": raw_response,
            "iteration": 0,  # Server tracks iteration
        }

    def _invoke_llm(
        self,
        prompt: str,
        thinking_required: bool,
        thinking_level: str,
    ) -> tuple[str, int, bool]:
        """Invoke LLM for examination.

        Args:
            prompt: Examination prompt
            thinking_required: Whether extended thinking is required
            thinking_level: Thinking level (standard, high, max)

        Returns:
            Tuple of (raw_response, thinking_tokens_used, thinking_fallback)
        """
        provider = self._llm_config.get("provider", "anthropic")
        model = self._llm_config.get("model", "default")
        resolved_thinking_level = self._llm_config.get("thinking_level", "medium")
        if not thinking_required:
            resolved_thinking_level = "off"

        logger.debug(
            f"Invoking LLM via CLI: provider={provider} model={model} "
            f"thinking_required={thinking_required} requested_level={thinking_level}"
        )

        def _stream(chunk: str) -> None:
            if self._on_stream:
                self._on_stream("llm_streaming", chunk)

        try:
            response = invoke_llm_via_cli(
                prompt=prompt,
                cwd=self._working_dir,
                provider=provider,
                model=model,
                thinking_level=resolved_thinking_level,
                on_stream=_stream if self._on_stream else None,
            )
            return response, 0, False
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return json.dumps({"issues": []}), 0, False

    def _parse_issues(self, raw_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into issues list.

        Args:
            raw_response: Raw LLM response

        Returns:
            List of issue dictionaries
        """
        try:
            # Try to extract JSON from response
            response = raw_response.strip()

            if response.startswith("```"):
                lines = response.split("\n")
                start = 1 if lines[0].startswith("```") else 0
                end = len(lines) - 1 if lines[-1] == "```" else len(lines)
                response = "\n".join(lines[start:end])

            # Parse JSON
            data = json.loads(response)

            # Extract issues
            if isinstance(data, dict) and "issues" in data:
                issues = data["issues"]
            elif isinstance(data, list):
                issues = data
            else:
                logger.warning("Unexpected response format")
                return []

            # Validate and normalize issues
            normalized = []
            for i, issue in enumerate(issues):
                normalized_issue = {
                    "id": issue.get("id", f"I{i + 1}"),
                    "category": issue.get("category", "other"),
                    "severity": self._normalize_severity(issue.get("severity", "low")),
                    "description": issue.get("description", ""),
                    "affected_items": issue.get("affected_items", []),
                }
                normalized.append(normalized_issue)

            return normalized

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse issues JSON: {e}")
            return []

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity string.

        Args:
            severity: Raw severity string

        Returns:
            Normalized severity (critical, high, medium, low, or P0-P3)
        """
        severity_lower = severity.lower()

        # Map common severity strings
        mapping = {
            "critical": "critical",
            "p0": "P0",
            "blocker": "critical",
            "high": "high",
            "p1": "P1",
            "major": "high",
            "medium": "medium",
            "p2": "P2",
            "minor": "medium",
            "low": "low",
            "p3": "P3",
            "trivial": "low",
        }

        return mapping.get(severity_lower, severity)


__all__ = ["ExamineHandler"]
