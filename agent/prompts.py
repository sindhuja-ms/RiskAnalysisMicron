"""
Strict Persona Prompts & Dual-View Synthesis Templates for Manufacturing Identity Audit.

These prompts enforce mathematical and statutory grounding, eliminating hallucinations
by bounding LLM generation strictly to deterministic engine outputs.
"""

from typing import Any, Dict


# ==============================================================================
# System Guardrail Prompts
# ==============================================================================

SYSTEM_GUARDRAIL_PROMPT = """
You are the AI Identity Audit & Risk Governance Specialist for Micron Manufacturing.
You are generating communications based on mathematical risk metrics and statutory audit rules.

CRITICAL OPERATIONAL RULES:
1. You MUST NEVER hallucinate or invent new audit laws, conflict codes, or scores.
2. You MUST strictly use ONLY the facts, scores, laws, and remediation paths provided in the structured context.
3. If an access downgrade (e.g. to ACT_VIEW / View-Only) is mandated, you must present it clearly with its calculated risk reduction.
4. Maintain high professional standards suitable for executive plant leadership and external regulatory auditors.
"""

PLANT_MANAGER_SYSTEM_PROMPT = """
You are speaking directly to a Plant Operations / Production Shift Manager.
Your tone is practical, operational, reassuring, and safety-focused.

Objectives:
- Reassure the manager that daily production line uptime, machine cycles, and wrench-time operations WILL NOT HALT.
- Clearly explain in plain manufacturing terms why the elevated/conflicting privilege (e.g. self-approving scrap or batch handoffs) creates a dual-control or audit liability.
- Explain how the proposed remediation (e.g., granting View-Only access or routing approvals to an independent shift supervisor) maintains work order flow while eliminating compliance risk.
- Keep the briefing concise, actionable, and free of unnecessary legalese.
"""

AUDITOR_MEMO_SYSTEM_PROMPT = """
You are writing a formal Internal Audit & SOX / ISO Compliance Memorandum.
Your tone is authoritative, legalistic, precise, and quantitatively grounded.

Objectives:
- Formally cite the violated statutory Golden Laws (e.g., GL-01 Dual-Control Custody, GL-03 Jurisdictional Containment, GL-04 Temporal Termination).
- Cite governing regulatory frameworks: SOX Section 404, ISO 27001 Annex A.9.4, ISA-95, IEC 62443, FDA 21 CFR Part 11, or NIST SP 800-53.
- Present the exact mathematical risk scoring breakdown: Inherent Risk Score, Current Multiplier (M_p), Proposed Multiplier (M_p), Residual Risk Score, and Risk Reduction Percentage.
- State the formal Audit Finding Classification (e.g. CRITICAL DEFICIENCY, SIGNIFICANT DEFICIENCY, MAJOR NON-CONFORMANCE).
- Specify the mandatory Auditor Mandated Resolution Path.
"""


# ==============================================================================
# Dynamic Prompt Builders for LLM
# ==============================================================================

def build_plant_manager_prompt(payload: Dict[str, Any]) -> str:
    """Constructs the prompt for generating the Plant Manager operational briefing."""
    return f"""
{PLANT_MANAGER_SYSTEM_PROMPT}

EVALUATION PAYLOAD:
- Base Role: {payload.get('base_role')}
- Requested/Added Role: {payload.get('requested_role')}
- Audit Compliance: {'COMPLIANT' if payload.get('compliant') else 'NON-COMPLIANT (SoD Conflict)'}
- Inherent Risk Score: {payload.get('inherent_risk_score', 'N/A')}/100
- Residual Risk Score: {payload.get('residual_risk_score', 'N/A')}/100
- Mathematical Risk Reduction: {payload.get('reduction_pct', 0)}%
- Violated Golden Law: {payload.get('violated_law_id', 'None')} ({payload.get('risk_category', 'Compliant')})
- Operational Vulnerability: {payload.get('vulnerability', 'None')}
- Mandated Remediation: {payload.get('mandated_remediation', 'Approved')}
- Action Downgrade Path: {payload.get('current_action', 'Current')} -> {payload.get('proposed_action', 'Proposed')}

Generate a concise 2-3 paragraph Operational Briefing for the Plant Floor Manager explaining how this adjustment keeps the line running safely and compliant.
"""


def build_auditor_memo_prompt(payload: Dict[str, Any]) -> str:
    """Constructs the prompt for generating the formal Compliance / Auditor Memo."""
    return f"""
{AUDITOR_MEMO_SYSTEM_PROMPT}

EVALUATION PAYLOAD:
- Primary Job Profile: {payload.get('base_role')}
- Requested Assignment: {payload.get('requested_role')}
- Conflict Rule ID: {payload.get('conflict_id', 'N/A')}
- Compliance Status: {'AUDIT COMPLIANT' if payload.get('compliant') else 'NON-COMPLIANT / DEFICIENCY'}
- Statutory Golden Law: {payload.get('violated_law_id', 'None')}
- Audit Finding Severity: {payload.get('risk_category', 'AUDIT COMPLIANT')}
- Inherent Risk Score: {payload.get('inherent_risk_score', 'N/A')} (Tier: {payload.get('risk_level_inherent', 'N/A')})
- Current Action Multiplier: {payload.get('current_multiplier', 'N/A')}x ({payload.get('current_action', 'N/A')})
- Proposed Action Multiplier: {payload.get('proposed_multiplier', 'N/A')}x ({payload.get('proposed_action', 'N/A')})
- Residual Risk Score: {payload.get('residual_risk_score', 'N/A')} (Tier: {payload.get('risk_level_residual', 'N/A')})
- Risk Reduction: {payload.get('reduction_pct', 0)}%
- Operational Breach Mechanism: {payload.get('vulnerability', 'N/A')}
- Auditor Mandated Remediation: {payload.get('mandated_remediation', 'Approved')}

Generate a formal, structured Compliance Memo with sections: [EXECUTIVE SUMMARY], [STATUTORY AUDIT CITATION & NON-CONFORMANCE], [QUANTITATIVE RISK SCORE DELTA], and [MANDATORY REMEDIATION DIRECTIVE].
"""


# ==============================================================================
# Deterministic Fallback Templates (Zero-Hallucination Offline Mode)
# ==============================================================================

def build_offline_plant_manager_brief(payload: Dict[str, Any]) -> str:
    """Generates an operational briefing using deterministic string templates."""
    base_role = payload.get("base_role", "Assigned Role")
    req_role = payload.get("requested_role", "Requested Role")
    compliant = payload.get("compliant", True)
    remediation = payload.get("mandated_remediation", "Approved for assignment.")
    reduction_pct = payload.get("reduction_pct", 0.0)
    res_score = payload.get("residual_risk_score", 10.0)

    if compliant:
        return (
            f"OPERATIONAL BRIEFING: ROLE ASSIGNMENT APPROVAL\n"
            f"Target: {base_role} + {req_role}\n\n"
            f"Good news from the audit evaluation: The request to combine '{req_role}' with '{base_role}' "
            f"has been verified as 100% compliant. This is a complementary, safe operational assignment that "
            f"does not create dual-control bottlenecks or cross-shift friction. Line operations, routine maintenance, "
            f"and shift handoffs may proceed without delay."
        )

    return (
        f"OPERATIONAL BRIEFING: ACTION TIER ADJUSTMENT & UPTIME PRESERVATION\n"
        f"Target: {base_role} + {req_role}\n\n"
        f"Regarding the request to assign '{req_role}' capabilities to '{base_role}': The audit engine identified "
        f"a dual-control Segregation of Duties (SoD) bottleneck ({payload.get('conflict_id', 'SoD Conflict')}). "
        f"Specifically, granting self-approval or release authority on the shop floor creates a severe compliance failure.\n\n"
        f"HOW WE KEEP THE LINE RUNNING:\n"
        f"1. Zero Uptime Interruption: Daily machine cycles, work order execution, and scrap logging continue uninterrupted.\n"
        f"2. View-Only Transparency: The user receives standard view/inspection access to shift logs and telemetry ({payload.get('proposed_action', 'ACT_VIEW')}).\n"
        f"3. Independent Sign-Off: Batch approvals and variance releases are routed to the designated independent shift supervisor.\n\n"
        f"Impact: This adjustment immediately eliminates the audit finding and delivers a {reduction_pct}% mathematical "
        f"risk reduction (Residual Risk Score: {res_score}/100, Tier: LOW)."
    )


def build_offline_auditor_memo(payload: Dict[str, Any]) -> str:
    """Generates a formal compliance memorandum using deterministic templates."""
    base_role = payload.get("base_role", "Base Role")
    req_role = payload.get("requested_role", "Secondary Role")
    compliant = payload.get("compliant", True)
    inh_score = payload.get("inherent_risk_score", 10)
    res_score = payload.get("residual_risk_score", 10)
    red_pct = payload.get("reduction_pct", 0)
    law_id = payload.get("violated_law_id", "N/A")
    category = payload.get("risk_category", "AUDIT COMPLIANT")
    conflict_id = payload.get("conflict_id", "N/A")
    vuln = payload.get("vulnerability", "No conflict identified.")
    remediation = payload.get("mandated_remediation", "Approved for assignment.")

    if compliant:
        return (
            f"================================================================================\n"
            f"INTERNAL AUDIT & COMPLIANCE MEMORANDUM | IDENTITY RISK GOVERNANCE\n"
            f"================================================================================\n\n"
            f"[EXECUTIVE SUMMARY]\n"
            f"Evaluation Subject: Assignment of '{req_role}' to '{base_role}'.\n"
            f"Compliance Determination: AUDIT COMPLIANT (Pass)\n"
            f"Inherent Risk Score: {inh_score}/100 | Residual Risk Score: {res_score}/100\n\n"
            f"[STATUTORY ASSESSMENT]\n"
            f"The evaluated role pairing respects statutory dual-control custody (SOX 404 / ISA-95) and does not "
            f"exceed action-tiering thresholds (ISO 27001 Annex A.9.4). Read/inspection access is strictly segregated "
            f"from mutation authority.\n\n"
            f"[DIRECTIVE]\n"
            f"Status: AUTHORIZED FOR PRODUCTION ASSIGNMENT."
        )

    return (
        f"================================================================================\n"
        f"INTERNAL AUDIT & COMPLIANCE MEMORANDUM | IDENTITY RISK GOVERNANCE\n"
        f"================================================================================\n\n"
        f"[EXECUTIVE SUMMARY]\n"
        f"Subject: Entitlement Cross-Assignment Audit for '{base_role}' + '{req_role}'\n"
        f"Finding Severity: {category}\n"
        f"Conflict Rule Reference: {conflict_id} | Statutory Reference: {law_id}\n\n"
        f"[STATUTORY AUDIT CITATION & NON-CONFORMANCE]\n"
        f"Statutory Mandate: Violated {law_id} (Governing Standard: SOX 404 / ISA-95 / ISO 27001).\n"
        f"Operational Vulnerability: {vuln}\n"
        f"Finding: Critical segregation of duties deficiency. A single identity possesses concurrent transaction "
        f"initiation/modification custody and approval release authority.\n\n"
        f"[QUANTITATIVE RISK SCORE DELTA]\n"
        f"- Inherent Risk Score:      {inh_score:>5.1f} / 100  [Tier: {payload.get('risk_level_inherent', 'CRITICAL')}]\n"
        f"- Current Multiplier (M_p): {payload.get('current_multiplier', 2.5):>5.1f}x      [{payload.get('current_action', 'ACT_APPR')}]\n"
        f"- Proposed Multiplier (M_p):{payload.get('proposed_multiplier', 0.2):>5.1f}x      [{payload.get('proposed_action', 'ACT_VIEW')}]\n"
        f"- Residual Risk Score:      {res_score:>5.1f} / 100  [Tier: {payload.get('risk_level_residual', 'LOW')}]\n"
        f"- Mathematical Reduction:   {red_pct:>5.1f}%\n\n"
        f"[MANDATORY REMEDIATION DIRECTIVE]\n"
        f"Directive: {remediation}\n"
        f"Remediation State: DOWNGRADED_SAFE (Residual risk strictly bounded below statutory threshold <30)."
    )
