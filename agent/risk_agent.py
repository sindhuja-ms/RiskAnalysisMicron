"""
AI Agent Core & Dual-View Persona Generator for Manufacturing Identity Audit.

This module orchestrates deterministic rules checking, mathematical risk scoring,
and persona-tailored synthesis for Plant Managers and Compliance Auditors using
Gemini AI with guaranteed offline fallback protection.
"""

import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Tuple, Union
from dotenv import load_dotenv

# Ensure project root is in sys.path for direct script execution and package imports
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data.loader import DataLoader
from engine.rules_engine import RulesEngine
from engine.scoring import RiskScoringEngine
from agent.prompts import (
    build_plant_manager_prompt,
    build_auditor_memo_prompt,
    build_offline_plant_manager_brief,
    build_offline_auditor_memo,
)


class AuditRiskAgent:
    """
    Intelligent Risk Governance Agent combining deterministic audit engines
    with dual-persona AI synthesis.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        loader: Optional[DataLoader] = None,
    ) -> None:
        """
        Initialize AuditRiskAgent with deterministic engines and optional Gemini API client.

        Args:
            api_key: Optional Gemini API Key. If not provided, reads from .env / environment.
            model_name: Gemini model name (default: 'gemini-2.5-flash').
            loader: Optional DataLoader instance.
        """
        # Load environment variables
        load_dotenv()

        self.loader = loader or DataLoader()
        self.rules_engine = RulesEngine(self.loader)
        self.scoring_engine = RiskScoringEngine(self.loader)
        self.model_name = model_name

        # Resolve API Key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        self.has_llm = False

        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
                self.has_llm = True
            except Exception as exc:
                print(f"[AuditRiskAgent] Notice: Gemini SDK initialization notice ({exc}). Operating in deterministic offline fallback mode.")
                self.has_llm = False

    def generate_dual_views(self, payload: Dict[str, Any]) -> Tuple[str, str, bool]:
        """
        Generates both the Plant Manager Brief and the Auditor Compliance Memo.
        Uses Gemini LLM if configured and connected; otherwise uses deterministic templates.

        Args:
            payload: Comprehensive audit and mathematical score evaluation payload.

        Returns:
            Tuple[str, str, bool]: (plant_manager_brief, auditor_memo, is_llm_generated)
        """
        if self.has_llm and self.client:
            try:
                # 1. Generate Plant Manager Brief
                pm_prompt = build_plant_manager_prompt(payload)
                pm_resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=pm_prompt,
                )
                pm_text = pm_resp.text.strip() if pm_resp and pm_resp.text else ""

                # 2. Generate Auditor Memo
                memo_prompt = build_auditor_memo_prompt(payload)
                memo_resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=memo_prompt,
                )
                memo_text = memo_resp.text.strip() if memo_resp and memo_resp.text else ""

                if pm_text and memo_text:
                    return pm_text, memo_text, True
            except Exception as exc:
                # Silently failover to guaranteed offline templates
                pass

        # Offline Deterministic Fallback
        pm_text = build_offline_plant_manager_brief(payload)
        memo_text = build_offline_auditor_memo(payload)
        return pm_text, memo_text, False

    def analyze_role_request(
        self,
        base_role: str,
        requested_role: str,
        proposed_downgrade: str = "ACT_VIEW",
    ) -> Dict[str, Any]:
        """
        Conducts an end-to-end audit of a role addition request:
        1. Evaluates deterministic SoD conflict via RulesEngine.
        2. Calculates mathematical risk scoring and downgrade delta via RiskScoringEngine.
        3. Synthesizes dual-persona briefings for Plant Operations and Audit Compliance.

        Args:
            base_role: Current / baseline job role.
            requested_role: Secondary / requested role to be added.
            proposed_downgrade: Proposed de-risking action tier (default: 'ACT_VIEW').

        Returns:
            Dict[str, Any]: Comprehensive audit evaluation report.
        """
        # Step 1: Evaluate SoD Rules
        conflict_eval = self.rules_engine.evaluate_role_addition(base_role, requested_role)

        # Step 2: Mathematical Risk Scoring & Remediation Simulation
        scoring_eval = self.scoring_engine.simulate_sod_remediation(
            base_conflict_payload=conflict_eval,
            proposed_action=proposed_downgrade,
        )

        # Assemble unified payload
        report_payload = {
            "base_role": base_role,
            "requested_role": requested_role,
            "compliant": conflict_eval.get("compliant", True),
            "conflict_id": conflict_eval.get("conflict_id"),
            "violated_law_id": conflict_eval.get("violated_law_id"),
            "risk_category": conflict_eval.get("risk_category", "AUDIT COMPLIANT"),
            "inherent_risk_score": scoring_eval.get("inherent_risk", 10.0),
            "residual_risk_score": scoring_eval.get("residual_risk", 10.0),
            "reduction_pct": scoring_eval.get("reduction_pct", 0.0),
            "current_action": scoring_eval.get("current_action", "N/A"),
            "proposed_action": scoring_eval.get("proposed_action", proposed_downgrade),
            "current_multiplier": scoring_eval.get("current_multiplier", 1.0),
            "proposed_multiplier": scoring_eval.get("proposed_multiplier", 0.2),
            "risk_level_inherent": scoring_eval.get("risk_level_inherent", "LOW"),
            "risk_level_residual": scoring_eval.get("risk_level_residual", "LOW"),
            "remediation_status": scoring_eval.get("remediation_status", "NO_ACTION_REQUIRED"),
            "vulnerability": conflict_eval.get("vulnerability", "None."),
            "mandated_remediation": conflict_eval.get("mandated_remediation", "Approved."),
        }

        # Step 3: Generate Dual-Persona Briefings
        pm_brief, auditor_memo, is_llm = self.generate_dual_views(report_payload)

        report_payload["plant_manager_brief"] = pm_brief
        report_payload["auditor_memo"] = auditor_memo
        report_payload["llm_generated"] = is_llm

        return report_payload


if __name__ == "__main__":
    print("=" * 70)
    print("AuditRiskAgent Verification & Dual-View Generation")
    print("=" * 70)

    agent = AuditRiskAgent()
    print(f"Agent Status: LLM Engine Active = {agent.has_llm} (Model: {agent.model_name})")

    # Test Case 1: Severe Conflict (Operator + Supervisor)
    print("\n" + "-" * 70)
    print("TEST CASE 1: 'Production Operator' + 'Production Supervisor'")
    print("-" * 70)
    res_1 = agent.analyze_role_request("Production Operator", "Production Supervisor")
    print(f"Compliance:           {'PASS' if res_1['compliant'] else 'NON-COMPLIANT (SoD Conflict)'}")
    print(f"Conflict ID:          {res_1['conflict_id']}")
    print(f"Violated Law:         {res_1['violated_law_id']}")
    print(f"Inherent Risk Score:  {res_1['inherent_risk_score']} ({res_1['risk_level_inherent']})")
    print(f"Residual Risk Score:  {res_1['residual_risk_score']} ({res_1['risk_level_residual']})")
    print(f"Mathematical Reduction: {res_1['reduction_pct']}%")
    print(f"LLM Synthesis Used:   {res_1['llm_generated']}")

    print("\n--- [PERSONA 1: PLANT MANAGER BRIEF] ---")
    print(res_1["plant_manager_brief"])

    print("\n--- [PERSONA 2: AUDITOR COMPLIANCE MEMO] ---")
    print(res_1["auditor_memo"])

    # Test Case 2: Compliant Role (Operator + SOP Viewer)
    print("\n" + "=" * 70)
    print("TEST CASE 2: 'Production Operator' + 'Standard SOP Viewer'")
    print("=" * 70)
    res_2 = agent.analyze_role_request("Production Operator", "Standard SOP Viewer")
    print(f"Compliance:           {'PASS' if res_2['compliant'] else 'NON-COMPLIANT'}")
    print(f"Inherent Risk Score:  {res_2['inherent_risk_score']}")
    print(f"Residual Risk Score:  {res_2['residual_risk_score']}")
    print(f"LLM Synthesis Used:   {res_2['llm_generated']}")

    print("\n--- [PERSONA 1: PLANT MANAGER BRIEF] ---")
    print(res_2["plant_manager_brief"])

    print("\n--- [PERSONA 2: AUDITOR COMPLIANCE MEMO] ---")
    print(res_2["auditor_memo"])
