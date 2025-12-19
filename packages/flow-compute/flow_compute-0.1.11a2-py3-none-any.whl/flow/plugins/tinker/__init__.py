"""Tinker integration plugin for flow-compute.

This plugin deploys SkyRL-TX on Mithril GPU clusters to provide Tinker-compatible
training services. Flow handles infrastructure (provisioning, monitoring),
SkyRL-TX handles training (JAX/Flax engine with efficient multi-LoRA support).

Components:
    TinkerFrontendAdapter - Deploys SkyRL-TX on Mithril instances
    TinkerClient - SDK-compatible client for training/sampling operations

Usage:
    from flow.plugins.tinker import TinkerFrontendAdapter

    # Launch SkyRL-TX server on Mithril
    adapter = TinkerFrontendAdapter()
    handle = adapter.launch_server(
        base_model="Qwen/Qwen3-4B",
        instance_type="8xh100",
        checkpoints_base="s3://my-bucket/checkpoints",  # Optional S3 storage
    )

    # Use standard Tinker SDK
    import tinker
    client = tinker.ServiceClient(base_url=handle.base_url)

    # Or use flow-native TinkerClient
    from flow.plugins.tinker import TinkerClient
    client = TinkerClient(instance_type="8xh100")
    training = client.create_lora_training_client(
        base_model="Qwen/Qwen3-4B",
        rank=32,
    )
    training.forward_backward(data, loss_fn="cross_entropy")
    training.optim_step(adam_params)
"""

from flow.plugins.tinker.adapter import TinkerFrontendAdapter
from flow.plugins.tinker.client import TinkerClient

__all__ = [
    "TinkerClient",
    "TinkerFrontendAdapter",
]
