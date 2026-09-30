import asyncio
from typing import Dict, Any, List
from urllib.parse import urlparse
import tldextract
from playwright.async_api import async_playwright
from config.settings import settings

class BehavioralTrapAuditor:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.known_exfiltration_domains = [
            "api.telegram.org",
            "discord.com/api/webhooks",
            "discordapp.com/api/webhooks",
            "formspree.io",
            "formsubmit.co",
            "webhooks.site",
            "webhook.site",
            "requestbin.com",
            "pipedream.net"
        ]

    async def audit_page_behavior(self, url: str) -> Dict[str, Any]:
        """Perform Playwright interactive audit for back-button trap and form exfiltration."""
        trap_detected = False
        exfiltration_detected = False
        exfiltration_targets: List[str] = []
        trap_reason: List[str] = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = await browser.new_context(
                    user_agent=settings.USER_AGENT_DESKTOP,
                    ignore_https_errors=True
                )
                page = await context.new_page()

                # Handle and detect blocking dialog traps (alert, confirm, beforeunload)
                async def handle_dialog(dialog):
                    nonlocal trap_detected
                    trap_detected = True
                    trap_reason.append(f"Modal dialog trap detected: '{dialog.message}'")
                    try:
                        await dialog.dismiss()
                    except Exception:
                        pass

                page.on("dialog", lambda d: asyncio.create_task(handle_dialog(d)))

                # Step 1: Navigate to baseline history entry, then to Target URL
                try:
                    await page.goto("data:text/html,<html><head><title>Baseline</title></head><body>CloakBuster Navigation Baseline</body></html>", timeout=3000)
                    await page.goto(url, wait_until="domcontentloaded", timeout=int(self.timeout * 1000))
                    await page.wait_for_timeout(1000)
                except Exception:
                    pass

                # Step 2: Audit Form Actions with Registered Domain Matching (eTLD+1)
                page_ext = tldextract.extract(page.url)
                page_reg_domain = f"{page_ext.domain}.{page_ext.suffix}".lower() if page_ext.domain else ""

                forms = await page.eval_on_selector_all(
                    "form",
                    """forms => forms.map(f => {
                        const inputs = Array.from(f.querySelectorAll('input'));
                        const hasPassword = inputs.some(i => i.type === 'password');
                        const hasSensitive = inputs.some(i => {
                            const t = (i.type || '').toLowerCase();
                            const n = (i.name || '').toLowerCase();
                            const id = (i.id || '').toLowerCase();
                            return t === 'password' || t === 'email' || n.includes('user') || n.includes('login') || n.includes('pass') || n.includes('auth') || id.includes('login');
                        });
                        return {
                            action: f.action || '',
                            method: (f.method || 'get').toLowerCase(),
                            hasPassword: hasPassword,
                            hasSensitive: hasSensitive
                        };
                    })"""
                )

                oauth_and_search_domains = [
                    "google.com", "microsoft.com", "apple.com", "github.com", "facebook.com",
                    "okta.com", "auth0.com", "live.com", "algolia.com", "bing.com", "duckduckgo.com"
                ]

                for f_info in forms:
                    action_url = f_info.get("action", "")
                    method = f_info.get("method", "get")
                    has_password = f_info.get("hasPassword", False)
                    has_sensitive = f_info.get("hasSensitive", False)

                    if action_url:
                        action_lower = action_url.lower()
                        # Check known webhook exfiltration services (immediate red flag)
                        if any(known in action_lower for known in self.known_exfiltration_domains):
                            exfiltration_detected = True
                            exfiltration_targets.append(action_url)
                            continue

                        # Check cross-registered-domain submissions
                        # Must be POST (or contain password/sensitive credentials) to be flagged as exfiltration
                        action_ext = tldextract.extract(action_url)
                        action_reg_domain = f"{action_ext.domain}.{action_ext.suffix}".lower() if action_ext.domain else ""

                        if action_reg_domain and page_reg_domain and (action_reg_domain != page_reg_domain):
                            # Exclude known OAuth/SSO and benign search providers
                            if not any(oa in action_reg_domain for oa in oauth_and_search_domains):
                                # Credential exfiltration requires POST method or actual credentials in the form
                                if (method == "post" and has_sensitive) or has_password:
                                    exfiltration_detected = True
                                    exfiltration_targets.append(action_url)

                # Step 3: Script Analysis for Intentional Back-Button / PopState Trapping
                script_trap_info = await page.evaluate("""() => {
                    const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText || '').join('\\n');
                    const hasPopstatePushLoop = /onpopstate\\s*=\\s*.*pushState/is.test(scripts) ||
                                               /addEventListener\\s*\\(\\s*['"]popstate['"]\\s*,.*pushState/is.test(scripts) ||
                                               /history\\.pushState\\s*\\([^)]*\\)\\s*;.*onpopstate/is.test(scripts);
                    const hasBeforeUnloadLock = /onbeforeunload\\s*=\\s*function/i.test(scripts) ||
                                               /addEventListener\\s*\\(\\s*['"]beforeunload['"]/i.test(scripts);
                    return {
                        hasPopstatePushLoop,
                        hasBeforeUnloadLock
                    };
                }""")

                if script_trap_info.get("hasPopstatePushLoop"):
                    trap_detected = True
                    trap_reason.append("history.pushState back-button loop trap detected in page scripts")
                elif script_trap_info.get("hasBeforeUnloadLock"):
                    trap_detected = True
                    trap_reason.append("window.beforeunload navigation lock detected in page scripts")

                # Step 4: Test Back Navigation
                try:
                    await page.go_back(wait_until="domcontentloaded", timeout=4000)
                except Exception as ex:
                    if "dialog" in str(ex).lower() or "modal" in str(ex).lower():
                        trap_detected = True
                        trap_reason.append(f"Navigation dialog lock: {str(ex)}")

                await browser.close()

                return {
                    "trap_detected": trap_detected,
                    "trap_score": 1.0 if trap_detected else 0.0,
                    "trap_reasons": trap_reason,
                    "exfiltration_detected": exfiltration_detected,
                    "exfiltration_targets": exfiltration_targets,
                    "audit_success": True
                }
        except Exception as e:
            return {
                "trap_detected": False,
                "trap_score": 0.0,
                "trap_reasons": [f"Audit failed: {str(e)}"],
                "exfiltration_detected": False,
                "exfiltration_targets": [],
                "audit_success": False
            }
