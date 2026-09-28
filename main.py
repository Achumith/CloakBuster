"""
CloakBuster Main Entry Point
CLI tool to run individual components or inspect URLs directly from the terminal.
"""

import sys
import asyncio
import json
import argparse
from core.heuristics import URLHeuristicsAnalyzer
from core.dual_probing import DualPersonaProbingEngine
from core.behavioral_trap import BehavioralTrapAuditor
from core.differential_engine import DifferentialScoringEngine

async def analyze_cli(url: str):
    print(f"\n=======================================================")
    print(f"[SHIELD] CloakBuster Differential Probing Inspection")
    print(f"Target URL: {url}")
    print(f"=======================================================\n")

    heuristics_analyzer = URLHeuristicsAnalyzer()
    probing_engine = DualPersonaProbingEngine()
    trap_auditor = BehavioralTrapAuditor()
    differential_engine = DifferentialScoringEngine()

    print("[1/4] Running Module 1: Domain Heuristics & SSL Audit...")
    h_res = heuristics_analyzer.analyze(url)

    print("[2/4] Running Module 2: Dual-Persona Probing Engine (Bot vs Playwright Desktop)...")
    probe_res = await probing_engine.execute_dual_probe(h_res["canonical_url"])

    print("[3/4] Running Module 3: Behavioral Trap & Form Exfiltration Audit...")
    trap_res = await trap_auditor.audit_page_behavior(h_res["canonical_url"])

    print("[4/4] Running Module 4: Differential Engine Risk Scoring...")
    diff_res = differential_engine.evaluate_risk(h_res, probe_res, trap_res)

    print("\n------------------- RESULTS MATRIX -------------------")
    print(f"Persona A Status Code : {probe_res['persona_a']['status_code']}")
    print(f"Persona B Status Code : {probe_res['persona_b']['status_code']}")
    print(f"Persona A DOM Size   : {probe_res['persona_a']['dom_size']} Bytes")
    print(f"Persona B DOM Size   : {probe_res['persona_b']['dom_size']} Bytes")
    print(f"Back-Button Trap      : {'DETECTED [WARN]' if trap_res['trap_detected'] else 'Clean [OK]'}")
    print(f"Form Exfiltration     : {'DETECTED [WARN]' if trap_res['exfiltration_detected'] else 'Clean [OK]'}")
    print("------------------------------------------------------")
    print(f"COMPOSITE RISK SCORE : {diff_res['s_risk']} / 100")
    print(f"CLASSIFICATION          : {diff_res['risk_level']}")
    print(f"RECOMMENDED ACTION      : {diff_res['action_recommended']}")
    print("=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="CloakBuster Phishing & Cloaking Detection CLI")
    parser.add_argument("mode", choices=["analyze", "mock", "server", "ui"], help="Mode to execute")
    parser.add_argument("--url", default="http://127.0.0.1:5000/login", help="Target URL for analyze mode")

    args = parser.parse_args()

    if args.mode == "analyze":
        asyncio.run(analyze_cli(args.url))
    elif args.mode == "mock":
        from server.mock_server import start_mock_server
        start_mock_server()
    elif args.mode == "server":
        from server.api import start_api
        start_api()
    elif args.mode == "ui":
        import os
        os.system("streamlit run ui/app.py")

if __name__ == "__main__":
    main()
