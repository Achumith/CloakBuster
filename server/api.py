"""
FastAPI Backend API Server for CloakBuster Inspection Engine
Provides REST API endpoints for single-URL inspection, persona comparison, and Chrome Extension querying.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional

import asyncio
import base64
from core.heuristics import URLHeuristicsAnalyzer
from core.dual_probing import DualPersonaProbingEngine
from core.behavioral_trap import BehavioralTrapAuditor
from core.differential_engine import DifferentialScoringEngine
from core.multi_persona import MultiPersonaEngine
from core.visual_verification import VisualTwinClassifier
from config.settings import settings

app = FastAPI(
    title="CloakBuster Inspection API",
    description="Multi-Persona Differential Probing & Behavioral Anti-Evasion Engine",
    version="1.0.0"
)

# Enable CORS for Chrome Extension & Dashboard UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    url: str
    include_mobile: Optional[bool] = False

class AnalyzeResponse(BaseModel):
    url: str
    risk_score: float
    risk_level: str
    action_recommended: str
    cloaking_detected: bool
    heuristics: Dict[str, Any]
    persona_comparison: Dict[str, Any]
    behavioral_audit: Dict[str, Any]
    metrics: Dict[str, Any]
    visual_verification: Optional[Dict[str, Any]] = None

def bytes_to_b64(b: Optional[bytes]) -> Optional[str]:
    if not b:
        return None
    return base64.b64encode(b).decode("utf-8")

@app.get("/")
async def root():
    return {
        "service": "CloakBuster Analysis Engine",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/analyze")
async def analyze_url(req: AnalyzeRequest):
    raw_url = req.url
    if not raw_url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    # Instantiate engines
    heuristics_analyzer = URLHeuristicsAnalyzer()
    probing_engine = DualPersonaProbingEngine()
    trap_auditor = BehavioralTrapAuditor()
    differential_engine = DifferentialScoringEngine()
    visual_classifier = VisualTwinClassifier()

    try:
        # Step 1: Module 1 - Heuristic Inspection
        heuristics_res = heuristics_analyzer.analyze(raw_url)
        target_url = heuristics_res["canonical_url"]

        # Step 2 & 3: Execute Dual-Persona Probing and Behavioral Trap Audit concurrently
        dual_probe_res, behavioral_res = await asyncio.gather(
            probing_engine.execute_dual_probe(target_url),
            trap_auditor.audit_page_behavior(target_url)
        )

        # Step 4: Module 4 - Differential Scoring
        differential_res = differential_engine.evaluate_risk(
            heuristic_res=heuristics_res,
            dual_probe_res=dual_probe_res,
            behavioral_res=behavioral_res
        )

        # Step 5: Module 8 - Visual Impersonation & Perceptual Hashing (pHash)
        visual_res = visual_classifier.evaluate_visual_impersonation(
            dual_probe_res["persona_b"].get("screenshot_bytes"),
            heuristics_res["hostname"]
        )

        persona_comp = {
            "persona_a": {
                "name": dual_probe_res["persona_a"]["persona"],
                "status_code": dual_probe_res["persona_a"]["status_code"],
                "dom_size_bytes": dual_probe_res["persona_a"]["dom_size"],
                "form_count": dual_probe_res["persona_a"]["form_count"],
                "sensitive_input_count": dual_probe_res["persona_a"]["sensitive_input_count"],
                "password_input_count": dual_probe_res["persona_a"].get("password_input_count", 0),
                "screenshot_base64": bytes_to_b64(dual_probe_res["persona_a"].get("screenshot_bytes"))
            },
            "persona_b": {
                "name": dual_probe_res["persona_b"]["persona"],
                "status_code": dual_probe_res["persona_b"]["status_code"],
                "dom_size_bytes": dual_probe_res["persona_b"]["dom_size"],
                "form_count": dual_probe_res["persona_b"]["form_count"],
                "sensitive_input_count": dual_probe_res["persona_b"]["sensitive_input_count"],
                "password_input_count": dual_probe_res["persona_b"].get("password_input_count", 0),
                "screenshot_base64": bytes_to_b64(dual_probe_res["persona_b"].get("screenshot_bytes"))
            }
        }

        # Step 6: Module 6 - Optional Persona C (Mobile Device Emulation)
        if req.include_mobile:
            mobile_engine = MultiPersonaEngine()
            persona_c_res = await mobile_engine.probe_persona_c_mobile(target_url)
            persona_comp["persona_c"] = {
                "name": persona_c_res.get("persona", "Persona C (Mobile)"),
                "status_code": persona_c_res.get("status_code", 0),
                "dom_size_bytes": persona_c_res.get("dom_size", 0),
                "input_count": persona_c_res.get("input_count", 0),
                "screenshot_base64": bytes_to_b64(persona_c_res.get("screenshot_bytes"))
            }

        return {
            "url": target_url,
            "risk_score": differential_res["s_risk"],
            "risk_level": differential_res["risk_level"],
            "action_recommended": differential_res["action_recommended"],
            "cloaking_detected": differential_res["cloaking_evasion_detected"],
            "waf_detected": differential_res.get("waf_detected", False),
            "is_high_reputation": differential_res.get("is_high_reputation", False),
            "heuristics": heuristics_res,
            "persona_comparison": persona_comp,
            "behavioral_audit": {
                "back_button_trap_detected": behavioral_res["trap_detected"],
                "trap_reasons": behavioral_res["trap_reasons"],
                "third_party_exfiltration_detected": behavioral_res["exfiltration_detected"],
                "exfiltration_targets": behavioral_res["exfiltration_targets"]
            },
            "visual_verification": visual_res,
            "metrics": differential_res["metrics"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

def start_api():
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)

if __name__ == "__main__":
    start_api()
