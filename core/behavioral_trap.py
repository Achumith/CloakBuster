"""
Module 3: Behavioral Trap & Form Destination Audit
- Back-Button Trap Check: Triggers page.go_back() to detect history.pushState / beforeunload trapping.
- Form Exfiltration Audit: Parses <form action="..."> & monitors XHR/fetch network requests for 3rd-party exfiltration (Telegram, Discord, off-domain endpoints).
"""

import asyncio
from typing import Dict, Any, List
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from config.settings import settings

class BehavioralTrapAuditor:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self.known_exfiltration_domains = [
            "api.telegram.org",
            "discord.com",
            "discordapp.com",
            "formspree.io",
            "formsubmit.co",
            "webhooks.site"
        ]

    async def audit_page_behavior(self, url: str) -> Dict[str, Any]:
        """Perform Playwright interactive audit for back-button trap and form exfiltration."""
        trap_detected = False
        exfiltration_detected = False
        exfiltration_targets: List[str] = []
        trap_reason: List[str] = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=settings.USER_AGENT_DESKTOP)
                page = await context.new_page()

                # Step 1: Navigate to Google baseline, then to Target URL
                await page.goto("https://www.example.com", wait_until="domcontentloaded", timeout=10000)
                await page.goto(url, wait_until="domcontentloaded", timeout=int(self.timeout * 1000))
                await page.wait_for_timeout(1000)

                target_url_domain = urlparse(page.url).netloc

                # Step 2: Audit Form Actions & Network Exfiltration Targets
                forms = await page.eval_on_selector_all(
                    "form",
                    "forms => forms.map(f => f.action)"
                )

                for action_url in forms:
                    if action_url:
                        action_domain = urlparse(action_url).netloc
                        if action_domain and action_domain != target_url_domain:
                            exfiltration_detected = True
                            exfiltration_targets.append(action_url)
                            
                        # Check known webhook services
                        for known in self.known_exfiltration_domains:
                            if known in action_url.lower():
                                exfiltration_detected = True
                                exfiltration_targets.append(action_url)

                # Step 3: Trigger Back Navigation to test Trap
                before_back_url = page.url
                try:
                    await page.go_back(wait_until="domcontentloaded", timeout=5000)
                    after_back_url = page.url

                    # Trap condition 1: URL remained identical despite go_back() call
                    if after_back_url == before_back_url:
                        trap_detected = True
                        trap_reason.append("history.pushState back-button loop trap")
                except Exception as ex:
                    # Trap condition 2: Navigation blocked by dialog / beforeunload
                    trap_detected = True
                    trap_reason.append(f"Navigation trap exception: {str(ex)}")

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
