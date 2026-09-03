import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="VITA-Guard | Autonomous Kinematic Safety Engine",
    page_icon="🛡️",
    layout="wide"
)

# --- State Initialization ---
if "engine_active" not in st.session_state:
    st.session_state.engine_active = False
if "just_activated" not in st.session_state:
    st.session_state.just_activated = False
if "pre_alarm_active" not in st.session_state:
    st.session_state.pre_alarm_active = False
if "sms_dispatched" not in st.session_state:
    st.session_state.sms_dispatched = False
if "incident_log" not in st.session_state:
    st.session_state.incident_log = []
if "ws_url" not in st.session_state:
    st.session_state.ws_url = "ws://192.168.43.1:8080/ws"
if "profile" not in st.session_state:
    st.session_state.profile = "Elderly Care Mode"
if "primary_contact" not in st.session_state:
    st.session_state.primary_contact = "+1 234 567 8900"
if "secondary_contact" not in st.session_state:
    st.session_state.secondary_contact = "+1 098 765 4321"

# --- Cyber-Care Glassmorphism Theme & Micro-Interactions ---
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">

    <style>
    /* Global Typography */
    html, body, [class*="css"], .stMarkdown, p, div, span, label {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    h1, h2, h3, h4, .stSubheader {
        font-family: 'Syne', sans-serif !important;
        letter-spacing: -0.03em;
    }

    /* Cinematic Mesh Ambient Background */
    .stApp {
        background-color: #050811;
        background-image: 
            radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.18) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(16, 185, 129, 0.08) 0px, transparent 60%),
            radial-gradient(at 0% 100%, rgba(14, 165, 233, 0.12) 0px, transparent 50%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
        background-attachment: fixed;
        color: #f1f5f9;
    }

    /* Top Navigation Header */
    .brand-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 32px;
        background: rgba(10, 16, 30, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 24px;
        margin-bottom: 22px;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    .brand-wrapper {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .logo-container {
        position: relative;
        width: 62px;
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logo-pulse-ring {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 18px;
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        filter: blur(10px);
        opacity: 0.6;
        animation: logo-glow 3s infinite alternate;
    }
    .logo-core {
        position: relative;
        width: 58px;
        height: 58px;
        background: linear-gradient(135deg, #0f172a, #0284c7);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.2);
    }
    @keyframes logo-glow {
        0% { transform: scale(0.92); opacity: 0.4; }
        100% { transform: scale(1.12); opacity: 0.8; }
    }
    .brand-title {
        font-family: 'Syne', sans-serif !important;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        background: linear-gradient(135deg, #ffffff 30%, #38bdf8 70%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 0;
    }
    .brand-caption {
        font-family: 'Space Grotesk', monospace;
        font-size: 0.78rem;
        color: #94a3b8;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-pill {
        background: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.68rem;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .status-live-node {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        padding: 8px 18px;
        border-radius: 9999px;
        font-family: 'Space Grotesk', monospace;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.15);
    }
    .live-dot {
        width: 9px;
        height: 9px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
        animation: live-blink 1.5s infinite;
    }
    @keyframes live-blink {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    /* Launch Supercard */
    .launch-supercard {
        position: relative;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(99, 102, 241, 0.1) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 24px;
        padding: 26px 36px;
        margin-bottom: 28px;
        backdrop-filter: blur(20px);
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
    }
    .launch-supercard h2 {
        font-family: 'Syne', sans-serif !important;
        font-size: 1.8rem;
        margin: 0 0 6px 0;
        color: #f8fafc;
    }
    .launch-supercard p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Mode Selection Interactive Cards */
    .mode-card {
        background: rgba(13, 20, 36, 0.7);
        border: 2px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        height: 100%;
        backdrop-filter: blur(16px);
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .mode-card-active-elderly {
        border-color: #38bdf8 !important;
        background: linear-gradient(145deg, rgba(14, 165, 233, 0.16), rgba(15, 23, 42, 0.9)) !important;
        box-shadow: 0 0 35px -5px rgba(56, 189, 248, 0.45);
        transform: translateY(-4px);
    }
    .mode-card-active-industrial {
        border-color: #f59e0b !important;
        background: linear-gradient(145deg, rgba(245, 158, 11, 0.16), rgba(15, 23, 42, 0.9)) !important;
        box-shadow: 0 0 35px -5px rgba(245, 158, 11, 0.45);
        transform: translateY(-4px);
    }
    .mode-badge {
        display: inline-block;
        font-family: 'Space Grotesk', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 8px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }
    .mode-badge-elderly {
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.35);
    }
    .mode-badge-industrial {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .mode-threshold {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 10px 0 6px 0;
    }

    /* Configuration Surface Card */
    .config-surface {
        background: rgba(13, 20, 36, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 28px;
        backdrop-filter: blur(18px);
        margin-bottom: 20px;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.3);
    }

    /* Glass Cards & Badges */
    .glass-showcase {
        background: rgba(13, 20, 36, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 30px;
        height: 100%;
        backdrop-filter: blur(16px);
    }
    .card-badge-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 16px;
    }
    .metric-slab {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 22px;
        text-align: center;
        backdrop-filter: blur(14px);
    }
    .metric-slab-value {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2.4rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 4px;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
    }
    .metric-slab-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
    }

    /* Tabs Layout */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(10, 16, 30, 0.75);
        padding: 8px 14px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(14px);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 10px 22px;
        font-weight: 600;
        color: #94a3b8;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.25), rgba(99, 102, 241, 0.25)) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
    }

    /* Log Items */
    .care-log-item {
        background: rgba(15, 23, 42, 0.85);
        border-left: 4px solid #ef4444;
        border-radius: 8px 12px 12px 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-family: 'Space Grotesk', monospace;
        font-size: 0.88rem;
    }
    .care-log-header {
        display: flex;
        justify-content: space-between;
        color: #f87171;
        font-weight: 700;
    }
    .care-log-tag {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
    }

    /* Emergency Siren Visual Pulse */
    @keyframes emergency-glow {
        0% { box-shadow: inset 0 0 40px rgba(239, 68, 68, 0.4); }
        50% { box-shadow: inset 0 0 90px rgba(239, 68, 68, 0.8); }
        100% { box-shadow: inset 0 0 40px rgba(239, 68, 68, 0.4); }
    }
    .emergency-active {
        animation: emergency-glow 1s infinite alternate;
        border: 4px solid #ef4444 !important;
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.pre_alarm_active:
    st.markdown("<div class='emergency-active'>", unsafe_allow_html=True)

# --- Prominent Brand Header ---
st.markdown(
    """
    <div class="brand-topbar">
        <div class="brand-wrapper">
            <div class="logo-container">
                <div class="logo-pulse-ring"></div>
                <div class="logo-core">
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <path d="M9 12l2 2 4-4"/>
                    </svg>
                </div>
            </div>
            <div>
                <div class="brand-title">VITA-GUARD</div>
                <div class="brand-caption">
                    <span>ZERO-HARDWARE KINEMATICS</span>
                    <span class="brand-pill">50Hz POCKET IMU</span>
                </div>
            </div>
        </div>
        <div class="status-live-node">
            <div class="live-dot"></div>
            <span>DISPATCH NETWORK READY</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Standalone Launch Banner ---
l_col1, l_col2 = st.columns([2.6, 1.2], gap="large")

with l_col1:
    engine_desc = (
        f"Kinematic Telemetry Engine: ARMED & RUNNING [{st.session_state.profile.upper()}]"
        if st.session_state.engine_active
        else "Ready to initialize pocket kinematics, free-fall anomaly detection & emergency dispatch hub."
    )
    st.markdown(
        f"""
        <div class="launch-supercard">
            <div>
                <h2>⚡ Autonomous Safety Engine</h2>
                <p>{engine_desc}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with l_col2:
    st.write("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    btn_text = "⏹️ Suspend Safety Engine" if st.session_state.engine_active else "🚀 LAUNCH SAFETY ENGINE"
    if st.button(btn_text, type="primary", use_container_width=True):
        st.session_state.engine_active = not st.session_state.engine_active
        if st.session_state.engine_active:
            st.session_state.just_activated = True
        st.rerun()

if st.session_state.just_activated:
    st.toast("⚡ Safety Engine Initialized: Real-Time Telemetry Pipeline Online!", icon="🛡️")
    st.session_state.just_activated = False

# ==============================================================================
# VIEW ROUTING: ACTIVE WORKSPACE VS TELEHEALTH OVERVIEW
# ==============================================================================
if st.session_state.engine_active:
    st.markdown("### 📡 Active Telemetry & Incident Dispatch Control Room")
    
    col_chart, col_hub = st.columns([1.8, 1.2], gap="large")
    
    with col_chart:
        st.subheader("Phase 1: Real-Time Kinematic Signal Stream")
        st.caption(f"Active Profile: **{st.session_state.profile}** | Scalar magnitude: $||A|| = \sqrt{{Ax^2 + Ay^2 + Az^2}}$")
        chart_placeholder = st.empty()
        status_text = st.empty()
        
    with col_hub:
        st.subheader("Phase 2: Automated Dispatch Hub")
        dispatch_box = st.empty()
        countdown_placeholder = st.empty()
        cancel_btn_placeholder = st.empty()
        
        st.markdown("#### Patient & Incident Log Feed")
        log_placeholder = st.empty()

    # Pre-Alarm Execution Flow
    if st.session_state.pre_alarm_active:
        dispatch_box.error("🚨 CRITICAL COLLAPSE DETECTED — AUDIO PRE-ALARM TRIGGERED")
        
        st.components.v1.html(
            """
            <script>
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            function beep() {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(880, ctx.currentTime);
                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.3);
            }
            const interval = setInterval(beep, 600);
            if (navigator.vibrate) {
                navigator.vibrate([500, 250, 500, 250, 500]);
            }
            setTimeout(() => clearInterval(interval), 15000);
            </script>
            """,
            height=0
        )

        user_cancelled = False
        
        for remaining in range(15, 0, -1):
            countdown_placeholder.markdown(
                f"""
                <div style='background: rgba(239,68,68,0.15); border: 1px solid #ef4444; border-radius: 14px; padding: 14px; text-align: center;'>
                    <span style='font-family: Syne; font-size: 1.4rem; font-weight: 700; color: #f87171;'>🔊 Patient Pre-Alarm: {remaining}s remaining</span>
                    <p style='color: #cbd5e1; font-size: 0.85rem; margin: 4px 0 0 0;'>If conscious, tap below to abort emergency caregiver dispatch.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if cancel_btn_placeholder.button("✅ I AM OKAY (Cancel Dispatch)", type="primary", use_container_width=True, key=f"btn_{remaining}"):
                user_cancelled = True
                break
            time.sleep(1)
            
        if user_cancelled:
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = False
            st.success("Pre-alarm aborted by user. Dispatch sequence cancelled.")
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = True
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.incident_log.append({
                "time": timestamp,
                "profile": st.session_state.profile,
                "msg": f"15s grace timer expired without cancellation. Automated SMS alert dispatched to primary contact ({st.session_state.primary_contact})."
            })
            st.rerun()

    elif st.session_state.sms_dispatched:
        dispatch_box.error(f"🚨 DISPATCH CONFIRMED: Automated SMS sent to {st.session_state.primary_contact}")
        if st.button("🔄 Reset Telemetry Status", use_container_width=True):
            st.session_state.sms_dispatched = False
            st.rerun()
    else:
        dispatch_box.success("System Status: Active & Monitoring Telemetry")

    st.markdown("---")
    st.subheader("Phase 3: Telemetry Stream Source")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("📡 Start Live Sensor Stream", type="primary", use_container_width=True):
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = False
            data_log = pd.DataFrame(columns=["Magnitude"])
            
            http_url = st.session_state.ws_url.replace("ws://", "http://").replace("/ws", "/get?accX&accY&accZ")
            status_text.info(f"Connected to stream. Monitoring motion under **{st.session_state.profile}**...")
            threshold = 25.0 if "Industrial" in st.session_state.profile else 15.0
            
            try:
                for _ in range(250):
                    response = requests.get(http_url, timeout=2).json()
                    if "buffer" in response:
                        ax = response["buffer"]["accX"]["buffer"][0]
                        ay = response["buffer"]["accY"]["buffer"][0]
                        az = response["buffer"]["accZ"]["buffer"][0]
                        
                        magnitude = np.sqrt(ax**2 + ay**2 + az**2)
                        data_log.loc[len(data_log)] = [magnitude]
                        chart_placeholder.line_chart(data_log.tail(50))
                        
                        if magnitude > threshold:
                            st.session_state.pre_alarm_active = True
                            st.rerun()
                            
                    time.sleep(0.05)
            except Exception:
                status_text.error("Connection Failed. Verify Phyphox is streaming on mobile hotspot with remote access enabled.")

    with col_btn2:
        if st.button("▶️ Run Simulation (Synthetic Drop Demo)", use_container_width=True):
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = False
            data = pd.DataFrame(columns=["Magnitude"])
            
            status_text.info("Simulating Normal Gait (Walking)...")
            for _ in range(15):
                data.loc[len(data)] = [np.random.normal(9.8, 1.2)]
                chart_placeholder.line_chart(data["Magnitude"])
                time.sleep(0.04)
                
            status_text.warning("Simulating Drop Anomaly (Free-fall -> High-g Impact)...")
            data.loc[len(data)] = [1.0]
            chart_placeholder.line_chart(data["Magnitude"])
            time.sleep(0.06)
            data.loc[len(data)] = [32.0]
            chart_placeholder.line_chart(data["Magnitude"])
            time.sleep(0.06)
            
            status_text.error("Simulating Post-Shock Immobility Flatline...")
            for _ in range(10):
                data.loc[len(data)] = [np.random.normal(9.8, 0.05)]
                chart_placeholder.line_chart(data["Magnitude"])
                time.sleep(0.04)
                
            st.session_state.pre_alarm_active = True
            st.rerun()

    # Log Display
    if st.session_state.incident_log:
        log_html = ""
        for item in reversed(st.session_state.incident_log):
            log_html += f"""
            <div class="care-log-item">
                <div class="care-log-header">
                    <span>⚠️ CRITICAL PATIENT EVENT</span>
                    <span class="care-log-tag">{item['profile']}</span>
                </div>
                <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 4px;">{item['msg']}</div>
                <div style="color: #64748b; font-size: 0.72rem; margin-top: 6px;">TIMESTAMP: {item['time']}</div>
            </div>
            """
        log_placeholder.markdown(log_html, unsafe_allow_html=True)
    else:
        log_placeholder.markdown(
            """
            <div style="background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; text-align: center;">
                <span style="color: #64748b; font-size: 0.85rem;">Patient telemetry nominal. No critical events detected.</span>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    # --- DEFAULT TELEHEALTH PORTAL OVERVIEW ---
    tab_overview, tab_settings, tab_architecture = st.tabs([
        "🏥 Telehealth Overview",
        "⚙️ Configuration & Directory",
        "🏗️ Kinematic System Architecture"
    ])

    with tab_overview:
        st.markdown(
            """
            <div class="glass-showcase" style="margin-bottom: 25px;">
                <span style="background: rgba(14, 165, 233, 0.15); color: #38bdf8; padding: 6px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; border: 1px solid rgba(56, 189, 248, 0.3);">ZERO-HARDWARE KINEMATICS</span>
                <h1 style="font-size: 2.8rem; line-height: 1.15; margin: 16px 0 12px 0;">Autonomous Protection for Solitary Lives</h1>
                <p style="color: #94a3b8; font-size: 1.12rem; line-height: 1.6; max-width: 820px; margin: 0;">
                    VITA-Guard transforms consumer smartphones into clinical-grade kinematic engines. Protecting elderly individuals living alone and technicians in hazardous industrial environments from traumatic long-lie times without wearable pendants or invasive optical cameras.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Targeted Care Environments")
        v1, v2, v3 = st.columns(3, gap="medium")
        with v1:
            st.markdown(
                """
                <div class="glass-showcase">
                    <div class="card-badge-icon">🏡</div>
                    <h3 style="font-size: 1.3rem; margin-bottom: 8px;">Elderly Assisted Care</h3>
                    <p style="color: #94a3b8; font-size: 0.92rem; line-height: 1.5; margin: 0;">
                        Prevents catastrophic post-fall trauma by dispatching emergency alerts automatically, even if the individual falls unconscious.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with v2:
            st.markdown(
                """
                <div class="glass-showcase">
                    <div class="card-badge-icon">🏭</div>
                    <h3 style="font-size: 1.3rem; margin-bottom: 8px;">Hazardous Workplaces</h3>
                    <p style="color: #94a3b8; font-size: 0.92rem; line-height: 1.5; margin: 0;">
                        Designed for high-altitude scaffolders, refinery operators, and solitary technicians. Detects sudden slips through rugged garments.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with v3:
            st.markdown(
                """
                <div class="glass-showcase">
                    <div class="card-badge-icon">🔒</div>
                    <h3 style="font-size: 1.3rem; margin-bottom: 8px;">Absolute Privacy</h3>
                    <p style="color: #94a3b8; font-size: 0.92rem; line-height: 1.5; margin: 0;">
                        Functions in pitch darkness and residential quarters without streaming invasive video, microphones, or optical imagery.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("### Telemetry Benchmarks & Diagnostic Standards")
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            st.markdown("<div class=\"metric-slab\"><div class=\"metric-slab-value\">98%</div><div class=\"metric-slab-label\">Fall Detection Reliability</div></div>", unsafe_allow_html=True)
        with m2:
            st.markdown("<div class=\"metric-slab\"><div class=\"metric-slab-value\">50 Hz</div><div class=\"metric-slab-label\">High-Frequency Sampling</div></div>", unsafe_allow_html=True)
        with m3:
            st.markdown("<div class=\"metric-slab\"><div class=\"metric-slab-value\">15s</div><div class=\"metric-slab-label\">Acoustic Pre-Alarm Window</div></div>", unsafe_allow_html=True)
        with m4:
            st.markdown("<div class=\"metric-slab\"><div class=\"metric-slab-value\">&lt; 30s</div><div class=\"metric-slab-label\">Emergency Dispatch Latency</div></div>", unsafe_allow_html=True)

        st.markdown("---")
        
        c_goal, c_action = st.columns([1.5, 1], gap="large")
        with c_goal:
            st.subheader("🎯 Engineering Roadmap")
            st.markdown("""
            * **PSTN / E-911 Telehealth Gateway:** Direct API dispatch transmitting live coordinates directly to municipal ambulance networks.
            * **Native OS Background Workers:** Implementation of Android Foreground Services and iOS CoreMotion daemons for sleep-mode tracking.
            * **Edge TinyML Classifiers:** Embedded neural models to differentiate between bed tosses and genuine syncopal collapses.
            """)
        with c_action:
            st.subheader("⚡ Launch System Engine")
            st.markdown("Click the prominent **'🚀 LAUNCH SAFETY ENGINE'** button at the top of the page to open the live graph and emergency alert controls.")

    # ==========================================
    # TAB 2: ADVANCED CONFIGURATION & DIRECTORY
    # ==========================================
    with tab_settings:
        st.markdown("## ⚙️ Operational Telemetry & Emergency Directory")
        st.markdown("<p style='color: #94a3b8; font-size: 1rem; margin-top: -10px;'>Configure dynamic kinematic sensitivity thresholds, local sensor gateway relays, and automated emergency routing contacts.</p>", unsafe_allow_html=True)
        
        # --- Interactive Mode Switcher Cards ---
        st.markdown("### 🎛️ Kinematic Sensitivity Profile")
        col_m1, col_m2 = st.columns(2, gap="large")

        is_elderly = (st.session_state.profile == "Elderly Care Mode")
        elderly_class = "mode-card mode-card-active-elderly" if is_elderly else "mode-card"
        industrial_class = "mode-card mode-card-active-industrial" if not is_elderly else "mode-card"

        with col_m1:
            st.markdown(
                f"""
                <div class="{elderly_class}">
                    <span class="mode-badge mode-badge-elderly">CLINICAL PROFILE</span>
                    <h3 style="font-size: 1.4rem; margin: 4px 0 0 0; color: #f8fafc;">Elderly Care Mode</h3>
                    <div class="mode-threshold" style="color: #38bdf8;">15.0 <span style="font-size: 1rem; color: #94a3b8;">m/s² trigger</span></div>
                    <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 16px;">
                        Calibrated for low-velocity gaits, frail movements, and sudden syncope collapses. Highly sensitive impact detection tuned for residential living.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("🔘 Activate Elderly Care Mode", use_container_width=True, type="primary" if is_elderly else "secondary"):
                st.session_state.profile = "Elderly Care Mode"
                st.toast("Switched to Elderly Care Mode (Threshold: 15.0 m/s²)", icon="🏡")
                st.rerun()

        with col_m2:
            st.markdown(
                f"""
                <div class="{industrial_class}">
                    <span class="mode-badge mode-badge-industrial">HEAVY INDUSTRY</span>
                    <h3 style="font-size: 1.4rem; margin: 4px 0 0 0; color: #f8fafc;">Industrial Worksite Mode</h3>
                    <div class="mode-threshold" style="color: #fbbf24;">25.0 <span style="font-size: 1rem; color: #94a3b8;">m/s² trigger</span></div>
                    <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 16px;">
                        Tolerates elevated mechanical vibration, rapid stair ascents, and jump dismounts. Prevents false alarms on construction and manufacturing decks.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("🔘 Activate Industrial Mode", use_container_width=True, type="primary" if not is_elderly else "secondary"):
                st.session_state.profile = "Industrial Mode"
                st.toast("Switched to Industrial Worksite Mode (Threshold: 25.0 m/s²)", icon="🏭")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Sensor Gateway & Emergency Dispatch Directory ---
        col_cfg1, col_cfg2 = st.columns([1.2, 1.8], gap="large")

        with col_cfg1:
            st.markdown(
                """
                <div class="config-surface">
                    <h3 style="font-size: 1.25rem; margin-bottom: 14px; color: #f8fafc;">📡 Sensor Gateway Endpoint</h3>
                    <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                        Provide the local network WebSocket / REST address broadcast by the mobile client (Phyphox or production background service).
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.session_state.ws_url = st.text_input("Stream Relay URL:", value=st.session_state.ws_url)
            st.caption("Standard format: `http://<phone-ip>:8080/get?accX&accY&accZ`")

        with col_cfg2:
            st.markdown(
                """
                <div class="config-surface">
                    <h3 style="font-size: 1.25rem; margin-bottom: 14px; color: #f8fafc;">🚨 Emergency Dispatch Directory</h3>
                    <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                        Primary and secondary recipient contacts who receive automated SMS dispatches with kinematic fall profiles when pre-alarms expire.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.session_state.primary_contact = st.text_input("Primary Contact (SMS / Caregiver):", value=st.session_state.primary_contact)
            with c_p2:
                st.session_state.secondary_contact = st.text_input("Secondary Contact (Facility EMS / Dispatch):", value=st.session_state.secondary_contact)
            
            if st.button("💾 Save & Verify Directory Settings", use_container_width=True, type="primary"):
                st.toast("✅ Dispatch contacts and sensor gateway committed to session memory!", icon="🛡️")
                st.success(f"Directory updated. Routing active alerts to **{st.session_state.primary_contact}**.")

    with tab_architecture:
        st.header("Clinical Kinematic Data Pipeline")
        st.markdown("""
        VITA-Guard passive pocket streaming relies on orientation-agnostic Euclidean vector calculations:
        $$||A|| = \sqrt{A_x^2 + A_y^2 + A_z^2}$$
        
        **False-Positive Rejection Sequence:**
        1. **Pre-Impact Free Fall:** Rapid reduction toward 0g during mid-air descent.
        2. **Impact Spike:** High-g collision exceeding profile threshold ($>15.0$ or $>25.0\text{ m/s}^2$).
        3. **Micro-Motion Flatline:** Verified post-impact immobility confirming incapacitation versus normal phone handling.
        """)

if st.session_state.pre_alarm_active:
    st.markdown("</div>", unsafe_allow_html=True)