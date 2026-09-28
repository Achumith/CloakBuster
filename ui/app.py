"""
Module 5B: Triage UI Dashboard
Interactive Streamlit Dashboard showing live side-by-side persona comparison matrix,
computed risk score, and detected cloaking & behavioral evasion mechanisms.
"""

import streamlit as st
import httpx
import asyncio
import pandas as pd

API_ENDPOINT = "http://127.0.0.1:8000/api/v1/analyze"

st.set_page_config(
    page_title="CloakBuster - Zero-Hour Phishing Detection",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ CloakBuster: Differential Probing & Cloaking Detection Engine")
st.markdown("""
**CloakBuster** detects advanced zero-hour phishing kits that employ **pre-render cloaking** and **client-side anti-analysis mechanisms**.
It simultaneously probes targets across synthetic personas to quantify response divergence and intercept stealth attacks.
""")

st.sidebar.header("🔧 Configuration & Test Target")
default_url = "http://127.0.0.1:5000/login"
target_url = st.sidebar.text_input("Target URL to Probe:", value=default_url)

st.sidebar.markdown("""
---
**Quick Test Targets:**
- `http://127.0.0.1:5000/login` *(Local Mock Cloaking Server)*
- `https://www.google.com` *(Benign Public Site)*
""")

if st.sidebar.button("🔍 Execute Multi-Persona Probe", type="primary"):
    if not target_url:
        st.error("Please enter a valid URL.")
    else:
        with st.spinner("Probing candidate target across synthetic personas..."):
            try:
                response = httpx.post(API_ENDPOINT, json={"url": target_url}, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete!")

                    # Top Metrics Banner
                    st.subheader("🎯 Threat Scoring & Risk Assessment")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    score = data["risk_score"]
                    risk_level = data["risk_level"]

                    col1.metric("Composite Risk Score", f"{score} / 100")
                    col2.metric("Threat Classification", risk_level)
                    col3.metric("Recommended Action", data["action_recommended"])
                    col4.metric("Cloaking Evasion Detected", "YES ⚠️" if data["cloaking_detected"] else "NO ✅")

                    st.markdown("---")

                    # Side-by-Side Persona Comparison Table
                    st.subheader("📊 Dual-Persona Divergence Matrix")
                    
                    p_a = data["persona_comparison"]["persona_a"]
                    p_b = data["persona_comparison"]["persona_b"]

                    matrix_data = {
                        "Parameter": [
                            "Persona Type",
                            "HTTP Status Code",
                            "DOM Size (Bytes)",
                            "Detected Form Count",
                            "Sensitive Inputs (Password/Email)"
                        ],
                        "Persona A (Naive Bot)": [
                            p_a["name"],
                            f"HTTP {p_a['status_code']}",
                            f"{p_a['dom_size_bytes']} B",
                            p_a["form_count"],
                            p_a["sensitive_input_count"]
                        ],
                        "Persona B (Emulated Desktop)": [
                            p_b["name"],
                            f"HTTP {p_b['status_code']}",
                            f"{p_b['dom_size_bytes']} B",
                            p_b["form_count"],
                            p_b["sensitive_input_count"]
                        ],
                        "Divergence Indicator": [
                            "-",
                            "⚠️ Delta S = 1 (Blocked Bot, Allowed Browser)" if data["metrics"]["delta_s"] > 0 else "Normal",
                            f"⚠️ R_DOM = {data['metrics']['r_dom']}x (Content Suppression)" if data["metrics"]["r_dom"] > 5.0 else "Normal",
                            "-",
                            f"⚠️ Delta F = {data['metrics']['delta_f']} (Hidden Credentials)" if data["metrics"]["delta_f"] > 0 else "Normal"
                        ]
                    }

                    df = pd.DataFrame(matrix_data)
                    st.table(df)

                    st.markdown("---")

                    # Behavioral Evasion Audit & Form Exfiltration
                    col_b1, col_b2 = st.columns(2)

                    with col_b1:
                        st.subheader("🚨 Behavioral Trap Audit")
                        audit = data["behavioral_audit"]
                        if audit["back_button_trap_detected"]:
                            st.error("⚠️ **Back-Button Trap Detected!** Page overrides browser back history (`pushState` / `beforeunload`).")
                            for reason in audit["trap_reasons"]:
                                st.write(f"- {reason}")
                        else:
                            st.info("✅ No back-button trap detected.")

                    with col_b2:
                        st.subheader("🌐 Form Exfiltration Audit")
                        if audit["third_party_exfiltration_detected"]:
                            st.error("⚠️ **3rd-Party Exfiltration Detected!** Credentials are being routed to external endpoints:")
                            for target in audit["exfiltration_targets"]:
                                st.code(target)
                        else:
                            st.info("✅ Form submission endpoints match domain origin.")

                    # Domain Heuristics
                    st.markdown("---")
                    st.subheader("🔍 Domain & SSL Heuristics")
                    h = data["heuristics"]
                    col_h1, col_h2, col_h3 = st.columns(3)
                    col_h1.write(f"**Canonical Domain:** `{h['hostname']}`")
                    col_h2.write(f"**Punycode / Homoglyph:** `{'Yes ⚠️' if h['punycode_info']['is_homoglyph_risk'] else 'No ✅'}`")
                    col_h3.write(f"**SSL Certificate:** `{'Valid ✅' if h['ssl_info']['ssl_valid'] else 'Invalid / HTTP ⚠️'}`")

                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to CloakBuster Inspection API (http://127.0.0.1:8000). Ensure the backend is running. Details: {e}")
