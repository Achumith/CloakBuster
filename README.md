# CloakBuster: Zero-Hour Phishing Detection

**CloakBuster** is an advanced cybersecurity inspection platform designed to detect zero-hour phishing kits that employ **pre-render cloaking** and **client-side anti-analysis mechanisms** (such as serving 404s to scrapers, back-button traps, and third-party exfiltration routes).

---

## 🛠️ Modular Project Architecture

```
CloakBuster/
├── config/
│   └── settings.py              # System thresholds, weights, and scoring parameters
├── core/
│   ├── heuristics.py            # Module 1: URL Preprocessing, Punycode & WHOIS/SSL Audit
│   ├── dual_probing.py          # Module 2: Persona A (HTTP Bot) vs Persona B (Playwright Desktop)
│   ├── behavioral_trap.py       # Module 3: Back-Button History Trap & Exfiltration Auditor
│   ├── differential_engine.py   # Module 4: Response Divergence & Mathematical Risk Engine
│   ├── multi_persona.py         # Module 6: Persona C (Mobile Context Emulation)
│   └── visual_verification.py   # Module 8: Screenshots & pHash Visual Twin Classifier
├── server/
│   ├── mock_server.py           # Module 5A: Local Cloaking Target Mock Server (Port 5000)
│   └── api.py                   # FastAPI Inspection Backend Server (Port 8000)
├── ui/
│   └── app.py                   # Module 5B: Streamlit Interactive Triage Dashboard
├── extension/                   # Module 9: Real-Time Interception Chrome Extension (Manifest V3)
│   ├── manifest.json
│   ├── background.js
│   └── blocked.html
├── main.py                      # Unified Command Line Interface (CLI)
└── requirements.txt             # Python project dependencies
```

---

## 🚀 Step-by-Step Execution Guide

### 1. Installation & Environment Setup

```bash
# Navigate to the project directory
cd C:\Users\USER\.gemini\antigravity-ide\scratch\CloakBuster

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

---

### 2. Running the Local Test Harness & Demonstration (Viva Demo)

CloakBuster includes a local **Mock Cloaking Server** configured to return a `404 Not Found` to bot scrapers (Persona A) and a fake credential-harvesting login page to real browsers (Persona B).

#### Step 1: Start the Local Mock Cloaking Server (Terminal 1)
```bash
python main.py mock
# Server runs on http://127.0.0.1:5000/login
```

#### Step 2: Start the FastAPI Inspection Backend (Terminal 2)
```bash
python main.py server
# API runs on http://127.0.0.1:8000
```

#### Step 3: Launch the Streamlit Triage Dashboard (Terminal 3)
```bash
python main.py ui
# Opens interactive dashboard in browser at http://localhost:8501
```

---

### 3. Command Line Interface (CLI) Direct Analysis

You can also run a direct inspection of any URL straight from your terminal:

```bash
# Analyze the local mock cloaking target
python main.py analyze --url http://127.0.0.1:5000/login

# Analyze a public target
python main.py analyze --url https://www.google.com
```

---

## 🔬 Mathematical Risk Scoring Model

The risk score $S_{\text{risk}} \in [0, 100]$ is calculated dynamically using:

$$S_{\text{risk}} = (\Delta S \times 30) + (\min(R_{\text{DOM}}, 10) \times 3) + (\min(\Delta F, 2) \times 15) + (S_{\text{trap}} \times 20) + (S_{\text{heuristics}} \times 5) + (S_{\text{exfil}} \times 15)$$

Where:
- $\Delta S$: Status Code Divergence ($1$ if Persona A gets `404`/`403` while Persona B gets `200 OK`).
- $R_{\text{DOM}}$: DOM Volumetric Ratio ($\text{Size}(\text{DOM}_B) / \text{Size}(\text{DOM}_A)$).
- $\Delta F$: Form Element Differential (count of hidden password/email fields).
- $S_{\text{trap}}$: Back-button history trap detected ($1$ or $0$).
- $S_{\text{exfil}}$: Third-party exfiltration endpoint detected ($1$ or $0$).

---

## 🧩 Chrome Extension Installation (Module 9)

1. Open Chrome browser and navigate to `chrome://extensions/`.
2. Enable **Developer Mode** (toggle in upper right corner).
3. Click **Load unpacked**.
4. Select the directory: `C:\Users\USER\.gemini\antigravity-ide\scratch\CloakBuster\extension`.
5. Now, any main-frame web navigation with a CloakBuster risk score $\ge 70$ will automatically trigger an immediate red **Access Blocked Interstitial Page**.
