import uuid
from typing import Dict

from provider_base import CloudProvider
from models import ProvisionRequest, ProvisionResponse, InstanceTier

class GCPProvider(CloudProvider):
    @property
    def provider_name(self) -> str:
        return "GCP"

    def provision_server(self, request: ProvisionRequest) -> ProvisionResponse:
        cost = self.get_cost(request.tier, request.region)
        instance_id = f"instance-{uuid.uuid4().hex[:10]}"

        return ProvisionResponse(
            provider_name=self.provider_name,
            instance_id=instance_id,
            ip_address="34.12.34.56",
            cost_per_month=cost,
            status="provisioned"
        )

    def get_cost(self, tier: InstanceTier, region: str) -> float:
        # Mock high cost for GCP
        costs = {
            InstanceTier.PLATFORM_SMALL: 24.0,
            InstanceTier.PLATFORM_MEDIUM: 48.0,
            InstanceTier.PLATFORM_LARGE: 96.0,
        }
        return costs.get(tier, 0.0)

    def get_latency(self, region: str) -> float:
        # Mock low latency for GCP
        return 12.0
