"""Derive handler for Hybrid Orchestrator.

This module handles the DERIVE action from the server. It takes an objective
and derives an implementation plan using the local LLM invocation.

The derivation process:
    1. Receive DeriveRequest with objective and context
    2. Gather local project context (files, structure, etc.)
    3. Invoke LLM to generate plan
    4. Parse structured output into plan items
    5. Return DerivedPlan to report to server

Related:
    - docs/design/prds/UNIFIED_HYBRID_ARCHITECTURE_PRD.md Section 1
    - obra/api/protocol.py
    - obra/hybrid/orchestrator.py
"""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from obra.api.protocol import DeriveRequest
from obra.display import console, print_info
from obra.hybrid.prompt_enricher import PromptEnricher
from obra.llm.cli_runner import invoke_llm_via_cli

logger = logging.getLogger(__name__)


class DeriveHandler:
    """Handler for DERIVE action.

    Derives an implementation plan from the objective using LLM.
    The plan is structured as a list of plan items (tasks/stories).

    ## Architecture Context (ADR-027)

    This handler implements the two-tier prompting architecture where:
    - **Server (Tier 1)**: Generates strategic base prompts with CLIENT_CONTEXT_MARKER
    - **Client (Tier 2)**: Enriches base prompts with local tactical context

    **Implementation Flow**:
    1. Server sends DeriveRequest with base_prompt containing strategic instructions
    2. Client enriches base_prompt via PromptEnricher (adds file structure, git log)
    3. Client invokes LLM with enriched prompt locally
    4. Client reports plan items and raw response back to server

    ## IP Protection

    Strategic prompt engineering (system patterns, quality standards) stays on server.
    This protects Obra's proprietary prompt engineering IP from client-side inspection.

    ## Privacy Protection

    Tactical context (file contents, git messages, errors) never sent to server.
    Only LLM response summary (plan items) is transmitted.

    See: docs/decisions/ADR-027-two-tier-prompting-architecture.md

    Example:
        >>> handler = DeriveHandler(Path("/path/to/project"))
        >>> request = DeriveRequest(objective="Add user authentication")
        >>> result = handler.handle(request)
        >>> print(result["plan_items"])
    """

    def __init__(
        self,
        working_dir: Path,
        on_stream: Optional[Callable[[str, str], None]] = None,
        llm_config: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize DeriveHandler.

        Args:
            working_dir: Working directory for file access
            on_stream: Optional callback for LLM streaming chunks (S3.T6)
            llm_config: Optional LLM configuration (S4.T2)
        """
        self._working_dir = working_dir
        self._on_stream = on_stream
        self._llm_config = llm_config or {}

    def handle(self, request: DeriveRequest) -> Dict[str, Any]:
        """Handle DERIVE action.

        Args:
            request: DeriveRequest from server with base_prompt

        Returns:
            Dict with plan_items and raw_response

        Raises:
            ValueError: If request.base_prompt is None (server must provide base_prompt)
        """
        logger.info(f"Deriving plan for: {request.objective[:50]}...")
        print_info(f"Deriving plan for: {request.objective[:50]}...")

        # Validate base_prompt (server-side prompting required)
        if request.base_prompt is None:
            error_msg = "DeriveRequest.base_prompt is None. Server must provide base prompt (ADR-027)."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Enrich base prompt with local tactical context
        enricher = PromptEnricher(self._working_dir)
        enriched_prompt = enricher.enrich(request.base_prompt)

        # Invoke LLM with enriched prompt
        raw_response = self._invoke_llm(enriched_prompt, request.llm_provider)

        # Parse response into plan items
        plan_items = self._parse_plan(raw_response)

        logger.info(f"Derived {len(plan_items)} plan items")
        print_info(f"Derived {len(plan_items)} plan items")

        return {
            "plan_items": plan_items,
            "raw_response": raw_response,
        }

    def _invoke_llm(self, prompt: str, provider: str) -> str:
        """Invoke LLM to generate plan.

        Args:
            prompt: Derivation prompt
            provider: LLM provider name

        Returns:
            Raw LLM response
        """
        provider = self._llm_config.get("provider", provider)
        model = self._llm_config.get("model", "default")
        thinking_level = self._llm_config.get("thinking_level", "medium")

        logger.debug(f"Invoking LLM via CLI: provider={provider} model={model} thinking={thinking_level}")

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
                    "plan_items": [
                        {
                            "id": "ERROR",
                            "item_type": "task",
                            "title": "LLM Error",
                            "description": f"LLM invocation failed: {str(e)}",
                            "acceptance_criteria": [],
                            "dependencies": [],
                        }
                    ]
                }
            )

    def _parse_plan(self, raw_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into plan items.

        Args:
            raw_response: Raw LLM response

        Returns:
            List of plan item dictionaries
        """
        try:
            # Try to extract JSON from response
            # Handle case where response might have markdown code blocks
            response = raw_response.strip()

            if response.startswith("```"):
                # Extract from code block
                lines = response.split("\n")
                start = 1 if lines[0].startswith("```") else 0
                end = len(lines) - 1 if lines[-1] == "```" else len(lines)
                response = "\n".join(lines[start:end])

            # Parse JSON
            data = json.loads(response)

            # Extract plan_items
            if isinstance(data, dict) and "plan_items" in data:
                items = data["plan_items"]
            elif isinstance(data, list):
                items = data
            else:
                logger.warning("Unexpected response format, wrapping as single item")
                items = [data]

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

            return normalized

        except json.JSONDecodeError as e:
            return self._create_parse_error_fallback(raw_response, e)

    def _create_parse_error_fallback(
        self, raw_response: str, error: json.JSONDecodeError
    ) -> List[Dict[str, Any]]:
        """Create diagnostic fallback plan when JSON parsing fails.

        Args:
            raw_response: The raw response that failed to parse
            error: The JSONDecodeError exception

        Returns:
            List containing single diagnostic task with actionable information
        """
        # Analyze the response to provide helpful diagnostics
        response_length = len(raw_response)
        trimmed = raw_response.strip()
        is_empty = response_length == 0 or len(trimmed) == 0

        # Extract first few characters for preview (safely handle empty)
        preview = trimmed[:100] if trimmed else "(empty response)"
        if len(trimmed) > 100:
            preview += "..."

        # Build diagnostic description
        description_parts = [
            "**LLM Response Parse Error**",
            "",
            f"**Error**: {error.msg}",
            f"**Position**: Line {error.lineno}, Column {error.colno}",
            "",
        ]

        if is_empty:
            description_parts.extend([
                "**Issue**: The LLM returned an empty response.",
                "",
                "**Possible Causes**:",
                "- LLM CLI failed silently without error code",
                "- Response was filtered or truncated",
                "- Timeout or connection issue during streaming",
                "",
                "**Recommended Actions**:",
                "1. Check LLM provider logs for errors",
                "2. Verify LLM CLI is properly configured (`obra config`)",
                "3. Test LLM connection directly (e.g., `claude --version`)",
                "4. Try again with `--verbose` flag for detailed output",
            ])
        else:
            description_parts.extend([
                "**Response Preview**:",
                f"```",
                f"{preview}",
                f"```",
                "",
                f"**Response Length**: {response_length} characters",
                "",
                "**Possible Causes**:",
                "- LLM returned natural language instead of JSON",
                "- Response format changed or is malformed",
                "- Code block markers (```) not properly removed",
                "",
                "**Recommended Actions**:",
                "1. Review the raw response in session logs",
                "2. Check if LLM is using correct output format",
                "3. Try with different LLM provider or model",
                "4. Report issue if this persists",
            ])

        description = "\n".join(description_parts)

        logger.error(
            f"Failed to parse plan JSON: {error}. "
            f"Response length: {response_length}, "
            f"Is empty: {is_empty}, "
            f"Preview: {preview}"
        )

        # Return diagnostic fallback item
        return [
            {
                "id": "PARSE_ERROR",
                "item_type": "task",
                "title": "LLM Response Parse Error - Manual Review Required",
                "description": description,
                "acceptance_criteria": [
                    "Investigate root cause of parse error",
                    "Verify LLM configuration is correct",
                    "Retry derivation with corrected setup",
                ],
                "dependencies": [],
            }
        ]


__all__ = ["DeriveHandler"]
