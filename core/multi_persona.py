"""
Module 6: Multi-Vector Persona Matrix
- Persona C (Mobile Device): Touch events, mobile viewport (390x844), mobile UA.
- Persona D (Egress / Network variations): Egress configuration variations.
"""

from typing import Dict, Any
from playwright.async_api import async_playwright
from config.settings import settings

class MultiPersonaEngine:
    async def probe_persona_c_mobile(self, url: str) -> Dict[str, Any]:
        """Persona C: Mobile context probe (iPhone 13 viewport & touch emulation)."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=settings.USER_AGENT_MOBILE,
                    viewport={"width": 390, "height": 844},
                    has_touch=True,
                    is_mobile=True
                )
                page = await context.new_page()

                response = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                status_code = response.status if response else 0
                await page.wait_for_timeout(1500)

                dom_text = await page.content()
                
                inputs = await page.eval_on_selector_all("input", "inputs => inputs.map(i => i.type)")
                
                screenshot_bytes = await page.screenshot(type="png", full_page=False)

                await browser.close()

                return {
                    "persona": "Persona C (Mobile Device - iPhone 13)",
                    "status_code": status_code,
                    "dom_size": len(dom_text),
                    "input_count": len(inputs),
                    "screenshot_bytes": screenshot_bytes,
                    "success": True,
                    "error": None
                }
        except Exception as e:
            return {
                "persona": "Persona C (Mobile Device - iPhone 13)",
                "status_code": 0,
                "dom_size": 0,
                "input_count": 0,
                "screenshot_bytes": None,
                "success": False,
                "error": str(e)
            }
