from __future__ import annotations

import enum
from decimal import Decimal
from typing import Self

import pydantic as pd
from kubernetes.client.models import V1Container

from robusta_krr.utils import resource_units


class ResourceType(str, enum.Enum):
    """The type of resource.

    Just add new types here and they will be automatically supported.
    """

    CPU = "cpu"
    Memory = "memory"


class ResourceAllocations(pd.BaseModel):
    requests: dict[ResourceType, Decimal | None]
    limits: dict[ResourceType, Decimal | None]

    @pd.validator("requests", "limits", pre=True)
    def validate_requests(cls, value: dict[ResourceType, str | Decimal | None]) -> dict[ResourceType, Decimal | None]:
        return {
            resource_type: resource_units.parse(resource_value) if isinstance(resource_value, str) else resource_value
            for resource_type, resource_value in value.items()
        }

    @classmethod
    def from_container(cls, container: V1Container) -> Self:
        """Get the resource allocations from a Kubernetes container.

        Args:
            container: The Kubernetes container.

        Returns:
            The resource allocations.
        """

        return cls(
            requests={
                ResourceType.CPU: container.resources.requests.get("cpu")
                if container.resources and container.resources.requests
                else None,
                ResourceType.Memory: container.resources.requests.get("memory")
                if container.resources and container.resources.requests
                else None,
            },
            limits={
                ResourceType.CPU: container.resources.limits.get("cpu")
                if container.resources and container.resources.limits
                else None,
                ResourceType.Memory: container.resources.limits.get("memory")
                if container.resources and container.resources.limits
                else None,
            },
        )
