"""
Federated Execution for FlowMason.

Enables distributed pipeline execution across multiple clouds and regions.
"""

from flowmason_core.federation.coordinator import FederationCoordinator
from flowmason_core.federation.remote_executor import RemoteExecutor
from flowmason_core.federation.data_router import DataRouter
from flowmason_core.federation.models import (
    FederationConfig,
    FederationStrategy,
    RegionConfig,
    RemoteNode,
    FederatedStageConfig,
    AggregationStrategy,
)

__all__ = [
    "FederationCoordinator",
    "RemoteExecutor",
    "DataRouter",
    "FederationConfig",
    "FederationStrategy",
    "RegionConfig",
    "RemoteNode",
    "FederatedStageConfig",
    "AggregationStrategy",
]
