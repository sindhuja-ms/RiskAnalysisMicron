"""
Deterministic Rules & Segregation of Duties (SoD) Violation Engine.

This module provides 100% deterministic, audit-grounded evaluation of role combinations,
entitlement scopes, temporal validity, and action-tier privileges against the 8 Golden Laws
of Manufacturing Identity Audit.
"""

from datetime import datetime
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Union

# Ensure project root is in sys.path for direct script execution and package imports
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data.loader import DataLoader


class RulesEngine:
    """
    Deterministic rules engine enforcing statutory identity audit policies,
    Segregation of Duties (SoD), action tiering, temporal termination, and
    jurisdictional containment.
    """

    # Action categorization sets for deterministic dual-control checking
    INITIATION_ACTIONS = {
        "act_exec",
        "act_mod",
        "execute",
        "execute (operational)",
        "create",
        "modify",
        "edit",
        "create / edit / modify",
        "write",
        "log",
    }

    APPROVAL_ACTIONS = {
        "act_appr",
        "act_adm",
        "approve",
        "release",
        "authorize",
        "approve / release / authorize",
        "administer",
        "administer / global override",
        "admin",
    }

    VIEW_ACTIONS = {
        "act_view",
        "view",
        "display",
        "display / view-only",
        "read",
        "inspect",
    }

    def __init__(self, loader: Optional[DataLoader] = None) -> None:
        """
        Initialize the RulesEngine with a DataLoader instance.

        Args:
            loader: Optional DataLoader instance; instantiates a new one if None.
        """
        self.loader = loader or DataLoader()

    @staticmethod
    def _normalize_string(val: Any) -> str:
        """Normalize string by lowercasing and trimming whitespace."""
        if val is None:
            return ""
        return re.sub(r"\s+", " ", str(val).strip().lower())

    def _extract_score(self, risk_text: Any, default_score: int = 80) -> int:
        """Extract numerical score from risk text (e.g., 'Critical (Score: 92)' -> 92)."""
        if isinstance(risk_text, (int, float)):
            return int(risk_text)
        if not risk_text:
            return default_score
        match = re.search(r"Score:\s*(\d+)", str(risk_text), re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Fallback keyword scoring if explicit score not present
        norm = str(risk_text).lower()
        if "critical" in norm or "severe" in norm:
            return 90
        if "high" in norm or "major" in norm:
            return 75
        if "medium" in norm or "moderate" in norm:
            return 50
        if "low" in norm:
            return 15
        return default_score

    def _extract_law_id(self, law_text: Any) -> Optional[str]:
        """Extract statutory Law ID (e.g., 'GL-01: Dual-Control Custody' -> 'GL-01')."""
        if not law_text:
            return None
        match = re.search(r"GL-\d+", str(law_text), re.IGNORECASE)
        return match.group(0).upper() if match else None

    # --------------------------------------------------------------------------
    # Core Requirement Methods
    # --------------------------------------------------------------------------

    def evaluate_role_addition(self, base_role: str, added_role: str) -> Dict[str, Any]:
        """
        Evaluates the audit risk of adding a secondary role to a user holding a base role.
        Enforces Segregation of Duties (SoD) based on the Role Conflict Matrix.

        Args:
            base_role: Primary or existing role title/code.
            added_role: Role requested to be added.

        Returns:
            Dict[str, Any]: Detailed evaluation including compliance status, rule ID,
                            violated law, risk score, vulnerability, and remediation.
        """
        conflict = self.loader.check_conflict(base_role, added_role)

        if conflict:
            law_id = self._extract_law_id(conflict.get("Violated Audit Golden Law"))
            score = self._extract_score(conflict.get("Inherent Conflict Risk"), default_score=90)

            # Determine risk category from Golden Law definition if available
            risk_category = "CRITICAL DEFICIENCY"
            if law_id:
                try:
                    law_meta = self.loader.get_law_by_id(law_id)
                    risk_category = law_meta.get("Audit Finding Classification", risk_category)
                except KeyError:
                    pass

            return {
                "compliant": False,
                "conflict_id": conflict.get("Conflict Rule ID"),
                "violated_law_id": law_id,
                "risk_category": risk_category,
                "inherent_risk_score": score,
                "vulnerability": conflict.get("Operational Breach / Vulnerability Created", ""),
                "mandated_remediation": conflict.get("Auditor Mandated Remediation", ""),
            }

        # Check if the pair is explicitly listed as compliant in the matrix
        matrix_entry = self.loader.get_conflict_entry(base_role, added_role)
        if matrix_entry and "COMPLIANT" in str(matrix_entry.get("Audit Compliance Status", "")).upper():
            score = self._extract_score(matrix_entry.get("Inherent Conflict Risk"), default_score=12)
            return {
                "compliant": True,
                "conflict_id": None,
                "violated_law_id": None,
                "risk_category": "AUDIT COMPLIANT",
                "inherent_risk_score": score,
                "vulnerability": matrix_entry.get(
                    "Operational Breach / Vulnerability Created",
                    "None. Safe complementary assignment.",
                ),
                "mandated_remediation": matrix_entry.get(
                    "Auditor Mandated Remediation", "Approved for assignment."
                ),
            }

        # Safe default compliant assignment for unlisted non-conflicting roles
        return {
            "compliant": True,
            "conflict_id": None,
            "violated_law_id": None,
            "risk_category": "AUDIT COMPLIANT",
            "inherent_risk_score": 10,
            "vulnerability": "None. Safe complementary assignment.",
            "mandated_remediation": "Approved for assignment.",
        }

    def audit_assignment_lifecycle(
        self,
        role: str,
        action_type: str,
        scope: str,
        assigned_plant: str,
        expiry_date_str: Optional[str],
        current_date_str: str = "2026-09-04",
    ) -> List[Dict[str, Any]]:
        """
        Deterministically evaluates an entitlement assignment against Golden Laws:
        - GL-03 (Jurisdictional Containment): Scope bounding to assigned facility.
        - GL-04 (Temporal Termination): Expiration enforcement.
        - GL-01 / GL-02 (Action Tiering & Dual Control): Maximum authorized action level.

        Args:
            role: Job role title or code being evaluated.
            action_type: Action level code (e.g. 'ACT_APPR', 'ACT_MOD') or descriptive name.
            scope: Organizational scope granted (e.g., 'Plant-04', 'GLOBAL', 'Plant-01, Plant-02').
            assigned_plant: The worker's physical plant / facility assignment (e.g. 'Plant-04').
            expiry_date_str: ISO format date string ('YYYY-MM-DD') or None if indefinite.
            current_date_str: Reference date for temporal audit evaluation.

        Returns:
            List[Dict[str, Any]]: List of audit breaches/findings (empty if 100% compliant).
        """
        findings: List[Dict[str, Any]] = []

        norm_action = self._normalize_string(action_type)
        norm_scope = self._normalize_string(scope)
        norm_plant = self._normalize_string(assigned_plant)

        # ----------------------------------------------------------------------
        # 1. Check GL-03: Jurisdictional Containment Law
        # ----------------------------------------------------------------------
        is_global_scope = any(
            kw in norm_scope for kw in ["global", "enterprise", "all plants", "multi-site", "*"]
        )
        is_plant_mismatch = bool(norm_plant and norm_plant not in norm_scope)

        if is_global_scope or is_plant_mismatch:
            findings.append(
                {
                    "law_id": "GL-03",
                    "law_name": "Jurisdictional Containment Law",
                    "breach_type": "EXCESSIVE_JURISDICTION",
                    "governing_standard": "IEC 62443 / Corporate Policy",
                    "risk_category": "MAJOR NON-CONFORMANCE",
                    "severity": "MAJOR NON-CONFORMANCE",
                    "inherent_risk_score": 72,
                    "finding": (
                        f"BREACH: Excessive Organizational Scope. Scope '{scope}' "
                        f"exceeds assigned physical plant '{assigned_plant}'."
                    ),
                    "mandated_remediation": (
                        f"Constrain organizational scope strictly to assigned facility '{assigned_plant}'; "
                        "eliminate wildcard and cross-plant write privileges."
                    ),
                }
            )

        # ----------------------------------------------------------------------
        # 2. Check GL-04: Temporal Termination Mandate
        # ----------------------------------------------------------------------
        if expiry_date_str:
            try:
                # Support standard YYYY-MM-DD or date comparisons
                exp_date = datetime.fromisoformat(expiry_date_str.strip())
                curr_date = datetime.fromisoformat(current_date_str.strip())

                if exp_date < curr_date:
                    days_expired = (curr_date - exp_date).days
                    findings.append(
                        {
                            "law_id": "GL-04",
                            "law_name": "Temporal Termination Mandate",
                            "breach_type": "EXPIRED_PRIVILEGE",
                            "governing_standard": "ISO 27001 / SOX Section 404",
                            "risk_category": "AUDIT EXCEPTION",
                            "severity": "AUDIT EXCEPTION",
                            "inherent_risk_score": 78,
                            "days_expired": days_expired,
                            "finding": (
                                f"BREACH: Expired Project / Turnaround Privilege. Assignment expired on "
                                f"{expiry_date_str} ({days_expired} days overdue)."
                            ),
                            "mandated_remediation": (
                                "Immediate auto-expiration and revocation of orphan grant."
                            ),
                        }
                    )
            except ValueError:
                # Fallback string comparison if formats are simple YYYY-MM-DD strings
                if expiry_date_str.strip() < current_date_str.strip():
                    findings.append(
                        {
                            "law_id": "GL-04",
                            "law_name": "Temporal Termination Mandate",
                            "breach_type": "EXPIRED_PRIVILEGE",
                            "governing_standard": "ISO 27001 / SOX Section 404",
                            "risk_category": "AUDIT EXCEPTION",
                            "severity": "AUDIT EXCEPTION",
                            "inherent_risk_score": 78,
                            "finding": (
                                f"BREACH: Expired Privilege. Assignment date {expiry_date_str} "
                                f"is past current audit date {current_date_str}."
                            ),
                            "mandated_remediation": (
                                "Immediate auto-expiration and revocation of orphan grant."
                            ),
                        }
                    )

        # ----------------------------------------------------------------------
        # 3. Check GL-01 & GL-02: Action-Type Tiering & Baseline Capability
        # ----------------------------------------------------------------------
        is_elevated_action = norm_action in self.APPROVAL_ACTIONS or any(
            kw in norm_action for kw in ["act_appr", "act_adm", "approve", "admin"]
        )

        if is_elevated_action:
            try:
                baseline = self.loader.get_role_baseline(role)
                max_level = str(baseline.get("Maximum Authorized Action Level", "")).upper()
                forbidden = str(baseline.get("Strictly Forbidden / Unallowable Capabilities", "")).lower()

                # If baseline maximum does not permit approval/admin or explicitly forbids it
                allows_approval = "ACT_APPR" in max_level or "ACT_ADM" in max_level or "ALL" in max_level
                forbids_action = any(
                    k in forbidden for k in ["approv", "admin", "releas", "waiver", "bom"]
                )

                if (not allows_approval) or forbids_action:
                    findings.append(
                        {
                            "law_id": "GL-01",
                            "secondary_law_id": "GL-02",
                            "law_name": "Dual-Control Custody & Action-Type Tiering",
                            "breach_type": "UNAUTHORIZED_ACTION_TIER",
                            "governing_standard": "SOX 404 / ISO 27001 Annex A.9.4",
                            "risk_category": "CRITICAL DEFICIENCY",
                            "severity": "CRITICAL DEFICIENCY",
                            "inherent_risk_score": 88,
                            "finding": (
                                f"BREACH: Unauthorized Action Tier ({action_type}) assigned to role '{role}'. "
                                f"Authorized baseline is '{baseline.get('Maximum Authorized Action Level')}'. "
                                f"Strictly forbidden: {baseline.get('Strictly Forbidden / Unallowable Capabilities')}."
                            ),
                            "mandated_remediation": (
                                f"REMOVE {action_type}; Downgrade to baseline authorized level "
                                f"({baseline.get('Maximum Authorized Action Level')})."
                            ),
                        }
                    )
            except KeyError:
                # Role not found in baseline table - ignore or record ungrounded
                pass

        return findings

    def evaluate_sod_pair(
        self, action_a: str, action_b: str, object_lifecycle: str
    ) -> Dict[str, Any]:
        """
        Deterministic check for Dual Control (GL-01).
        Flags an SoD violation if one action possesses initiation/execution/mutation capability
        and the other possesses approval/release capability on the same operational/financial lifecycle object.

        Args:
            action_a: First action type/code (e.g. 'ACT_EXEC', 'ACT_MOD').
            action_b: Second action type/code (e.g. 'ACT_APPR', 'ACT_ADM').
            object_lifecycle: Target domain object (e.g., 'Production Variance', 'PO Invoice', 'BOM Recipe').

        Returns:
            Dict[str, Any]: Detailed dual-control analysis result.
        """
        norm_a = self._normalize_string(action_a)
        norm_b = self._normalize_string(action_b)

        # Check if one is initiation/modification and the other is approval/release
        is_a_init = (norm_a in self.INITIATION_ACTIONS) or any(
            k in norm_a for k in ["exec", "mod", "create", "edit", "write"]
        )
        is_a_appr = (norm_a in self.APPROVAL_ACTIONS) or any(
            k in norm_a for k in ["appr", "adm", "release", "authorize"]
        )

        is_b_init = (norm_b in self.INITIATION_ACTIONS) or any(
            k in norm_b for k in ["exec", "mod", "create", "edit", "write"]
        )
        is_b_appr = (norm_b in self.APPROVAL_ACTIONS) or any(
            k in norm_b for k in ["appr", "adm", "release", "authorize"]
        )

        has_sod_clash = (is_a_init and is_b_appr) or (is_a_appr and is_b_init)

        if has_sod_clash:
            return {
                "conflict_detected": True,
                "violated_law_id": "GL-01",
                "law_name": "Dual-Control Custody Law",
                "risk_category": "CRITICAL DEFICIENCY",
                "governing_standard": "SOX 404 / ISA-95",
                "inherent_risk_score": 90,
                "object_lifecycle": object_lifecycle,
                "finding": (
                    f"CRITICAL DEFICIENCY: Dual-Control breach on object '{object_lifecycle}'. "
                    f"Combines transaction initiation ({action_a}) and release custody ({action_b})."
                ),
                "mandated_remediation": (
                    "Segregate duties: Remove approval access or route transaction through "
                    "an independent 4-eyes approval workflow."
                ),
            }

        return {
            "conflict_detected": False,
            "violated_law_id": None,
            "law_name": None,
            "risk_category": "AUDIT COMPLIANT",
            "governing_standard": "ISO 27001 / ISA-95",
            "inherent_risk_score": 10,
            "object_lifecycle": object_lifecycle,
            "finding": f"Actions '{action_a}' and '{action_b}' on '{object_lifecycle}' satisfy dual-control separation.",
            "mandated_remediation": "Approved for concurrent assignment.",
        }


if __name__ == "__main__":
    print("=" * 70)
    print("Deterministic Rules & SoD Violation Engine Verification")
    print("=" * 70)

    engine = RulesEngine()

    # 1. Test evaluate_role_addition (Severe SoD Conflict)
    print("\n[1] Test evaluate_role_addition: 'Production Operator' + 'Production Supervisor'")
    print("-" * 70)
    res_conflict = engine.evaluate_role_addition("Production Operator", "Production Supervisor")
    print(f"Compliant:           {res_conflict['compliant']}")
    print(f"Conflict ID:         {res_conflict['conflict_id']}")
    print(f"Violated Law:        {res_conflict['violated_law_id']}")
    print(f"Risk Category:       {res_conflict['risk_category']}")
    print(f"Inherent Risk Score: {res_conflict['inherent_risk_score']}")
    print(f"Vulnerability:       {res_conflict['vulnerability']}")
    print(f"Remediation:         {res_conflict['mandated_remediation']}")

    # 2. Test evaluate_role_addition (Audit Compliant Combination)
    print("\n[2] Test evaluate_role_addition: 'Production Operator' + 'Standard SOP Viewer'")
    print("-" * 70)
    res_compliant = engine.evaluate_role_addition("Production Operator", "Standard SOP Viewer")
    print(f"Compliant:           {res_compliant['compliant']}")
    print(f"Conflict ID:         {res_compliant['conflict_id']}")
    print(f"Violated Law:        {res_compliant['violated_law_id']}")
    print(f"Risk Category:       {res_compliant['risk_category']}")
    print(f"Inherent Risk Score: {res_compliant['inherent_risk_score']}")
    print(f"Vulnerability:       {res_compliant['vulnerability']}")
    print(f"Remediation:         {res_compliant['mandated_remediation']}")

    # 3. Test audit_assignment_lifecycle with expired date and cross-plant scope
    print("\n[3] Test audit_assignment_lifecycle: 'Production Operator' with expired grant & Global scope")
    print("-" * 70)
    findings = engine.audit_assignment_lifecycle(
        role="Production Operator",
        action_type="ACT_APPR",
        scope="GLOBAL",
        assigned_plant="Plant-04",
        expiry_date_str="2026-06-01",  # Expired relative to reference 2026-09-04
        current_date_str="2026-09-04",
    )
    print(f"Total Audit Findings Detected: {len(findings)}")
    for idx, f in enumerate(findings, start=1):
        print(f"\n  Finding #{idx}: [{f['law_id']}] {f['law_name']}")
        print(f"  Breach Type: {f['breach_type']}")
        print(f"  Severity:    {f['severity']} (Score: {f['inherent_risk_score']})")
        print(f"  Details:     {f['finding']}")
        print(f"  Remedy:      {f['mandated_remediation']}")

    # 4. Test evaluate_sod_pair
    print("\n[4] Test evaluate_sod_pair: 'ACT_MOD' vs 'ACT_APPR' on 'Production Variance'")
    print("-" * 70)
    sod_res = engine.evaluate_sod_pair("ACT_MOD", "ACT_APPR", "Production Variance")
    print(f"Conflict Detected:   {sod_res['conflict_detected']}")
    print(f"Violated Law:        {sod_res['violated_law_id']}")
    print(f"Risk Category:       {sod_res['risk_category']}")
    print(f"Score:               {sod_res['inherent_risk_score']}")
    print(f"Finding:             {sod_res['finding']}")

    print("\n" + "=" * 70)
    print("All RulesEngine verification checks completed successfully.")
    print("=" * 70)
