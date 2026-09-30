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

def is_sensitive_credential_input(inp_type: str, inp_name: str, inp_id: str = "", placeholder: str = "") -> bool:
    inp_type = (inp_type or "").lower().strip()
    inp_name = (inp_name or "").lower().strip()
    inp_id = (inp_id or "").lower().strip()
    placeholder = (placeholder or "").lower().strip()
    
    if inp_type == "password":
        return True
    
    combined_str = f"{inp_name} {inp_id} {placeholder}"
    if inp_name in ["q", "query", "search", "search_query"] or any(k in combined_str for k in ["search", "query", "find", "filter", "keyword"]):
        return False
        
    auth_keywords = ["username", "user", "login", "email", "passwd", "pass", "signin", "auth", "account", "identifier", "credential"]
    if inp_type in ["email", "tel"]:
        return True
    if any(k in combined_str for k in auth_keywords):
        return True
        
    return False

def is_password_input(inp_type: str) -> bool:
    return (inp_type or "").lower().strip() == "password"

class DualPersonaProbingEngine:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def render_persona_a_screenshot(self, dom_text: str, status_code: int, error_msg: Optional[str] = None) -> Optional[bytes]:
        """Render the response received by Persona A into a screenshot for visual comparison."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Disable JS for Persona A bot emulation to prevent slow external scripts from hanging
                page = await browser.new_page(
                    viewport={"width": 1280, "height": 800},
                    java_script_enabled=False
                )
                
                if dom_text and len(dom_text.strip()) > 0:
                    try:
                        # wait_until="commit" commits HTML directly into the DOM without waiting for external assets
                        await page.set_content(dom_text, wait_until="commit", timeout=5000)
                    except Exception:
                        await page.set_content(
                            f"<div style='font-family:sans-serif;padding:24px;background:#f8f9fa;'><h3>Persona A Response:</h3><pre>{dom_text[:2000]}</pre></div>",
                            wait_until="commit",
                            timeout=3000
                        )
                else:
                    html_error = f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Persona A Response</title></head>
                    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
                        <div style="background: #1e293b; padding: 40px; border-radius: 12px; border: 1px solid #334155; text-align: center; max-width: 520px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                            <div style="font-size: 40px; margin-bottom: 10px;">🤖</div>
                            <h2 style="color: #ef4444; margin: 0 0 10px 0; font-size: 24px;">HTTP {status_code}</h2>
                            <p style="color: #94a3b8; font-size: 14px; margin: 0 0 20px 0;">{error_msg or 'Empty or unrenderable response received by automated bot crawler.'}</p>
                            <div style="font-size: 12px; color: #64748b; background: #0f172a; padding: 10px; border-radius: 6px; border: 1px solid #1e293b;">
                                <code>Probe UA: {settings.USER_AGENT_BOT}</code>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    await page.set_content(html_error, wait_until="commit", timeout=3000)

                screenshot_bytes = await page.screenshot(type="png", full_page=False, timeout=5000)
                await browser.close()
                return screenshot_bytes
        except Exception:
            return None

    async def probe_persona_a(self, url: str) -> Dict[str, Any]:
        """Persona A (Naive Bot): Raw HTTP GET without JavaScript execution."""
        headers = {"User-Agent": settings.USER_AGENT_BOT}
        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                dom_text = response.text
                soup = BeautifulSoup(dom_text, "html.parser")
                
                inputs = soup.find_all("input")
                password_inputs = [inp for inp in inputs if is_password_input(inp.get("type", "text"))]
                sensitive_inputs = [
                    inp for inp in inputs
                    if is_sensitive_credential_input(
                        inp.get("type", "text"),
                        str(inp.get("name", "")),
                        str(inp.get("id", "")),
                        str(inp.get("placeholder", ""))
                    )
                ]

                # Render screenshot of the exact content received by Persona A
                screenshot_bytes = await self.render_persona_a_screenshot(dom_text, response.status_code)

                return {
                    "persona": "Persona A (Naive Bot)",
                    "status_code": response.status_code,
                    "final_url": str(response.url),
                    "dom_size": len(dom_text),
                    "form_count": len(soup.find_all("form")),
                    "sensitive_input_count": len(sensitive_inputs),
                    "password_input_count": len(password_inputs),
                    "input_types": [inp.get("type", "text") for inp in inputs],
                    "screenshot_bytes": screenshot_bytes,
                    "raw_dom": dom_text[:2000],  # truncated sample
                    "success": True,
                    "error": None
                }
        except Exception as e:
            screenshot_bytes = await self.render_persona_a_screenshot("", 0, error_msg=str(e))
            return {
                "persona": "Persona A (Naive Bot)",
                "status_code": 0,
                "final_url": url,
                "dom_size": 0,
                "form_count": 0,
                "sensitive_input_count": 0,
                "input_types": [],
                "screenshot_bytes": screenshot_bytes,
                "raw_dom": "",
                "success": False,
                "error": str(e)
            }

    async def probe_persona_b(self, url: str) -> Dict[str, Any]:
        """Persona B (Emulated Desktop Browser): Playwright Chromium with JS runtime."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    user_agent=settings.USER_AGENT_DESKTOP,
                    viewport={"width": 1280, "height": 800},
                    device_scale_factor=1,
                    ignore_https_errors=True,
                    bypass_csp=True
                )
                page = await context.new_page()

                # Automatically dismiss dialogs so alerts/cookie popups do not block rendering
                page.on("dialog", lambda d: asyncio.create_task(d.dismiss()))

                # Collect network calls for exfiltration check
                outbound_requests = []
                page.on("request", lambda req: outbound_requests.append(req.url))

                status_code = 0
                try:
                    response = await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=int(self.timeout * 1000)
                    )
                    status_code = response.status if response else 0
                except Exception:
                    # If domcontentloaded times out due to heavy external trackers, proceed with rendered content
                    status_code = 200

                await page.wait_for_timeout(1500)  # allow dynamic JS rendering

                dom_text = await page.content()
                final_url = page.url
                
                # Analyze rendered DOM
                raw_inputs = await page.eval_on_selector_all(
                    "input",
                    """inputs => inputs.map(i => ({
                        type: i.type,
                        name: i.name,
                        id: i.id,
                        placeholder: i.placeholder,
                        action: i.form ? i.form.action : null
                    }))"""
                )
                
                forms = await page.eval_on_selector_all(
                    "form",
                    "forms => forms.map(f => ({ action: f.action, method: f.method }))"
                )

                password_inputs = [i for i in raw_inputs if is_password_input(i.get("type"))]
                sensitive_inputs = [
                    i for i in raw_inputs
                    if is_sensitive_credential_input(
                        i.get("type", ""),
                        i.get("name", ""),
                        i.get("id", ""),
                        i.get("placeholder", "")
                    )
                ]

                screenshot_bytes = None
                try:
                    screenshot_bytes = await page.screenshot(type="png", full_page=False, timeout=5000)
                except Exception:
                    screenshot_bytes = None

                await browser.close()

                return {
                    "persona": "Persona B (Emulated Desktop)",
                    "status_code": status_code,
                    "final_url": final_url,
                    "dom_size": len(dom_text),
                    "form_count": len(forms),
                    "forms": forms,
                    "sensitive_input_count": len(sensitive_inputs),
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
