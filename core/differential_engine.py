"""
Module 4: Differential Engine & Mathematical Risk Scoring
Quantifies divergence between Persona A (Bot) and Persona B (Desktop Browser):
- Delta S: Status Code Divergence
- R_DOM: DOM Volumetric Ratio
- Delta F: Form Element Differential
- S_trap: Behavioral Trap Score
- S_heuristics: Domain Heuristics Score
- S_risk: Composite Risk Score [0, 100]
"""

from typing import Dict, Any
from config.settings import settings

class DifferentialScoringEngine:
    def __init__(self):
        self.epsilon = 1.0

    def compute_status_divergence(self, status_a: int, status_b: int) -> float:
        """
        Delta S = 1 if Persona A gets 403, 404, or 0, while Persona B gets 200 OK.
        Otherwise 0.
        """
        bot_blocked = status_a in [403, 404, 500, 502, 503, 0]
        browser_ok = status_b == 200
        
        if bot_blocked and browser_ok:
            return 1.0
        return 0.0

    def compute_dom_volumetric_ratio(self, dom_size_a: int, dom_size_b: int) -> float:
        """
        R_DOM = (Size(DOM_B) + epsilon) / (Size(DOM_A) + epsilon)
        """
        r_dom = (float(dom_size_b) + self.epsilon) / (float(dom_size_a) + self.epsilon)
        return round(r_dom, 2)

    def compute_form_differential(self, sensitive_inputs_a: int, sensitive_inputs_b: int) -> float:
        """
        Delta F = count of sensitive inputs (password/email) present in Persona B but missing in Persona A.
        """
        diff = max(0, sensitive_inputs_b - sensitive_inputs_a)
        return float(diff)

    def evaluate_risk(
        self,
        heuristic_res: Dict[str, Any],
        dual_probe_res: Dict[str, Any],
        behavioral_res: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute the overall composite risk score and generate risk classification."""
        res_a = dual_probe_res["persona_a"]
        res_b = dual_probe_res["persona_b"]

        # 1. Delta S
        delta_s = self.compute_status_divergence(res_a["status_code"], res_b["status_code"])
        
        # 2. R_DOM
        r_dom = self.compute_dom_volumetric_ratio(res_a["dom_size"], res_b["dom_size"])
        r_dom_capped = min(r_dom, settings.MAX_DOM_RATIO_CAP)

        # 3. Delta F
        delta_f = self.compute_form_differential(
            res_a["sensitive_input_count"],
            res_b["sensitive_input_count"]
        )
        delta_f_capped = min(delta_f, settings.MAX_FORM_DIVERGENCE_CAP)

        # 4. S_trap
        s_trap = 1.0 if behavioral_res.get("trap_detected", False) else 0.0

        # 5. S_heuristics
        s_heuristics = float(heuristic_res.get("heuristic_score", 0))

        # 6. S_exfil
        s_exfil = 1.0 if behavioral_res.get("exfiltration_detected", False) else 0.0

        # Compute Composite Risk Score (S_risk in [0, 100])
        raw_score = (
            (delta_s * settings.WEIGHT_STATUS_DIVERGENCE) +
            (r_dom_capped * settings.WEIGHT_DOM_RATIO) +
            (delta_f_capped * settings.WEIGHT_FORM_DIVERGENCE) +
            (s_trap * settings.WEIGHT_BEHAVIORAL_TRAP) +
            (s_heuristics * settings.WEIGHT_HEURISTICS) +
            (s_exfil * settings.WEIGHT_EXFILTRATION)
        )

        s_risk = round(min(100.0, max(0.0, raw_score)), 1)

        # Risk Classification
        if s_risk >= 70.0:
            risk_level = "CRITICAL / HIGH CLOAKING RISK"
            action_recommended = "BLOCK & WARN USER IMMEDIATELY"
        elif s_risk >= 40.0:
            risk_level = "MODERATE SUSPICION"
            action_recommended = "FLAG FOR MANUAL REVIEW"
        else:
            risk_level = "LOW RISK / BENIGN"
            action_recommended = "ALLOW ACCESS"

        return {
            "s_risk": s_risk,
            "risk_level": risk_level,
            "action_recommended": action_recommended,
            "metrics": {
                "delta_s": delta_s,
                "r_dom": r_dom,
                "r_dom_capped": r_dom_capped,
                "delta_f": delta_f,
                "delta_f_capped": delta_f_capped,
                "s_trap": s_trap,
                "s_heuristics": s_heuristics,
                "s_exfil": s_exfil
            },
            "cloaking_evasion_detected": (delta_s > 0 or r_dom > 5.0 or delta_f > 0 or s_trap > 0 or s_exfil > 0)
        }
