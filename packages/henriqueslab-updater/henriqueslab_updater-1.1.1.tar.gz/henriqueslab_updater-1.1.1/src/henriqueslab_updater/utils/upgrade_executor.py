"""Upgrade command executor with support for compound commands.

This module provides utilities for executing package upgrade commands,
including automatic handling of compound shell commands (e.g., "brew update && brew upgrade pkg").
"""

import shlex
import subprocess
from typing import Optional, Tuple


class UpgradeError(Exception):
    """Exception raised when an upgrade command fails."""

    def __init__(self, message: str, returncode: int, command: str):
        """Initialize upgrade error.

        Args:
            message: Error description
            returncode: Process return code
            command: The command that failed
        """
        self.message = message
        self.returncode = returncode
        self.command = command
        super().__init__(message)


def execute_upgrade(
    upgrade_command: str,
    *,
    show_output: bool = True,
    timeout: Optional[int] = 300,
) -> Tuple[bool, Optional[str]]:
    """Execute an upgrade command, handling compound commands automatically.

    This function safely executes upgrade commands using subprocess, with automatic
    support for compound commands joined with &&. Each command is properly parsed
    using shlex.split() to prevent shell injection vulnerabilities.

    For compound commands (containing " && "), each part is executed sequentially.
    If any part fails, execution stops and an error is returned.

    Args:
        upgrade_command: The upgrade command string (e.g., "brew update && brew upgrade pkg")
        show_output: Whether to show command output to user (default: True)
        timeout: Command timeout in seconds (default: 300)

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
        - (True, None) if upgrade succeeded
        - (False, error_message) if upgrade failed

    Raises:
        UpgradeError: If a command fails with non-zero exit code

    Examples:
        >>> # Single command
        >>> success, error = execute_upgrade("pip install --upgrade mypackage")
        >>> if not success:
        ...     print(f"Upgrade failed: {error}")

        >>> # Compound command (automatically split and run sequentially)
        >>> success, error = execute_upgrade("brew update && brew upgrade mypackage")

        >>> # Capture output instead of showing it
        >>> success, error = execute_upgrade("pipx upgrade mypackage", show_output=False)
    """
    try:
        # Check if this is a compound command with &&
        if " && " in upgrade_command:
            # Split compound command and run each part sequentially
            commands = upgrade_command.split(" && ")

            for cmd in commands:
                cmd = cmd.strip()
                if not cmd:
                    continue

                # Parse command safely using shlex
                try:
                    cmd_args = shlex.split(cmd)
                except ValueError as e:
                    return (False, f"Failed to parse command '{cmd}': {e}")

                # Execute the command
                result = subprocess.run(
                    cmd_args,
                    check=False,
                    capture_output=not show_output,
                    text=True,
                    timeout=timeout,
                )

                # Check if command succeeded
                if result.returncode != 0:
                    if show_output:
                        error_msg = f"Command '{cmd}' exited with code {result.returncode}"
                    else:
                        stderr = result.stderr.strip() if result.stderr else ""
                        stdout = result.stdout.strip() if result.stdout else ""
                        error_output = stderr or stdout or "No error output"
                        error_msg = f"Command '{cmd}' failed: {error_output}"

                    return (False, error_msg)

        else:
            # Single command - parse and execute
            try:
                cmd_args = shlex.split(upgrade_command)
            except ValueError as e:
                return (False, f"Failed to parse command '{upgrade_command}': {e}")

            result = subprocess.run(
                cmd_args,
                check=False,
                capture_output=not show_output,
                text=True,
                timeout=timeout,
            )

            if result.returncode != 0:
                if show_output:
                    error_msg = f"Upgrade command exited with code {result.returncode}"
                else:
                    stderr = result.stderr.strip() if result.stderr else ""
                    stdout = result.stdout.strip() if result.stdout else ""
                    error_output = stderr or stdout or "No error output"
                    error_msg = f"Upgrade failed: {error_output}"

                return (False, error_msg)

        # All commands succeeded
        return (True, None)

    except subprocess.TimeoutExpired:
        return (False, f"Upgrade command timed out after {timeout} seconds")

    except FileNotFoundError as e:
        # Command not found
        cmd_name = upgrade_command.split()[0] if upgrade_command else "command"
        return (False, f"Command '{cmd_name}' not found. Is it installed?")

    except Exception as e:
        return (False, f"Unexpected error during upgrade: {e}")


def execute_upgrade_raise(
    upgrade_command: str,
    *,
    show_output: bool = True,
    timeout: Optional[int] = 300,
) -> None:
    """Execute upgrade command, raising UpgradeError on failure.

    This is a convenience wrapper around execute_upgrade() that raises an
    exception instead of returning an error tuple.

    Args:
        upgrade_command: The upgrade command string
        show_output: Whether to show command output to user (default: True)
        timeout: Command timeout in seconds (default: 300)

    Raises:
        UpgradeError: If upgrade fails

    Examples:
        >>> try:
        ...     execute_upgrade_raise("brew update && brew upgrade mypackage")
        ...     print("Upgrade successful!")
        ... except UpgradeError as e:
        ...     print(f"Upgrade failed: {e.message}")
        ...     print(f"Command: {e.command}")
        ...     print(f"Exit code: {e.returncode}")
    """
    success, error = execute_upgrade(
        upgrade_command,
        show_output=show_output,
        timeout=timeout,
    )

    if not success:
        # Try to extract return code from error message
        returncode = 1
        if error and "exited with code" in error:
            try:
                returncode = int(error.split("exited with code")[1].strip().split()[0])
            except (ValueError, IndexError):
                pass

        raise UpgradeError(error or "Upgrade failed", returncode, upgrade_command)
