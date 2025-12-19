"""Tinker-compatible data types for flow-compute integration.

These types mirror the Tinker SDK's data structures to ensure API compatibility.
Based on skyrl-tx types with adaptations for flow-compute.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class RequestType(str, Enum):
    """Types of requests that can be processed by the Tinker engine."""

    CREATE_MODEL = "create_model"
    FORWARD_BACKWARD = "forward_backward"
    OPTIM_STEP = "optim_step"
    SAVE_WEIGHTS_FOR_SAMPLER = "save_weights_for_sampler"
    SAVE_WEIGHTS = "save_weights"
    LOAD_WEIGHTS = "load_weights"
    SAMPLE = "sample"
    EXTERNAL = "external"


class RequestStatus(str, Enum):
    """Status of a request in the processing queue."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class CheckpointType(str, Enum):
    """Type of checkpoint."""

    TRAINING = "training"
    SAMPLER = "sampler"


class TinkerPath(BaseModel):
    """Parsed tinker:// URL."""

    primary_id: str
    kind: str
    secondary_id: str

    @classmethod
    def parse(cls, url: str) -> TinkerPath | None:
        """Parse a tinker:// URL into components."""
        parsed = urlparse(url)

        match (parsed.scheme, *parsed.path.split("/")):
            case ("tinker", "", secondary_id):
                return cls(primary_id=parsed.netloc, kind="", secondary_id=secondary_id)
            case ("tinker", "", kind, secondary_id):
                return cls(primary_id=parsed.netloc, kind=kind, secondary_id=secondary_id)
            case _:
                return None


class AdamParams(BaseModel):
    """Adam optimizer parameters."""

    learning_rate: float = Field(default=1e-4, ge=0.0)
    beta1: float = Field(default=0.9, ge=0.0, lt=1.0)
    beta2: float = Field(default=0.95, ge=0.0, lt=1.0)
    eps: float = Field(default=1e-12, gt=0.0)


class LoraConfig(BaseModel):
    """LoRA adapter configuration."""

    rank: int = Field(..., gt=0, le=256)
    alpha: float = Field(default=32.0)
    train_attn: bool = True
    train_mlp: bool = True
    train_unembed: bool = False


class ModelInputChunk(BaseModel):
    """A chunk of input tokens."""

    tokens: list[int]


class ModelInput(BaseModel):
    """Model input consisting of token chunks."""

    chunks: list[ModelInputChunk]

    @classmethod
    def from_tokens(cls, tokens: list[int]) -> ModelInput:
        """Create ModelInput from a flat list of tokens."""
        return cls(chunks=[ModelInputChunk(tokens=tokens)])

    def to_tokens(self) -> list[int]:
        """Flatten all chunks into a single token list."""
        return [t for chunk in self.chunks for t in chunk.tokens]

    @property
    def length(self) -> int:
        """Total number of tokens across all chunks."""
        return sum(len(chunk.tokens) for chunk in self.chunks)


class TensorData(BaseModel):
    """Tensor data as a flat list with optional metadata."""

    data: list[int] | list[float]
    dtype: str = "float32"
    shape: list[int] | None = None


class LossFnInputs(BaseModel):
    """Inputs to the loss function for training."""

    target_tokens: TensorData
    weights: TensorData
    advantages: TensorData = Field(default_factory=lambda: TensorData(data=[]))
    logprobs: TensorData = Field(default_factory=lambda: TensorData(data=[]))


class Datum(BaseModel):
    """A single training example with inputs and loss function targets."""

    model_input: ModelInput
    loss_fn_inputs: dict[str, TensorData]

    @classmethod
    def for_supervised(
        cls,
        input_tokens: list[int],
        target_tokens: list[int],
        weights: list[float] | None = None,
    ) -> Datum:
        """Create a Datum for supervised fine-tuning."""
        if weights is None:
            weights = [1.0] * len(target_tokens)
        return cls(
            model_input=ModelInput.from_tokens(input_tokens),
            loss_fn_inputs={
                "target_tokens": TensorData(data=target_tokens),
                "weights": TensorData(data=weights),
            },
        )

    @classmethod
    def for_rl(
        cls,
        input_tokens: list[int],
        target_tokens: list[int],
        logprobs: list[float],
        advantages: list[float],
        weights: list[float] | None = None,
    ) -> Datum:
        """Create a Datum for reinforcement learning."""
        if weights is None:
            weights = [1.0] * len(target_tokens)
        return cls(
            model_input=ModelInput.from_tokens(input_tokens),
            loss_fn_inputs={
                "target_tokens": TensorData(data=target_tokens),
                "weights": TensorData(data=weights),
                "logprobs": TensorData(data=logprobs),
                "advantages": TensorData(data=advantages),
            },
        )


class SamplingParams(BaseModel):
    """Parameters for text generation/sampling."""

    max_tokens: int = Field(..., gt=0)
    temperature: float = Field(default=1.0, ge=0.0)
    seed: int | None = None
    stop: list[int] | None = None
    top_k: int = -1
    top_p: float = 1.0


class GeneratedSequence(BaseModel):
    """A single generated sequence from sampling."""

    tokens: list[int]
    logprobs: list[float]
    stop_reason: Literal["length", "stop"]


# Request/Response types for the REST API


class CreateModelRequest(BaseModel):
    """Request to create a new LoRA model."""

    base_model: str
    lora_config: LoraConfig


class CreateModelResponse(BaseModel):
    """Response from creating a model."""

    model_id: str
    base_model: str
    lora_config: LoraConfig
    status: str = "created"
    request_id: str


class ForwardBackwardInput(BaseModel):
    """Input for forward_backward operation."""

    data: list[Datum]
    loss_fn: Literal["cross_entropy", "importance_sampling", "ppo"]


class ForwardBackwardRequest(BaseModel):
    """Request for forward_backward operation."""

    model_id: str
    forward_backward_input: ForwardBackwardInput


class ForwardBackwardOutput(BaseModel):
    """Output from forward_backward operation."""

    loss_fn_output_type: str = "scalar"
    loss_fn_outputs: list[dict]
    metrics: dict = Field(default_factory=dict)


class OptimStepRequest(BaseModel):
    """Request for optimizer step."""

    model_id: str
    adam_params: AdamParams


class OptimStepResponse(BaseModel):
    """Response from optimizer step."""

    pass


class SampleRequest(BaseModel):
    """Request for sampling/generation."""

    prompt: ModelInput
    sampling_params: SamplingParams
    num_samples: int = 1
    base_model: str | None = None
    model_path: str | None = None
    prompt_logprobs: bool = False


class SampleResponse(BaseModel):
    """Response from sampling."""

    sequences: list[GeneratedSequence]
    prompt_logprobs: list[float] | None = None


class SaveWeightsRequest(BaseModel):
    """Request to save training weights."""

    model_id: str
    path: str


class SaveWeightsResponse(BaseModel):
    """Response from saving weights."""

    path: str
    type: str = "save_weights"


class FutureResponse(BaseModel):
    """Response for async operations."""

    future_id: str
    status: str = "pending"
    request_id: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["ok"]


class ServerCapabilities(BaseModel):
    """Server capabilities response."""

    supported_models: list[str]
    max_lora_adapters: int
    max_lora_rank: int
