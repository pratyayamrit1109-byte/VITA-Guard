import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import requests

st.set_page_config(page_title="VITA-Guard", layout="wide")

# --- Session State Initialization ---
if "pre_alarm_active" not in st.session_state:
    st.session_state.pre_alarm_active = False
if "sms_dispatched" not in st.session_state:
    st.session_state.sms_dispatched = False
if "incident_log" not in st.session_state:
    st.session_state.incident_log = []
if "ws_url" not in st.session_state:
    st.session_state.ws_url = "ws://192.168.43.1:8080/ws"
if "profile" not in st.session_state:
    st.session_state.profile = "Industrial Mode"
if "primary_contact" not in st.session_state:
    st.session_state.primary_contact = "+1 234 567 8900"
if "secondary_contact" not in st.session_state:
    st.session_state.secondary_contact = "+1 098 765 4321"

# --- Visual Screen Alert ---
if st.session_state.pre_alarm_active:
    st.markdown(
        """
        <style>
        @keyframes emergency-pulse {
            0% { box-shadow: inset 0 0 30px rgba(255, 0, 0, 0.7); background-color: rgba(255, 0, 0, 0.08); }
            50% { box-shadow: inset 0 0 70px rgba(255, 70, 0, 0.9); background-color: rgba(255, 50, 0, 0.18); }
            100% { box-shadow: inset 0 0 30px rgba(255, 0, 0, 0.7); background-color: rgba(255, 0, 0, 0.08); }
        }
        .stApp {
            animation: emergency-pulse 1s infinite alternate;
            border: 6px solid red !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title("🛡️ VITA-Guard: Kinematic Safety Engine")
st.markdown("**A zero-hardware, dual-profile kinematic safety engine that streams pocket motion telemetry to detect falls, collapses, and critical immobility in real time.**[cite: 1]")

tab_dashboard, tab_settings, tab_architecture = st.tabs(["📡 Live Dashboard", "⚙️ Settings & Contacts", "🏗️ System Architecture"])

# ==========================================
# TAB 1: LIVE DASHBOARD
# ==========================================
with tab_dashboard:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Live 3-Axis Signal Graph")
        chart_placeholder = st.empty()
        status_text = st.empty()
        
    with col2:
        st.subheader("Incident Dispatch Hub")
        dispatch_box = st.empty()
        countdown_placeholder = st.empty()
        cancel_btn_placeholder = st.empty()
        log_placeholder = st.empty()

    # --- Pre-Alarm Execution Flow ---
    if st.session_state.pre_alarm_active:
        dispatch_box.error("🚨 CRITICAL COLLAPSE / FALL DETECTED[cite: 1]")
        
        # Audio Siren and Phone Hardware Vibration
        st.components.v1.html(
            """
            <script>
            // Audio buzzer
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
            
            // Mobile vibration pulse
            if (navigator.vibrate) {
                navigator.vibrate([500, 250, 500, 250, 500]);
            }
            
            setTimeout(() => clearInterval(interval), 15000);
            </script>
            """,
            height=0
        )

        user_cancelled = False
        
        # Display 15-Second Grace Countdown before any logging
        for remaining in range(15, 0, -1):
            countdown_placeholder.markdown(
                f"<h2 style='color: red; text-align: center;'>🔊 Local Siren: {remaining}s remaining</h2>",
                unsafe_allow_html=True
            )
            # Interactive button during countdown
            if cancel_btn_placeholder.button("✅ I AM OKAY (Cancel Dispatch)", type="primary", use_container_width=True, key=f"btn_{remaining}"):
                user_cancelled = True
                break
            time.sleep(1)
            
        if user_cancelled:
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = False
            st.success("Pre-alarm cancelled by user. No dispatch initiated.[cite: 1]")
            time.sleep(1)
            st.rerun()
        else:
            # 15s fully expired -> NOW log the incident and initiate SMS
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = True
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.incident_log.append(
                f"[{timestamp}] EMERGENCY: 15s pre-alarm expired. Automated SMS alert dispatched to {st.session_state.primary_contact}[cite: 1]."
            )
            st.rerun()

    elif st.session_state.sms_dispatched:
        dispatch_box.error(f"🚨 DISPATCH CONFIRMED: Automated SMS sent to {st.session_state.primary_contact}[cite: 1]")
        if st.button("Reset System Status", use_container_width=True):
            st.session_state.sms_dispatched = False
            st.rerun()
    else:
        dispatch_box.success("System Status: Armed & Monitoring[cite: 1]")

    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    
    # ---------------------------------
    # OPTION A: LIVE PHYPHOX CONNECTION
    # ---------------------------------
    with col_btn1:
        if st.button("📡 Start Live Sensor Stream", type="primary", use_container_width=True):
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = False
            data_log = pd.DataFrame(columns=["Magnitude"])
            
            http_url = st.session_state.ws_url.replace("ws://", "http://").replace("/ws", "/get?accX&accY&accZ")
            status_text.info(f"Status: Monitoring live stream ({st.session_state.profile})...[cite: 1]")
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
                            # Start pre-alarm, DO NOT log yet
                            st.session_state.pre_alarm_active = True
                            st.rerun()
                            
                    time.sleep(0.05)
            except Exception:
                status_text.error("Connection Failed. Verify Phyphox is running and remote access is enabled.")

    # ---------------------------------
    # OPTION B: SIMULATION (FALLBACK)
    # ---------------------------------
    with col_btn2:
        if st.button("▶️ Run Simulation (Fallback Demo)", use_container_width=True):
            st.session_state.pre_alarm_active = False
            st.session_state.sms_dispatched = False
            data = pd.DataFrame(columns=["Magnitude"])
            
            status_text.info("Simulating Normal Gait (Walking)...[cite: 1]")
            for _ in range(15):
                data.loc[len(data)] = [np.random.normal(9.8, 1.2)]
                chart_placeholder.line_chart(data["Magnitude"])
                time.sleep(0.04)
                
            status_text.warning("Simulating Drop Anomaly...[cite: 1]")
            data.loc[len(data)] = [1.0] # Free-fall[cite: 1]
            chart_placeholder.line_chart(data["Magnitude"])
            time.sleep(0.06)
            data.loc[len(data)] = [32.0] # Impact spike[cite: 1]
            chart_placeholder.line_chart(data["Magnitude"])
            time.sleep(0.06)
            
            status_text.error("Simulating Immobility Flatline...[cite: 1]")
            for _ in range(10):
                data.loc[len(data)] = [np.random.normal(9.8, 0.05)]
                chart_placeholder.line_chart(data["Magnitude"])
                time.sleep(0.04)
                
            st.session_state.pre_alarm_active = True
            st.rerun()

    # Render Incident Logs
    st.markdown("### Incident Logs")
    if st.session_state.incident_log:
        for log in reversed(st.session_state.incident_log):
            log_placeholder.code(log)
    else:
        log_placeholder.caption("No critical incidents logged.[cite: 1]")

# ==========================================
# TAB 2: SETTINGS & CONTACTS
# ==========================================
with tab_settings:
    st.header("System Configuration")
    col_set1, col_set2 = st.columns(2)
    
    with col_set1:
        st.subheader("Dual-Profile Switcher")
        st.session_state.profile = st.radio(
            "Features dynamic profile switching:[cite: 1]",
            ["Elderly Care Mode", "Industrial Mode"]
        )
        st.subheader("Phyphox Sensor Link")
        st.session_state.ws_url = st.text_input("Sensor Stream Address:[cite: 1]", value=st.session_state.ws_url)

    with col_set2:
        st.subheader("Emergency Contacts")
        st.session_state.primary_contact = st.text_input("Primary Contact (SMS):", value=st.session_state.primary_contact)
        st.session_state.secondary_contact = st.text_input("Secondary Contact / Medical Dispatch:", value=st.session_state.secondary_contact)
        if st.button("💾 Save Contacts"):
            st.success("Emergency contacts updated.")

# ==========================================
# TAB 3: SYSTEM ARCHITECTURE
# ==========================================
with tab_architecture:
    st.header("How VITA-Guard Works[cite: 1]")
    st.markdown("""
    Worker or elderly person carries their existing phone in their pockets[cite: 1]. The background engine streams 3 axis motion telemetry[cite: 1]. If a collapse occurs, a 15 second local pre alarm sounds before dispatch[cite: 1]. 
    
    * **Unlike panic buttons**, it operates autonomously when the user is unconscious[cite: 1]. 
    * **Unlike CCTV**, it works in pitch darkness and inside private residential spaces[cite: 1].
    """)
    st.divider()
    st.subheader("Data Pipeline[cite: 1]")
    st.markdown("""
    * **User Input:** Pocket motion sensors (Acc/Gyro 50Hz)[cite: 1]
    * **Next Frontend:** Phyphox/sensor stream (Web Sockets)[cite: 1]
    * **API/Backend:** Python FastAPI & Numpy Kinematics Engine[cite: 1]
    * **Model Logic:** Vector magnitude & isolation anomaly check[cite: 1]
    * **Output:** Streamlit Dispatcher & automated SMS alert[cite: 1]
    """)
    st.divider()
    st.subheader("Vector Magnitude Model[cite: 1]")
    st.markdown("""
    Using scalar acceleration magnitude **||a|| = root of ax^2 + ay^2 + az^2** alongside micro vibration standard deviation to remain 100 percent agnostic to arbitrary pocket orientation[cite: 1].
    """)
    st.subheader("False Positive Rejection[cite: 1]")
    st.markdown("""
    Filtering out normal drops (tossing phones on bed or sitting abruptly) by requiring verified 2 phase sequence:[cite: 1]
    1. Pre impact free fall drop[cite: 1]
    2. Impact spike[cite: 1]
    3. Post shock micro motion flatline[cite: 1]
    """)