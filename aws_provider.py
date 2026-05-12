import uuid
from typing import Dict

from provider_base import CloudProvider
from models import ProvisionRequest, ProvisionResponse, InstanceTier

class AWSProvider(CloudProvider):
    @property
    def provider_name(self) -> str:
        return "AWS"

    def provision_server(self, request: ProvisionRequest) -> ProvisionResponse:
        cost = self.get_cost(request.tier, request.region)
        instance_id = f"i-{uuid.uuid4().hex[:17]}"

        return ProvisionResponse(
            provider_name=self.provider_name,
            instance_id=instance_id,
            ip_address="3.2.1.45",
            cost_per_month=cost,
            status="provisioned"
        )

    def get_cost(self, tier: InstanceTier, region: str) -> float:
        # Mock high cost for AWS
        costs = {
            InstanceTier.PLATFORM_SMALL: 25.0,
            InstanceTier.PLATFORM_MEDIUM: 50.0,
            InstanceTier.PLATFORM_LARGE: 100.0,
        }
        return costs.get(tier, 0.0)

    def get_latency(self, region: str) -> float:
        # Mock low latency for AWS due to extensive regions
        return 10.0
