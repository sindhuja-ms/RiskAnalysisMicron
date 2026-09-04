"""
Unit tests for Member 3's Mathematical Risk Scoring & Downgrade Engine (engine/scoring.py).
"""

import pytest
from engine.scoring import RiskScoringEngine
from data.loader import DataLoader


@pytest.fixture(scope="module")
def scoring_engine() -> RiskScoringEngine:
    """Fixture providing a cached instance of RiskScoringEngine."""
    return RiskScoringEngine()


def test_initialization_and_multipliers(scoring_engine: RiskScoringEngine) -> None:
    """Verify action multipliers are properly loaded and mapped."""
    assert scoring_engine.get_action_multiplier("ACT_VIEW") == pytest.approx(0.2)
    assert scoring_engine.get_action_multiplier("ACT_EXEC") == pytest.approx(1.0)
    assert scoring_engine.get_action_multiplier("ACT_MOD") == pytest.approx(2.0)
    assert scoring_engine.get_action_multiplier("ACT_APPR") == pytest.approx(2.5)
    assert scoring_engine.get_action_multiplier("ACT_ADM") == pytest.approx(3.0)


def test_downgrade_appr_to_view(scoring_engine: RiskScoringEngine) -> None:
    """
    Test downgrade from ACT_APPR (2.5) to ACT_VIEW (0.2) with inherent 92.
    Expected: Residual = 92 * (0.2 / 2.5) = 7.36, Reduction = 92.0%.
    """
    res = scoring_engine.calculate_residual_risk(
        inherent_risk=92.0,
        current_action="ACT_APPR",
        proposed_action="ACT_VIEW",
    )

    assert res["inherent_risk"] == pytest.approx(92.0)
    assert res["residual_risk"] == pytest.approx(7.36)
    assert res["reduction_pct"] == pytest.approx(92.0, abs=0.1)
    assert res["risk_level_inherent"] == "CRITICAL"
    assert res["risk_level_residual"] == "LOW"


def test_downgrade_mod_to_view(scoring_engine: RiskScoringEngine) -> None:
    """
    Test downgrade from ACT_MOD (2.0) to ACT_VIEW (0.2) with inherent 85.
    Expected: Residual = 85 * (0.2 / 2.0) = 8.5, Reduction = 90.0%.
    """
    res = scoring_engine.calculate_residual_risk(
        inherent_risk=85.0,
        current_action="ACT_MOD",
        proposed_action="ACT_VIEW",
    )

    assert res["inherent_risk"] == pytest.approx(85.0)
    assert res["residual_risk"] == pytest.approx(8.5)
    assert res["reduction_pct"] == pytest.approx(90.0, abs=0.1)
    assert res["risk_level_inherent"] == "CRITICAL"
    assert res["risk_level_residual"] == "LOW"


def test_same_tier_action_no_reduction(scoring_engine: RiskScoringEngine) -> None:
    """Test same-tier action (ACT_EXEC to ACT_EXEC) results in 0% reduction."""
    res = scoring_engine.calculate_residual_risk(
        inherent_risk=50.0,
        current_action="ACT_EXEC",
        proposed_action="ACT_EXEC",
    )

    assert res["inherent_risk"] == pytest.approx(50.0)
    assert res["residual_risk"] == pytest.approx(50.0)
    assert res["reduction_pct"] == pytest.approx(0.0)
    assert res["risk_level_inherent"] == "MEDIUM"
    assert res["risk_level_residual"] == "MEDIUM"


def test_edge_case_zero_inherent_risk(scoring_engine: RiskScoringEngine) -> None:
    """Verify zero inherent risk does not cause division by zero errors."""
    res = scoring_engine.calculate_residual_risk(
        inherent_risk=0.0,
        current_action="ACT_APPR",
        proposed_action="ACT_VIEW",
    )

    assert res["inherent_risk"] == pytest.approx(0.0)
    assert res["residual_risk"] == pytest.approx(0.0)
    assert res["reduction_pct"] == pytest.approx(0.0)
    assert res["risk_level_inherent"] == "LOW"
    assert res["risk_level_residual"] == "LOW"


def test_simulate_sod_remediation_conflict(scoring_engine: RiskScoringEngine) -> None:
    """Verify simulate_sod_remediation correctly applies downgrade to conflict payload."""
    conflict_payload = {
        "compliant": False,
        "conflict_id": "RCF-01",
        "violated_law_id": "GL-01",
        "risk_category": "CRITICAL DEFICIENCY",
        "inherent_risk_score": 92,
        "vulnerability": "Unauthorized batch approval rights.",
        "mandated_remediation": "Remove supervisor role.",
    }

    sim = scoring_engine.simulate_sod_remediation(conflict_payload, proposed_action="ACT_VIEW")

    assert sim["compliant"] is False
    assert sim["conflict_id"] == "RCF-01"
    assert sim["inherent_risk"] == pytest.approx(92.0)
    assert sim["residual_risk"] == pytest.approx(7.36)
    assert sim["reduction_pct"] == pytest.approx(92.0, abs=0.1)
    assert sim["remediation_status"] == "DOWNGRADED_SAFE"


def test_simulate_sod_remediation_compliant(scoring_engine: RiskScoringEngine) -> None:
    """Verify simulate_sod_remediation for compliant roles reports zero reduction needed."""
    compliant_payload = {
        "compliant": True,
        "conflict_id": None,
        "violated_law_id": None,
        "risk_category": "AUDIT COMPLIANT",
        "inherent_risk_score": 12,
        "vulnerability": "None. Safe complementary assignment.",
        "mandated_remediation": "Approved for assignment.",
    }

    sim = scoring_engine.simulate_sod_remediation(compliant_payload)

    assert sim["compliant"] is True
    assert sim["reduction_pct"] == pytest.approx(0.0)
    assert sim["residual_risk"] == pytest.approx(12.0)
    assert sim["remediation_status"] == "NO_ACTION_REQUIRED"


def test_validate_against_benchmarks(scoring_engine: RiskScoringEngine) -> None:
    """
    Test benchmark dataset execution: ensures all 8 cases in Sheet 5
    match calculated numbers within tolerance.
    """
    benchmarks = scoring_engine.validate_against_benchmarks()

    assert len(benchmarks) == 8
    case_ids = [b["case_id"] for b in benchmarks]
    assert case_ids == [
        "AUD-01",
        "AUD-02",
        "AUD-03",
        "AUD-04",
        "AUD-05",
        "AUD-06",
        "AUD-07",
        "AUD-08",
    ]

    # All benchmark cases must match calculations within tolerance
    for case in benchmarks:
        assert (
            case["matches_benchmark"] is True
        ), f"Benchmark mismatch for {case['case_id']} ({case['target_role']}): Expected {case['benchmark_reduction_pct']}%, Got {case['calculated_reduction_pct']}%"
