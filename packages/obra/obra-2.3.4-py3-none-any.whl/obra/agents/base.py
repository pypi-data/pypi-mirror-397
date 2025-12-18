"""Base class and types for review agents.

This module defines the BaseAgent abstract class and AgentResult dataclass
that all review agents must implement.

Agent Architecture:
    - Agents are lightweight, stateless workers
    - Each agent runs as a subprocess for isolation
    - Agents analyze code and return structured results
    - Results include issues (with priority) and dimension scores

Related:
    - obra/agents/deployer.py
    - obra/api/protocol.py
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from obra.api.protocol import AgentType, Priority

logger = logging.getLogger(__name__)


@dataclass
class AgentIssue:
    """Issue found by a review agent.

    Attributes:
        id: Unique issue identifier
        title: Short description of the issue
        description: Detailed description
        priority: Issue priority (P0-P3)
        file_path: File where issue was found (if applicable)
        line_number: Line number (if applicable)
        dimension: Quality dimension (security, testing, docs, maintainability)
        suggestion: Suggested fix
        metadata: Additional metadata
    """

    id: str
    title: str
    description: str
    priority: Priority
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    dimension: str = ""
    suggestion: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "dimension": self.dimension,
            "suggestion": self.suggestion,
            "metadata": self.metadata,
        }


@dataclass
class AgentResult:
    """Result from agent execution.

    Attributes:
        agent_type: Type of agent that produced this result
        status: Execution status (complete, timeout, error)
        issues: List of issues found
        scores: Dimension scores (0.0 - 1.0)
        execution_time_ms: Time taken in milliseconds
        error: Error message if status is error
        metadata: Additional metadata
    """

    agent_type: AgentType
    status: str  # complete, timeout, error
    issues: List[AgentIssue] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    execution_time_ms: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "agent_type": self.agent_type.value,
            "status": self.status,
            "issues": [issue.to_dict() for issue in self.issues],
            "scores": self.scores,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """Abstract base class for review agents.

    All review agents must implement this interface. Agents analyze code
    in a workspace and return structured results with issues and scores.

    Implementing a new agent:
        1. Subclass BaseAgent
        2. Implement analyze() method
        3. Register with AgentRegistry
        4. Add to obra/agents/__init__.py

    Example:
        >>> class MyAgent(BaseAgent):
        ...     agent_type = AgentType.SECURITY
        ...
        ...     def analyze(self, item_id, changed_files, timeout_ms):
        ...         issues = self._check_for_issues(changed_files)
        ...         scores = self._calculate_scores(changed_files)
        ...         return AgentResult(
        ...             agent_type=self.agent_type,
        ...             status="complete",
        ...             issues=issues,
        ...             scores=scores
        ...         )
    """

    # Subclasses must set this
    agent_type: AgentType

    def __init__(self, working_dir: Path) -> None:
        """Initialize agent.

        Args:
            working_dir: Working directory containing code to analyze
        """
        self._working_dir = working_dir
        logger.debug(f"Initialized {self.__class__.__name__} for {working_dir}")

    @property
    def working_dir(self) -> Path:
        """Get working directory."""
        return self._working_dir

    @abstractmethod
    def analyze(
        self,
        item_id: str,
        changed_files: Optional[List[str]] = None,
        timeout_ms: int = 60000,
    ) -> AgentResult:
        """Analyze code and return results.

        This is the main entry point for agent execution. Agents should
        analyze the code in working_dir and return issues and scores.

        Args:
            item_id: Plan item ID being reviewed
            changed_files: List of files that changed (optional, for focused review)
            timeout_ms: Maximum execution time in milliseconds

        Returns:
            AgentResult with issues and scores

        Raises:
            TimeoutError: If analysis exceeds timeout_ms
            Exception: If analysis fails
        """
        pass

    def get_files_to_analyze(
        self,
        changed_files: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
    ) -> List[Path]:
        """Get list of files to analyze.

        Args:
            changed_files: If provided, only analyze these files
            extensions: If provided, filter by file extensions (e.g., [".py", ".js"])

        Returns:
            List of file paths to analyze
        """
        if changed_files:
            # Filter to existing files
            files = []
            for f in changed_files:
                path = self._working_dir / f if not Path(f).is_absolute() else Path(f)
                if path.exists() and path.is_file():
                    files.append(path)
            return files

        # Scan all files in working directory
        files = []
        ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            ".tox",
            ".mypy_cache",
            ".pytest_cache",
            "dist",
            "build",
        }

        for path in self._working_dir.rglob("*"):
            # Skip ignored directories
            if any(part in ignore_dirs for part in path.parts):
                continue

            if not path.is_file():
                continue

            # Filter by extension if specified
            if extensions and path.suffix not in extensions:
                continue

            files.append(path)

        return files

    def read_file(self, path: Path) -> str:
        """Read file contents safely.

        Args:
            path: Path to file

        Returns:
            File contents or empty string if unreadable
        """
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not read {path}: {e}")
            return ""

    def _generate_issue_id(self, prefix: str, index: int) -> str:
        """Generate unique issue ID.

        Args:
            prefix: Agent prefix (e.g., "SEC", "TEST")
            index: Issue index

        Returns:
            Unique issue ID (e.g., "SEC-001")
        """
        return f"{prefix}-{index:03d}"


__all__ = ["BaseAgent", "AgentResult", "AgentIssue"]
