from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class InstanceTier(Enum):
    PLATFORM_SMALL = "Platform_Small"
    PLATFORM_MEDIUM = "Platform_Medium"
    PLATFORM_LARGE = "Platform_Large"

@dataclass
class ServerSpec:
    vcpus: int
    ram_gb: int
    disk_gb: int

# Standardize the tiers
TIER_SPECS = {
    InstanceTier.PLATFORM_SMALL: ServerSpec(vcpus=2, ram_gb=4, disk_gb=40),
    InstanceTier.PLATFORM_MEDIUM: ServerSpec(vcpus=4, ram_gb=8, disk_gb=80),
    InstanceTier.PLATFORM_LARGE: ServerSpec(vcpus=8, ram_gb=16, disk_gb=160),
}

@dataclass
class ProvisionRequest:
    tier: InstanceTier
    region: str
    low_latency_required: bool = False
    additional_metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProvisionResponse:
    provider_name: str
    instance_id: str
    ip_address: str
    cost_per_month: float
    status: str
