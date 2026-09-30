"""
Module 5B: Triage UI Dashboard - God-Level Cyber SOC Edition
Interactive Streamlit Dashboard showing live side-by-side persona comparison matrix,
hardware-rendered device mockups, perceptual visual twin classification,
and threat analysis with cybersecurity aesthetics.
"""

import streamlit as st
import httpx
import asyncio
import pandas as pd
import base64

API_ENDPOINT = "http://127.0.0.1:8000/api/v1/analyze"

st.set_page_config(
    page_title="CloakBuster // Zero-Hour Cloaking & Phishing Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# GOD-LEVEL CSS DESIGN SYSTEM (Cyberpunk / High-Tech SOC Theme)
# ==============================================================================
CUSTOM_CSS = """
<style>
/* ----------------- FONTS IMPORT ----------------- */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

/* ----------------- GLOBAL STYLES & RESET ----------------- */
html, body, p, div, span, button, input, label, h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #e2e8f0;
}

[data-testid="stSidebarCollapseButton"] span, .material-symbols-rounded {
    font-family: 'Material Symbols Rounded', sans-serif !important;
}

/* Deep Obsidian background with subtle cybernetic ambient glows */
.stApp {
    background-color: #07090e !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 45%),
        radial-gradient(at 100% 0%, rgba(168, 85, 247, 0.10) 0px, transparent 40%),
        radial-gradient(at 50% 100%, rgba(14, 165, 233, 0.08) 0px, transparent 50%),
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;
    background-size: 100% 100%, 100% 100%, 100% 100%, 48px 48px, 48px 48px !important;
    background-attachment: fixed !important;
}

/* ----------------- HEADER & CHIPS ----------------- */
.cyber-brand-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
}

.brand-title-wrap {
    display: flex;
    align-items: center;
    gap: 16px;
}

.brand-icon-shield {
    font-size: 32px;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
    border: 1px solid rgba(99, 102, 241, 0.4);
    padding: 8px 14px;
    border-radius: 14px;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
}

.brand-text h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    margin: 0 !important;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

.brand-text p {
    font-size: 13px;
    color: #94a3b8;
    margin: 2px 0 0 0;
}

.status-indicator-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 6px 14px;
    border-radius: 999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #10b981;
    font-weight: 600;
}

.status-dot-pulse {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 10px #10b981;
    animation: pulse 1.8s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* ----------------- SIDEBAR CYBER STYLING ----------------- */
[data-testid="stSidebar"] {
    background-color: rgba(10, 14, 23, 0.85) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}

[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #f1f5f9 !important;
    letter-spacing: -0.3px;
}

/* Inputs */
.stTextInput > div > div > input {
    background-color: rgba(15, 23, 42, 0.8) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    transition: all 0.25s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.4) !important;
}

/* Execute Button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #9333ea 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    width: 100% !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 28px rgba(124, 58, 237, 0.65) !important;
}

/* Secondary quick select buttons */
.stButton > button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.5) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    margin-bottom: 4px !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(99, 102, 241, 0.15) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
    color: #ffffff !important;
}

/* ----------------- THREAT SCORE HUD CARD ----------------- */
.threat-hud {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 28px;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
    display: grid;
    grid-template-columns: 240px 1fr;
    gap: 28px;
    align-items: center;
}

.score-circle-container {
    text-align: center;
    padding: 20px;
    border-radius: 16px;
    position: relative;
}

.score-circle-critical {
    background: radial-gradient(circle, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.02) 70%);
    border: 2px solid rgba(239, 68, 68, 0.4);
    box-shadow: 0 0 35px rgba(239, 68, 68, 0.25);
}

.score-circle-warning {
    background: radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.02) 70%);
    border: 2px solid rgba(245, 158, 11, 0.4);
    box-shadow: 0 0 35px rgba(245, 158, 11, 0.25);
}

.score-circle-safe {
    background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.02) 70%);
    border: 2px solid rgba(16, 185, 129, 0.4);
    box-shadow: 0 0 35px rgba(16, 185, 129, 0.25);
}

.score-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 54px;
    font-weight: 800;
    line-height: 1;
    margin: 0;
}

.score-critical { color: #f87171; text-shadow: 0 0 20px rgba(239, 68, 68, 0.6); }
.score-warning { color: #fbbf24; text-shadow: 0 0 20px rgba(245, 158, 11, 0.6); }
.score-safe { color: #34d399; text-shadow: 0 0 20px rgba(16, 185, 129, 0.6); }

.score-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #94a3b8;
    margin-top: 6px;
    font-weight: 600;
}

.hud-details {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.hud-stat-box {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 16px;
    transition: all 0.2s ease;
}

.hud-stat-box:hover {
    border-color: rgba(99, 102, 241, 0.3);
    background: rgba(30, 41, 59, 0.6);
}

.hud-stat-title {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    margin-bottom: 6px;
}

.hud-stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #f1f5f9;
}

/* ----------------- HARDWARE MOCKUP WINDOW FRAMES ----------------- */
/* Persona B macOS Window Mockup */
.browser-window {
    background: #0f172a;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    margin-bottom: 24px;
}

.browser-header-bar {
    background: #1e293b;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.traffic-dots {
    display: flex;
    gap: 6px;
}

.t-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.t-red { background: #ef4444; }
.t-yellow { background: #f59e0b; }
.t-green { background: #10b981; }

.browser-omnibox {
    flex-grow: 1;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 5px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #94a3b8;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.browser-pill-badge {
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 6px;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #a5b4fc;
    font-family: 'JetBrains Mono', monospace;
}

/* Persona A Hacker Terminal Frame */
.terminal-window {
    background: #080d1a;
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    margin-bottom: 24px;
}

.terminal-header-bar {
    background: #0d1527;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(56, 189, 248, 0.15);
}

.terminal-title-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    color: #38bdf8;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Persona C iPhone Mobile Frame */
.mobile-chassis {
    width: 340px;
    margin: 0 auto;
    background: #111827;
    border: 4px solid #374151;
    border-radius: 44px;
    padding: 10px;
    box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8), inset 0 0 10px rgba(0,0,0,0.5);
    position: relative;
}

.mobile-dynamic-island {
    width: 100px;
    height: 24px;
    background: #000;
    border-radius: 20px;
    margin: 4px auto 10px auto;
}

/* ----------------- DIVERGENCE CALLOUT BANNER ----------------- */
.divergence-alert-card {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(185, 28, 28, 0.05) 100%);
    border: 1px solid rgba(239, 68, 68, 0.4);
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 28px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
    box-shadow: 0 10px 25px rgba(239, 68, 68, 0.15);
}

.divergence-parity-card {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%);
    border: 1px solid rgba(16, 185, 129, 0.4);
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 28px;
    display: flex;
    align-items: flex-start;
    gap: 16px;
    box-shadow: 0 10px 25px rgba(16, 185, 129, 0.15);
}

/* ----------------- TABLES & EXPANDERS ----------------- */
div[data-testid="stTable"] {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    overflow: hidden;
}

div[data-testid="stTable"] table {
    color: #e2e8f0 !important;
    font-size: 13px !important;
}

div[data-testid="stExpander"] {
    background: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# HERO BRAND BANNER (SOC HEADER)
# ==============================================================================
st.markdown("""
<div class="cyber-brand-bar">
    <div class="brand-title-wrap">
        <div class="brand-icon-shield">🛡️</div>
        <div class="brand-text">
            <h1>CLOAKBUSTER // ZERO-HOUR THREAT RADAR</h1>
            <p>Multi-Persona Differential Probing & Client-Side Anti-Evasion Engine</p>
        </div>
    </div>
    <div class="status-indicator-pill">
        <div class="status-dot-pulse"></div>
        LIVE INSPECTION PIPELINE
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# INTERACTIVE SIDEBAR CONTROLS
# ==============================================================================
st.sidebar.markdown("### 🎛️ Inspection Console")

# Quick Target Preset Helpers
if "target_url_state" not in st.session_state:
    st.session_state["target_url_state"] = "http://127.0.0.1:5000/login"

def set_target(url_val):
    st.session_state["target_url_state"] = url_val

target_url = st.sidebar.text_input(
    "Target URL to Probe:",
    value=st.session_state["target_url_state"],
    placeholder="https://domain.com/login"
)

include_mobile = st.sidebar.checkbox("📱 Emulate Mobile Persona C (iPhone 13)", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚡ Quick Target Presets")

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("🎭 Mock Target", key="preset_mock"):
        set_target("http://127.0.0.1:5000/login")
        st.rerun()
    if st.button("🌐 Google", key="preset_google"):
        set_target("https://www.google.com")
        st.rerun()
with col_btn2:
    if st.button("📚 Wikipedia", key="preset_wiki"):
        set_target("https://www.wikipedia.org")
        st.rerun()
    if st.button("💻 GitHub", key="preset_github"):
        set_target("https://github.com")
        st.rerun()

st.sidebar.markdown("""
---
<div style="font-size: 11px; color: #64748b; line-height: 1.6;">
<b>ENGINE SPECIFICATIONS:</b><br>
• Playwright Chromium v124<br>
• Dual Probing Pipeline v2.4<br>
• Perceptual Visual Hashing (pHash)<br>
• Anti-Exit Trap Interceptor
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# EXECUTION & AUDIT PIPELINE
# ==============================================================================
execute_probe = st.sidebar.button("⚡ EXECUTE MULTI-PERSONA PROBE", type="primary")

if execute_probe:
    if not target_url:
        st.error("Please enter a valid target URL.")
    else:
        with st.spinner("⚡ Initializing Playwright browser engines & executing multi-persona probe..."):
            try:
                response = httpx.post(
                    API_ENDPOINT,
                    json={"url": target_url, "include_mobile": include_mobile},
                    timeout=45.0
                )
                if response.status_code == 200:
                    data = response.json()

                    score = data["risk_score"]
                    risk_level = data["risk_level"]
                    cloaking_detected = data["cloaking_detected"]
                    action = data["action_recommended"]

                    # ---------------------------------------------------------
                    # THREAT RADAR HUD BANNER
                    # ---------------------------------------------------------
                    if score >= 70:
                        circle_class = "score-circle-critical"
                        num_class = "score-critical"
                        badge_bg = "#ef4444"
                    elif score >= 40:
                        circle_class = "score-circle-warning"
                        num_class = "score-warning"
                        badge_bg = "#f59e0b"
                    else:
                        circle_class = "score-circle-safe"
                        num_class = "score-safe"
                        badge_bg = "#10b981"

                    st.markdown(f"""
                    <div class="threat-hud">
                        <div class="score-circle-container {circle_class}">
                            <div class="score-number {num_class}">{score}</div>
                            <div class="score-label">Composite Risk / 100</div>
                        </div>
                        <div class="hud-details">
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Threat Classification</div>
                                <div class="hud-stat-value" style="color: {badge_bg};">{risk_level}</div>
                            </div>
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Cloaking Evasion</div>
                                <div class="hud-stat-value">{'🚨 DETECTED' if cloaking_detected else ('🛡️ WAF SHIELD' if data.get('waf_detected') else '✅ CLEAN')}</div>
                            </div>
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Recommended Action</div>
                                <div class="hud-stat-value" style="font-size: 14px;">{action}</div>
                            </div>
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Target Hostname</div>
                                <div class="hud-stat-value" style="font-family: 'JetBrains Mono', monospace; font-size: 13px;">{data['heuristics']['hostname']}</div>
                            </div>
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">DOM Volumetric Ratio</div>
                                <div class="hud-stat-value">{data['metrics']['r_dom']}x ({'Penalty' if data['metrics'].get('r_dom_penalty', 0) > 0 else 'Benign'})</div>
                            </div>
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Status Divergence (ΔS)</div>
                                <div class="hud-stat-value">{'🛡️ WAF Filter' if data.get('waf_detected') else ('🚨 Blocked Bot' if data['metrics']['delta_s'] > 0 else '✅ Parity')}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ---------------------------------------------------------
                    # HARDWARE-MOCKED VISUAL SCREENSHOT COMPARISON SHOWCASE
                    # ---------------------------------------------------------
                    st.markdown("### 📸 Hardware-Mocked Visual Persona Comparison")
                    st.markdown(
                        "<p style='color: #94a3b8; font-size: 14px; margin-bottom: 20px;'>"
                        "Live comparison rendering what <b>automated crawlers / bot scrapers</b> see "
                        "versus what <b>real desktop human visitors</b> see."
                        "</p>",
                        unsafe_allow_html=True
                    )

                    p_a = data["persona_comparison"]["persona_a"]
                    p_b = data["persona_comparison"]["persona_b"]
                    b64_a = p_a.get("screenshot_base64")
                    b64_b = p_b.get("screenshot_base64")

                    # Divergence Banner & Assessment
                    waf_active = data.get("waf_detected", False)
                    is_visual_cloaked = cloaking_detected

                    if is_visual_cloaked:
                        st.markdown("""
                        <div class="divergence-alert-card">
                            <div style="font-size: 28px;">🚨</div>
                            <div>
                                <h4 style="margin: 0 0 4px 0; color: #f87171;">VISUAL PRE-RENDER CLOAKING CONFIRMED</h4>
                                <p style="margin: 0; font-size: 13px; color: #fca5a5; line-height: 1.5;">
                                    The remote server selectively manipulated content: Automated scrapers were served a suppressed or decoy response,
                                    while real human browsers were exposed to an active interactive credential harvest interface.
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif waf_active:
                        st.markdown("""
                        <div class="divergence-parity-card" style="border: 1px solid rgba(99, 102, 241, 0.4); background: rgba(99, 102, 241, 0.08);">
                            <div style="font-size: 28px;">🛡️</div>
                            <div>
                                <h4 style="margin: 0 0 4px 0; color: #a5b4fc;">STANDARD ANTI-SCRAPING WAF ACTIVE</h4>
                                <p style="margin: 0; font-size: 13px; color: #c7d2fe; line-height: 1.5;">
                                    The remote server filtered automated scrapers with anti-bot rate limiting (HTTP 403/429).
                                    However, no deceptive phishing or credential concealment indicators were observed in the browser render.
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="divergence-parity-card">
                            <div style="font-size: 28px;">✅</div>
                            <div>
                                <h4 style="margin: 0 0 4px 0; color: #34d399;">VISUAL PARITY CONFIRMED</h4>
                                <p style="margin: 0; font-size: 13px; color: #a7f3d0; line-height: 1.5;">
                                    Both automated bot crawlers and interactive desktop browsers observed non-divergent, consistent interface states.
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    col_vis_a, col_vis_b = st.columns(2)

                    with col_vis_a:
                        status_color = "#ef4444" if p_a["status_code"] in [403, 404, 500, 0] else "#10b981"
                        st.markdown(f"""
                        <div class="terminal-window">
                            <div class="terminal-header-bar">
                                <div class="terminal-title-text">
                                    <span>🤖</span> PERSONA A // BOT SCRAPER CONSOLE
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <span class="browser-pill-badge" style="color: {status_color}; border-color: {status_color};">HTTP {p_a['status_code']}</span>
                                    <span class="browser-pill-badge">{p_a['dom_size_bytes']} B</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if b64_a:
                            img_a = base64.b64decode(b64_a)
                            st.image(img_a, caption="Automated Scraper Render (User-Agent: CloakBuster-Bot-Probe)", use_container_width=True)
                            st.download_button(
                                "💾 Download Persona A Screenshot",
                                data=img_a,
                                file_name="persona_a_bot_view.png",
                                mime="image/png"
                            )
                        else:
                            st.warning("No screenshot available for Persona A.")

                    with col_vis_b:
                        status_b_color = "#10b981" if p_b["status_code"] == 200 else "#ef4444"
                        st.markdown(f"""
                        <div class="browser-window">
                            <div class="browser-header-bar">
                                <div class="traffic-dots">
                                    <div class="t-dot t-red"></div>
                                    <div class="t-dot t-yellow"></div>
                                    <div class="t-dot t-green"></div>
                                </div>
                                <div class="browser-omnibox">
                                    <span>🔒</span>
                                    <span>{data['url']}</span>
                                </div>
                                <span class="browser-pill-badge" style="color: {status_b_color}; border-color: {status_b_color};">HTTP {p_b['status_code']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if b64_b:
                            img_b = base64.b64decode(b64_b)
                            st.image(img_b, caption=f"Playwright Chromium Desktop Render (1280x800 • Forms: {p_b['form_count']})", use_container_width=True)
                            st.download_button(
                                "💾 Download Persona B Screenshot",
                                data=img_b,
                                file_name="persona_b_desktop_view.png",
                                mime="image/png"
                            )
                        else:
                            st.warning("No screenshot available for Persona B.")

                    # ---------------------------------------------------------
                    # PERSONA C (MOBILE DEVICE VIEW)
                    # ---------------------------------------------------------
                    if "persona_c" in data["persona_comparison"] and data["persona_comparison"]["persona_c"]:
                        p_c = data["persona_comparison"]["persona_c"]
                        b64_c = p_c.get("screenshot_base64")
                        st.markdown("---")
                        st.markdown("### 📱 Persona C (Mobile Touch Viewport - iPhone 13 Emulation)")
                        
                        col_mob_left, col_mob_right = st.columns([1, 2])
                        with col_mob_left:
                            if b64_c:
                                img_c = base64.b64decode(b64_c)
                                st.markdown("""
                                <div class="mobile-chassis">
                                    <div class="mobile-dynamic-island"></div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.image(img_c, caption="iPhone 13 (390x844 Touch Viewport)", width=320)
                                st.download_button(
                                    "💾 Download Mobile Screenshot",
                                    data=img_c,
                                    file_name="persona_c_mobile.png",
                                    mime="image/png"
                                )
                        with col_mob_right:
                            st.markdown(f"""
                            <div class="hud-stat-box" style="margin-top: 20px;">
                                <div class="hud-stat-title">Mobile Context Telemetry</div>
                                <p style="font-size: 13px; color: #cbd5e1; line-height: 1.6;">
                                    <b>HTTP Status:</b> HTTP {p_c['status_code']}<br>
                                    <b>DOM Size:</b> {p_c['dom_size_bytes']} Bytes<br>
                                    <b>Interactive Input Count:</b> {p_c.get('input_count', 0)} inputs<br>
                                    <b>Touch Emulation:</b> Enabled (WebKit / iOS Safari)
                                </p>
                                <p style="font-size: 12px; color: #94a3b8;">
                                    Mobile context probing verifies whether cloaking rules inspect navigator touch headers, screen dimensions, or accelerometer hooks to selectively serve mobile phishing kits.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                    # ---------------------------------------------------------
                    # VISUAL TWIN & pHash BRAND CLASSIFIER (MODULE 8)
                    # ---------------------------------------------------------
                    if "visual_verification" in data and data["visual_verification"]:
                        v_ver = data["visual_verification"]
                        st.markdown("---")
                        st.markdown("### 👁️ Module 8: Perceptual Hashing (pHash) & Visual Twin Audit")

                        phash_val = v_ver.get("phash_computed") or "N/A"
                        matched_brand = v_ver.get("matched_brand") or "None (Original Layout Signature)"
                        is_twin = v_ver.get("is_visual_impersonation", False)

                        c_v1, c_v2, c_v3 = st.columns(3)
                        with c_v1:
                            st.markdown(f"""
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Computed Perceptual Hash (pHash)</div>
                                <div style="font-family: 'JetBrains Mono', monospace; font-size: 15px; color: #818cf8; word-break: break-all;">
                                    <code>{phash_val}</code>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        with c_v2:
                            st.markdown(f"""
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Visual Impersonation Match</div>
                                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 700; color: {'#ef4444' if is_twin else '#10b981'};">
                                    {'⚠️ YES (MATCH DETECTED)' if is_twin else '✅ NO (UNIQUE LAYOUT)'}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        with c_v3:
                            st.markdown(f"""
                            <div class="hud-stat-box">
                                <div class="hud-stat-title">Target Brand Vector</div>
                                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 700; color: #f1f5f9;">
                                    {matched_brand}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        if is_twin:
                            st.error(f"🚨 **CRITICAL BRAND SPOOFING DETECTED:** {v_ver.get('alert')}")

                    # ---------------------------------------------------------
                    # DUAL-PERSONA DIVERGENCE MATRIX
                    # ---------------------------------------------------------
                    st.markdown("---")
                    st.markdown("### 📊 Dual-Persona Divergence Telemetry Matrix")

                    matrix_data = {
                        "Inspection Parameter": [
                            "Persona Type",
                            "HTTP Status Code",
                            "DOM Size (Bytes)",
                            "Detected Form Count",
                            "Sensitive Inputs (Password/Auth)"
                        ],
                        "Persona A (Naive Bot)": [
                            str(p_a["name"]),
                            f"HTTP {p_a['status_code']}",
                            f"{p_a['dom_size_bytes']} B",
                            str(p_a["form_count"]),
                            str(p_a["sensitive_input_count"])
                        ],
                        "Persona B (Emulated Desktop)": [
                            str(p_b["name"]),
                            f"HTTP {p_b['status_code']}",
                            f"{p_b['dom_size_bytes']} B",
                            str(p_b["form_count"]),
                            str(p_b["sensitive_input_count"])
                        ],
                        "Divergence Differential": [
                            "-",
                            "⚠️ Delta S = 1 (Bot Blocked, Browser Allowed)" if data["metrics"]["delta_s"] > 0 else "Normal (Parity)",
                            f"⚠️ R_DOM = {data['metrics']['r_dom']}x (Suppression)" if data["metrics"]["r_dom"] > 5.0 else "Normal (Parity)",
                            "-",
                            f"⚠️ Delta F = {data['metrics']['delta_f']} (Hidden Auth Fields)" if data["metrics"]["delta_f"] > 0 else "Normal"
                        ]
                    }

                    df = pd.DataFrame(matrix_data)
                    st.table(df)

                    # ---------------------------------------------------------
                    # BEHAVIORAL EVASION & EXFILTRATION AUDIT
                    # ---------------------------------------------------------
                    st.markdown("---")
                    col_b1, col_b2 = st.columns(2)

                    with col_b1:
                        st.markdown("### 🚨 Behavioral Trap Audit")
                        audit = data["behavioral_audit"]
                        if audit["back_button_trap_detected"]:
                            st.error("⚠️ **Back-Button Trap Detected!** Page intercepts navigation (`history.pushState` / `beforeunload`).")
                            for reason in audit["trap_reasons"]:
                                st.write(f"- {reason}")
                        else:
                            st.info("✅ No back-button history trap detected.")

                    with col_b2:
                        st.markdown("### 🌐 Form Exfiltration Audit")
                        if audit["third_party_exfiltration_detected"]:
                            st.error("⚠️ **3rd-Party Exfiltration Detected!** Credential submissions routed off-domain:")
                            for target in audit["exfiltration_targets"]:
                                st.code(target)
                        else:
                            st.info("✅ All form submissions match origin domain.")

                    # ---------------------------------------------------------
                    # DOMAIN & SSL HEURISTICS
                    # ---------------------------------------------------------
                    st.markdown("---")
                    st.markdown("### 🔍 Domain & SSL Cryptographic Heuristics")
                    h = data["heuristics"]
                    col_h1, col_h2, col_h3 = st.columns(3)
                    col_h1.markdown(f"**Canonical Domain:** `{h['hostname']}`")
                    col_h2.markdown(f"**Punycode / Homoglyph:** `{'Yes ⚠️ (Spoof Risk)' if h['punycode_info']['is_homoglyph_risk'] else 'No ✅ (Clean)'}`")
                    col_h3.markdown(f"**SSL Certificate:** `{'Valid ✅' if h['ssl_info']['ssl_valid'] else 'Invalid / HTTP ⚠️'}`")

                else:
                    st.error(f"Inspection Engine Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to communicate with CloakBuster API (http://127.0.0.1:8000). Error: {e}")
