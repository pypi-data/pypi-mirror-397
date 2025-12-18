"""Revise handler for Hybrid Orchestrator.

This module handles the REVISE action from the server. It revises the current
plan based on issues identified during examination.

The revision process:
    1. Receive RevisionRequest with issues to address
    2. Build revision prompt with issues and guidance
    3. Invoke LLM to generate revised plan
    4. Parse revised plan items
    5. Return RevisedPlan to report to server

Related:
    - docs/design/prds/UNIFIED_HYBRID_ARCHITECTURE_PRD.md Section 1
    - obra/api/protocol.py
    - obra/hybrid/orchestrator.py
"""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from obra.api.protocol import RevisionRequest
from obra.display import console, print_info
from obra.hybrid.prompt_enricher import PromptEnricher
from obra.llm.cli_runner import invoke_llm_via_cli

logger = logging.getLogger(__name__)


class ReviseHandler:
    """Handler for REVISE action.

    Revises the current plan based on issues from examination.
    Returns updated plan items with changes summary.

    ## Architecture Context (ADR-027)

    This handler implements the two-tier prompting architecture where:
    - **Server (Tier 1)**: Generates strategic base prompts with revision guidance
    - **Client (Tier 2)**: Enriches base prompts with local tactical context

    **Implementation Flow**:
    1. Server sends RevisionRequest with base_prompt containing revision instructions
    2. Client enriches base_prompt via PromptEnricher (adds file structure, git log)
    3. Client invokes LLM with enriched prompt locally
    4. Client reports revised plan items and changes summary back to server

    ## IP Protection

    Strategic revision guidance (issue patterns, quality standards) stay on server.
    This protects Obra's proprietary quality assessment IP from client-side inspection.

    ## Privacy Protection

    Tactical context (file contents, git messages, errors) never sent to server.
    Only LLM revision results (revised plan and changes summary) is transmitted.

    See: docs/decisions/ADR-027-two-tier-prompting-architecture.md

    Example:
        >>> handler = ReviseHandler(Path("/path/to/project"))
        >>> request = RevisionRequest(
        ...     issues=[{"id": "I1", "description": "Missing error handling"}],
        ...     blocking_issues=[{"id": "I1", ...}]
        ... )
        >>> result = handler.handle(request)
        >>> print(result["plan_items"])
    """

    def __init__(
        self,
        working_dir: Path,
        on_stream: Optional[Callable[[str, str], None]] = None,
        llm_config: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize ReviseHandler.

        Args:
            working_dir: Working directory for file access
            on_stream: Optional callback for LLM streaming chunks (S3.T6)
            llm_config: Optional LLM configuration (S4.T4)
        """
        self._working_dir = working_dir
        self._on_stream = on_stream
        self._llm_config = llm_config or {}

    def handle(self, request: RevisionRequest) -> Dict[str, Any]:
        """Handle REVISE action.

        Args:
            request: RevisionRequest from server with base_prompt

        Returns:
            Dict with plan_items, changes_summary, and raw_response

        Raises:
            ValueError: If request.base_prompt is None (server must provide base_prompt)
        """
        logger.info(f"Revising plan to address {len(request.issues)} issues")
        print_info(f"Revising plan ({len(request.blocking_issues)} blocking issues)...")

        # Validate base_prompt (server-side prompting required)
        if request.base_prompt is None:
            error_msg = "RevisionRequest.base_prompt is None. Server must provide base prompt (ADR-027)."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Enrich base prompt with local tactical context
        enricher = PromptEnricher(self._working_dir)
        enriched_prompt = enricher.enrich(request.base_prompt)

        # Invoke LLM with enriched prompt
        raw_response = self._invoke_llm(enriched_prompt)

        # Parse revised plan
        plan_items, changes_summary = self._parse_revision(raw_response)

        logger.info(f"Revised plan has {len(plan_items)} items")
        print_info(f"Revised plan: {len(plan_items)} items")

        return {
            "plan_items": plan_items,
            "changes_summary": changes_summary,
            "raw_response": raw_response,
        }

    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM for revision.

        Args:
            prompt: Revision prompt

        Returns:
            Raw LLM response
        """
        provider = self._llm_config.get("provider", "anthropic")
        model = self._llm_config.get("model", "default")
        thinking_level = self._llm_config.get("thinking_level", "medium")

        logger.debug(f"Invoking LLM via CLI for revision: provider={provider} model={model}")

        def _stream(chunk: str) -> None:
            if self._on_stream:
                self._on_stream("llm_streaming", chunk)

        try:
            return invoke_llm_via_cli(
                prompt=prompt,
                cwd=self._working_dir,
                provider=provider,
                model=model,
                thinking_level=thinking_level,
                on_stream=_stream if self._on_stream else None,
            )
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return json.dumps(
                {
                    "plan_items": [],
                    "changes_summary": f"LLM error: {str(e)}",
                }
            )

    def _parse_revision(self, raw_response: str) -> tuple[List[Dict[str, Any]], str]:
        """Parse LLM response into revised plan.

        Args:
            raw_response: Raw LLM response

        Returns:
            Tuple of (plan_items, changes_summary)
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

            # Extract plan_items
            if isinstance(data, dict):
                items = data.get("plan_items", [])
                summary = data.get("changes_summary", "")
            elif isinstance(data, list):
                items = data
                summary = ""
            else:
                logger.warning("Unexpected response format")
                return [], ""

            # Validate and normalize items
            normalized = []
            for i, item in enumerate(items):
                normalized_item = {
                    "id": item.get("id", f"T{i + 1}"),
                    "item_type": item.get("item_type", "task"),
                    "title": item.get("title", "Untitled"),
                    "description": item.get("description", ""),
                    "acceptance_criteria": item.get("acceptance_criteria", []),
                    "dependencies": item.get("dependencies", []),
                }
                normalized.append(normalized_item)

            return normalized, summary

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse revision JSON: {e}")
            return [], f"Parse error: {str(e)}"


__all__ = ["ReviseHandler"]
