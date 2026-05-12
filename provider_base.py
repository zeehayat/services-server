from abc import ABC, abstractmethod
from typing import Dict, Any

from models import ProvisionRequest, ProvisionResponse, InstanceTier

class CloudProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the cloud provider."""
        pass

    @abstractmethod
    def provision_server(self, request: ProvisionRequest) -> ProvisionResponse:
        """Provisions a server based on the standardized request."""
        pass

    @abstractmethod
    def get_cost(self, tier: InstanceTier, region: str) -> float:
        """Returns the monthly cost for the specified tier and region."""
        pass

    @abstractmethod
    def get_latency(self, region: str) -> float:
        """Returns the estimated latency in milliseconds to the specified region."""
        pass
