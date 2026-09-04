"""
Unit tests for Member 1's Data Access & Ingestion Layer (data/loader.py).
"""

import pytest
import pandas as pd
from data.loader import DataLoader


@pytest.fixture(scope="module")
def loader():
    """Module-level fixture to instantiate DataLoader once."""
    return DataLoader()


def test_initialization_sheet_shapes(loader):
    """Verify all 5 sheets are loaded with expected minimum row counts."""
    assert isinstance(loader.golden_laws_df, pd.DataFrame)
    assert len(loader.golden_laws_df) == 8

    assert isinstance(loader.action_risk_df, pd.DataFrame)
    assert len(loader.action_risk_df) == 5

    assert isinstance(loader.job_baselines_df, pd.DataFrame)
    assert len(loader.job_baselines_df) == 10

    assert isinstance(loader.role_conflicts_df, pd.DataFrame)
    assert len(loader.role_conflicts_df) == 10

    assert isinstance(loader.audit_benchmarks_df, pd.DataFrame)
    assert len(loader.audit_benchmarks_df) == 8


def test_get_golden_laws(loader):
    """Verify get_golden_laws returns all 8 statutory laws."""
    laws_df = loader.get_golden_laws()
    assert isinstance(laws_df, pd.DataFrame)
    assert len(laws_df) == 8
    assert "Golden Law ID" in laws_df.columns
    assert "Law Name & Principle" in laws_df.columns
    assert "GL-01" in laws_df["Golden Law ID"].values
    assert "GL-08" in laws_df["Golden Law ID"].values


def test_get_law_by_id(loader):
    """Verify get_law_by_id returns specific law details case-insensitively."""
    law_1 = loader.get_law_by_id("GL-01")
    assert law_1["Golden Law ID"] == "GL-01"
    assert "Dual-Control" in law_1["Law Name & Principle"]
    assert "SOX 404" in law_1["Governing Standard"]

    # Case-insensitive and trimmed lookup
    law_1_lower = loader.get_law_by_id("  gl-01  ")
    assert law_1_lower["Golden Law ID"] == "GL-01"

    # Test GL-08
    law_8 = loader.get_law_by_id("gl-08")
    assert law_8["Golden Law ID"] == "GL-08"
    assert "Compensating Control" in law_8["Law Name & Principle"]


def test_get_law_by_id_invalid(loader):
    """Verify KeyError is raised when an invalid law ID is queried."""
    with pytest.raises(KeyError, match="not found"):
        loader.get_law_by_id("GL-99")


def test_get_action_multipliers(loader):
    """Verify get_action_multipliers returns the correct multiplier values."""
    multipliers = loader.get_action_multipliers()
    assert isinstance(multipliers, dict)
    assert multipliers["ACT_VIEW"] == pytest.approx(0.2)
    assert multipliers["ACT_EXEC"] == pytest.approx(1.0)
    assert multipliers["ACT_MOD"] == pytest.approx(2.0)
    assert multipliers["ACT_APPR"] == pytest.approx(2.5)
    assert multipliers["ACT_ADM"] == pytest.approx(3.0)


def test_get_action_multiplier_scalar(loader):
    """Verify individual multiplier lookups by code and name."""
    assert loader.get_action_multiplier("ACT_VIEW") == pytest.approx(0.2)
    assert loader.get_action_multiplier("act_mod") == pytest.approx(2.0)
    assert loader.get_action_multiplier("Display / View-Only") == pytest.approx(0.2)

    with pytest.raises(KeyError, match="not found"):
        loader.get_action_multiplier("ACT_UNKNOWN")


def test_get_role_baseline(loader):
    """Verify get_role_baseline returns all required baseline tasks and capabilities."""
    baseline = loader.get_role_baseline("Production Operator")
    assert baseline["Job Role Code"] == "JOB_PROD_OPR"
    assert baseline["Job Role Title"] == "Production Operator"
    assert "Task 1: Core Standard Task" in baseline
    assert "Task 2: Secondary Operational Task" in baseline
    assert "Task 3: Reporting / Monitoring Task" in baseline
    assert "Maximum Authorized Action Level" in baseline
    assert "Strictly Forbidden / Unallowable Capabilities" in baseline
    assert "ACT_EXEC" in baseline["Task 1: Core Standard Task"]
    assert "ACT_MOD" in baseline["Maximum Authorized Action Level"]

    # Test lookup by Role Code
    baseline_by_code = loader.get_role_baseline("JOB_PROD_OPR")
    assert baseline_by_code["Job Role Title"] == "Production Operator"

    # Test case-insensitivity
    baseline_lower = loader.get_role_baseline("  production operator  ")
    assert baseline_lower["Job Role Code"] == "JOB_PROD_OPR"

    # Test alias lookup (Quality Engineer -> Quality Assurance Engineer)
    baseline_qa = loader.get_role_baseline("Quality Engineer")
    assert baseline_qa["Job Role Code"] == "JOB_QUAL_ENG"


def test_get_role_baseline_invalid(loader):
    """Verify KeyError is raised when an unknown role is requested."""
    with pytest.raises(KeyError, match="not found"):
        loader.get_role_baseline("Chief Space Officer")


def test_check_conflict_bidirectional(loader):
    """Verify check_conflict correctly identifies SoD conflicts bidirectionally."""
    # Operator vs Supervisor -> Severe SoD
    conflict_ab = loader.check_conflict("Production Operator", "Production Supervisor")
    assert conflict_ab is not None
    assert conflict_ab["Conflict Rule ID"] == "RCF-01"
    assert "NON-COMPLIANT" in conflict_ab["Audit Compliance Status"]
    assert "GL-01" in conflict_ab["Violated Audit Golden Law"]

    # Reverse order: Supervisor vs Operator
    conflict_ba = loader.check_conflict("Production Supervisor", "Production Operator")
    assert conflict_ba is not None
    assert conflict_ba["Conflict Rule ID"] == "RCF-01"

    # Case-insensitive & trimmed
    conflict_case = loader.check_conflict(
        "  PRODUCTION OPERATOR  ", "production supervisor"
    )
    assert conflict_case is not None
    assert conflict_case["Conflict Rule ID"] == "RCF-01"


def test_check_conflict_compliant_cases(loader):
    """Verify compliant combinations return None from check_conflict."""
    # Operator vs Standard SOP Viewer is AUDIT COMPLIANT -> returns None
    result = loader.check_conflict("Production Operator", "Standard SOP Viewer")
    assert result is None

    # Maintenance Technician vs Reliability Dashboard Viewer is AUDIT COMPLIANT
    result_maint = loader.check_conflict(
        "Maintenance Technician", "Reliability Dashboard Viewer"
    )
    assert result_maint is None

    # Unrelated role pair with no conflict defined
    unrelated = loader.check_conflict("Procurement Buyer", "Standard SOP Viewer")
    assert unrelated is None


def test_get_conflict_entry(loader):
    """Verify get_conflict_entry returns the raw row dictionary even for compliant pairs."""
    entry = loader.get_conflict_entry("Production Operator", "Standard SOP Viewer")
    assert entry is not None
    assert entry["Conflict Rule ID"] == "RCF-09"
    assert entry["Audit Compliance Status"] == "AUDIT COMPLIANT"


def test_get_benchmark_cases(loader):
    """Verify get_benchmark_cases returns all 8 validation benchmark cases."""
    benchmarks_df = loader.get_benchmark_cases()
    assert isinstance(benchmarks_df, pd.DataFrame)
    assert len(benchmarks_df) == 8
    assert "Audit Case ID" in benchmarks_df.columns
    assert "Target Job Profile" in benchmarks_df.columns
    assert "AUD-01" in benchmarks_df["Audit Case ID"].values
    assert "AUD-08" in benchmarks_df["Audit Case ID"].values
