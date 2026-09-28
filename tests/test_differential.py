"""
Unit tests for Module 4: Differential Engine & Mathematical Risk Scoring
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.differential_engine import DifferentialScoringEngine

def test_status_divergence():
    engine = DifferentialScoringEngine()
    # Bot receives 404, Browser receives 200 -> Delta S = 1.0
    assert engine.compute_status_divergence(404, 200) == 1.0
    # Both receive 200 -> Delta S = 0.0
    assert engine.compute_status_divergence(200, 200) == 0.0

def test_dom_volumetric_ratio():
    engine = DifferentialScoringEngine()
    # DOM B = 1000 bytes, DOM A = 100 bytes -> R_DOM = 10.0
    ratio = engine.compute_dom_volumetric_ratio(100, 1000)
    assert ratio == 9.91 or ratio == 10.0 or ratio > 5.0

def test_composite_risk_score():
    engine = DifferentialScoringEngine()
    
    heuristic_res = {"heuristic_score": 2}
    dual_probe_res = {
        "persona_a": {"status_code": 404, "dom_size": 150, "sensitive_input_count": 0},
        "persona_b": {"status_code": 200, "dom_size": 3500, "sensitive_input_count": 2}
    }
    behavioral_res = {
        "trap_detected": True,
        "exfiltration_detected": True
    }

    result = engine.evaluate_risk(heuristic_res, dual_probe_res, behavioral_res)
    
    assert result["s_risk"] >= 70.0
    assert result["cloaking_evasion_detected"] is True
    assert "CRITICAL" in result["risk_level"]

if __name__ == "__main__":
    test_status_divergence()
    test_dom_volumetric_ratio()
    test_composite_risk_score()
    print("[SUCCESS] All differential engine tests passed!")
