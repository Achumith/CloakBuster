# CloakBuster Project Feasibility & Technical Feasibility Report

## Executive Summary

**Project Title:** CloakBuster: Zero-Hour Phishing Detection via Multi-Persona Differential Probing, Behavioral Anti-Evasion, and Visual Twin Verification  
**Feasibility Rating:** **10 / 10 — Highly Feasible**  
**Assessment:** This project is not only 100% technically feasible using modern open-source Python, Playwright, and Web technologies, but it is also **exceptionally well-designed**, **academically rigorous**, and addresses an active real-world security vulnerability (pre-render cloaking and client-side anti-analysis).

---

## 1. Technical Feasibility Analysis by Module

### Minor Project Scope (Semester 5/6)

| Module | Technical Objective | Implementation Mechanism | Feasibility & Tools |
| :--- | :--- | :--- | :--- |
| **Module 1: URL Pre-Processing & Heuristics** | Canonicalization, Homoglyph/Punycode detection, WHOIS age & SSL checks | Python `idna`, `tldextract`, `python-whois`, standard `ssl`/`socket` modules | **100% Feasible** (Standard libraries) |
| **Module 2: Dual-Persona Probing Engine** | Persona A (Raw HTTP request) vs. Persona B (Full Desktop Headless Browser) | Python `requests` / `httpx` + `playwright-python` (Chromium execution with JS runtime) | **100% Feasible** (Playwright natively supports header & viewport manipulation) |
| **Module 3: Behavioral Trap & Form Destination Audit** | Test `history.pushState` / `beforeunload` back-button traps; audit `<form action>` & XHR/fetch endpoints | `page.go_back()`, DOM element inspection, network request listeners (`page.on("request")`) | **100% Feasible** (Built-in Playwright APIs support network & navigation event hooking) |
| **Module 4: Differential Logic & Mathematical Scoring** | Calculate $\Delta S$, $R_{\text{DOM}}$, $\Delta F$, and compute $S_{\text{risk}} \in [0, 100]$ | Pure Python mathematical & algorithmic scoring logic | **100% Feasible** (Simple, fast mathematical evaluations) |
| **Module 5: Local Test Harness & UI Dashboard** | Mock cloaking server + interactive triage UI | Flask/FastAPI mock server + Streamlit or Vite/React dashboard | **100% Feasible** (Great for viva demonstrations) |

---

### Major Project Scope (Semester 7/8)

| Module | Technical Objective | Implementation Mechanism | Feasibility & Tools |
| :--- | :--- | :--- | :--- |
| **Module 6: Multi-Vector Persona Matrix** | Persona C (Mobile Device) & Persona D (Egress/Proxy variation) | Playwright device descriptors (`playwright.devices['iPhone 13']`) + Proxy rotation configs | **100% Feasible** (Playwright handles device emulation natively) |
| **Module 7: Advanced Anti-Analysis Evasion** | Headless fingerprint masking, CDP artifact obfuscation, `MutationObserver` tracking | `playwright-stealth` / custom CDP scripts, JavaScript evaluation inside browser context | **95% Feasible** (Cat-and-mouse game with anti-bot frameworks, but stealth packages handle standard checks) |
| **Module 8: Visual Verification via pHash** | Full-page screenshot capture & Perceptual Hashing (Hamming distance comparison) | Playwright `page.screenshot()`, Python `imagehash` (`phash()`, `dhash()`), OpenCV/PIL, vector storage | **100% Feasible** (Standard computer vision / security pattern) |
| **Module 9: Real-Time Interception Extension** | Chrome Manifest V3 extension for URL interception and warning page display | `declarativeNetRequest` / `webNavigation` APIs connecting to FastAPI REST backend | **100% Feasible** (Standard Chrome extension architecture) |

---

## 2. Infrastructure & Financial Cost Breakdown

- **Total Hardware & Software Cost:** **₹0 (100% Free / Open-Source Stack)**
- **Language & Runtime:** Python 3.11+, JavaScript (Node.js / Browser)
- **Browser Automation:** Playwright (`playwright-python`)
- **Backend & APIs:** FastAPI, Uvicorn, Celery, Redis
- **Frontend UI:** React (Vite) + Tailwind CSS OR Streamlit
- **Storage:** SQLite (Development) / PostgreSQL + Redis (Production)
- **Deployment:** Can run completely offline on a local laptop/workstation for viva & code review demonstrations.

---

## 3. Potential Challenges & Engineering Mitigation Strategies

1. **Challenge 1: Latency during Probing**
   - *Problem:* Launching Playwright browsers and navigating pages takes 3 to 8 seconds per URL.
   - *Mitigation:* Perform initial light check with Persona A. If Persona A detects suspicious redirect or status code, trigger full parallel persona execution via Python `asyncio` or Celery background tasks. Cache domain risk scores in Redis/SQLite.

2. **Challenge 2: False Positives in pHash Visual Twin Verification**
   - *Problem:* A legitimate login page might change its background hero image or layout slightly, altering the perceptual hash.
   - *Mitigation:* Combine pHash Hamming distance ($\ge 88\%$) with domain ownership verification (WHOIS / SSL Certificate issuer matching) and DOM form input structure comparison.

3. **Challenge 3: Anti-Headless Detection by Sophisticated Cloaking Kits**
   - *Problem:* Advanced phishing kits look for `navigator.webdriver`, headless user-agents, or specific WebGL renderer strings.
   - *Mitigation:* Use `playwright-stealth` or Chrome DevTools Protocol (`stealth` injection scripts) to patch navigator properties before any page scripts load.

---

## 4. Key Takeaways & Recommendations for Implementation

1. **Semester 5/6 Focus (Minor Project):**
   - Build **Modules 1 through 5**.
   - Create the local mock cloaking server first! Having a controllable mock server that returns `404` to `python-requests` (Persona A) and a fake Google/Microsoft login page to `Playwright Desktop` (Persona B) guarantees a 100% reliable, zero-risk demonstration for evaluators.

2. **Semester 7/8 Focus (Major Project):**
   - Expand into **Modules 6 through 9**.
   - Add Mobile context probing, `imagehash` visual twin database of popular targets (Google, Microsoft, PayPal, Netflix), and the Chrome Extension Manifest V3.

3. **Academic Impact:**
   - This project touches on cutting-edge research in **Cybersecurity, Automated Web Scraping, Differential Testing, and Machine Learning/Perceptual Computer Vision**. It is suitable for publishing as a research paper in IEEE / Springer conferences.

---

**Conclusion:**  
The project concept is **100% feasible**, well-scoped, and highly practical. You can begin implementation immediately.
