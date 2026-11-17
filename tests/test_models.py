"""Unit tests for Pydantic domain models and API contracts."""

import pytest
from pydantic import ValidationError

from infragraph.models import (
    AttackPathRequest,
    AttackPathResponse,
    AttackStep,
    ChokepointDetail,
    CriticalNodesResponse,
    Host,
    TopologyScenario,
    Vulnerability,
    VulnerabilitySeverity,
)


def test_valid_host_creation() -> None:
    """Verifies that a Host instance is created with valid fields and defaults."""
    host = Host(
        id="srv-web",
        name="Public Web Server",
        ip="203.0.113.10",
        is_exposed=True,
    )
    assert host.id == "srv-web"
    assert host.is_exposed is True

    # Test default is_exposed
    internal_host = Host(id="srv-db", name="Internal DB", ip="10.0.0.5")
    assert internal_host.is_exposed is False


def test_vulnerability_cve_pattern_and_score_validation() -> None:
    """Verifies that CVE regex pattern and CVSS score ranges are strictly enforced."""
    # Valid vulnerability
    vuln = Vulnerability(
        cve_id="CVE-2023-38606",
        severity=VulnerabilitySeverity.CRITICAL,
        cvss_score=9.8,
        description="Remote Code Execution",
    )
    assert vuln.cve_id == "CVE-2023-38606"
    assert vuln.cvss_score == 9.8

    # Invalid CVE ID format
    with pytest.raises(ValidationError) as exc_info:
        Vulnerability(
            cve_id="MALFORMED-CVE",
            severity=VulnerabilitySeverity.HIGH,
            cvss_score=8.0,
        )
    assert "cve_id" in str(exc_info.value)

    # Invalid CVSS score (> 10.0)
    with pytest.raises(ValidationError) as exc_info:
        Vulnerability(
            cve_id="CVE-2023-1111",
            severity=VulnerabilitySeverity.HIGH,
            cvss_score=11.5,
        )
    assert "cvss_score" in str(exc_info.value)


def test_valid_topology_scenario() -> None:
    """Verifies that a complete valid scenario passes referential integrity."""
    scenario_data = {
        "scenario_name": "Test Breach",
        "hosts": [
            {"id": "srv-web", "name": "Web", "ip": "1.1.1.1", "is_exposed": True},
            {"id": "srv-internal", "name": "Internal", "ip": "10.0.0.1"},
        ],
        "vulnerabilities": [
            {
                "cve_id": "CVE-2023-38606",
                "severity": "CRITICAL",
                "cvss_score": 9.8,
            }
        ],
        "users": [
            {"username": "deploy_user", "role": "DevOps", "is_privileged": True}
        ],
        "critical_assets": [
            {
                "id": "db-production",
                "name": "DB",
                "asset_type": "DATABASE",
                "business_impact": "CATASTROPHIC",
            }
        ],
        "relationships": [
            {"source": "srv-web", "type": "EXPOSES", "target": "CVE-2023-38606"},
            {"source": "deploy_user", "type": "HAS_SESSION", "target": "srv-web"},
            {"source": "deploy_user", "type": "CAN_SSH_TO", "target": "srv-internal"},
            {"source": "srv-internal", "type": "ACCESSES", "target": "db-production"},
        ],
    }

    scenario = TopologyScenario.model_validate(scenario_data)
    assert scenario.scenario_name == "Test Breach"
    assert len(scenario.hosts) == 2
    assert len(scenario.relationships) == 4


def test_referential_integrity_detects_unknown_source() -> None:
    """Verifies that relationships referencing non-existent sources raise an error."""
    scenario_data = {
        "scenario_name": "Broken Scenario",
        "hosts": [{"id": "srv-web", "name": "Web", "ip": "1.1.1.1"}],
        "relationships": [
            {"source": "unknown-node", "type": "CAN_SSH_TO", "target": "srv-web"}
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        TopologyScenario.model_validate(scenario_data)
    assert "Relationship source 'unknown-node' does not exist" in str(exc_info.value)


def test_referential_integrity_detects_unknown_target() -> None:
    """Verifies that relationships referencing non-existent targets raise an error."""
    scenario_data = {
        "scenario_name": "Broken Scenario",
        "hosts": [{"id": "srv-web", "name": "Web", "ip": "1.1.1.1"}],
        "relationships": [
            {"source": "srv-web", "type": "ACCESSES", "target": "non-existent-asset"}
        ],
    }

    with pytest.raises(ValidationError) as exc_info:
        TopologyScenario.model_validate(scenario_data)
    assert "Relationship target 'non-existent-asset' does not exist" in str(
        exc_info.value
    )


def test_attack_path_request_and_response() -> None:
    """Verifies creation and validation of API request and response models."""
    req = AttackPathRequest(start_host_id="srv-web", target_asset_id="db-production")
    assert req.start_host_id == "srv-web"

    # Empty string is forbidden
    with pytest.raises(ValidationError):
        AttackPathRequest(start_host_id="", target_asset_id="db-production")

    step1 = AttackStep(
        step=1, node="srv-web", type="Host", action="Initial exposed entry point"
    )
    step2 = AttackStep(
        step=2, node="db-production", type="CriticalAsset", action="Breach achieved"
    )

    res = AttackPathResponse(
        found=True,
        hops_count=1,
        attack_vector=[step1, step2],
        chokepoints=["srv-web"],
    )
    assert res.found is True
    assert len(res.attack_vector) == 2
    assert res.chokepoints == ["srv-web"]


def test_critical_nodes_response() -> None:
    """Verifies the critical nodes response schema."""
    chokepoint = ChokepointDetail(
        node_id="deploy_user",
        type="User",
        impact_percentage=85.5,
        risk_reason="Widespread administrative access",
    )
    res = CriticalNodesResponse(total_analyzed=10, top_chokepoints=[chokepoint])
    assert res.total_analyzed == 10
    assert res.top_chokepoints[0].impact_percentage == 85.5
