"""Security review agent for vulnerability detection.

This module provides SecurityAgent, which analyzes code for security
vulnerabilities including OWASP Top 10 issues.

Checks Performed:
    - Hardcoded credentials and secrets
    - SQL injection vulnerabilities
    - XSS vulnerabilities
    - Command injection
    - Path traversal
    - Insecure cryptography
    - Input validation issues
    - Unsafe deserialization

Scoring Dimensions:
    - vulnerability_free: No known vulnerabilities
    - secure_defaults: Uses secure defaults
    - input_validation: Proper input validation

Related:
    - obra/agents/base.py
    - obra/agents/registry.py
    - functions/src/security/injection_defense.py
"""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from obra.api.protocol import AgentType, Priority
from obra.agents.base import AgentIssue, AgentResult, BaseAgent
from obra.agents.registry import register_agent

logger = logging.getLogger(__name__)


# Security patterns to check
SECURITY_PATTERNS = {
    # Hardcoded credentials
    "hardcoded_password": {
        "pattern": r"(password|passwd|pwd|secret|api_key|apikey|auth_token)\s*=\s*['\"][^'\"]+['\"]",
        "priority": Priority.P0,
        "title": "Hardcoded credential detected",
        "description": "Credentials should not be hardcoded in source code. Use environment variables or secret management.",
        "dimension": "vulnerability_free",
    },
    "hardcoded_aws_key": {
        "pattern": r"(AKIA[0-9A-Z]{16}|aws_secret_access_key\s*=\s*['\"][^'\"]+['\"])",
        "priority": Priority.P0,
        "title": "Hardcoded AWS credential detected",
        "description": "AWS credentials detected in source code. Use IAM roles or AWS Secrets Manager.",
        "dimension": "vulnerability_free",
    },
    # SQL Injection
    "sql_injection": {
        "pattern": r"(execute|cursor\.execute|query)\s*\(\s*[\"'].*%.*[\"']\s*%",
        "priority": Priority.P0,
        "title": "Potential SQL injection vulnerability",
        "description": "String formatting in SQL queries can lead to injection. Use parameterized queries.",
        "dimension": "input_validation",
    },
    "sql_injection_fstring": {
        "pattern": r"(execute|cursor\.execute|query)\s*\(\s*f[\"']",
        "priority": Priority.P0,
        "title": "SQL injection via f-string",
        "description": "Using f-strings in SQL queries is dangerous. Use parameterized queries.",
        "dimension": "input_validation",
    },
    # Command Injection
    "command_injection": {
        "pattern": r"(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*\+",
        "priority": Priority.P0,
        "title": "Potential command injection vulnerability",
        "description": "String concatenation in shell commands can lead to injection. Use list arguments with shell=False.",
        "dimension": "input_validation",
    },
    "shell_true": {
        "pattern": r"subprocess\.(run|call|Popen)\s*\([^)]*shell\s*=\s*True",
        "priority": Priority.P1,
        "title": "Subprocess with shell=True",
        "description": "Using shell=True can be dangerous if input is not properly sanitized.",
        "dimension": "secure_defaults",
    },
    # Path Traversal
    "path_traversal": {
        "pattern": r"open\s*\([^)]*\+[^)]*\)",
        "priority": Priority.P1,
        "title": "Potential path traversal vulnerability",
        "description": "Concatenating user input with file paths can lead to path traversal. Validate and sanitize paths.",
        "dimension": "input_validation",
    },
    # XSS
    "xss_template": {
        "pattern": r"\|\s*safe\s*\}",
        "priority": Priority.P1,
        "title": "Potential XSS via template safe filter",
        "description": "Using 'safe' filter can lead to XSS if content is not properly sanitized.",
        "dimension": "vulnerability_free",
    },
    # Insecure Crypto
    "weak_hash_md5": {
        "pattern": r"hashlib\.md5\s*\(",
        "priority": Priority.P2,
        "title": "Weak hash function: MD5",
        "description": "MD5 is cryptographically broken. Use SHA-256 or stronger.",
        "dimension": "secure_defaults",
    },
    "weak_hash_sha1": {
        "pattern": r"hashlib\.sha1\s*\(",
        "priority": Priority.P2,
        "title": "Weak hash function: SHA1",
        "description": "SHA1 is deprecated for security purposes. Use SHA-256 or stronger.",
        "dimension": "secure_defaults",
    },
    # Unsafe Deserialization
    "pickle_load": {
        "pattern": r"pickle\.loads?\s*\(",
        "priority": Priority.P1,
        "title": "Unsafe deserialization with pickle",
        "description": "pickle.load on untrusted data can execute arbitrary code. Use safer alternatives like JSON.",
        "dimension": "vulnerability_free",
    },
    "yaml_load": {
        "pattern": r"yaml\.load\s*\([^)]*(?!Loader)",
        "priority": Priority.P1,
        "title": "Unsafe YAML loading",
        "description": "yaml.load without Loader can execute arbitrary code. Use yaml.safe_load().",
        "dimension": "vulnerability_free",
    },
    # Debug Mode
    "flask_debug": {
        "pattern": r"app\.run\s*\([^)]*debug\s*=\s*True",
        "priority": Priority.P1,
        "title": "Flask debug mode enabled",
        "description": "Debug mode should not be enabled in production. It exposes sensitive information.",
        "dimension": "secure_defaults",
    },
    "django_debug": {
        "pattern": r"DEBUG\s*=\s*True",
        "priority": Priority.P1,
        "title": "Django DEBUG mode enabled",
        "description": "DEBUG mode should not be enabled in production.",
        "dimension": "secure_defaults",
    },
    # Assert Statements
    "assert_security": {
        "pattern": r"assert\s+.*(?:admin|auth|permission|role|user)",
        "priority": Priority.P2,
        "title": "Security check using assert",
        "description": "Assert statements can be disabled with -O flag. Use proper conditionals for security checks.",
        "dimension": "secure_defaults",
    },
    # Eval/Exec
    "eval_usage": {
        "pattern": r"\beval\s*\(",
        "priority": Priority.P0,
        "title": "Dangerous use of eval()",
        "description": "eval() can execute arbitrary code. Avoid using it with user input.",
        "dimension": "vulnerability_free",
    },
    "exec_usage": {
        "pattern": r"\bexec\s*\(",
        "priority": Priority.P0,
        "title": "Dangerous use of exec()",
        "description": "exec() can execute arbitrary code. Avoid using it with user input.",
        "dimension": "vulnerability_free",
    },
}


@register_agent(AgentType.SECURITY)
class SecurityAgent(BaseAgent):
    """Security review agent for vulnerability detection.

    Analyzes code for common security vulnerabilities including
    OWASP Top 10 issues, hardcoded credentials, and insecure patterns.

    Example:
        >>> agent = SecurityAgent(Path("/workspace"))
        >>> result = agent.analyze(
        ...     item_id="T1",
        ...     changed_files=["src/auth.py"],
        ...     timeout_ms=60000
        ... )
        >>> print(f"Found {len(result.issues)} security issues")
    """

    agent_type = AgentType.SECURITY

    def analyze(
        self,
        item_id: str,
        changed_files: Optional[List[str]] = None,
        timeout_ms: int = 60000,
    ) -> AgentResult:
        """Analyze code for security vulnerabilities.

        Args:
            item_id: Plan item ID being reviewed
            changed_files: List of files that changed
            timeout_ms: Maximum execution time

        Returns:
            AgentResult with security issues and scores
        """
        start_time = time.time()
        deadline = start_time + (timeout_ms / 1000)
        issues: List[AgentIssue] = []
        issue_index = 0

        logger.info(f"SecurityAgent analyzing {item_id}")

        # Get files to analyze (Python files only)
        files = self.get_files_to_analyze(
            changed_files=changed_files,
            extensions=[".py", ".js", ".ts", ".jsx", ".tsx"],
        )

        logger.debug(f"Analyzing {len(files)} files for security issues")

        # Stats for scoring
        total_patterns_checked = 0
        vulnerabilities_found = 0
        input_validation_issues = 0
        secure_default_issues = 0

        for file_path in files:
            # Check timeout
            if time.time() > deadline:
                logger.warning("SecurityAgent timed out")
                return AgentResult(
                    agent_type=self.agent_type,
                    status="timeout",
                    issues=issues,
                    scores=self._calculate_scores(
                        vulnerabilities_found,
                        input_validation_issues,
                        secure_default_issues,
                        total_patterns_checked,
                    ),
                    execution_time_ms=int((time.time() - start_time) * 1000),
                )

            content = self.read_file(file_path)
            if not content:
                continue

            # Check each security pattern
            for pattern_name, pattern_info in SECURITY_PATTERNS.items():
                total_patterns_checked += 1
                matches = list(
                    re.finditer(
                        pattern_info["pattern"], content, re.IGNORECASE | re.MULTILINE
                    )
                )

                for match in matches:
                    # Find line number
                    line_number = content[: match.start()].count("\n") + 1

                    issue_index += 1
                    issues.append(
                        AgentIssue(
                            id=self._generate_issue_id("SEC", issue_index),
                            title=pattern_info["title"],
                            description=pattern_info["description"],
                            priority=pattern_info["priority"],
                            file_path=str(file_path.relative_to(self._working_dir)),
                            line_number=line_number,
                            dimension=pattern_info["dimension"],
                            suggestion=f"Review and fix the pattern at line {line_number}",
                            metadata={
                                "pattern_name": pattern_name,
                                "matched_text": match.group(0)[:100],
                            },
                        )
                    )

                    # Update stats
                    dimension = pattern_info["dimension"]
                    if dimension == "vulnerability_free":
                        vulnerabilities_found += 1
                    elif dimension == "input_validation":
                        input_validation_issues += 1
                    elif dimension == "secure_defaults":
                        secure_default_issues += 1

        execution_time = int((time.time() - start_time) * 1000)
        logger.info(
            f"SecurityAgent complete: {len(issues)} issues found in {execution_time}ms"
        )

        return AgentResult(
            agent_type=self.agent_type,
            status="complete",
            issues=issues,
            scores=self._calculate_scores(
                vulnerabilities_found,
                input_validation_issues,
                secure_default_issues,
                total_patterns_checked,
            ),
            execution_time_ms=execution_time,
            metadata={
                "files_analyzed": len(files),
                "patterns_checked": total_patterns_checked,
            },
        )

    def _calculate_scores(
        self,
        vulnerabilities: int,
        input_issues: int,
        default_issues: int,
        total_checks: int,
    ) -> Dict[str, float]:
        """Calculate dimension scores based on findings.

        Scores range from 0.0 (many issues) to 1.0 (no issues).

        Args:
            vulnerabilities: Count of vulnerability findings
            input_issues: Count of input validation issues
            default_issues: Count of secure defaults issues
            total_checks: Total patterns checked

        Returns:
            Dict of dimension scores
        """
        # Exponential decay: each issue reduces score significantly
        def score(issue_count: int) -> float:
            if issue_count == 0:
                return 1.0
            elif issue_count == 1:
                return 0.7
            elif issue_count == 2:
                return 0.5
            elif issue_count <= 5:
                return 0.3
            else:
                return 0.1

        return {
            "vulnerability_free": score(vulnerabilities),
            "input_validation": score(input_issues),
            "secure_defaults": score(default_issues),
        }


__all__ = ["SecurityAgent"]
