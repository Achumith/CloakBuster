"""
Module 4: Differential Engine & Mathematical Risk Scoring
Quantifies divergence between Persona A (Bot) and Persona B (Desktop Browser):
- Delta S: Status Code Divergence (with Anti-Scraping WAF vs Phishing distinction)
- R_DOM: DOM Volumetric Ratio (conditioned on decoy stubs and credential exposure)
- Delta F: Form Element Differential (sensitive credentials concealed from bots)
- S_trap: Behavioral Trap Score (popstate / back-button hijacking)
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
        Delta S = 1 if Persona A gets 403, 404, 429, 500, or 0, while Persona B gets 200 OK.
        Otherwise 0.
        """
        bot_blocked = status_a in [403, 404, 429, 500, 502, 503, 0]
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
        Delta F = count of sensitive inputs (password/email/login) present in Persona B but concealed from Persona A.
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

        is_high_reputation = heuristic_res.get("is_high_reputation", False)

        # 1. Delta S
        raw_delta_s = self.compute_status_divergence(res_a["status_code"], res_b["status_code"])
        
        # 2. R_DOM
        r_dom = self.compute_dom_volumetric_ratio(res_a["dom_size"], res_b["dom_size"])
        r_dom_capped = min(r_dom, settings.MAX_DOM_RATIO_CAP)

        # 3. Delta F & Password Inputs
        delta_f = self.compute_form_differential(
            res_a.get("sensitive_input_count", 0),
            res_b.get("sensitive_input_count", 0)
        )
        delta_f_capped = min(delta_f, settings.MAX_FORM_DIVERGENCE_CAP)
        password_count_b = res_b.get("password_input_count", 0)
        sensitive_count_b = res_b.get("sensitive_input_count", 0)

        # 4. S_trap & S_exfil
        s_trap = 1.0 if behavioral_res.get("trap_detected", False) else 0.0
        s_exfil = 1.0 if behavioral_res.get("exfiltration_detected", False) else 0.0

        # 5. S_heuristics
        s_heuristics = float(heuristic_res.get("heuristic_score", 0))

        # Check for WAF Anti-Scraping vs True Phishing Cloaking
        # If Persona A was blocked (403/404), but Persona B has NO passwords, NO hidden forms, NO traps, NO exfil:
        # It's an anti-bot WAF (e.g. Wikipedia, Cloudflare), NOT a cloaked phishing kit!
        waf_detected = False
        is_cloaked_phishing = False

        if raw_delta_s > 0:
            if password_count_b > 0 or delta_f > 0 or s_trap > 0 or s_exfil > 0:
                is_cloaked_phishing = True
            else:
                waf_detected = True

        # Delta S score: Full weight (30 pts) if cloaking credentials; 10 pts informational if WAF
        if is_cloaked_phishing:
            delta_s_effective = 1.0
            delta_s_score = delta_s_effective * settings.WEIGHT_STATUS_DIVERGENCE
        elif waf_detected:
            delta_s_effective = 0.33  # ~10 points
            delta_s_score = 10.0
        else:
            delta_s_effective = 0.0
            delta_s_score = 0.0

        # DOM Ratio score:
        # Only penalize if it's cloaked phishing or hidden credentials.
        # WAF blocks or standard dynamic JS hydration = 0 penalty.
        if is_high_reputation or waf_detected:
            r_dom_penalty = 0.0
        elif (res_a["dom_size"] < 500 and res_b["dom_size"] > 1500 and (password_count_b > 0 or delta_f > 0)) or is_cloaked_phishing:
            r_dom_penalty = r_dom_capped * settings.WEIGHT_DOM_RATIO
        else:
            r_dom_penalty = 0.0

        # Form divergence score
        delta_f_score = delta_f_capped * settings.WEIGHT_FORM_DIVERGENCE

        # Trap, heuristics, exfil
        trap_score = s_trap * settings.WEIGHT_BEHAVIORAL_TRAP
        heuristics_score = s_heuristics * settings.WEIGHT_HEURISTICS
        exfil_score = s_exfil * settings.WEIGHT_EXFILTRATION

        # Compute Raw Composite Risk Score
        raw_score = delta_s_score + r_dom_penalty + delta_f_score + trap_score + heuristics_score + exfil_score

        # High-Reputation Whitelist Override (e.g. google.com, wikipedia.org, example.com)
        if is_high_reputation:
            raw_score = 0.0
            risk_level = "VERIFIED LEGITIMATE (BENIGN)"
            action_recommended = "ALLOW ACCESS - VERIFIED AUTHENTIC DOMAIN"
            cloaking_evasion_detected = False
        else:
            s_risk = round(min(100.0, max(0.0, raw_score)), 1)
            
            # Risk Classification
            if s_risk >= 70.0:
                risk_level = "CRITICAL / HIGH CLOAKING RISK"
                action_recommended = "BLOCK & WARN USER IMMEDIATELY"
            elif s_risk >= 40.0:
                risk_level = "MODERATE SUSPICION"
                action_recommended = "FLAG FOR MANUAL REVIEW"
            elif waf_detected:
                risk_level = "LOW RISK / BENIGN (WAF SHIELD ACTIVE)"
                action_recommended = "ALLOW ACCESS - STANDARD ANTI-BOT WAF"
            else:
                risk_level = "LOW RISK / BENIGN"
                action_recommended = "ALLOW ACCESS"

            # Cloaking Evasion Detection Flag
            cloaking_evasion_detected = (
                is_cloaked_phishing or
                delta_f > 0 or
                s_trap > 0 or
                s_exfil > 0 or
                (r_dom > 5.0 and res_a["dom_size"] < 500 and sensitive_count_b > 0)
            )

        s_risk = 0.0 if is_high_reputation else round(min(100.0, max(0.0, raw_score)), 1)

        return {
            "s_risk": s_risk,
            "risk_level": risk_level,
            "action_recommended": action_recommended,
            "waf_detected": waf_detected,
            "is_high_reputation": is_high_reputation,
            "metrics": {
                "delta_s": raw_delta_s,
                "delta_s_effective": delta_s_effective,
                "r_dom": r_dom,
                "r_dom_capped": r_dom_capped,
                "r_dom_penalty": r_dom_penalty,
                "delta_f": delta_f,
                "delta_f_capped": delta_f_capped,
                "s_trap": s_trap,
                "s_heuristics": s_heuristics,
                "s_exfil": s_exfil
            },
            "cloaking_evasion_detected": cloaking_evasion_detected
        }
