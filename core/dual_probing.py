"""
Module 2: Dual-Persona Probing Engine
- Persona A (Naive Bot): Lightweight HTTP GET request (requests/httpx) with raw User-Agent.
- Persona B (Emulated Desktop Browser): Headless Chromium via Playwright with JS execution, 1920x1080 viewport.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from config.settings import settings

class DualPersonaProbingEngine:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def probe_persona_a(self, url: str) -> Dict[str, Any]:
        """Persona A (Naive Bot): Raw HTTP GET without JavaScript execution."""
        headers = {"User-Agent": settings.USER_AGENT_BOT}
        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                dom_text = response.text
                soup = BeautifulSoup(dom_text, "html.parser")
                
                inputs = soup.find_all("input")
                sensitive_inputs = [
                    inp for inp in inputs
                    if inp.get("type") in ["password", "email", "text", "tel"] or
                       any(k in str(inp.get("name", "")).lower() for k in ["user", "login", "pass", "auth"])
                ]

                return {
                    "persona": "Persona A (Naive Bot)",
                    "status_code": response.status_code,
                    "final_url": str(response.url),
                    "dom_size": len(dom_text),
                    "form_count": len(soup.find_all("form")),
                    "sensitive_input_count": len(sensitive_inputs),
                    "input_types": [inp.get("type", "text") for inp in inputs],
                    "raw_dom": dom_text[:2000],  # truncated sample
                    "success": True,
                    "error": None
                }
        except Exception as e:
            return {
                "persona": "Persona A (Naive Bot)",
                "status_code": 0,
                "final_url": url,
                "dom_size": 0,
                "form_count": 0,
                "sensitive_input_count": 0,
                "input_types": [],
                "raw_dom": "",
                "success": False,
                "error": str(e)
            }

    async def probe_persona_b(self, url: str) -> Dict[str, Any]:
        """Persona B (Emulated Desktop Browser): Playwright Chromium with JS runtime."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=settings.USER_AGENT_DESKTOP,
                    viewport={"width": 1920, "height": 1080},
                    device_scale_factor=1,
                )
                page = await context.new_page()

                # Collect network calls for exfiltration check
                outbound_requests = []
                page.on("request", lambda req: outbound_requests.append(req.url))

                response = await page.goto(url, wait_until="domcontentloaded", timeout=int(self.timeout * 1000))
                status_code = response.status if response else 0
                await page.wait_for_timeout(2000)  # allow dynamic JS rendering

                dom_text = await page.content()
                final_url = page.url
                
                # Analyze rendered DOM
                sensitive_inputs = await page.eval_on_selector_all(
                    "input",
                    """inputs => inputs.map(i => ({
                        type: i.type,
                        name: i.name,
                        id: i.id,
                        action: i.form ? i.form.action : null
                    }))"""
                )
                
                forms = await page.eval_on_selector_all(
                    "form",
                    "forms => forms.map(f => ({ action: f.action, method: f.method }))"
                )

                password_inputs = [i for i in sensitive_inputs if i.get("type") == "password"]
                email_inputs = [i for i in sensitive_inputs if i.get("type") in ["email", "text"] and any(k in (i.get("name") or "").lower() for k in ["user", "email", "login"])]

                screenshot_bytes = await page.screenshot(type="png", full_page=True)

                await browser.close()

                return {
                    "persona": "Persona B (Emulated Desktop)",
                    "status_code": status_code,
                    "final_url": final_url,
                    "dom_size": len(dom_text),
                    "form_count": len(forms),
                    "forms": forms,
                    "sensitive_input_count": len(password_inputs) + len(email_inputs),
                    "password_input_count": len(password_inputs),
                    "input_details": sensitive_inputs,
                    "outbound_requests": outbound_requests,
                    "screenshot_bytes": screenshot_bytes,
                    "raw_dom": dom_text[:2000],
                    "success": True,
                    "error": None
                }
        except Exception as e:
            return {
                "persona": "Persona B (Emulated Desktop)",
                "status_code": 0,
                "final_url": url,
                "dom_size": 0,
                "form_count": 0,
                "forms": [],
                "sensitive_input_count": 0,
                "password_input_count": 0,
                "input_details": [],
                "outbound_requests": [],
                "screenshot_bytes": None,
                "raw_dom": "",
                "success": False,
                "error": str(e)
            }

    async def execute_dual_probe(self, url: str) -> Dict[str, Any]:
        """Execute Persona A and Persona B in parallel."""
        res_a, res_b = await asyncio.gather(
            self.probe_persona_a(url),
            self.probe_persona_b(url)
        )
        return {
            "persona_a": res_a,
            "persona_b": res_b
        }
