"""
Main Interactive CLI Runner for Manufacturing Identity & Access Risk Analysis.

Provides an executive terminal interface for running role conflict audits,
lifecycle entitlement compliance checks, statutory benchmark verifications,
and test suite executions.
"""

import argparse
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
from typing import Optional

# Ensure UTF-8 output encoding for cross-platform and Windows console safety
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data.loader import DataLoader
from engine.rules_engine import RulesEngine
from engine.scoring import RiskScoringEngine
from agent.risk_agent import AuditRiskAgent


# ==============================================================================
# Terminal UI Formatting Helpers
# ==============================================================================

def print_banner() -> None:
    """Print the application header banner."""
    print("\n" + "=" * 78)
    print("   MICRON MANUFACTURING IDENTITY & ACCESS RISK GOVERNANCE SYSTEM")
    print("       Deterministic Audit Grounding & Dual-View AI Agent Engine")
    print("=" * 78)


def print_section_header(title: str) -> None:
    """Print formatted section header."""
    print("\n" + "#" * 78)
    print(f"  {title.upper()}")
    print("#" * 78)


def print_table_row(label: str, value: str, width: int = 28) -> None:
    """Print formatted key-value pair."""
    print(f"  {label:<{width}}: {value}")


# ==============================================================================
# Workflow 1: Interactive Role Conflict Audit
# ==============================================================================

def run_role_conflict_audit(
    agent: AuditRiskAgent,
    base_role: Optional[str] = None,
    requested_role: Optional[str] = None,
    proposed_downgrade: str = "ACT_VIEW",
) -> None:
    """Run interactive role conflict evaluation with dual-persona briefings."""
    print_section_header("Workflow 1: Dual-Role Conflict & SoD Audit")

    if not base_role:
        print("\nPreset Common Roles:")
        print("  1. Production Operator")
        print("  2. Warehouse Operator")
        print("  3. Maintenance Technician")
        print("  4. Master Data Specialist")
        print("  5. Quality Assurance Engineer")
        print("  6. Plant Finance Analyst")
        
        inp_base = input("\nEnter Primary Base Role (or press Enter for 'Production Operator'): ").strip()
        base_role = inp_base if inp_base else "Production Operator"

    if not requested_role:
        print("\nPreset Requested Additions:")
        print("  1. Production Supervisor (Severe SoD Conflict)")
        print("  2. Standard SOP Viewer (Compliant View-Only)")
        print("  3. Inventory Controller (Theft Risk)")
        print("  4. Procurement Buyer (Ghost Inventory)")
        
        inp_req = input("Enter Requested Role (or press Enter for 'Production Supervisor'): ").strip()
        requested_role = inp_req if inp_req else "Production Supervisor"

    print(f"\n[+] Analyzing: '{base_role}' + '{requested_role}'...")
    report = agent.analyze_role_request(
        base_role=base_role,
        requested_role=requested_role,
        proposed_downgrade=proposed_downgrade,
    )

    # 1. Structured Audit Summary Table
    print("\n" + "-" * 78)
    print("  DETERMINISTIC AUDIT & RISK REDUCTION METRICS")
    print("-" * 78)
    status_str = "COMPLIANT (Pass)" if report["compliant"] else "NON-COMPLIANT (SoD Violation)"
    print_table_row("Audit Status", status_str)
    print_table_row("Conflict Rule ID", str(report.get("conflict_id") or "None"))
    print_table_row("Violated Golden Law", str(report.get("violated_law_id") or "None"))
    print_table_row("Severity Classification", report["risk_category"])
    print_table_row("Inherent Risk Score", f"{report['inherent_risk_score']:.1f} / 100 ({report['risk_level_inherent']})")
    print_table_row("Current Action Tier", f"{report['current_action']} ({report['current_multiplier']}x)")
    print_table_row("Proposed Action Tier", f"{report['proposed_action']} ({report['proposed_multiplier']}x)")
    print_table_row("Residual Risk Score", f"{report['residual_risk_score']:.1f} / 100 ({report['risk_level_residual']})")
    print_table_row("Mathematical Reduction", f"{report['reduction_pct']:.1f}%")
    print_table_row("Remediation State", report["remediation_status"])
    print_table_row("AI Synthesis Engine", "Gemini LLM" if report["llm_generated"] else "Deterministic Offline Template")

    # 2. Persona 1 Output
    print("\n" + "=" * 78)
    print("  [PERSONA 1: PLANT FLOOR & PRODUCTION MANAGER OPERATIONAL BRIEF]")
    print("=" * 78)
    print(report["plant_manager_brief"])

    # 3. Persona 2 Output
    print("\n" + "=" * 78)
    print("  [PERSONA 2: INTERNAL AUDIT & SOX/ISO COMPLIANCE MEMORANDUM]")
    print("=" * 78)
    print(report["auditor_memo"])


# ==============================================================================
# Workflow 2: Lifecycle Assignment Audit (Scope & Expiry)
# ==============================================================================

def run_lifecycle_assignment_audit(
    rules_engine: RulesEngine,
    role: Optional[str] = None,
    action_type: Optional[str] = None,
    scope: Optional[str] = None,
    assigned_plant: Optional[str] = None,
    expiry_date: Optional[str] = None,
) -> None:
    """Run deterministic lifecycle audit on jurisdiction, expiration, and action tiers."""
    print_section_header("Workflow 2: Entitlement Lifecycle & Jurisdictional Scope Audit")

    if not role:
        inp_role = input("Enter Role Title (default 'Production Operator'): ").strip()
        role = inp_role if inp_role else "Production Operator"

    if not action_type:
        inp_act = input("Enter Action Tier [ACT_VIEW, ACT_EXEC, ACT_MOD, ACT_APPR, ACT_ADM] (default 'ACT_APPR'): ").strip()
        action_type = inp_act if inp_act else "ACT_APPR"

    if not assigned_plant:
        inp_plant = input("Enter Worker's Assigned Physical Plant (default 'Plant-04'): ").strip()
        assigned_plant = inp_plant if inp_plant else "Plant-04"

    if not scope:
        inp_scope = input("Enter Entitlement Scope [e.g. 'Plant-04', 'GLOBAL', 'Plant-01, Plant-02'] (default 'GLOBAL'): ").strip()
        scope = inp_scope if inp_scope else "GLOBAL"

    if not expiry_date:
        inp_exp = input("Enter Expiration Date [YYYY-MM-DD or 'none'] (default '2026-06-01' [Expired]): ").strip()
        if inp_exp.lower() == "none":
            expiry_date = None
        else:
            expiry_date = inp_exp if inp_exp else "2026-06-01"

    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"\n[+] Inspecting assignment against Statutory Golden Laws (Reference Date: {current_date})...")

    findings = rules_engine.audit_assignment_lifecycle(
        role=role,
        action_type=action_type,
        scope=scope,
        assigned_plant=assigned_plant,
        expiry_date_str=expiry_date,
        current_date_str=current_date,
    )

    print("\n" + "-" * 78)
    print(f"  AUDIT FINDINGS SUMMARY (Total Findings Detected: {len(findings)})")
    print("-" * 78)

    if not findings:
        print("  [PASS] 100% COMPLIANT: All jurisdictional, temporal, and action-tier rules satisfied.")
        return

    for idx, f in enumerate(findings, start=1):
        print(f"\n  FINDING #{idx}: [{f['law_id']}] {f['law_name']}")
        print_table_row("Breach Type", f["breach_type"])
        print_table_row("Severity Class", f["severity"])
        print_table_row("Inherent Score", f"{f['inherent_risk_score']}/100")
        print_table_row("Non-Conformance", f["finding"])
        print_table_row("Mandated Remedy", f["mandated_remediation"])


# ==============================================================================
# Workflow 3: Statutory Benchmark Verification Suite
# ==============================================================================

def run_benchmark_verification(scoring_engine: RiskScoringEngine) -> None:
    """Execute mathematical verification across all 8 statutory benchmark cases."""
    print_section_header("Workflow 3: Benchmark Verification Suite (AUD-01 to AUD-08)")

    benchmarks = scoring_engine.validate_against_benchmarks()

    print("\n  " + "-" * 74)
    print(f"  {'Case ID':<8} | {'Target Role':<28} | {'Inh':>4} -> {'Res':>4} | {'Expected':>8} | {'Calculated':>10} | {'Status':<6}")
    print("  " + "-" * 74)

    all_passed = True
    for b in benchmarks:
        status = "PASS" if b["matches_benchmark"] else "FAIL"
        if not b["matches_benchmark"]:
            all_passed = False
        print(
            f"  {b['case_id']:<8} | {b['target_role']:<28} | "
            f"{b['inherent_risk']:>4.0f} -> {b['benchmark_residual']:>4.0f} | "
            f"{b['benchmark_reduction_pct']:>7.0f}% | {b['calculated_reduction_pct']:>9.1f}% | "
            f"[{status}]"
        )

    print("  " + "-" * 74)
    if all_passed:
        print("\n  [PASS] VERIFICATION SUCCESS: All 8 benchmark cases strictly match mathematical model.")
    else:
        print("\n  [FAIL] VERIFICATION FAILURE: One or more benchmark cases deviated from expected tolerance.")


# ==============================================================================
# Workflow 4: Run Full Pytest Suite
# ==============================================================================

def run_pytest_suite() -> None:
    """Execute all pytest test cases in the tests/ directory."""
    print_section_header("Workflow 4: Automated Pytest Suite Execution")
    print("[+] Executing test discovery across tests/ ...\n")
    
    python_exe = sys.executable
    cmd = [python_exe, "-m", "pytest", "-v"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"\n[!] Test suite finished with return code {exc.returncode}")
    except Exception as exc:
        print(f"\n[!] Failed to execute pytest: {exc}")


# ==============================================================================
# Main Interactive CLI Loop & Argument Parser
# ==============================================================================

def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Micron Identity & Access Risk Governance Engine"
    )
    parser.add_argument(
        "--audit-role",
        nargs=2,
        metavar=("BASE_ROLE", "ADDED_ROLE"),
        help="Audit conflict and risk between two roles",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run validation across all 8 statutory benchmark cases",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Execute the full pytest automated test suite",
    )

    args = parser.parse_args()

    # Shared Engine Initialization
    loader = DataLoader()
    rules_engine = RulesEngine(loader)
    scoring_engine = RiskScoringEngine(loader)
    agent = AuditRiskAgent(loader=loader)

    # Non-interactive CLI flag execution
    if args.audit_role:
        run_role_conflict_audit(agent, base_role=args.audit_role[0], requested_role=args.audit_role[1])
        return

    if args.benchmark:
        run_benchmark_verification(scoring_engine)
        return

    if args.run_tests:
        run_pytest_suite()
        return

    # Interactive Loop
    while True:
        print_banner()
        print("  1. Run Role Conflict Audit (SoD Check, Risk Scoring & Dual Persona)")
        print("  2. Audit Entitlement Lifecycle (Temporal Expiration & Jurisdiction)")
        print("  3. Verify Statutory Benchmark Suite (AUD-01 through AUD-08)")
        print("  4. Execute Automated Test Suite (Pytest)")
        print("  5. Exit")
        print("=" * 78)

        try:
            choice = input("\nSelect an option [1-5]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.\n")
            break

        if choice == "1":
            run_role_conflict_audit(agent)
        elif choice == "2":
            run_lifecycle_assignment_audit(rules_engine)
        elif choice == "3":
            run_benchmark_verification(scoring_engine)
        elif choice == "4":
            run_pytest_suite()
        elif choice == "5" or choice.lower() in ["exit", "q", "quit"]:
            print("\nExiting Risk Governance System. Goodbye.\n")
            break
        else:
            print("\n[!] Invalid selection. Please enter a number between 1 and 5.")

        try:
            input("\nPress Enter to return to main menu...")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye.\n")
            break


if __name__ == "__main__":
    main()
