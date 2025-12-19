"""Tinker-compatible client for flow-compute.

This module provides a Python SDK that mirrors the Tinker API, allowing users
to write training code that works with both Thinking Machines' Tinker service
and flow-compute on Mithril.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

import httpx

from flow.plugins.tinker.adapter import TinkerFrontendAdapter, TinkerTaskHandle
from flow.plugins.tinker.types import (
    AdamParams,
    CreateModelResponse,
    Datum,
    ForwardBackwardOutput,
    FutureResponse,
    LoraConfig,
    ModelInput,
    OptimStepResponse,
    SampleResponse,
    SamplingParams,
    SaveWeightsResponse,
)

logger = logging.getLogger(__name__)


class APIFuture:
    """A future representing an async API operation.

    Compatible with Tinker SDK's APIFuture interface.
    """

    def __init__(
        self,
        client: httpx.Client,
        request_id: str,
        result_parser: Callable[[dict], Any],
    ):
        self._client = client
        self._request_id = request_id
        self._result_parser = result_parser
        self._result: Any = None
        self._done = False
        self._error: Exception | None = None

    def result(self, timeout: float = 300.0) -> Any:
        """Block until the result is available.

        Handles transient network errors with retries.
        """
        if self._done:
            if self._error:
                raise self._error
            return self._result

        deadline = time.time() + timeout
        poll_interval = 0.1
        max_poll = 2.0
        consecutive_errors = 0
        max_consecutive_errors = 10

        while time.time() < deadline:
            try:
                response = self._client.post(
                    "/api/v1/retrieve_future",
                    json={"request_id": self._request_id},
                )
                consecutive_errors = 0  # Reset on successful request

                if response.status_code == 200:
                    self._result = self._result_parser(response.json())
                    self._done = True
                    return self._result

                if response.status_code == 408:
                    # Timeout from server, keep polling
                    pass
                elif response.status_code == 500:
                    # Server error - check if it's a failure result
                    try:
                        error_data = response.json()
                        if error_data.get("status") == "failed":
                            error_msg = error_data.get("error", "Unknown error")
                            self._error = RuntimeError(f"Request failed: {error_msg}")
                            self._done = True
                            raise self._error
                    except (ValueError, KeyError):
                        pass  # JSON parse error or missing field, keep polling
                elif response.status_code >= 400:
                    raise RuntimeError(f"Request failed: {response.text}")

            except httpx.ConnectError as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    raise RuntimeError(
                        f"Lost connection to server after {max_consecutive_errors} attempts. "
                        f"Server may have crashed."
                    ) from e
                logger.warning(f"Connection error (attempt {consecutive_errors}): {e}")
            except httpx.RequestError as e:
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    raise RuntimeError(f"Request error: {e}") from e
                logger.warning(f"Request error (attempt {consecutive_errors}): {e}")

            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, max_poll)

        raise TimeoutError(f"Request {self._request_id} timed out after {timeout}s")

    async def result_async(self, timeout: float = 300.0) -> Any:
        """Async version of result()."""
        import asyncio

        return await asyncio.get_event_loop().run_in_executor(None, lambda: self.result(timeout))

    @property
    def done(self) -> bool:
        """Check if the future is complete."""
        return self._done


@dataclass
class TrainingClient:
    """Client for training operations on a specific model.

    Mirrors the Tinker SDK's TrainingClient interface.
    """

    _http: httpx.Client
    _model_id: str
    _base_model: str
    _lora_config: LoraConfig
    _executor: ThreadPoolExecutor = field(default_factory=lambda: ThreadPoolExecutor(max_workers=4))

    @property
    def model_id(self) -> str:
        """The unique identifier for this training model."""
        return self._model_id

    @property
    def base_model(self) -> str:
        """The base model this adapter is built on."""
        return self._base_model

    def forward_backward(
        self,
        data: list[Datum],
        loss_fn: str = "cross_entropy",
    ) -> APIFuture:
        """Compute forward pass and accumulate gradients.

        Args:
            data: List of training examples
            loss_fn: Loss function ("cross_entropy", "importance_sampling", "ppo")

        Returns:
            APIFuture that resolves to ForwardBackwardOutput
        """
        response = self._http.post(
            "/api/v1/forward_backward",
            json={
                "model_id": self._model_id,
                "forward_backward_input": {
                    "data": [d.model_dump() for d in data],
                    "loss_fn": loss_fn,
                },
            },
        )
        response.raise_for_status()
        future_data = FutureResponse.model_validate(response.json())

        return APIFuture(
            client=self._http,
            request_id=future_data.request_id,
            result_parser=lambda d: ForwardBackwardOutput.model_validate(d),
        )

    async def forward_backward_async(
        self,
        data: list[Datum],
        loss_fn: str = "cross_entropy",
    ) -> APIFuture:
        """Async version of forward_backward."""
        return self.forward_backward(data, loss_fn)

    def optim_step(self, adam_params: AdamParams) -> APIFuture:
        """Apply accumulated gradients with optimizer step.

        Args:
            adam_params: Optimizer parameters

        Returns:
            APIFuture that resolves to OptimStepResponse
        """
        response = self._http.post(
            "/api/v1/optim_step",
            json={
                "model_id": self._model_id,
                "adam_params": adam_params.model_dump(),
            },
        )
        response.raise_for_status()
        future_data = FutureResponse.model_validate(response.json())

        return APIFuture(
            client=self._http,
            request_id=future_data.request_id,
            result_parser=lambda d: OptimStepResponse.model_validate(d),
        )

    async def optim_step_async(self, adam_params: AdamParams) -> APIFuture:
        """Async version of optim_step."""
        return self.optim_step(adam_params)

    def save_weights(self, name: str) -> APIFuture:
        """Save training weights and optimizer state.

        Args:
            name: Checkpoint name/path

        Returns:
            APIFuture that resolves to SaveWeightsResponse
        """
        response = self._http.post(
            "/api/v1/save_weights",
            json={"model_id": self._model_id, "path": name},
        )
        response.raise_for_status()
        future_data = FutureResponse.model_validate(response.json())

        return APIFuture(
            client=self._http,
            request_id=future_data.request_id,
            result_parser=lambda d: SaveWeightsResponse.model_validate(d),
        )

    def save_weights_for_sampler(self, name: str) -> APIFuture:
        """Save weights in a format suitable for inference/sampling.

        Args:
            name: Checkpoint name/path

        Returns:
            APIFuture that resolves to SaveWeightsResponse with sampler path
        """
        response = self._http.post(
            "/api/v1/save_weights_for_sampler",
            json={"model_id": self._model_id, "path": name},
        )
        response.raise_for_status()
        future_data = FutureResponse.model_validate(response.json())

        return APIFuture(
            client=self._http,
            request_id=future_data.request_id,
            result_parser=lambda d: SaveWeightsResponse.model_validate(d),
        )

    def save_weights_and_get_sampling_client(self, name: str) -> SamplingClient:
        """Save weights and return a SamplingClient for inference.

        This is a convenience method that combines save_weights_for_sampler
        and create_sampling_client.

        Args:
            name: Checkpoint name

        Returns:
            SamplingClient configured to use the saved checkpoint
        """
        result = self.save_weights_for_sampler(name).result()
        return SamplingClient(
            _http=self._http,
            _model_path=result.path,
            _base_model=None,
        )

    async def save_weights_and_get_sampling_client_async(self, name: str) -> SamplingClient:
        """Async version of save_weights_and_get_sampling_client."""
        result = await self.save_weights_for_sampler(name).result_async()
        return SamplingClient(
            _http=self._http,
            _model_path=result.path,
            _base_model=None,
        )

    def load_weights(self, path: str) -> APIFuture:
        """Load weights from a checkpoint.

        Args:
            path: Tinker path to the checkpoint (tinker://model_id/weights/name)

        Returns:
            APIFuture that resolves when loading is complete
        """
        response = self._http.post(
            "/api/v1/load_weights",
            json={"model_id": self._model_id, "path": path},
        )
        response.raise_for_status()
        future_data = FutureResponse.model_validate(response.json())

        return APIFuture(
            client=self._http,
            request_id=future_data.request_id,
            result_parser=lambda d: d,
        )


@dataclass
class SamplingClient:
    """Client for sampling/inference operations.

    Mirrors the Tinker SDK's SamplingClient interface.
    """

    _http: httpx.Client
    _model_path: str | None
    _base_model: str | None

    @property
    def model_path(self) -> str | None:
        """The tinker path to the model checkpoint."""
        return self._model_path

    def sample(
        self,
        prompt: ModelInput | list[int],
        sampling_params: SamplingParams,
        num_samples: int = 1,
        prompt_logprobs: bool = False,
    ) -> Future[SampleResponse]:
        """Generate samples from the model.

        Args:
            prompt: Input tokens as ModelInput or list of ints
            sampling_params: Generation parameters
            num_samples: Number of sequences to generate
            prompt_logprobs: Whether to return prompt logprobs

        Returns:
            Future that resolves to SampleResponse
        """
        if isinstance(prompt, list):
            prompt = ModelInput.from_tokens(prompt)

        request_body = {
            "prompt": prompt.model_dump(),
            "sampling_params": sampling_params.model_dump(),
            "num_samples": num_samples,
            "prompt_logprobs": prompt_logprobs,
        }

        if self._model_path:
            request_body["model_path"] = self._model_path
        elif self._base_model:
            request_body["base_model"] = self._base_model

        response = self._http.post("/api/v1/asample", json=request_body)
        response.raise_for_status()
        future_data = FutureResponse.model_validate(response.json())

        return APIFuture(
            client=self._http,
            request_id=future_data.request_id,
            result_parser=lambda d: SampleResponse.model_validate(d),
        )

    async def sample_async(
        self,
        prompt: ModelInput | list[int],
        sampling_params: SamplingParams,
        num_samples: int = 1,
        prompt_logprobs: bool = False,
    ) -> Future[SampleResponse]:
        """Async version of sample."""
        return self.sample(prompt, sampling_params, num_samples, prompt_logprobs)


@dataclass
class TinkerClient:
    """Main client for Tinker operations on flow-compute.

    This client manages the connection to a Tinker server running on Mithril
    and provides factory methods for creating training and sampling clients.

    Example:
        # Connect to an existing server
        client = TinkerClient(base_url="http://mithril-instance:8000")
        training = client.create_lora_training_client(
            base_model="Qwen/Qwen3-4B",
            rank=32,
        )

        # Or launch a new server automatically
        client = TinkerClient(instance_type="4xh100")
        training = client.create_lora_training_client(
            base_model="Qwen/Qwen3-4B",
            rank=32,
        )
    """

    base_url: str | None = None
    instance_type: str | None = None
    _http: httpx.Client | None = field(default=None, repr=False)
    _adapter: TinkerFrontendAdapter | None = field(default=None, repr=False)
    _server_handle: TinkerTaskHandle | None = field(default=None, repr=False)

    def __post_init__(self):
        if self.base_url:
            self._http = httpx.Client(
                base_url=self.base_url,
                timeout=httpx.Timeout(30.0, read=300.0),
            )

    def _ensure_server(self, base_model: str) -> httpx.Client:
        """Ensure a server is running and return HTTP client."""
        if self._http:
            return self._ensure_connection()

        if not self.instance_type:
            raise ValueError(
                "Either base_url or instance_type must be provided. "
                "Use base_url to connect to an existing server, or "
                "instance_type to launch a new server on Mithril."
            )

        # Launch a new server
        if self._adapter is None:
            self._adapter = TinkerFrontendAdapter()

        self._server_handle = self._adapter.launch_server(
            base_model=base_model,
            instance_type=self.instance_type,
        )

        self._http = httpx.Client(
            base_url=self._server_handle.base_url,
            timeout=httpx.Timeout(30.0, read=300.0),
        )
        return self._http

    def _ensure_connection(self) -> httpx.Client:
        """Ensure HTTP connection is alive, reconnect if needed."""
        if self._http is None:
            raise RuntimeError("No HTTP client configured")

        try:
            # Quick health check
            response = self._http.get("/api/v1/healthz", timeout=5.0)
            if response.status_code == 200:
                return self._http
        except httpx.RequestError:
            pass

        # Connection lost, attempt reconnect
        logger.warning("Connection lost, attempting reconnect...")
        self._http.close()

        # Determine base URL
        if self._server_handle:
            base_url = self._server_handle.base_url
        elif self.base_url:
            base_url = self.base_url
        else:
            raise RuntimeError("Cannot reconnect: no base URL available")

        self._http = httpx.Client(
            base_url=base_url,
            timeout=httpx.Timeout(30.0, read=300.0),
        )

        # Verify reconnection
        try:
            response = self._http.get("/api/v1/healthz", timeout=10.0)
            response.raise_for_status()
            logger.info("Reconnected successfully")
            return self._http
        except httpx.RequestError as e:
            raise RuntimeError(f"Failed to reconnect: {e}") from e

    def create_lora_training_client(
        self,
        base_model: str,
        rank: int = 32,
        alpha: float = 32.0,
        user_metadata: dict[str, str] | None = None,
    ) -> TrainingClient:
        """Create a new LoRA training client.

        Args:
            base_model: HuggingFace model ID
            rank: LoRA rank (default 32)
            alpha: LoRA alpha scaling factor
            user_metadata: Optional metadata for tracking

        Returns:
            TrainingClient for training operations
        """
        http = self._ensure_server(base_model)
        lora_config = LoraConfig(rank=rank, alpha=alpha)

        response = http.post(
            "/api/v1/create_model",
            json={
                "base_model": base_model,
                "lora_config": {"rank": rank},
            },
        )
        response.raise_for_status()
        model_data = CreateModelResponse.model_validate(response.json())

        logger.info(f"Created training client: model_id={model_data.model_id}")

        return TrainingClient(
            _http=http,
            _model_id=model_data.model_id,
            _base_model=base_model,
            _lora_config=lora_config,
        )

    async def create_lora_training_client_async(
        self,
        base_model: str,
        rank: int = 32,
        alpha: float = 32.0,
        user_metadata: dict[str, str] | None = None,
    ) -> TrainingClient:
        """Async version of create_lora_training_client."""
        return self.create_lora_training_client(base_model, rank, alpha, user_metadata)

    def create_sampling_client(
        self,
        base_model: str | None = None,
        model_path: str | None = None,
    ) -> SamplingClient:
        """Create a client for sampling/inference.

        Args:
            base_model: HuggingFace model ID for base model inference
            model_path: Tinker path for fine-tuned model inference

        Returns:
            SamplingClient for generation
        """
        if base_model is None and model_path is None:
            raise ValueError("Either base_model or model_path must be provided")

        http = self._ensure_server(base_model or "")

        return SamplingClient(
            _http=http,
            _model_path=model_path,
            _base_model=base_model,
        )

    def get_server_capabilities(self) -> dict[str, Any]:
        """Get the capabilities of the connected server."""
        http = self._ensure_server("")
        response = http.get("/api/v1/get_server_capabilities")
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the client and optionally stop the server."""
        if self._http:
            self._http.close()
            self._http = None

    def stop_server(self) -> None:
        """Stop the Mithril server if we launched it."""
        if self._server_handle and self._adapter:
            self._adapter.stop_server(self._server_handle)
            self._server_handle = None

    def __enter__(self) -> TinkerClient:
        return self

    def __exit__(self, *args) -> None:
        self.close()
