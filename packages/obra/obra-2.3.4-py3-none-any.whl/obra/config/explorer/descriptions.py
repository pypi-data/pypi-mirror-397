"""Setting descriptions for the Configuration Explorer.

Provides human-readable descriptions for all configuration options,
used for inline documentation in the TUI.
"""

from typing import Optional

# Mapping from dot-notation path to description text.
# Descriptions should be concise but informative, explaining what the
# setting does and any important considerations.
CONFIG_DESCRIPTIONS: dict[str, str] = {
    # ==========================================================================
    # LLM Settings - Local Config
    # ==========================================================================
    "llm": "LLM provider configuration for orchestration and implementation layers.",
    "llm.orchestrator": (
        "Settings for the orchestration layer LLM (planning, validation, decisions)."
    ),
    "llm.orchestrator.provider": (
        "LLM provider for the orchestration layer. "
        "Handles planning, validation, and decision-making. "
        "Options: anthropic (Claude), google (Gemini), openai (GPT)."
    ),
    "llm.orchestrator.model": (
        "Model to use for orchestration. "
        "Options: default (provider's recommended), sonnet, opus, haiku, "
        "or a full model name like 'claude-sonnet-4-5'. "
        "'default' is recommended for OAuth users."
    ),
    "llm.orchestrator.auth_method": (
        "Authentication method for the orchestration LLM. "
        "'oauth' uses flat-rate billing through Obra subscription. "
        "'api_key' bills directly to your provider account (pay-per-token)."
    ),
    "llm.implementation": (
        "Settings for the implementation layer LLM (code generation, file modifications)."
    ),
    "llm.implementation.provider": (
        "LLM provider for the implementation layer. "
        "Handles code generation and file modifications. "
        "Options: anthropic (Claude Code), google (Gemini CLI), openai (Codex)."
    ),
    "llm.implementation.model": (
        "Model to use for implementation. "
        "Options: default (provider's recommended), sonnet, opus, haiku, "
        "or a full model name. 'default' is recommended."
    ),
    "llm.implementation.auth_method": (
        "Authentication method for the implementation LLM. "
        "'oauth' uses your provider's CLI authentication. "
        "'api_key' requires setting the provider's API key environment variable."
    ),
    # ==========================================================================
    # Local Settings
    # ==========================================================================
    "api_base_url": (
        "Obra SaaS API endpoint URL. "
        "Only change this for testing, self-hosted instances, or staging environments. "
        "Default: production Obra API."
    ),
    "llm_timeout": (
        "Maximum time in seconds to wait for LLM responses. "
        "Increase for complex tasks that may take longer. "
        "Default: 1800 (30 minutes)."
    ),
    "terms_accepted": "Terms of Service and Privacy Policy acceptance state.",
    "terms_accepted.version": "Version of Terms of Service that was accepted.",
    "terms_accepted.privacy_version": "Version of Privacy Policy that was accepted.",
    "terms_accepted.accepted_at": "Timestamp when terms were accepted.",
    # ==========================================================================
    # Auth Display Fields (read-only)
    # ==========================================================================
    "user_email": "Your authenticated email address (read-only).",
    "firebase_uid": (
        "Your unique Obra user identifier (read-only). "
        "This ID is used to identify your account in the Obra system."
    ),
    "auth_provider": (
        "Authentication provider used for sign-in (read-only). "
        "Examples: google.com, github.com."
    ),
    "display_name": "Your display name from the authentication provider (read-only).",
    "user_id": "Your email address used as user identifier (read-only).",
    # ==========================================================================
    # Server Settings - Features
    # ==========================================================================
    "features": "Feature flags and capabilities that can be enabled or disabled.",
    "features.performance_control": "Performance and resource management settings.",
    "features.performance_control.budgets": "Unified budget control for orchestration sessions.",
    "features.performance_control.budgets.enabled": (
        "Enable unified budget control for orchestration sessions. "
        "When enabled, Obra tracks time, iteration, token, and progress budgets. "
        "Sessions pause when budgets are exceeded, preventing runaway costs."
    ),
    "features.performance_control.budgets.defaults": (
        "Default budget limits when budgets are enabled."
    ),
    "features.performance_control.budgets.defaults.time_minutes": (
        "Default time budget in minutes for a single orchestration session. "
        "Session pauses when this limit is reached."
    ),
    "features.performance_control.budgets.defaults.iterations": (
        "Default iteration budget (number of LLM calls) per session. "
        "Helps prevent infinite loops or excessive API usage."
    ),
    "features.quality_automation": "Quality automation tools and agents.",
    "features.quality_automation.enabled": (
        "Master toggle for quality automation features. "
        "When disabled, all quality automation agents are inactive regardless of individual settings."
    ),
    "features.quality_automation.agents": "Specialized agents for automated tasks.",
    "features.quality_automation.agents.security_audit": (
        "Enable automatic security vulnerability scanning. "
        "Runs OWASP Top 10 checks on code changes. "
        "Recommended for production codebases."
    ),
    "features.quality_automation.agents.rca_agent": (
        "Enable root cause analysis agent. "
        "Automatically investigates test failures, errors, and unexpected behavior. "
        "Provides detailed analysis reports."
    ),
    "features.quality_automation.agents.doc_audit": (
        "Enable documentation audit agent. "
        "Checks documentation for accuracy, completeness, and staleness. "
        "Uses ROT methodology (Redundant, Outdated, Trivial)."
    ),
    "features.quality_automation.agents.code_review": (
        "Enable automatic code review agent. "
        "Reviews code changes for best practices, potential issues, and style consistency."
    ),
    # Alternative paths for quality_automation features (direct placement in some configs)
    "features.quality_automation.code_review": (
        "Enable automatic code review. "
        "Reviews code changes for best practices, potential issues, and style consistency."
    ),
    "features.quality_automation.advanced_planning": (
        "Enable advanced planning capabilities. "
        "Includes derivative plan architecture and enhanced task breakdown."
    ),
    "features.quality_automation.documentation_governance": (
        "Enable documentation governance (DG-001). "
        "Keeps documentation synchronized with code through INDEX.yaml coupling."
    ),
    "features.advanced_planning": "Advanced planning capabilities.",
    "features.advanced_planning.enabled": (
        "Enable advanced planning features. "
        "Includes derivative plan architecture and enhanced task breakdown capabilities."
    ),
    "features.documentation_governance": "Documentation governance settings.",
    "features.documentation_governance.enabled": (
        "Enable documentation governance (DG-001). "
        "Keeps documentation synchronized with code through INDEX.yaml coupling."
    ),
    "features.workflow": "Workflow orchestration settings.",
    "features.workflow.enabled": (
        "Enable pattern-guided workflow execution. "
        "Uses ProcessGuardian for validation and guided execution patterns."
    ),
    "features.workflow.process_patterns": "Process pattern configurations for workflow execution.",
    # ==========================================================================
    # Server Settings - Presets
    # ==========================================================================
    "preset": (
        "Configuration preset name. "
        "Presets are curated configurations for different use cases. "
        "Your overrides are applied on top of the preset defaults."
    ),
    # ==========================================================================
    # Advanced Settings
    # ==========================================================================
    "advanced": "Expert settings for advanced users. Change with caution.",
    "advanced.debug_mode": (
        "Enable debug mode for verbose logging. "
        "Useful for troubleshooting but produces much more output."
    ),
    "advanced.experimental_features": (
        "Enable experimental features that may be unstable. "
        "These features are in development and may change or be removed."
    ),
    "advanced.telemetry": "Telemetry and usage analytics settings.",
    "advanced.telemetry.enabled": (
        "Enable anonymous usage telemetry. "
        "Helps improve Obra by sending anonymized usage statistics. "
        "No personal data or code is ever sent."
    ),
}


def get_description(path: str) -> Optional[str]:
    """Get description for a configuration path.

    Args:
        path: Dot-notation path like "llm.orchestrator.provider"

    Returns:
        Description string or None if not found
    """
    return CONFIG_DESCRIPTIONS.get(path)


def get_all_paths() -> list[str]:
    """Get all documented configuration paths.

    Returns:
        List of all paths that have descriptions
    """
    return list(CONFIG_DESCRIPTIONS.keys())


# Mapping of paths to their choices (for enum types)
CONFIG_CHOICES: dict[str, list[str]] = {
    "llm.orchestrator.provider": ["anthropic", "google", "openai"],
    "llm.orchestrator.model": ["default", "sonnet", "opus", "haiku"],
    "llm.orchestrator.auth_method": ["oauth", "api_key"],
    "llm.implementation.provider": ["anthropic", "google", "openai"],
    "llm.implementation.model": ["default", "sonnet", "opus", "haiku"],
    "llm.implementation.auth_method": ["oauth", "api_key"],
}


def get_choices(path: str) -> Optional[list[str]]:
    """Get valid choices for an enum-type setting.

    Args:
        path: Dot-notation path

    Returns:
        List of valid choices or None if not an enum type
    """
    return CONFIG_CHOICES.get(path)


# Mapping of paths to their default values
CONFIG_DEFAULTS: dict[str, object] = {
    "llm.orchestrator.provider": "anthropic",
    "llm.orchestrator.model": "default",
    "llm.orchestrator.auth_method": "oauth",
    "llm.implementation.provider": "anthropic",
    "llm.implementation.model": "default",
    "llm.implementation.auth_method": "oauth",
    "llm_timeout": 1800,
    "features.performance_control.budgets.enabled": True,
    "features.performance_control.budgets.defaults.time_minutes": 30,
    "features.performance_control.budgets.defaults.iterations": 50,
    "features.quality_automation.agents.security_audit": False,
    "features.quality_automation.agents.rca_agent": True,
    "features.quality_automation.agents.doc_audit": False,
    "features.workflow.enabled": True,
    "advanced.debug_mode": False,
    "advanced.experimental_features": False,
    "advanced.telemetry.enabled": True,
}


def get_default(path: str) -> object:
    """Get default value for a setting.

    Args:
        path: Dot-notation path

    Returns:
        Default value or None if not defined
    """
    return CONFIG_DEFAULTS.get(path)


# Setting tier mapping (basic, standard, advanced)
SETTING_TIERS: dict[str, str] = {
    # Basic - most users need these
    "llm.orchestrator.provider": "basic",
    "llm.orchestrator.model": "basic",
    "llm.implementation.provider": "basic",
    "llm.implementation.model": "basic",
    "preset": "basic",
    # Standard - common use
    "llm.orchestrator.auth_method": "standard",
    "llm.implementation.auth_method": "standard",
    "features.performance_control.budgets.enabled": "standard",
    "features.quality_automation.agents.security_audit": "standard",
    "features.quality_automation.agents.rca_agent": "standard",
    "features.quality_automation.agents.doc_audit": "standard",
    "features.workflow.enabled": "standard",
    # Advanced - expert users
    "api_base_url": "advanced",
    "llm_timeout": "advanced",
    "advanced.debug_mode": "advanced",
    "advanced.experimental_features": "advanced",
    "advanced.telemetry.enabled": "advanced",
    "features.performance_control.budgets.defaults.time_minutes": "advanced",
    "features.performance_control.budgets.defaults.iterations": "advanced",
}


def get_tier(path: str) -> str:
    """Get visibility tier for a setting.

    Args:
        path: Dot-notation path

    Returns:
        "basic", "standard", or "advanced" (defaults to "standard")
    """
    return SETTING_TIERS.get(path, "standard")
