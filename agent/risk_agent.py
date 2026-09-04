import os
import json
from dotenv import load_dotenv

load_dotenv()

from engine.rules_engine import RulesEngine
from engine.scoring import RiskScoringEngine

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class AuditRiskAgent:
    def __init__(self, rules_engine=None, scoring_engine=None):
        self.rules_engine = rules_engine or RulesEngine()
        self.scoring_engine = scoring_engine or RiskScoringEngine()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        if HAS_GENAI and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def query(self, user_prompt: str) -> dict:
        """
        Determines whether the prompt is an access evaluation request
        or a general governance/conceptual query, routing appropriately.
        """
        prompt_lower = user_prompt.lower()
        
        # Check if query references explicit roles or conflict decisions
        is_evaluation = any(keyword in prompt_lower for keyword in [
            "assign", "operator", "supervisor", "handler", "buyer", 
            "approve", "request", "conflict", "sod", "access to"
        ]) and not prompt_lower.startswith(("what is", "explain", "how do", "define"))

        if is_evaluation:
            return self._handle_evaluation(user_prompt)
        else:
            return self._handle_general_query(user_prompt)

    def _handle_general_query(self, query: str) -> dict:
        if self.client:
            try:
                sys_instruct = (
                    "You are the Micron Sentinel Governance AI Copilot. "
                    "You are an expert on semiconductor manufacturing access control, "
                    "Segregation of Duties (SoD), SOX 404, ISA-95 levels, and ISO 27001. "
                    "Provide clear, professional, concise explanations without fluff."
                )
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=query,
                    config={"system_instruction": sys_instruct, "temperature": 0.2}
                )
                return {
                    "type": "informational",
                    "content": response.text
                }
            except Exception as e:
                pass

        # Fallback explanation if API is unavailable
        fallback_answers = {
            "what is access request": (
                "An **Access Request** is a formal, auditable workflow where an employee or system account "
                "requests permissions to execute transactions, modify master parameters, or approve records "
                "within manufacturing execution systems (MES), ERP, or shop-floor supervisory controls. "
                "In high-reliability semiconductor environments like Micron, every access request must be evaluated against "
                "strict Segregation of Duties (SoD) matrices to prevent fraud, scrap write-offs, and compliance violations."
            )
        }
        return {
            "type": "informational",
            "content": fallback_answers.get(
                query.strip().lower(),
                "In industrial access control, permissions are bounded by physical jurisdiction and role segregation "
                "to ensure line safety, shift continuity, and statutory SOX 404 / ISA-95 compliance."
            )
        }

    def _handle_evaluation(self, prompt: str) -> dict:
        prompt_lower = prompt.lower()
        base = "Production Operator"
        target = "Production Supervisor"

        if "warehouse" in prompt_lower or "handler" in prompt_lower:
            base = "Warehouse Material Handler"
        if "buyer" in prompt_lower or "procurement" in prompt_lower:
            target = "Procurement Buyer"
        elif "sop" in prompt_lower or "viewer" in prompt_lower:
            target = "Standard SOP Viewer"
        elif "inventory" in prompt_lower:
            target = "Inventory Controller"
        elif "supervisor" in prompt_lower:
            target = "Production Supervisor"

        conflict = self.rules_engine.evaluate_role_addition(base, target)
        is_comp = conflict.get("compliant", True)
        inh = float(conflict.get("inherent_risk_score", 15.0))
        calc = self.scoring_engine.calculate_residual_risk(inh, "ACT_APPR" if not is_comp else "ACT_VIEW", "ACT_VIEW")

        return {
            "type": "evaluation",
            "base_role": base,
            "target_role": target,
            "compliant": is_comp,
            "conflict_id": conflict.get("conflict_id") or "CLEARED",
            "violated_law_id": conflict.get("violated_law_id") or "GL-01",
            "inherent_score": inh,
            "residual_score": calc["residual_risk"],
            "reduction_pct": calc["reduction_pct"],
            "vulnerability": conflict.get("vulnerability", "No statutory conflict."),
            "remediation": conflict.get("mandated_remediation", "Authorization permitted.")
        }