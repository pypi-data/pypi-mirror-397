"""Upload target validation utilities."""

import time

from flow.core.code_upload.targets import UploadTargetError, UploadTargetPlan
from flow.errors import FlowError
from flow.protocols.remote_operations import RemoteOperationsProtocol


def ensure_remote_target(
    remote_ops: RemoteOperationsProtocol,
    task_id: str,
    plan: UploadTargetPlan,
    *,
    timeout: int = 30,
    allow_sudo: bool = False,
) -> float:
    """Ensure remote upload target exists and is writable.

    Args:
        remote_ops: Remote operations interface for executing commands.
        task_id: The task ID to execute commands against.
        plan: Upload target plan with remote paths.
        timeout: Command timeout in seconds.
        allow_sudo: Whether to allow sudo for creating absolute paths.

    Returns:
        Elapsed validation time in seconds.

    Raises:
        UploadTargetError: If the target cannot be created or is not writable.
    """
    start = time.monotonic()
    target = plan.remote_target

    # Expand tilde to $HOME for shell command safety
    if target == "~":
        shell_target = "$HOME"
    elif target.startswith("~/"):
        shell_target = "$HOME/" + target[2:]
    else:
        shell_target = target

    # Create directory
    mkdir_cmd = f'mkdir -p "{shell_target}"'
    if allow_sudo and target.startswith("/"):
        mkdir_cmd = f"sudo -n {mkdir_cmd} 2>/dev/null || {mkdir_cmd}"

    try:
        remote_ops.execute_command(task_id, mkdir_cmd, timeout=timeout)
    except (OSError, RuntimeError, TimeoutError, FlowError) as e:
        raise UploadTargetError(
            code="TARGET_CREATE_FAILED",
            message=f"Failed to create upload target: {target}",
            remediation=f"Check remote permissions or use a different path. Error: {e}",
        ) from e

    # Verify writability with touch test
    test_file = f"{shell_target}/.flow-write-test-{int(time.time())}"
    test_cmd = f'touch "{test_file}" && rm -f "{test_file}"'

    try:
        remote_ops.execute_command(task_id, test_cmd, timeout=timeout)
    except (OSError, RuntimeError, TimeoutError, FlowError) as e:
        raise UploadTargetError(
            code="TARGET_NOT_WRITABLE",
            message=f"Upload target {target} is not writable.",
            remediation=f"Adjust upload config or fix remote permissions. Error: {e}",
        ) from e

    return time.monotonic() - start
