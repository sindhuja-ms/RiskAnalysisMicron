"""
Unit test suite for Member 2's Deterministic Rules & SoD Violation Engine (engine/rules_engine.py).
"""

import pytest
from engine.rules_engine import RulesEngine
from data.loader import DataLoader


@pytest.fixture(scope="module")
def rules_engine() -> RulesEngine:
    """Fixture providing a cached instance of RulesEngine for testing."""
    return RulesEngine()


def test_operator_supervisor_conflict(rules_engine: RulesEngine) -> None:
    """Confirms adding Production Supervisor to Production Operator returns compliant=False, flags GL-01, and captures RCF-01."""
    result = rules_engine.evaluate_role_addition("Production Operator", "Production Supervisor")

    assert result["compliant"] is False
    assert result["conflict_id"] == "RCF-01"
    assert result["violated_law_id"] == "GL-01"
    assert result["risk_category"] == "CRITICAL DEFICIENCY"
    assert result["inherent_risk_score"] == 92
    assert "supervision" in result["vulnerability"].lower() or "defective" in result["vulnerability"].lower()
    assert "FORBIDDEN" in result["mandated_remediation"]


def test_operator_inventory_controller_conflict(rules_engine: RulesEngine) -> None:
    """Confirms adding Inventory Controller to Production Operator flags RCF-02 (Theft Risk) and GL-01."""
    result = rules_engine.evaluate_role_addition("Production Operator", "Inventory Controller")

    assert result["compliant"] is False
    assert result["conflict_id"] == "RCF-02"
    assert result["violated_law_id"] == "GL-01"
    assert result["risk_category"] == "CRITICAL DEFICIENCY"
    assert result["inherent_risk_score"] == 89
    assert "theft" in result["vulnerability"].lower() or "inventory" in result["vulnerability"].lower()


def test_warehouse_buyer_conflict(rules_engine: RulesEngine) -> None:
    """Confirms adding Procurement Buyer to Warehouse Operator flags RCF-04 (Ghost Inventory) and GL-01."""
    result = rules_engine.evaluate_role_addition("Warehouse Operator", "Procurement Buyer")

    assert result["compliant"] is False
    assert result["conflict_id"] == "RCF-04"
    assert result["violated_law_id"] == "GL-01"
    assert result["risk_category"] == "CRITICAL DEFICIENCY"
    assert result["inherent_risk_score"] == 95
    assert "purchase order" in result["vulnerability"].lower() or "ghost" in result["vulnerability"].lower()


def test_compliant_sop_viewer(rules_engine: RulesEngine) -> None:
    """Confirms adding Standard SOP Viewer to Production Operator returns compliant=True and low risk."""
    result = rules_engine.evaluate_role_addition("Production Operator", "Standard SOP Viewer")

    assert result["compliant"] is True
    assert result["conflict_id"] is None
    assert result["violated_law_id"] is None
    assert result["risk_category"] == "AUDIT COMPLIANT"
    assert result["inherent_risk_score"] <= 15
    assert "Approved" in result["mandated_remediation"] or "APPROVED" in result["mandated_remediation"]


def test_expired_assignment_gl04(rules_engine: RulesEngine) -> None:
    """Passes an expiry date of '2025-10-31' with current date '2026-09-04' and verifies GL-04 breach is detected."""
    findings = rules_engine.audit_assignment_lifecycle(
        role="Maintenance Technician",
        action_type="ACT_EXEC",
        scope="Plant-04",
        assigned_plant="Plant-04",
        expiry_date_str="2025-10-31",
        current_date_str="2026-09-04",
    )

    assert len(findings) >= 1
    gl04_findings = [f for f in findings if f["law_id"] == "GL-04"]
    assert len(gl04_findings) == 1

    gl04 = gl04_findings[0]
    assert gl04["breach_type"] == "EXPIRED_PRIVILEGE"
    assert gl04["risk_category"] == "AUDIT EXCEPTION"
    assert gl04["inherent_risk_score"] == 78
    assert "2025-10-31" in gl04["finding"]
    assert "revocation" in gl04["mandated_remediation"].lower()


def test_scope_violation_gl03(rules_engine: RulesEngine) -> None:
    """Passes a global scope for an operator assigned to Plant-04 and verifies GL-03 breach."""
    findings = rules_engine.audit_assignment_lifecycle(
        role="Production Operator",
        action_type="ACT_EXEC",
        scope="GLOBAL",
        assigned_plant="Plant-04",
        expiry_date_str=None,
        current_date_str="2026-09-04",
    )

    assert len(findings) >= 1
    gl03_findings = [f for f in findings if f["law_id"] == "GL-03"]
    assert len(gl03_findings) == 1

    gl03 = gl03_findings[0]
    assert gl03["breach_type"] == "EXCESSIVE_JURISDICTION"
    assert gl03["risk_category"] == "MAJOR NON-CONFORMANCE"
    assert gl03["inherent_risk_score"] == 72
    assert "Plant-04" in gl03["finding"]
    assert "GLOBAL" in gl03["finding"]
