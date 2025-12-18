"""Client-side protocol types for Hybrid Architecture.

This module mirrors the server-side protocol types from
functions/src/orchestration/coordinator.py and functions/src/state/session_schema.py.

Protocol Design (from PRD Section 1):
    - Server owns the brain (decisions, orchestration logic)
    - Client owns the hands (execution, code access)

Message Flow:
    Client -> Server: SessionStart, DerivedPlan, ExaminationReport,
                     RevisedPlan, ExecutionResult, AgentReport, FixResult, UserDecision
    Server -> Client: DeriveRequest, ExamineRequest, RevisionRequest,
                     ExecutionRequest, ReviewRequest, FixRequest, EscalationNotice,
                     CompletionNotice

Related:
    - docs/design/prds/UNIFIED_HYBRID_ARCHITECTURE_PRD.md Section 1
    - functions/src/orchestration/coordinator.py
    - functions/src/state/session_schema.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# Enums
# =============================================================================


class ActionType(str, Enum):
    """Server action types (server instructs client)."""

    DERIVE = "derive"  # Derive plan from objective
    EXAMINE = "examine"  # Examine current plan
    REVISE = "revise"  # Revise plan based on issues
    EXECUTE = "execute"  # Execute plan item
    REVIEW = "review"  # Run review agents
    FIX = "fix"  # Fix issues found in review
    COMPLETE = "complete"  # Session complete
    ESCALATE = "escalate"  # Escalate to human
    WAIT = "wait"  # Wait for async operation
    ERROR = "error"  # Error occurred


class SessionPhase(str, Enum):
    """Current phase of the orchestration session."""

    DERIVATION = "derivation"
    REFINEMENT = "refinement"
    EXECUTION = "execution"
    REVIEW = "review"


class SessionStatus(str, Enum):
    """Session status values."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


class Priority(str, Enum):
    """Priority classification for issues."""

    P0 = "P0"  # Critical - blocks execution
    P1 = "P1"  # High - should be fixed
    P2 = "P2"  # Medium - nice to fix
    P3 = "P3"  # Low - informational


class ExecutionStatus(str, Enum):
    """Status of plan item execution."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class AgentType(str, Enum):
    """Types of review agents."""

    SECURITY = "security"
    TESTING = "testing"
    DOCS = "docs"
    CODE_QUALITY = "code_quality"


class EscalationReason(str, Enum):
    """Reasons for escalation."""

    MAX_ITERATIONS = "max_iterations"
    OSCILLATION = "oscillation"
    USER_REQUESTED = "user_requested"
    BLOCKED = "blocked"


class UserDecisionChoice(str, Enum):
    """User decision options during escalation."""

    FORCE_COMPLETE = "force_complete"
    CONTINUE_FIXING = "continue_fixing"
    ABANDON = "abandon"


# =============================================================================
# Server -> Client Message Types
# =============================================================================


@dataclass
class ServerAction:
    """Action instruction from server to client.

    This is the base response type from the server. The `action` field
    determines what the client should do next, and `payload` contains
    action-specific data.

    Attributes:
        action: Action type to perform
        session_id: Session identifier
        iteration: Current iteration number
        payload: Action-specific data
        metadata: Additional metadata
        bypass_modes_active: List of active bypass modes (for warnings)
        error_code: Error code if action is ERROR
        error_message: Error message if action is ERROR
    """

    action: ActionType
    session_id: str
    iteration: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    bypass_modes_active: List[str] = field(default_factory=list)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerAction":
        """Create from API response dictionary."""
        return cls(
            action=ActionType(data.get("action", "error")),
            session_id=data.get("session_id", ""),
            iteration=data.get("iteration", 0),
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {}),
            bypass_modes_active=data.get("bypass_modes_active", []),
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
            timestamp=data.get("timestamp"),
        )

    def is_error(self) -> bool:
        """Check if this is an error action."""
        return self.action == ActionType.ERROR or self.error_code is not None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API response format."""
        from datetime import datetime, timezone

        ts = self.timestamp or datetime.now(timezone.utc).isoformat()
        return {
            "action": self.action.value,
            "session_id": self.session_id,
            "iteration": self.iteration,
            "payload": self.payload,
            "metadata": self.metadata,
            "bypass_modes_active": self.bypass_modes_active,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "timestamp": ts,
        }


@dataclass
class DeriveRequest:
    """Request to derive a plan from objective.

    Sent by server after SessionStart to instruct client
    to derive an implementation plan.

    Attributes:
        objective: Task objective to plan for
        project_context: Project context (languages, frameworks, etc.)
        llm_provider: LLM provider to use
        constraints: Derivation constraints
        base_prompt: Optional base prompt from server (ADR-027 two-tier prompting)
    """

    objective: str
    project_context: Dict[str, Any] = field(default_factory=dict)
    llm_provider: str = "anthropic"
    constraints: Dict[str, Any] = field(default_factory=dict)
    base_prompt: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "DeriveRequest":
        """Create from ServerAction payload."""
        return cls(
            objective=payload.get("objective", ""),
            project_context=payload.get("project_context", {}),
            llm_provider=payload.get("llm_provider", "anthropic"),
            constraints=payload.get("constraints", {}),
            base_prompt=payload.get("base_prompt"),
        )


@dataclass
class ExamineRequest:
    """Request to examine the current plan.

    Sent by server after DerivedPlan or RevisedPlan to instruct
    client to examine the plan using LLM.

    Attributes:
        plan_version_id: Version ID of plan to examine
        plan_items: Plan items to examine
        thinking_required: Whether extended thinking is required
        thinking_level: Thinking level (standard, high, max)
        base_prompt: Optional base prompt from server (ADR-027 two-tier prompting)
    """

    plan_version_id: str
    plan_items: List[Dict[str, Any]]
    thinking_required: bool = True
    thinking_level: str = "standard"
    base_prompt: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "ExamineRequest":
        """Create from ServerAction payload."""
        return cls(
            plan_version_id=payload.get("plan_version_id", ""),
            plan_items=payload.get("plan_items", []),
            thinking_required=payload.get("thinking_required", True),
            thinking_level=payload.get("thinking_level", "standard"),
            base_prompt=payload.get("base_prompt"),
        )


@dataclass
class RevisionRequest:
    """Request to revise the plan based on issues.

    Sent by server after ExaminationReport when blocking issues found.

    Attributes:
        issues: All issues from examination
        blocking_issues: Issues that must be addressed
        current_plan_version_id: Current plan version ID
        focus_areas: Areas to focus revision on
        base_prompt: Optional base prompt from server (ADR-027 two-tier prompting)
    """

    issues: List[Dict[str, Any]]
    blocking_issues: List[Dict[str, Any]]
    current_plan_version_id: str = ""
    focus_areas: List[str] = field(default_factory=list)
    base_prompt: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "RevisionRequest":
        """Create from ServerAction payload."""
        return cls(
            issues=payload.get("issues", []),
            blocking_issues=payload.get("blocking_issues", []),
            current_plan_version_id=payload.get("current_plan_version_id", ""),
            focus_areas=payload.get("focus_areas", []),
            base_prompt=payload.get("base_prompt"),
        )


@dataclass
class ExecutionRequest:
    """Request to execute a plan item.

    Sent by server when plan passes examination.

    Attributes:
        plan_items: All plan items
        execution_index: Index of item to execute
        current_item: The specific item to execute
        base_prompt: Optional base prompt from server (ADR-027 two-tier prompting)
    """

    plan_items: List[Dict[str, Any]]
    execution_index: int = 0
    current_item: Optional[Dict[str, Any]] = None
    base_prompt: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "ExecutionRequest":
        """Create from ServerAction payload."""
        plan_items = payload.get("plan_items", [])
        execution_index = payload.get("execution_index", 0)
        current_item = None
        if plan_items and not (0 <= execution_index < len(plan_items)):
            # Defensive fallback for partial plan payloads.
            execution_index = 0
        if plan_items and 0 <= execution_index < len(plan_items):
            current_item = plan_items[execution_index]
        return cls(
            plan_items=plan_items,
            execution_index=execution_index,
            current_item=current_item,
            base_prompt=payload.get("base_prompt"),
        )


@dataclass
class ReviewRequest:
    """Request to run review agents on executed item.

    Sent by server after ExecutionResult.

    Attributes:
        item_id: Plan item ID that was executed
        agents_to_run: List of agent types to run
        agent_budgets: Timeout/weight budgets per agent
    """

    item_id: str
    agents_to_run: List[str] = field(default_factory=list)
    agent_budgets: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "ReviewRequest":
        """Create from ServerAction payload."""
        return cls(
            item_id=payload.get("item_id", ""),
            agents_to_run=payload.get("agents_to_run", ["security", "testing", "docs", "code_quality"]),
            agent_budgets=payload.get("agent_budgets", {}),
        )


@dataclass
class FixRequest:
    """Request to fix issues found during review.

    Sent by server after AgentReport when issues need fixing.

    Attributes:
        issues_to_fix: List of issues to fix
        execution_order: Order to fix issues (by ID)
        base_prompt: Optional base prompt from server (ADR-027 two-tier prompting)
    """

    issues_to_fix: List[Dict[str, Any]]
    execution_order: List[str] = field(default_factory=list)
    base_prompt: Optional[str] = None

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "FixRequest":
        """Create from ServerAction payload."""
        return cls(
            issues_to_fix=payload.get("issues_to_fix", []),
            execution_order=payload.get("execution_order", []),
            base_prompt=payload.get("base_prompt"),
        )


@dataclass
class EscalationNotice:
    """Notice that session requires human intervention.

    Sent by server when max iterations reached or oscillation detected.

    Attributes:
        escalation_id: Unique escalation identifier
        reason: Reason for escalation
        blocking_issues: Issues causing escalation
        iteration_history: Summary of iterations
        options: Available user options
    """

    escalation_id: str
    reason: EscalationReason
    blocking_issues: List[Dict[str, Any]] = field(default_factory=list)
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    options: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "EscalationNotice":
        """Create from ServerAction payload."""
        return cls(
            escalation_id=payload.get("escalation_id", ""),
            reason=EscalationReason(payload.get("reason", "blocked")),
            blocking_issues=payload.get("blocking_issues", []),
            iteration_history=payload.get("iteration_history", []),
            options=payload.get("options", []),
        )


@dataclass
class CompletionNotice:
    """Notice that session has completed successfully.

    Sent by server when all items executed and reviewed.

    Attributes:
        session_summary: Summary of completed session
        items_completed: Number of items completed
        total_iterations: Total refinement iterations
        quality_score: Final quality score
    """

    session_summary: str = ""
    items_completed: int = 0
    total_iterations: int = 0
    quality_score: float = 0.0
    plan_final: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "CompletionNotice":
        """Create from ServerAction payload."""
        summary = payload.get("session_summary", {})
        return cls(
            session_summary=summary.get("objective", ""),
            items_completed=summary.get("items_completed", 0),
            total_iterations=summary.get("total_iterations", 0),
            quality_score=summary.get("quality_score", 0.0),
            plan_final=payload.get("plan_final", []),
        )


# =============================================================================
# Client -> Server Message Types
# =============================================================================


@dataclass
class PlanUploadRequest:
    """Request to upload a plan file to server.

    Sent by client to upload a MACHINE_PLAN.yaml file for reuse.

    Attributes:
        name: Plan name (typically work_id from YAML)
        plan_data: Parsed YAML structure (dict representation)
    """

    name: str
    plan_data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "name": self.name,
            "plan_data": self.plan_data,
        }


@dataclass
class PlanUploadResponse:
    """Response from plan upload operation.

    Sent by server after successful plan storage.

    Attributes:
        plan_id: UUID identifier for the uploaded plan
        name: Plan name (echoed from request)
        story_count: Number of stories in the plan
    """

    plan_id: str
    name: str
    story_count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanUploadResponse":
        """Create from API response dictionary."""
        return cls(
            plan_id=data.get("plan_id", ""),
            name=data.get("name", ""),
            story_count=data.get("story_count", 0),
        )


@dataclass
class SessionStart:
    """Start a new orchestration session.

    Sent by client to initiate a new session.

    Attributes:
        objective: Task objective
        project_hash: SHA256 hash of project path (privacy)
        project_context: Project context (languages, frameworks, etc.)
        client_version: Client version string
        llm_provider: LLM provider to use
        plan_id: Optional reference to uploaded plan (for plan import workflow)
    """

    objective: str
    project_hash: str
    project_context: Dict[str, Any] = field(default_factory=dict)
    client_version: str = ""
    llm_provider: str = "anthropic"
    plan_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        result = {
            "objective": self.objective,
            "project_hash": self.project_hash,
            "project_context": self.project_context,
            "client_version": self.client_version,
            "llm_provider": self.llm_provider,
        }
        if self.plan_id is not None:
            result["plan_id"] = self.plan_id
        return result


@dataclass
class DerivedPlan:
    """Report derived plan to server.

    Sent by client after completing derivation.

    Attributes:
        session_id: Session identifier
        plan_items: Derived plan items
        raw_response: Raw LLM response (for debugging)
    """

    session_id: str
    plan_items: List[Dict[str, Any]]
    raw_response: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "session_id": self.session_id,
            "plan_items": self.plan_items,
            "raw_response": self.raw_response,
        }


@dataclass
class ExaminationReport:
    """Report examination results to server.

    Sent by client after completing LLM examination.

    Attributes:
        session_id: Session identifier
        iteration: Examination iteration number
        issues: Issues found during examination
        thinking_budget_used: Tokens used for extended thinking
        thinking_fallback: Whether thinking mode fell back
        raw_response: Raw LLM response
    """

    session_id: str
    iteration: int
    issues: List[Dict[str, Any]]
    thinking_budget_used: int = 0
    thinking_fallback: bool = False
    raw_response: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "issues": self.issues,
            "thinking_budget_used": self.thinking_budget_used,
            "thinking_fallback": self.thinking_fallback,
            "raw_response": self.raw_response,
        }


@dataclass
class RevisedPlan:
    """Report revised plan to server.

    Sent by client after completing revision.

    Attributes:
        session_id: Session identifier
        plan_items: Revised plan items
        changes_summary: Summary of changes made
        raw_response: Raw LLM response
    """

    session_id: str
    plan_items: List[Dict[str, Any]]
    changes_summary: str = ""
    raw_response: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "session_id": self.session_id,
            "plan_items": self.plan_items,
            "changes_summary": self.changes_summary,
            "raw_response": self.raw_response,
        }


@dataclass
class ExecutionResult:
    """Report execution result to server.

    Sent by client after executing a plan item.

    Attributes:
        session_id: Session identifier
        item_id: Plan item ID that was executed
        status: Execution status (success, failure, partial)
        summary: LLM-generated summary
        files_changed: Number of files changed
        tests_passed: Whether tests passed
        test_count: Number of tests run
        coverage_delta: Change in coverage percentage
    """

    session_id: str
    item_id: str
    status: ExecutionStatus
    summary: str = ""
    files_changed: int = 0
    tests_passed: bool = False
    test_count: int = 0
    coverage_delta: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "session_id": self.session_id,
            "item_id": self.item_id,
            "status": self.status.value,
            "summary": self.summary,
            "files_changed": self.files_changed,
            "tests_passed": self.tests_passed,
            "test_count": self.test_count,
            "coverage_delta": self.coverage_delta,
        }


@dataclass
class AgentReport:
    """Report review agent results to server.

    Sent by client after running review agents.

    Attributes:
        session_id: Session identifier
        item_id: Plan item ID that was reviewed
        agent_type: Type of agent (security, testing, docs, code_quality)
        execution_time_ms: Time taken by agent
        status: Agent execution status
        issues: Issues found by agent
        scores: Dimension scores (0.0 - 1.0)
    """

    session_id: str
    item_id: str
    agent_type: AgentType
    execution_time_ms: int
    status: str  # complete, timeout, error
    issues: List[Dict[str, Any]] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "session_id": self.session_id,
            "item_id": self.item_id,
            "agent_type": self.agent_type.value,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status,
            "issues": self.issues,
            "scores": self.scores,
        }


@dataclass
class FixResult:
    """Report fix attempt result to server.

    Sent by client after attempting to fix an issue.

    Attributes:
        session_id: Session identifier
        issue_id: Issue ID that was fixed
        status: Fix status (fixed, failed, skipped)
        files_modified: List of modified file paths
        verification: Verification results
    """

    session_id: str
    issue_id: str
    status: str  # fixed, failed, skipped
    files_modified: List[str] = field(default_factory=list)
    verification: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "session_id": self.session_id,
            "issue_id": self.issue_id,
            "status": self.status,
            "files_modified": self.files_modified,
            "verification": self.verification,
        }


@dataclass
class UserDecision:
    """Report user decision during escalation.

    Sent by client when user responds to escalation.

    Attributes:
        session_id: Session identifier
        escalation_id: Escalation identifier
        decision: User's decision
        reason: Optional reason for decision
    """

    session_id: str
    escalation_id: str
    decision: UserDecisionChoice
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request dictionary."""
        return {
            "session_id": self.session_id,
            "escalation_id": self.escalation_id,
            "decision": self.decision.value,
            "reason": self.reason,
        }


# =============================================================================
# Resume Context
# =============================================================================


@dataclass
class ResumeContext:
    """Context for resuming an interrupted session.

    Returned by GET /session/{id} endpoint.

    Attributes:
        session_id: Session identifier
        status: Session status
        current_phase: Current phase
        can_resume: Whether session can be resumed
        last_successful_step: Description of last successful step
        pending_action: Human-readable pending action
        resume_instructions: Instructions for resuming
    """

    session_id: str
    status: SessionStatus
    current_phase: SessionPhase
    can_resume: bool = False
    last_successful_step: str = ""
    pending_action: str = ""
    resume_instructions: str = ""
    awaiting_message: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResumeContext":
        """Create from API response dictionary."""
        return cls(
            session_id=data.get("session_id", ""),
            status=SessionStatus(data.get("status", "active")),
            current_phase=SessionPhase(data.get("current_phase", "derivation")),
            can_resume=data.get("can_resume", False),
            last_successful_step=data.get("last_successful_step", ""),
            pending_action=data.get("pending_action", ""),
            resume_instructions=data.get("resume_instructions", ""),
            awaiting_message=data.get("awaiting_message", ""),
        )


__all__ = [
    # Enums
    "ActionType",
    "SessionPhase",
    "SessionStatus",
    "Priority",
    "ExecutionStatus",
    "AgentType",
    "EscalationReason",
    "UserDecisionChoice",
    # Server -> Client
    "ServerAction",
    "DeriveRequest",
    "ExamineRequest",
    "RevisionRequest",
    "ExecutionRequest",
    "ReviewRequest",
    "FixRequest",
    "EscalationNotice",
    "CompletionNotice",
    # Client -> Server
    "PlanUploadRequest",
    "PlanUploadResponse",
    "SessionStart",
    "DerivedPlan",
    "ExaminationReport",
    "RevisedPlan",
    "ExecutionResult",
    "AgentReport",
    "FixResult",
    "UserDecision",
    # Resume
    "ResumeContext",
]
