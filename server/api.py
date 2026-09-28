"""
FastAPI Backend API Server for CloakBuster Inspection Engine
Provides REST API endpoints for single-URL inspection, persona comparison, and Chrome Extension querying.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional

from core.heuristics import URLHeuristicsAnalyzer
from core.dual_probing import DualPersonaProbingEngine
from core.behavioral_trap import BehavioralTrapAuditor
from core.differential_engine import DifferentialScoringEngine
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

    try:
        # Step 1: Module 1 - Heuristic Inspection
        heuristics_res = heuristics_analyzer.analyze(raw_url)
        target_url = heuristics_res["canonical_url"]

        # Step 2: Module 2 - Dual-Persona Probing
        dual_probe_res = await probing_engine.execute_dual_probe(target_url)

        # Step 3: Module 3 - Behavioral Trap & Exfiltration Audit
        behavioral_res = await trap_auditor.audit_page_behavior(target_url)

        # Step 4: Module 4 - Differential Scoring
        differential_res = differential_engine.evaluate_risk(
            heuristic_res=heuristics_res,
            dual_probe_res=dual_probe_res,
            behavioral_res=behavioral_res
        )

        return {
            "url": target_url,
            "risk_score": differential_res["s_risk"],
            "risk_level": differential_res["risk_level"],
            "action_recommended": differential_res["action_recommended"],
            "cloaking_detected": differential_res["cloaking_evasion_detected"],
            "heuristics": heuristics_res,
            "persona_comparison": {
                "persona_a": {
                    "name": dual_probe_res["persona_a"]["persona"],
                    "status_code": dual_probe_res["persona_a"]["status_code"],
                    "dom_size_bytes": dual_probe_res["persona_a"]["dom_size"],
                    "form_count": dual_probe_res["persona_a"]["form_count"],
                    "sensitive_input_count": dual_probe_res["persona_a"]["sensitive_input_count"]
                },
                "persona_b": {
                    "name": dual_probe_res["persona_b"]["persona"],
                    "status_code": dual_probe_res["persona_b"]["status_code"],
                    "dom_size_bytes": dual_probe_res["persona_b"]["dom_size"],
                    "form_count": dual_probe_res["persona_b"]["form_count"],
                    "sensitive_input_count": dual_probe_res["persona_b"]["sensitive_input_count"],
                    "password_input_count": dual_probe_res["persona_b"]["password_input_count"]
                }
            },
            "behavioral_audit": {
                "back_button_trap_detected": behavioral_res["trap_detected"],
                "trap_reasons": behavioral_res["trap_reasons"],
                "third_party_exfiltration_detected": behavioral_res["exfiltration_detected"],
                "exfiltration_targets": behavioral_res["exfiltration_targets"]
            },
            "metrics": differential_res["metrics"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

def start_api():
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)

if __name__ == "__main__":
    start_api()
