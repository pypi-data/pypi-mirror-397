"""CLI command for validating MACHINE_PLAN.yaml files.

This module provides the ValidatePlanCommand class which implements
the 'obra validate-plan' command. It validates YAML syntax of plan files.

Note: Full schema validation happens on the server during upload.
This command provides quick local YAML syntax checking.

Usage:
    $ obra validate-plan path/to/MACHINE_PLAN.yaml
    $ obra validate-plan --verbose plan.yaml

Reference: FEAT-PLAN-VALIDATION-001 Story S2: CLI Command Implementation
"""

import logging
import sys
from pathlib import Path

import click
import yaml

logger = logging.getLogger(__name__)


class ValidatePlanCommand:
    """Command handler for validating MACHINE_PLAN.yaml files.

    This class implements the 'obra validate-plan' CLI command which validates
    plan files for YAML syntax errors. Full schema validation happens on the
    server during upload.

    Features:
    - YAML syntax validation using PyYAML
    - Colored output for success/failure
    - Exit code handling (0 for valid, 1 for invalid)

    Example:
        >>> cmd = ValidatePlanCommand()
        >>> cmd.execute("plan.yaml", verbose=False)
        0  # Returns exit code
    """

    def __init__(self) -> None:
        """Initialize ValidatePlanCommand."""
        pass

    def execute(
        self,
        file_path: str,
        verbose: bool = False,
    ) -> int:
        """Execute plan validation and display results.

        Validates the specified plan file for YAML syntax.

        Args:
            file_path: Path to the YAML plan file to validate
            verbose: Enable verbose output with additional details

        Returns:
            Exit code: 0 if validation passed, 1 if validation failed

        Example:
            >>> cmd = ValidatePlanCommand()
            >>> exit_code = cmd.execute("plan.yaml")
            >>> sys.exit(exit_code)
        """
        # Validate file path
        path = Path(file_path)

        if not path.exists():
            click.echo()
            click.echo(click.style("✗ File not found", fg="red", bold=True))
            click.echo(f"\nPath: {path}")
            click.echo()
            return 1

        if verbose:
            click.echo(f"\nValidating: {path}")
            click.echo(f"Absolute path: {path.absolute()}\n")

        # Parse YAML file
        try:
            with open(path, encoding="utf-8") as f:
                plan_data = yaml.safe_load(f)

            # Basic checks
            if not isinstance(plan_data, dict):
                click.echo()
                click.echo(click.style("✗ Validation FAILED", fg="red", bold=True))
                click.echo()
                click.echo(click.style("ERROR: ", fg="red", bold=True) + "Plan file must contain a YAML dictionary")
                click.echo()
                return 1

            # Success
            click.echo()
            click.echo(click.style("✓ YAML syntax is valid", fg="green", bold=True))
            click.echo(f"\nFile: {path}")
            click.echo()
            click.echo(click.style("Note:", fg="blue") + " Full schema validation happens on server during upload.")
            click.echo(click.style("      Use 'obra upload-plan' to validate schema.", fg="blue"))
            click.echo()
            return 0

        except yaml.YAMLError as e:
            click.echo()
            click.echo(click.style("✗ YAML Syntax Error", fg="red", bold=True))
            click.echo()
            click.echo(f"File: {path}")
            click.echo()
            click.echo(click.style("ERROR: ", fg="red", bold=True) + str(e))
            click.echo()
            return 1
        except Exception as e:
            click.echo()
            click.echo(click.style("✗ Validation Error", fg="red", bold=True))
            click.echo()
            click.echo(click.style("ERROR: ", fg="red", bold=True) + str(e))
            click.echo()
            return 1


# Click command decorator for CLI integration
@click.command(name="validate-plan")
@click.argument(
    "file_path",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with additional details",
)
def validate_plan_cli(file_path: str, verbose: bool) -> None:
    """Validate MACHINE_PLAN.yaml file syntax.

    Validates the specified plan file for YAML syntax errors.
    Full schema validation happens on the server during upload.

    Examples:

        \b
        # Validate a plan file
        $ obra validate-plan docs/development/MY_PLAN.yaml

        \b
        # Validate with verbose output
        $ obra validate-plan --verbose plan.yaml

    Exit Codes:
        0: Validation passed - YAML syntax is valid
        1: Validation failed - YAML syntax error
    """
    command = ValidatePlanCommand()
    exit_code = command.execute(file_path, verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    # Allow running as standalone script
    validate_plan_cli()
