import json
import os
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE & STATE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="UP Manila - Community Health Portal",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = "shared_survey_data.json"

def init_session_state():
    """Initializes authentication state and shared record state."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    
    # Load persistence data into state if missing
    if "data" not in st.session_state:
        st.session_state.data = load_storage()

def load_storage():
    """Reads stored survey records from disk."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"hh_records": [], "gov_records": [], "qual_records": [], "windshield_records": [], "diag_records": []}

def save_storage():
    """Persists state records to disk storage."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {e}")

init_session_state()

# -----------------------------------------------------------------------------
# 2. MODERN UI CUSTOM STYLING
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Global Clean Font & Background */
    .stApp { background-color: #F8FAFC; }
    
    /* Login Card Styling */
    .login-card {
        max-width: 420px;
        margin: 80px auto;
        padding: 32px;
        background: #FFFFFF;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        border: 1px solid #E2E8F0;
    }
    
    /* Executive Top Bar */
    .app-header {
        background: linear-gradient(135deg, #7B1113 0%, #4A0B0D 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(123, 17, 19, 0.15);
    }
    .app-header h1 { margin: 0; font-size: 24px; font-weight: 700; color: #FFFFFF; }
    .app-header p { margin: 4px 0 0 0; opacity: 0.85; font-size: 14px; }
    
    /* Metric Card Component */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-value { font-size: 28px; font-weight: 800; color: #0F172A; }
    .metric-label { font-size: 13px; font-weight: 600; color: #64748B; text-transform: uppercase; }

    /* Custom Input Sections */
    .form-section {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. AUTHENTICATION CONTROLLER (LOGIN / LOGOUT)
# -----------------------------------------------------------------------------
def login_user(username, password):
    if username == "palo" and password == "1719":
        st.session_state["authenticated"] = True
        st.session_state["user"] = username
        st.success("Authenticated successfully!")
        st.rerun()
    else:
        st.error("Invalid credentials. Please try again.")

def logout_user():
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.rerun()

def render_login_view():
    st.markdown("""
        <div class="login-card">
            <h2 style="text-align: center; color: #7B1113; margin-bottom: 8px;">🩺 UP Manila Portal</h2>
            <p style="text-align: center; color: #64748B; font-size: 14px; margin-bottom: 24px;">Community Health Information System</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        if submitted:
            login_user(username, password)

if not st.session_state["authenticated"]:
    render_login_view()
    st.stop()

# -----------------------------------------------------------------------------
# 4. DASHBOARD HEADER & NAVIGATION
# -----------------------------------------------------------------------------
header_col1, header_col2 = st.columns([8, 2])
with header_col1:
    st.markdown("""
        <div class="app-header">
            <h1>University of the Philippines Manila</h1>
            <p>School of Health Sciences — Community Health Field Portal</p>
        </div>
    """, unsafe_allow_html=True)

with header_col2:
    st.write("")
    st.write(f"👤 **{st.session_state['user']}**")
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        logout_user()

# Sidebar Navigation
st.sidebar.title("📌 Main Menu")
menu_selection = st.sidebar.radio(
    "Navigate Module",
    [
        "📊 Main Analytics Dashboard",
        "🏠 Master Household Survey",
        "🗺️ Spatial Spot Map",
        "📋 Governance Scorecard",
        "🔍 PERI Environmental Tool",
        "💾 Data Management"
    ]
)

# -----------------------------------------------------------------------------
# 5. MODULE IMPLEMENTATIONS
# -----------------------------------------------------------------------------

# --- MODULE: MAIN DASHBOARD ---
if menu_selection == "📊 Main Analytics Dashboard":
    st.subheader("📊 System Executive Dashboard")
    
    # Dynamic Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    hh_count = len(st.session_state.data["hh_records"])
    gov_count = len(st.session_state.data["gov_records"])
    peri_count = len(st.session_state.data["windshield_records"])
    
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{hh_count}</div><div class="metric-label">Households Surveyed</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{gov_count}</div><div class="metric-label">Governance Reviews</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{peri_count}</div><div class="metric-label">PERI Assessments</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="metric-card"><div class="metric-value">100%</div><div class="metric-label">System Health</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("### 📈 Data Distribution Overview")
    if hh_count > 0:
        df_hh = pd.DataFrame(st.session_state.data["hh_records"])
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Households by Purok**")
            st.bar_chart(df_hh["Purok"].value_counts())
        with c2:
            st.write("**Risk Classifications**")
            st.bar_chart(df_hh["Risk"].value_counts())
    else:
        st.info("No survey data recorded yet. Submit household forms to generate analytics.")

# --- MODULE: MASTER HOUSEHOLD SURVEY ---
elif menu_selection == "🏠 Master Household Survey":
    st.subheader("🏠 Custom Household Submission Form")

    # Custom Submit Handler Callback
    def handle_form_submission(hh_id, barangay, purok, sys_bp, risk_type, flood_risk):
        new_record = {
            "HH_ID": hh_id,
            "Barangay": barangay,
            "Purok": purok,
            "BP": f"{sys_bp}/80",
            "Risk": risk_type,
            "Flood_Prone": flood_risk,
            "Lat": 11.1560 + (np.random.randn() * 0.002),
            "Lon": 124.9920 + (np.random.randn() * 0.002),
            "Color": [192, 38, 211, 230] if flood_risk == "Yes" else [34, 197, 94, 200]
        }
        st.session_state.data["hh_records"].append(new_record)
        save_storage()
        st.toast(f"Record {hh_id} successfully saved!", icon="✅")

    # Modern Custom Form Entry
    with st.form("custom_household_form", clear_on_submit=True):
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("#### Household Identification")
        c1, c2, c3 = st.columns(3)
        f_id = c1.text_input("Household ID", value=f"HH-{len(st.session_state.data['hh_records'])+1:03d}")
        f_brgy = c2.text_input("Barangay Name", value="Barangay 1")
        f_purok = c3.selectbox("Purok Zone", [f"Purok {i}" for i in range(1, 8)])
        
        st.markdown("#### Health & Environmental Risk")
        c1, c2, c3 = st.columns(3)
        f_bp = c1.number_input("Systolic BP (mmHg)", min_value=70, max_value=220, value=120)
        f_risk = c2.selectbox("Primary Risk Indicator", ["Normal", "Hypertensive Risk", "High Priority"])
        f_flood = c3.selectbox("Flood Hazard Zone", ["No", "Yes"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        submit_btn = st.form_submit_button("Submit Record", type="primary", use_container_width=True)
        if submit_btn:
            handle_form_submission(f_id, f_brgy, f_purok, f_bp, f_risk, f_flood)

# --- MODULE: SPATIAL MAP ---
elif menu_selection == "🗺️ Spatial Spot Map":
    st.subheader("🗺️ Geographic Risk Distribution Map")
    records = st.session_state.data["hh_records"]
    
    if len(records) == 0:
        st.info("No geographic markers available. Submit records in the Household Survey module.")
    else:
        map_df = pd.DataFrame(records)
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=["Lon", "Lat"],
            get_color="Color",
            get_radius=20,
            pickable=True,
        )
        view = pdk.ViewState(
            latitude=map_df["Lat"].mean(),
            longitude=map_df["Lon"].mean(),
            zoom=15
        )
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"text": "HH: {HH_ID}\nPurok: {Purok}\nBP: {BP}"}))

# --- MODULE: DATA MANAGEMENT ---
elif menu_selection == "💾 Data Management":
    st.subheader("💾 System Data Management & JSON Backup")
    
    st.json({
        "Total Household Records": len(st.session_state.data["hh_records"]),
        "Total Governance Scorecards": len(st.session_state.data["gov_records"]),
        "Total PERI Inspections": len(st.session_state.data["windshield_records"])
    })
    
    json_data = json.dumps(st.session_state.data, indent=4)
    st.download_button(
        label="📥 Download Complete Storage (JSON)",
        data=json_data,
        file_name="shared_survey_data.json",
        mime="application/json",
        type="primary"
    )
