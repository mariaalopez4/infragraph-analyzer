"""Domain models and Pydantic v2 schemas for InfraGraph Analyzer.

Defines the graph entities (Host, Vulnerability, User, CriticalAsset),
their directed relationships, the declarative topology scenario schema,
and the REST API request/response contracts.
"""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class VulnerabilitySeverity(StrEnum):
    """CVSS vulnerability severity levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AssetType(StrEnum):
    """Classification of critical business assets."""

    DATABASE = "DATABASE"
    DOMAIN_CONTROLLER = "DOMAIN_CONTROLLER"
    SECRET_VAULT = "SECRET_VAULT"
    INTERNAL_SERVICE = "INTERNAL_SERVICE"


class BusinessImpact(StrEnum):
    """Business impact level if a critical asset is compromised."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CATASTROPHIC = "CATASTROPHIC"


class RelationshipType(StrEnum):
    """Allowed directed relationship types between graph nodes."""

    EXPOSES = "EXPOSES"
    HAS_SESSION = "HAS_SESSION"
    CAN_SSH_TO = "CAN_SSH_TO"
    ACCESSES = "ACCESSES"


# ------------------------------------------------------------------------------
# Graph Entities (Nodes)
# ------------------------------------------------------------------------------


class BaseEntity(BaseModel):
    """Base schema with strict validation and whitespace stripping."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Host(BaseEntity):
    """Represents a physical machine, virtual instance, or container."""

    id: str = Field(..., min_length=1, description="Unique identifier for the host")
    name: str = Field(..., min_length=1, description="Human-readable host name")
    ip: str = Field(..., min_length=1, description="Host IP address or hostname")
    is_exposed: bool = Field(
        default=False,
        description="Whether the host is directly reachable from public Internet",
    )


class Vulnerability(BaseEntity):
    """Represents a known security flaw or CVE associated with a host."""

    cve_id: str = Field(
        ...,
        pattern=r"^CVE-\d{4}-\d{4,}$",
        description="Standard CVE identifier (e.g. CVE-2023-38606)",
    )
    severity: VulnerabilitySeverity = Field(
        ..., description="Severity category of the vulnerability"
    )
    cvss_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Common Vulnerability Scoring System score between 0.0 and 10.0",
    )
    description: str = Field(
        default="", description="Summary of the vulnerability impact"
    )


class User(BaseEntity):
    """Represents a user account, service identity, or credential."""

    username: str = Field(
        ..., min_length=1, description="Unique account or service username"
    )
    role: str = Field(
        default="User", description="Functional role or group membership"
    )
    is_privileged: bool = Field(
        default=False,
        description="Whether the account possesses elevated/administrator privileges",
    )


class CriticalAsset(BaseEntity):
    """Represents a high-value crown jewel asset targeted by attackers."""

    id: str = Field(
        ..., min_length=1, description="Unique identifier for the critical asset"
    )
    name: str = Field(..., min_length=1, description="Descriptive name of the asset")
    asset_type: AssetType = Field(
        default=AssetType.DATABASE, description="Classification of the critical asset"
    )
    business_impact: BusinessImpact = Field(
        default=BusinessImpact.HIGH,
        description="Severity of damage if this asset is compromised",
    )


# ------------------------------------------------------------------------------
# Graph Relationships (Edges)
# ------------------------------------------------------------------------------


class Relationship(BaseEntity):
    """Represents a directed relationship between two entities in the graph."""

    source: str = Field(
        ..., min_length=1, description="Identifier of the origin node"
    )
    type: RelationshipType = Field(
        ..., description="Type of directed relationship connecting the nodes"
    )
    target: str = Field(
        ..., min_length=1, description="Identifier of the destination node"
    )


# ------------------------------------------------------------------------------
# Declarative Topology Scenario
# ------------------------------------------------------------------------------


class TopologyScenario(BaseEntity):
    """Complete declarative definition of an infrastructure network graph."""

    scenario_name: str = Field(..., min_length=1, description="Name of the scenario")
    version: str = Field(
        default="1.0", description="Schema specification version for the scenario"
    )
    hosts: list[Host] = Field(
        default_factory=list, description="List of infrastructure hosts"
    )
    vulnerabilities: list[Vulnerability] = Field(
        default_factory=list, description="List of known security vulnerabilities"
    )
    users: list[User] = Field(
        default_factory=list, description="List of user and service accounts"
    )
    critical_assets: list[CriticalAsset] = Field(
        default_factory=list, description="List of critical crown jewel assets"
    )
    relationships: list[Relationship] = Field(
        default_factory=list, description="List of directed relationships"
    )

    @model_validator(mode="after")
    def validate_referential_integrity(self) -> Self:
        """Ensures all relationship sources and targets reference existing entities."""
        known_identifiers: set[str] = set()

        for host in self.hosts:
            known_identifiers.add(host.id)
        for vuln in self.vulnerabilities:
            known_identifiers.add(vuln.cve_id)
        for user in self.users:
            known_identifiers.add(user.username)
        for asset in self.critical_assets:
            known_identifiers.add(asset.id)

        for rel in self.relationships:
            if rel.source not in known_identifiers:
                raise ValueError(
                    f"Relationship source '{rel.source}' does not exist in scenario."
                )
            if rel.target not in known_identifiers:
                raise ValueError(
                    f"Relationship target '{rel.target}' does not exist in scenario."
                )

        return self


# ------------------------------------------------------------------------------
# API Request and Response Schemas (DTOs)
# ------------------------------------------------------------------------------


class AttackPathRequest(BaseEntity):
    """Payload for finding attack paths between an entry host and a target."""

    start_host_id: str = Field(
        ..., min_length=1, description="ID of the starting host (entry point)"
    )
    target_asset_id: str = Field(
        ..., min_length=1, description="ID of the target critical asset"
    )


class AttackStep(BaseEntity):
    """A single hop in an attack vector path."""

    step: int = Field(..., ge=1, description="Sequential step number (1-based)")
    node: str = Field(..., description="Identifier or name of the node in this hop")
    type: str = Field(
        ..., description="Entity type (Host, User, Vulnerability, CriticalAsset)"
    )
    action: str = Field(
        ..., description="Security explanation of what happens in this step"
    )


class AttackPathResponse(BaseEntity):
    """Response payload containing the shortest attack path and chokepoints."""

    found: bool = Field(..., description="Whether a valid attack path exists")
    hops_count: int = Field(default=0, ge=0, description="Total number of hops")
    attack_vector: list[AttackStep] = Field(
        default_factory=list, description="Ordered sequence of attack steps"
    )
    chokepoints: list[str] = Field(
        default_factory=list,
        description="Critical intermediate nodes where the path can be cut",
    )


class ChokepointDetail(BaseEntity):
    """Detail of a high-centrality bottleneck entity."""

    node_id: str = Field(..., description="Identifier of the chokepoint node")
    type: str = Field(..., description="Type of the node (User, Host, etc.)")
    impact_percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Percentage of network reachable through this node",
    )
    risk_reason: str = Field(..., description="Contextual explanation of the risk")


class CriticalNodesResponse(BaseEntity):
    """Response payload listing top infrastructure chokepoints."""

    total_analyzed: int = Field(..., ge=0, description="Total nodes evaluated")
    top_chokepoints: list[ChokepointDetail] = Field(
        default_factory=list, description="Ranked list of critical chokepoints"
    )
