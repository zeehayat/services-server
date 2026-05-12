import uuid
from typing import Dict

from provider_base import CloudProvider
from models import ProvisionRequest, ProvisionResponse, InstanceTier

class HetznerProvider(CloudProvider):
    @property
    def provider_name(self) -> str:
        return "Hetzner"

    def provision_server(self, request: ProvisionRequest) -> ProvisionResponse:
        cost = self.get_cost(request.tier, request.region)
        instance_id = str(uuid.uuid4().int)[:8] # Hetzner uses integer IDs

        return ProvisionResponse(
            provider_name=self.provider_name,
            instance_id=instance_id,
            ip_address="116.203.1.2",
            cost_per_month=cost,
            status="provisioned"
        )

    def get_cost(self, tier: InstanceTier, region: str) -> float:
        # Mock low cost for Hetzner
        costs = {
            InstanceTier.PLATFORM_SMALL: 7.0,   # e.g., CPX21
            InstanceTier.PLATFORM_MEDIUM: 15.0,
            InstanceTier.PLATFORM_LARGE: 30.0,
        }
        return costs.get(tier, 0.0)

    def get_latency(self, region: str) -> float:
        # Mock slightly higher latency for Hetzner depending on region
        # Assuming European focus
        if region.lower() in ["eu-central-1", "europe"]:
            return 15.0
        return 50.0
