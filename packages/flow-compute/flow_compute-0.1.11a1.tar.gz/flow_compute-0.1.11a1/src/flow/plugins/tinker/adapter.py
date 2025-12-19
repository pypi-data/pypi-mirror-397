"""Tinker frontend adapter for flow-compute.

This adapter deploys SkyRL-TX on Mithril GPU instances to provide Tinker-compatible
training services. Flow handles infrastructure (provisioning, monitoring),
SkyRL-TX handles training (JAX/Flax engine with efficient multi-LoRA support).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# Default instance type - 8xH100 is the standard Mithril offering
# Instance type validation is handled by flow-compute/Mithril provider
DEFAULT_INSTANCE_TYPE = "8xh100"

# Estimated model sizes for auto-selecting tensor parallelism
# These are advisory - actual requirements depend on batch size, LoRA rank, etc.
MODEL_PARAM_BILLIONS: dict[str, float] = {
    "Qwen/Qwen3-0.6B": 0.6,
    "Qwen/Qwen3-1.7B": 1.7,
    "Qwen/Qwen3-4B": 4,
    "Qwen/Qwen3-8B": 8,
    "Qwen/Qwen3-14B": 14,
    "Qwen/Qwen3-30B-A3B": 30,  # MoE - active params ~3B
    "meta-llama/Llama-3.2-1B": 1,
    "meta-llama/Llama-3.2-3B": 3,
    "meta-llama/Llama-3.1-8B": 8,
    "meta-llama/Llama-3.1-8B-Instruct": 8,
    "meta-llama/Llama-3.1-70B": 70,
    "meta-llama/Llama-3.1-70B-Instruct": 70,
}


@dataclass
class TinkerServerConfig:
    """Configuration for launching a SkyRL-TX Tinker server on Mithril."""

    base_model: str
    instance_type: str | None = None
    max_lora_adapters: int = 32
    max_lora_rank: int = 32  # SkyRL-TX default is 32
    port: int = 8000
    host: str = "0.0.0.0"
    checkpoints_base: str = "/tmp/tx_checkpoints"  # Supports s3:// URLs via cloudpathlib
    database_url: str | None = None  # Defaults to SQLite
    tensor_parallel_size: int = 1
    gradient_checkpointing: bool = False
    external_inference_url: str | None = None  # For vLLM offloading

    def resolve_instance_type(self) -> str:
        """Determine the best instance type for the base model.

        Instance type validation is delegated to flow-compute/Mithril provider.
        If invalid, flow.run() will raise an appropriate error.
        """
        if self.instance_type:
            return self.instance_type
        return DEFAULT_INSTANCE_TYPE

    def resolve_tensor_parallelism(self, gpu_count: int) -> int:
        """Determine optimal tensor parallelism for the model.

        Args:
            gpu_count: Number of GPUs available on the instance

        Returns:
            Recommended tensor parallel size (1 to gpu_count)
        """
        if self.tensor_parallel_size > 1:
            return min(self.tensor_parallel_size, gpu_count)

        # Estimate based on model size
        # Rule of thumb: ~10B params per GPU in bf16 with some headroom for activations
        params_b = MODEL_PARAM_BILLIONS.get(self.base_model, 7.0)  # Default to 7B

        if params_b <= 3:
            return 1
        elif params_b <= 14:
            return min(2, gpu_count)
        elif params_b <= 35:
            return min(4, gpu_count)
        else:
            return gpu_count  # Use all GPUs for very large models

    def to_server_args(self) -> list[str]:
        """Convert config to command-line arguments for SkyRL-TX server."""
        args = [
            f"--host={self.host}",
            f"--port={self.port}",
            f"--base-model={self.base_model}",
            f"--max-lora-adapters={self.max_lora_adapters}",
            f"--max-lora-rank={self.max_lora_rank}",
            f"--checkpoints-base={self.checkpoints_base}",
            f"--tensor-parallel-size={self.tensor_parallel_size}",
        ]
        if self.database_url:
            args.append(f"--database-url={self.database_url}")
        if self.gradient_checkpointing:
            args.append("--gradient-checkpointing")
        if self.external_inference_url:
            args.append(f"--external-inference-url={self.external_inference_url}")
        return args


# Realistic timeouts accounting for Mithril VM startup
DEFAULT_VM_STARTUP_TIMEOUT = 1800  # 30 minutes - VMs can take 20+ min in bad cases
DEFAULT_SERVER_READY_TIMEOUT = 900  # 15 minutes - model download can be slow
DEFAULT_TOTAL_TIMEOUT = 2700  # 45 minutes total


@dataclass
class TinkerTaskHandle:
    """Handle to a running Tinker server task on Mithril."""

    task_id: str
    host: str
    port: int
    base_model: str
    config: TinkerServerConfig

    @property
    def base_url(self) -> str:
        """Get the base URL for the Tinker REST API."""
        return f"http://{self.host}:{self.port}"

    @property
    def api_url(self) -> str:
        """Get the full API URL."""
        return f"{self.base_url}/api/v1"


@dataclass
class TinkerFrontendAdapter:
    """Frontend adapter that deploys SkyRL-TX on Mithril for Tinker workloads.

    This adapter handles:
    1. Provisioning GPU instances on Mithril
    2. Installing and launching SkyRL-TX with appropriate configuration
    3. Providing connection details for the Tinker SDK

    SkyRL-TX provides efficient multi-LoRA training with JAX/Flax, including
    look-ahead scheduling and request batching for optimal GPU utilization.

    Example:
        adapter = TinkerFrontendAdapter()
        handle = adapter.launch_server(
            base_model="Qwen/Qwen3-4B",
            instance_type="2xh100",
            checkpoints_base="s3://my-bucket/checkpoints",  # Optional S3 storage
        )
        # Use standard Tinker SDK
        client = tinker.ServiceClient(base_url=handle.base_url)
    """

    name: str = "tinker"
    _flow_client: Any = field(default=None, repr=False)

    def _get_flow_client(self) -> Any:
        """Lazily initialize the flow client."""
        if self._flow_client is None:
            from flow.sdk import Flow

            self._flow_client = Flow()
        return self._flow_client

    def launch_server(
        self,
        base_model: str,
        instance_type: str | None = None,
        max_lora_adapters: int = 32,
        max_lora_rank: int = 32,
        port: int = 8000,
        tensor_parallel_size: int | None = None,
        gradient_checkpointing: bool = False,
        wait_for_ready: bool = True,
        timeout: int | None = None,
        vm_startup_timeout: int | None = None,
        checkpoints_base: str = "/tmp/tx_checkpoints",
        database_url: str | None = None,
        external_inference_url: str | None = None,
        **flow_kwargs: Any,
    ) -> TinkerTaskHandle:
        """Launch a SkyRL-TX Tinker server on Mithril.

        Args:
            base_model: HuggingFace model ID (e.g., "Qwen/Qwen3-4B")
            instance_type: GPU instance type (auto-selected if not provided)
            max_lora_adapters: Maximum number of concurrent LoRA adapters
            max_lora_rank: Maximum LoRA rank
            port: Port for the REST API
            tensor_parallel_size: Tensor parallelism (auto-detected from instance)
            gradient_checkpointing: Enable gradient checkpointing for memory savings
            wait_for_ready: Wait for server to be ready before returning
            timeout: Total timeout in seconds (default 45 min - accounts for VM + model download)
            vm_startup_timeout: Timeout for VM to become SSH-ready (default 30 min)
            checkpoints_base: Base path for checkpoints. Supports local paths or
                cloud storage URLs (s3://bucket/prefix, gs://bucket/prefix)
            database_url: Database URL for request tracking (defaults to SQLite)
            external_inference_url: Optional vLLM URL for inference offloading
            **flow_kwargs: Additional arguments passed to flow.run()

        Returns:
            TinkerTaskHandle with connection details

        Note:
            Mithril VMs can take 20+ minutes to start in worst cases, and large
            models (70B+) can take 10-30 minutes to download. Default timeouts
            are set conservatively to handle these scenarios.
        """
        timeout = timeout or DEFAULT_TOTAL_TIMEOUT
        vm_startup_timeout = vm_startup_timeout or DEFAULT_VM_STARTUP_TIMEOUT

        config = TinkerServerConfig(
            base_model=base_model,
            instance_type=instance_type,
            max_lora_adapters=max_lora_adapters,
            max_lora_rank=max_lora_rank,
            port=port,
            tensor_parallel_size=tensor_parallel_size or 1,
            gradient_checkpointing=gradient_checkpointing,
            checkpoints_base=checkpoints_base,
            database_url=database_url,
            external_inference_url=external_inference_url,
        )

        resolved_instance = config.resolve_instance_type()
        gpu_count = self._parse_gpu_count(resolved_instance)

        # Auto-detect tensor parallelism based on model size and available GPUs
        if tensor_parallel_size is None:
            config.tensor_parallel_size = config.resolve_tensor_parallelism(gpu_count)

        logger.info(
            f"Launching Tinker server for {base_model} on {resolved_instance} "
            f"(tensor_parallel={config.tensor_parallel_size}/{gpu_count} GPUs)"
        )

        # Build the server command - install SkyRL-TX and run
        server_args = config.to_server_args()
        # Install SkyRL-TX from GitHub with tinker extras
        install_cmd = (
            "pip install "
            "'git+https://github.com/mithrilcompute/SkyRL.git#subdirectory=skyrl-tx&egg=skyrl-tx[tinker]' "
            "--quiet 2>/dev/null || true"
        )
        server_cmd = f"python -m tx.tinker.api {' '.join(server_args)}"
        command = f"{install_cmd} && {server_cmd}"

        # Merge flow kwargs with defaults
        run_kwargs = {
            "name": f"tinker-{base_model.split('/')[-1].lower()}",
            "instance_type": resolved_instance,
            "ports": [port],
            **flow_kwargs,
        }

        flow = self._get_flow_client()
        task = flow.run(command=command, **run_kwargs)

        logger.info(f"Task submitted: {task.task_id}")
        logger.info(f"Waiting for VM to start (timeout: {vm_startup_timeout}s)...")

        # Wait for VM to be SSH-ready first
        try:
            flow.wait_for_ssh(task.task_id, timeout=vm_startup_timeout)
        except Exception as e:
            # Check if task failed
            status = flow.status(task.task_id)
            if hasattr(status, "status") and status.status in ("failed", "cancelled"):
                raise RuntimeError(
                    f"Task {task.task_id} failed to start. Status: {status.status}. "
                    f"Check logs: flow logs {task.task_id}"
                ) from e
            raise

        # Now get the actual host - should be available after SSH is ready
        status = flow.status(task.task_id)
        host = getattr(status, "ssh_host", None) or getattr(task, "ssh_host", None)
        if not host:
            raise RuntimeError(
                f"Could not determine host for task {task.task_id}. Task status: {status}"
            )

        handle = TinkerTaskHandle(
            task_id=task.task_id,
            host=host,
            port=port,
            base_model=base_model,
            config=config,
        )

        if wait_for_ready:
            remaining_timeout = max(60, timeout - vm_startup_timeout)
            self._wait_for_server(handle, timeout=remaining_timeout)

        return handle

    def _parse_gpu_count(self, instance_type: str) -> int:
        """Extract GPU count from instance type string."""
        # Parse formats like "8xh100", "4xh100", "1xh100"
        if "x" in instance_type.lower():
            try:
                return int(instance_type.split("x")[0])
            except ValueError:
                pass
        return 1

    def _wait_for_server(
        self, handle: TinkerTaskHandle, timeout: int = DEFAULT_SERVER_READY_TIMEOUT
    ) -> None:
        """Wait for the Tinker server to become ready.

        This polls the health endpoint while also checking task status to fail
        fast if the task crashes.
        """
        import time

        import httpx

        start = time.time()
        health_url = f"{handle.api_url}/healthz"
        flow = self._get_flow_client()
        last_status_check = 0
        status_check_interval = 30  # Check task status every 30s

        logger.info(f"Waiting for Tinker server at {health_url} (timeout: {timeout}s)")
        logger.info("Note: First startup may take 10-30 min for large models due to download")

        while time.time() - start < timeout:
            elapsed = time.time() - start

            # Periodically check if task is still running
            if time.time() - last_status_check > status_check_interval:
                try:
                    status = flow.status(handle.task_id)
                    task_status = getattr(status, "status", "unknown")
                    if task_status in ("failed", "cancelled", "terminated"):
                        raise RuntimeError(
                            f"Task {handle.task_id} {task_status} while waiting for server. "
                            f"Check logs: flow logs {handle.task_id}"
                        )
                    last_status_check = time.time()
                except Exception as e:
                    if "failed" in str(e) or "cancelled" in str(e):
                        raise
                    # Status check failed, but continue waiting
                    logger.debug(f"Status check failed: {e}")

            # Try health endpoint
            try:
                response = httpx.get(health_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Tinker server is ready (took {elapsed:.0f}s)")
                    return
            except httpx.ConnectError:
                # Server not up yet - expected during startup
                pass
            except httpx.RequestError as e:
                logger.debug(f"Health check failed: {e}")

            # Log progress periodically
            if int(elapsed) % 60 == 0 and elapsed > 0:
                logger.info(f"Still waiting for server... ({elapsed:.0f}s elapsed)")

            time.sleep(5)

        raise TimeoutError(
            f"Tinker server did not become ready within {timeout}s. "
            f"This could be due to:\n"
            f"  - Large model still downloading from HuggingFace\n"
            f"  - Server crashed during startup\n"
            f"  - Network/firewall issues\n"
            f"Check logs: flow logs {handle.task_id}"
        )

    def stop_server(self, handle: TinkerTaskHandle) -> None:
        """Stop a running Tinker server."""
        flow = self._get_flow_client()
        flow.cancel(handle.task_id)
        logger.info(f"Stopped Tinker server {handle.task_id}")


def estimate_gpu_memory_gb(base_model: str, lora_rank: int = 32, batch_size: int = 1) -> float:
    """Estimate GPU memory requirements for a model and workload.

    This is a rough estimate. Actual requirements depend on:
    - Sequence length
    - Gradient checkpointing
    - Mixed precision settings
    - Framework overhead

    Args:
        base_model: HuggingFace model ID
        lora_rank: LoRA rank
        batch_size: Training batch size

    Returns:
        Estimated GPU memory in GB (per GPU with tensor parallelism)
    """
    params_b = MODEL_PARAM_BILLIONS.get(base_model, 7.0)

    # Rough formula: params * 2 (bf16) + activations + optimizer states
    # With LoRA, we only store optimizer states for adapter params
    base_memory = params_b * 2  # Model weights in bf16
    activation_memory = params_b * 0.5 * batch_size  # Rough activation estimate
    lora_overhead = lora_rank * 0.01 * params_b  # LoRA adapter memory

    return base_memory + activation_memory + lora_overhead
