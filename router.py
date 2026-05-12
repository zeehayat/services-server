from typing import List, Optional, Tuple

from provider_base import CloudProvider
from models import ProvisionRequest, ProvisionResponse
from aws_provider import AWSProvider
from gcp_provider import GCPProvider
from hetzner_provider import HetznerProvider
from vultr_provider import VultrProvider

class ProviderRouter:
    def __init__(self, providers: Optional[List[CloudProvider]] = None):
        if providers is None:
            self.providers = [
                AWSProvider(),
                GCPProvider(),
                HetznerProvider(),
                VultrProvider()
            ]
        else:
            self.providers = providers

    def _normalize_scores(self, raw_scores: List[float], invert: bool = False) -> List[float]:
        """
        Normalizes scores to be between 0 and 1.
        If invert is True, lower raw scores will map to higher normalized scores (closer to 1),
        which is useful for cost and latency where lower is better.
        """
        if not raw_scores:
            return []

        min_score = min(raw_scores)
        max_score = max(raw_scores)

        if max_score == min_score:
            return [1.0] * len(raw_scores)

        normalized = []
        for score in raw_scores:
            norm_score = (score - min_score) / (max_score - min_score)
            if invert:
                norm_score = 1.0 - norm_score
            normalized.append(norm_score)

        return normalized

    def find_best_provider(self, request: ProvisionRequest) -> CloudProvider:
        """
        Finds the best provider based on the formula:
        Score = (W_c * CostScore) + (W_l * LatencyScore)
        """
        # Collect raw cost and latency values
        raw_costs = []
        raw_latencies = []

        for provider in self.providers:
            raw_costs.append(provider.get_cost(request.tier, request.region))
            raw_latencies.append(provider.get_latency(request.region))

        # Normalize them so lower cost/latency gets a higher score (closer to 1.0)
        norm_costs = self._normalize_scores(raw_costs, invert=True)
        norm_latencies = self._normalize_scores(raw_latencies, invert=True)

        # Determine weights based on request
        if request.low_latency_required:
            w_c = 0.3
            w_l = 0.7
        else:
            w_c = 0.9
            w_l = 0.1

        best_score = -1.0
        best_provider = None

        for i, provider in enumerate(self.providers):
            score = (w_c * norm_costs[i]) + (w_l * norm_latencies[i])
            if score > best_score:
                best_score = score
                best_provider = provider

        return best_provider

    def route_request(self, request: ProvisionRequest) -> ProvisionResponse:
        """Routes the provision request to the best matching provider."""
        best_provider = self.find_best_provider(request)
        if not best_provider:
            raise Exception("No suitable provider found.")

        return best_provider.provision_server(request)
