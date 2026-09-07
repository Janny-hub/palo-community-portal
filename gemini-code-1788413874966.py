import json
import os
from collections import Counter
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="UP Manila - Community Clerks Portal",
    page_icon="🩺",
    layout="wide",
)

# ================= PALO, LEYTE CONSTANTS =================
PALO_BARANGAYS = [
    "Anibong", "Arado", "Baras", "Barayong", "Bato",
    "Cabarasan Daku", "Cabarasan Guti", "Campetic", "Candahug", "Cangumbang",
    "Canmaidange", "Gogon", "Guindapunan", "Liberty", "Loking",
    "Majulay", "Makinhas", "Malirong", "Naga-naga", "Opao",
    "Poblacion District 1", "Poblacion District 2", "Poblacion District 3",
    "Poblacion District 4", "Poblacion District 5", "Poblacion District 6",
    "Poblacion District 7", "Poblacion District 8", "Poblacion District 9",
    "San Agustin", "San Antonio", "San Fernando", "San Isidro",
    "San Jose", "San Roque", "Santa Cruz", "Santisimo Rosario",
    "Salvacion", "Tacuranga", "Teraza", "Tinaogan", "Victoria"
]

ENUMERATORS = [
    "Jan Art A. Serna, RMT",
    "Leila Projimo, PTRP",
    "Aubrey Maye Arrieta"
]

# ================= PERMANENT MULTI-ENUMERATOR DATA PERSISTENCE =================
DATA_FILE = "shared_survey_data.json"


def load_shared_data():
    """Reads shared survey records from persistent disk storage."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "hh_records": [],
        "gov_records": [],
        "qual_records": [],
        "windshield_records": [],
        "diag_records": [],
    }


def save_shared_data(data):
    """Saves survey records permanently to disk storage."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error persisting shared data: {e}")


def sync_session_from_disk():
    """Syncs local Streamlit session state with persistent disk storage."""
    shared = load_shared_data()
    st.session_state.hh_records = shared.get("hh_records", [])
    st.session_state.gov_records = shared.get("gov_records", [])
    st.session_state.qual_records = shared.get("qual_records", [])
    st.session_state.windshield_records = shared.get("windshield_records", [])
    st.session_state.diag_records = shared.get("diag_records", [])


def save_session_to_disk():
    """Writes session state records permanently into disk storage."""
    shared = {
        "hh_records": st.session_state.get("hh_records", []),
        "gov_records": st.session_state.get("gov_records", []),
        "qual_records": st.session_state.get("qual_records", []),
        "windshield_records": st.session_state.get("windshield_records", []),
        "diag_records": st.session_state.get("diag_records", []),
    }
    save_shared_data(shared)


# Always sync latest data on rerun to guarantee permanent file storage
sync_session_from_disk()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


def show_login_screen():
    st.markdown(
        """
        <style>
        .login-box {
            width: 4in !important;
            max-width: 4in !important;
            margin: 60px auto;
            padding: 25px;
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 3px solid #7B1113;
            box-shadow: 0 10px 25px rgba(123, 17, 19, 0.25);
            text-align: center;
        }
        .login-title {
            color: #7B1113;
            font-weight: 800;
            font-size: 22px;
            margin-bottom: 4px;
        }
        .login-sub {
            color: #D97706;
            font-size: 13px;
            margin-bottom: 20px;
            font-weight: 700;
        }
        .login-box div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-title">🩺 UP Manila Clerks Portal</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="login-sub">Lead Developer: Jan Art A. Serna, RMT</div>',
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In", use_container_width=True)

        if submit_button:
            if username_input == "palo" and password_input == "1719":
                st.session_state["authenticated"] = True
                st.success("Access Granted!")
                st.rerun()
            else:
                st.error("Invalid Username or Password.")
    st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state["authenticated"]:
    show_login_screen()
    st.stop()

# ================= MAROON & YELLOW STYLING =================

CSS_STYLE = """<style>
:root {
    --maroon-primary: #7B1113;
    --maroon-dark: #4A0A0C;
    --yellow-gold: #FFD700;
    --yellow-accent: #FCD34D;
    --text-dark: #0F172A;
    --text-muted: #334155;
    --bg-light: #FFFDF0;
}

body, .stApp {
    background-color: var(--bg-light);
    color: var(--text-dark);
}

.sticky-progress-container {
    position: sticky;
    top: 0;
    z-index: 99999;
    background-color: #FFFFFF;
    padding: 14px 12px;
    margin-bottom: 15px;
    border: 1px solid #FDE68A;
    border-top: 4px solid #7B1113;
    border-radius: 8px;
    box-shadow: 0 4px 6px -1px rgba(123, 17, 19, 0.1);
}

.up-navbar {
    background: linear-gradient(135deg, #7B1113 0%, #4A0A0C 100%);
    border-bottom: 5px solid #FFD700;
    padding: 22px 24px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 10px 15px -3px rgba(123, 17, 19, 0.3);
}
.up-navbar-title {
    color: #FFFFFF !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    margin: 0 !important;
    line-height: 1.2;
    letter-spacing: 0.5px;
}
.up-navbar-sub {
    color: #FCD34D !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    margin: 4px 0 0 0 !important;
}
.up-navbar-detail {
    color: #FFFFFF !important;
    font-size: 13px !important;
    margin-top: 4px !important;
    font-weight: 500;
}
.up-navbar-lead {
    color: #FFD700 !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    margin-top: 6px !important;
}

div[data-testid="stForm"] {
    border: 2px solid #7B1113;
    border-radius: 10px;
    background-color: #FFFFFF;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(123, 17, 19, 0.08);
}

section[data-testid="stSidebar"] {
    background-color: #FEF3C7;
    border-right: 2px solid #FDE68A;
}

.adult-card {
    background-color: #FFF5F5;
    border: 1px solid #FECDD3;
    border-left: 5px solid #7B1113;
    padding: 14px 16px;
    border-radius: 8px;
    margin-bottom: 12px;
    color: #0F172A;
}

.child-card {
    background-color: #FEFCE8;
    border: 1px solid #FEF08A;
    border-left: 5px solid #CA8A04;
    padding: 14px 16px;
    border-radius: 8px;
    margin-bottom: 12px;
    color: #0F172A;
}

.peri-domain-header {
    background: linear-gradient(90deg, #7B1113 0%, #9B1C1E 100%);
    color: #FFD700 !important;
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 12px;
    box-shadow: 0 2px 4px rgba(123, 17, 19, 0.15);
}

.dash-card {
    background-color: #FFFFFF;
    border: 1px solid #FDE68A;
    border-top: 4px solid #7B1113;
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 15px;
}

.dash-metric-val {
    font-size: 28px;
    font-weight: 800;
    color: #7B1113;
}

.dash-metric-lbl {
    font-size: 12px;
    font-weight: 700;
    color: #B45309;
    text-transform: uppercase;
}

.insight-alert-high {
    background-color: #FEF2F2;
    border-left: 5px solid #7B1113;
    border: 1px solid #FCA5A5;
    padding: 14px 16px;
    border-radius: 6px;
    margin-bottom: 12px;
    color: #7F1D1D;
}

.insight-alert-warn {
    background-color: #FFFBEB;
    border-left: 5px solid #D97706;
    border: 1px solid #FCD34D;
    padding: 14px 16px;
    border-radius: 6px;
    margin-bottom: 12px;
    color: #78350F;
}

.insight-alert-good {
    background-color: #FEFCE8;
    border-left: 5px solid #CA8A04;
    border: 1px solid #FEF08A;
    padding: 14px 16px;
    border-radius: 6px;
    margin-bottom: 12px;
    color: #713F12;
}

.stButton>button {
    background-color: #7B1113 !important;
    color: #FFD700 !important;
    font-weight: 700 !important;
    border: 1px solid #FFD700 !important;
    border-radius: 6px !important;
}

.stButton>button:hover {
    background-color: #4A0A0C !important;
    color: #FFFFFF !important;
}

label, .stMarkdown p {
    color: #0F172A !important;
    font-weight: 500;
}
</style>"""

st.markdown(CSS_STYLE, unsafe_allow_html=True)

col_header, col_logout = st.columns([8.5, 1.5])

with col_header:
    HEADER_HTML = """<div class="up-navbar">
    <div class="up-navbar-title">UNIVERSITY OF THE PHILIPPINES MANILA</div>
    <div class="up-navbar-sub">School of Health Sciences — Comprehensive Community Health Field Portal</div>
    <div class="up-navbar-detail">Integrated System: Spatial Mapping, Geocoding, Analytics & Action Planning (Phases 1–6) | Palo, Leyte</div>
    <div class="up-navbar-lead">Lead Developer: Jan Art A. Serna, RMT</div>
    </div>"""
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

with col_logout:
    st.write("")
    st.write("")
    if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
        st.session_state["authenticated"] = False
        st.rerun()


def compute_child_nutrition(age_months, weight_kg, height_cm):
    if height_cm <= 0 or weight_kg <= 0:
        return {
            "BMI": "N/A",
            "Wasting": "Invalid Input",
            "Stunting": "Invalid Input",
            "Underweight": "Invalid Input",
        }

    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m**2)

    if bmi < 13.5:
        wasting = "Severely Wasted / SAM"
    elif bmi < 14.5:
        wasting = "Wasted / MAM"
    elif bmi > 18.0:
        wasting = "Overweight / Obese Risk"
    else:
        wasting = "Normal Weight-for-Height"

    exp_height = 50.0 + (age_months * 1.15)
    if height_cm < (exp_height * 0.85):
        stunting = "Severely Stunted"
    elif height_cm < (exp_height * 0.92):
        stunting = "Stunted"
    else:
        stunting = "Normal Height-for-Age"

    exp_weight = 3.3 + (age_months * 0.5)
    if weight_kg < (exp_weight * 0.70):
        underweight = "Severely Underweight"
    elif weight_kg < (exp_weight * 0.80):
        underweight = "Underweight"
    else:
        underweight = "Normal Weight-for-Age"

    return {
        "BMI": f"{bmi:.1f} kg/m²",
        "Wasting": wasting,
        "Stunting": stunting,
        "Underweight": underweight,
    }


# Dynamic Progress Tracker
p1_status = len(st.session_state.gov_records) > 0
p2_status = len(st.session_state.hh_records) > 0
p3_status = len(st.session_state.qual_records) > 0
p4_status = len(st.session_state.windshield_records) > 0
p5_status = p2_status
p6_status = len(st.session_state.diag_records) > 0

completed_phases = sum(
    [p1_status, p2_status, p3_status, p4_status, p5_status, p6_status]
)
overall_progress_pct = int((completed_phases / 6) * 100)

st.sidebar.markdown(
    f"""
<div class="sticky-progress-container">
    <div style="font-weight: 700; color: #0F172A; font-size: 14px; margin-bottom: 4px;">📊 Phase Completion Tracker</div>
    <div style="font-weight: 800; color: #7B1113; font-size: 20px; margin-bottom: 4px;">{overall_progress_pct}% Completed</div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.progress(overall_progress_pct / 100)

if st.sidebar.button(
    "🔄 Sync / Refresh Shared Data",
    use_container_width=True,
    help="Fetch live submissions from persistent storage",
):
    sync_session_from_disk()
    st.sidebar.success("Data synced with persistent storage!")
    st.rerun()

with st.sidebar.expander("🔍 View Detailed Phase Status", expanded=False):
    st.write(f"{'✅' if p1_status else '🔴'} **Phase 1 (Governance):** {'100%' if p1_status else '0%'}")
    st.write(f"{'✅' if p2_status else '🔴'} **Phase 2 (Master Survey):** {'100%' if p2_status else '0%'}")
    st.write(f"{'✅' if p3_status else '🔴'} **Phase 3 (Qualitative):** {'100%' if p3_status else '0%'}")
    st.write(f"{'✅' if p4_status else '🔴'} **Phase 4 (Expanded PERI):** {'100%' if p4_status else '0%'}")
    st.write(f"{'✅' if p5_status else '🔴'} **Phase 5 (Analytics):** {'100%' if p5_status else '0%'}")
    st.write(f"{'✅' if p6_status else '🔴'} **Phase 6 (Action Plan):** {'100%' if p6_status else '0%'}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Navigation Menu")
menu = st.sidebar.radio(
    "Select Field Module",
    [
        "📊 Executive Health Dashboard & Smart Risk Engine",
        "🗺️ Interactive Spot Map",
        "📋 Phase 1: Full Governance Scorecard",
        "🏠 Phase 2: Master Household Survey",
        "🗣️ Phase 3: Qualitative Field Tools",
        "🔍 Phase 4: Expanded PERI Windshield Tool",
        "📈 Phase 5: Spatial & Statistical Analytics",
        "📋 Phase 6: Community Diagnosis & Action Plan",
        "💾 Data Management & Export",
    ],
)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout Account", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

# ================= MODULE 0: EXECUTIVE DASHBOARD & SMART RISK ENGINE =================
if menu == "📊 Executive Health Dashboard & Smart Risk Engine":
    st.subheader("📊 Executive Field Intelligence Dashboard & Automated Risk Engine")
    st.caption("Real-Time Multi-Phase Field Analytics, Epidemiological Insights & Automated Public Health Risk Prediction | Palo, Leyte")

    hh_data = st.session_state.hh_records
    gov_data = st.session_state.gov_records
    peri_data = st.session_state.windshield_records
    qual_data = st.session_state.qual_records
    diag_data = st.session_state.diag_records

    all_adults = [a for hh in hh_data for a in hh.get("Adults", [])]
    all_children = [c for hh in hh_data for c in hh.get("Children", [])]

    tot_hh = len(hh_data)
    tot_pop = len(all_adults) + len(all_children)
    
    htn_count = sum(1 for a in all_adults if a.get("Risk") == "Hypertensive Risk" or a.get("Sys", 0) >= 140 or a.get("Dia", 0) >= 90)
    htn_rate = (htn_count / len(all_adults) * 100) if len(all_adults) > 0 else 0.0

    avg_peri = np.mean([p.get("PERI_Index", 0) for p in peri_data]) if len(peri_data) > 0 else 0.0
    latest_gov = gov_data[-1].get("Score", 0) if len(gov_data) > 0 else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Surveyed HHs", f"{tot_hh}", delta=f"{tot_pop} People Profiled" if tot_pop > 0 else None)
    m2.metric("Adult Hypertensive Risk", f"{htn_rate:.1f}%", delta=f"{htn_count} High BP Adults", delta_color="inverse")
    m3.metric("Avg PERI Risk Index", f"{avg_peri:.2f}", delta="Cat C Critical" if avg_peri >= 2.3 else ("Cat B Concern" if avg_peri >= 1.5 else "Cat A Low Risk"), delta_color="inverse")
    m4.metric("BHB Governance Score", f"{latest_gov}/100", delta="High Functioning" if latest_gov >= 80 else "Needs Action", delta_color="normal")
    m5.metric("Action Plans Saved", f"{len(diag_data)} Plans", delta=f"{len(qual_data)} Qualitative Notes")

    st.markdown("---")

    st.markdown("### 🤖 Automated Community Health Risk & Vulnerability Predictor")
    st.caption("Dynamically evaluates multi-phase field vectors and generates priority public health interventions.")

    risk_triggers = []
    
    if htn_rate > 25.0:
        risk_triggers.append({
            "type": "high",
            "title": "🚨 Severe Adult Cardiovascular & Hypertension Surge",
            "desc": f"Hyper-prevalence detected: **{htn_rate:.1f}%** of screened adults present with high BP (≥140/90 mmHg). Urgent community NCD screening and BHS compliance monitoring required.",
            "action": "Deploy BHWs for immediate home BP monitoring & RHU physician referral."
        })
    
    flood_hhs = sum(1 for hh in hh_data if hh.get("Flood_Prone") == "Yes")
    if tot_hh > 0 and (flood_hhs / tot_hh) >= 0.3:
        risk_triggers.append({
            "type": "high",
            "title": "🌊 Critical Climate & Flood Vector Exposure",
            "desc": f"**{(flood_hhs/tot_hh*100):.1f}%** of surveyed households are located directly within severe flood-prone zones.",
            "action": "Coordinate with Municipal DRRMO for pre-disaster evacuation protocols and waterborne infection prophylaxis."
        })

    stunted_cnt = sum(1 for c in all_children if "Stunted" in c.get("Nutr", {}).get("Stunting", ""))
    if len(all_children) > 0 and (stunted_cnt / len(all_children)) >= 0.2:
        risk_triggers.append({
            "type": "warn",
            "title": "👶 Elevated Child Malnutrition & Stunting Cluster",
            "desc": f"Child anthropometric screening reveals **{(stunted_cnt/len(all_children)*100):.1f}%** stunting rate among profiled children under 5 years.",
            "action": "Enroll affected households in RHU supplementary feeding and IYCF nutrition education."
        })

    unsafe_water = sum(1 for hh in hh_data if "Unsafe" in hh.get("Water", ""))
    if unsafe_water > 0:
        risk_triggers.append({
            "type": "warn",
            "title": "🚰 Environmental WASH Vulnerability (Unsafe Water)",
            "desc": f"**{unsafe_water}** household(s) rely on shallow wells or unprotected water sources, heightening diarrheal disease risk.",
            "action": "Distribute chlorine tablets / point-of-use water disinfection units and inspect water sources."
        })

    if not risk_triggers:
        st.markdown(
            """<div class="insight-alert-good">
            <strong>✅ Low Baseline Risk Detected:</strong> Current field data indicates manageable community health indicators. Continue quarterly monitoring and standard BHS preventive interventions.
            </div>""",
            unsafe_allow_html=True
        )
    else:
        for trig in risk_triggers:
            box_cls = "insight-alert-high" if trig["type"] == "high" else "insight-alert-warn"
            st.markdown(
                f"""<div class="{box_cls}">
                <strong>{trig['title']}</strong><br>
                {trig['desc']}<br>
                <em>🎯 Recommended Action: {trig['action']}</em>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("---")

    dash_tab1, dash_tab2, dash_tab3, dash_tab4, dash_tab5 = st.tabs([
        "📈 Disease & Vitals Analytics",
        "🩺 Diabetic & Hypertensive Patient Roster",
        "👥 Household Head List by Enumerator",
        "🌍 Environmental & PERI Breakdown",
        "🔍 Real-Time Master Household Roster"
    ])

    with dash_tab1:
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("**Adult Systolic BP Distribution**")
            if len(all_adults) > 0:
                sys_vals = [a.get("Sys", 120) for a in all_adults if a.get("Sys", 0) > 0]
                df_sys = pd.DataFrame({"Systolic BP": sys_vals})
                st.bar_chart(df_sys["Systolic BP"].value_counts().sort_index())
            else:
                st.info("No adult BP vitals recorded yet.")

        with c_right:
            st.markdown("**Chronic Disease Prevalence in Households**")
            if tot_hh > 0:
                htn_hhs = sum(1 for hh in hh_data if "Diagnosed" in hh.get("Hypertension_Status", ""))
                dm_hhs = sum(1 for hh in hh_data if "Diagnosed" in hh.get("Diabetes_Status", ""))
                asthma_hhs = sum(1 for hh in hh_data if "Diagnosed" in hh.get("Asthma_Status", ""))
                tb_hhs = sum(1 for hh in hh_data if "DOTS" in hh.get("TB_Status", ""))
                
                df_chronic = pd.DataFrame({
                    "Condition": ["Hypertension", "Diabetes", "Asthma/COPD", "Tuberculosis"],
                    "Diagnosed HH Count": [htn_hhs, dm_hhs, asthma_hhs, tb_hhs]
                }).set_index("Condition")
                st.bar_chart(df_chronic)
            else:
                st.info("No household morbidity records available.")

    # NEW REQUIRED TAB: DIABETIC AND HYPERTENSIVE PATIENT ROSTER
    with dash_tab2:
        st.markdown("### 🩺 Roster of Diabetic and Hypertensive Patients")
        st.caption("Complete listing of screened patients identified with Diabetes, Hypertension, or High BP with full names and addresses in Palo, Leyte.")

        patient_roster = []

        for hh in hh_data:
            brgy_name = hh.get("Barangay", "N/A")
            purok_name = hh.get("Purok", "N/A")
            full_address = f"{purok_name}, Brgy. {brgy_name}, Palo, Leyte"
            hh_id_val = hh.get("HH_ID", "N/A")
            
            htn_hh_flag = "Diagnosed" in hh.get("Hypertension_Status", "")
            dm_hh_flag = "Diagnosed" in hh.get("Diabetes_Status", "")

            # Check dynamic profiled adults
            adults_list = hh.get("Adults", [])
            for a in adults_list:
                a_name = a.get("Name", "").strip()
                is_htn = a.get("Risk") == "Hypertensive Risk" or a.get("Sys", 0) >= 140 or a.get("Dia", 0) >= 90 or htn_hh_flag
                is_dm = dm_hh_flag or "Diabetes" in str(a.get("Complaints", []))

                if is_htn or is_dm:
                    conds = []
                    if is_htn:
                        conds.append("Hypertension")
                    if is_dm:
                        conds.append("Diabetes")

                    patient_roster.append({
                        "Full Patient Name": a_name if a_name else f"Adult ({hh.get('Head_Name', 'HH Member')})",
                        "Condition(s)": " & ".join(conds),
                        "Full Address": full_address,
                        "Barangay": brgy_name,
                        "Purok": purok_name,
                        "Blood Pressure": a.get("BP", hh.get("BP", "N/A")),
                        "Age / Gender": f"{a.get('Age', 'N/A')} yrs / {a.get('Gender', 'N/A')}",
                        "HH ID": hh_id_val
                    })

            # If no adult sub-roster but HH tagged as diagnosed
            if len(adults_list) == 0 and (htn_hh_flag or dm_hh_flag):
                conds = []
                if htn_hh_flag:
                    conds.append("Hypertension")
                if dm_hh_flag:
                    conds.append("Diabetes")
                patient_roster.append({
                    "Full Patient Name": hh.get("Head_Name", "Unnamed Head"),
                    "Condition(s)": " & ".join(conds),
                    "Full Address": full_address,
                    "Barangay": brgy_name,
                    "Purok": purok_name,
                    "Blood Pressure": hh.get("BP", "N/A"),
                    "Age / Gender": "Head of Household",
                    "HH ID": hh_id_val
                })

        if len(patient_roster) > 0:
            df_patient_roster = pd.DataFrame(patient_roster)
            
            f_brgy = st.selectbox("Filter Roster by Barangay", ["All Barangays"] + PALO_BARANGAYS, key="rost_brgy_filter")
            if f_brgy != "All Barangays":
                df_patient_roster = df_patient_roster[df_patient_roster["Barangay"] == f_brgy]
                
            st.dataframe(df_patient_roster, use_container_width=True)
            st.caption(f"Showing **{len(df_patient_roster)}** recorded patient entry/entries.")
        else:
            st.info("No diabetic or hypertensive patients currently recorded in survey data.")

    # NEW REQUIRED TAB: HOUSEHOLDS INTERVIEWED BY THE 3 ENUMERATORS
    with dash_tab3:
        st.markdown("### 👥 Master List of Households by Head Interviewed by Enumerator")
        st.caption("Filter and view households organized by the 3 assigned enumerators: Jan Art A. Serna, RMT, Leila Projimo, PTRP, and Aubrey Maye Arrieta.")

        hh_enum_list = []
        for hh in hh_data:
            hh_enum_list.append({
                "Household Head Name": hh.get("Head_Name", "N/A"),
                "Enumerator": hh.get("Enumerator", "Unassigned"),
                "Barangay": hh.get("Barangay", "N/A"),
                "Purok": hh.get("Purok", "N/A"),
                "Full Address": f"{hh.get('Purok', 'N/A')}, Brgy. {hh.get('Barangay', 'N/A')}, Palo, Leyte",
                "HH ID": hh.get("HH_ID", "N/A"),
                "Survey Date": hh.get("Date", "N/A"),
                "Survey Status": hh.get("Survey_Status", "Completed")
            })

        if len(hh_enum_list) > 0:
            df_enum = pd.DataFrame(hh_enum_list)
            
            sel_enum_filter = st.selectbox("Filter List by Assigned Enumerator", ["All 3 Enumerators"] + ENUMERATORS, key="enum_dash_filter")
            
            if sel_enum_filter != "All 3 Enumerators":
                df_enum_filtered = df_enum[df_enum["Enumerator"] == sel_enum_filter]
            else:
                df_enum_filtered = df_enum

            st.dataframe(df_enum_filtered, use_container_width=True)
            
            # Summary stats per enumerator
            st.markdown("#### 📊 Enumerator Interview Breakdown Count")
            enum_counts = df_enum["Enumerator"].value_counts().reset_index()
            enum_counts.columns = ["Enumerator", "Households Interviewed"]
            st.table(enum_counts)
        else:
            st.info("No household survey records logged yet.")

    with dash_tab4:
        if len(peri_data) > 0:
            st.markdown("**Purok Environmental Risk Index (PERI) Domain Breakdown**")
            peri_df = pd.DataFrame(peri_data)[["Purok", "DS1_Sanitation", "DS2_Food", "DS3_BuiltEnv", "DS4_HealthInfra", "DS5_DRR", "DS6_Vector", "PERI_Index"]]
            st.dataframe(peri_df, use_container_width=True)
            st.bar_chart(peri_df.set_index("Purok")[["DS1_Sanitation", "DS2_Food", "DS3_BuiltEnv", "DS4_HealthInfra", "DS5_DRR", "DS6_Vector"]])
        else:
            st.info("No Phase 4 PERI windshield evaluations stored yet.")

    with dash_tab5:
        st.markdown("**Live Master Household Explorer**")
        if tot_hh > 0:
            search_query = st.text_input("🔎 Search by Household ID, Barangay, or Head Name", "")
            flat_hhs = []
            for h in hh_data:
                flat_hhs.append({
                    "HH ID": h.get("HH_ID"),
                    "Barangay": h.get("Barangay"),
                    "Purok": h.get("Purok"),
                    "Head Name": h.get("Head_Name"),
                    "Enumerator": h.get("Enumerator"),
                    "Vitals BP": h.get("BP"),
                    "Health Risk": h.get("Risk"),
                    "Flood Zone": h.get("Flood_Prone"),
                    "Income": h.get("Income"),
                    "Water Source": h.get("Water")
                })
            df_display = pd.DataFrame(flat_hhs)
            if search_query:
                df_display = df_display[df_display.apply(lambda r: search_query.lower() in str(r).lower(), axis=1)]
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No household data logged.")

# MODULE 1: INTERACTIVE SPOT MAP
elif menu == "MAP: Interactive Spot Map" or menu == "🗺️ Interactive Spot Map":
    st.subheader("📍 Interactive Barangay Health & Environmental Hazard Spot Map (Palo, Leyte)")

    if len(st.session_state.hh_records) == 0:
        st.info("No household survey records stored yet. Showing baseline map with simulated hazard markers in Palo, Leyte.")
        map_df = pd.DataFrame([
            {"HH_ID": "HH-001", "Purok": "Purok 1", "Barangay": "Poblacion District 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk": "Hypertensive Risk", "Flood_Prone": "Yes", "Color": [192, 38, 211, 230]},
            {"HH_ID": "HH-002", "Purok": "Purok 1", "Barangay": "San Jose", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk": "Normal", "Flood_Prone": "No", "Color": [34, 197, 94, 200]},
            {"HH_ID": "HH-003", "Purok": "Purok 2", "Barangay": "Campetic", "Lat": 11.1555, "Lon": 124.9905, "BP": "120/80", "Risk": "Normal", "Flood_Prone": "Yes", "Color": [37, 99, 235, 220]},
            {"HH_ID": "HH-004", "Purok": "Purok 3", "Barangay": "Candahug", "Lat": 11.1570, "Lon": 124.9930, "BP": "150/98", "Risk": "Hypertensive Risk", "Flood_Prone": "No", "Color": [123, 17, 19, 220]},
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_m, col_f = st.columns([3, 1])

    with col_f:
        st.markdown("**Map Controls & Filters**")
        puroks = list(map_df["Purok"].unique()) if "Purok" in map_df.columns else ["Purok 1"]
        sel_puroks = st.multiselect("Filter Puroks", options=puroks, default=puroks)
        flood_filter = st.selectbox("Flood Risk Filter", ["Show All Households", "Flood-Prone Zones Only", "Non-Flood Zones Only"])

        st.markdown("---")
        st.markdown("**Map Marker Legend:**")
        st.markdown("🔵 **Blue:** Flood-Prone Zone Only")
        st.markdown("🔴 **Maroon:** Hypertensive Health Risk Only")
        st.markdown("🟣 **Purple:** Dual Hazard (Flood + Health Risk)")
        st.markdown("🟢 **Green:** Normal / Low Risk")

    filt_df = map_df[map_df["Purok"].isin(sel_puroks)] if "Purok" in map_df.columns else map_df
    if flood_filter == "Flood-Prone Zones Only":
        filt_df = filt_df[filt_df["Flood_Prone"] == "Yes"]
    elif flood_filter == "Non-Flood Zones Only":
        filt_df = filt_df[filt_df["Flood_Prone"] == "No"]

    total_map_hh = len(filt_df)
    flood_detected = sum(1 for _, r in filt_df.iterrows() if r.get("Flood_Prone") == "Yes")

    st.markdown(f"📊 **Detected Summary:** Showing **{total_map_hh}** households | ⚠️ **{flood_detected}** located in detected **Flood-Prone Zones**.")

    with col_m:
        view = pdk.ViewState(
            latitude=filt_df["Lat"].mean() if len(filt_df) > 0 else 11.1560,
            longitude=filt_df["Lon"].mean() if len(filt_df) > 0 else 124.9915,
            zoom=15,
            pitch=30,
        )
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filt_df,
            get_position=["Lon", "Lat"],
            get_color="Color",
            get_radius=16,
            pickable=True,
        )
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                tooltip={"text": "HH: {HH_ID}\nBarangay: {Barangay}\nPurok: {Purok}\nBP: {BP}\nHealth Risk: {Risk}\nFlood Prone: {Flood_Prone}"},
            )
        )

# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD (INTACT - UNCHANGED CONTENT)
elif menu == "📋 Phase 1: Full Governance Scorecard":
    st.subheader("Phase 1: Barangay Health Board (BHB) Governance Scorecard (100-Point Instrument)")

    with st.expander("📖 View Formal Scoring Criteria Matrix & Governance Categorization Guide", expanded=False):
        st.markdown("""
        ### Official Scoring Matrix & Verification Guide
        * **Domain 1. Legal Reconstitution (Max: 10 pts)**
          * **1.1** Signed Executive Order (EO) / Resolution reconstituting the BHB for the current term (5 pts) | *Verification Source:* Signed EO / Barangay Resolution Copy
          * **1.2** Mandatory Multi-sectoral Representation present: NGO/CBO, Youth/SK, BHW/BNS, Senior Citizen, DepEd (5 pts) | *Verification Source:* Appointment Papers / Roster of Members
        * **Domain 2. Meeting Regularity (Max: 20 pts)**
          * **2.1** Conduct of Regular Quarterly BHB Meetings (3 pts per quarter conducted = 12 pts max) | *Verification Source:* Minutes of Meeting & Attendance Sheets (Q1-Q4)
          * **2.2** Official Quorum (>50% member attendance) consistently documented in all meetings (4 pts) | *Verification Source:* Signed Attendance Logs
          * **2.3** Approved Action-Oriented Minutes with clear resolution/action point tracking (4 pts) | *Verification Source:* Approved BHB Minutes of Meetings
        * **Domain 3. Legislative Output (Max: 20 pts)**
          * **3.1** Enactment of specific local ordinances on Sanitation, WASH, Dengue, Rabies, or Tobacco/Vape Control (10 pts) | *Verification Source:* Official Barangay Ordinances
          * **3.2** Active enforcement mechanism, Task Force creation, or penalty/monitoring protocols (5 pts) | *Verification Source:* Enforcement Reports / Inspection Records
          * **3.3** Policy alignment with DOH Universal Health Care (UHC) & Municipal Health Priorities (5 pts) | *Verification Source:* Barangay Health Plan / Policy Framework
        * **Domain 4. AIP Budget Allocation (Max: 20 pts)**
          * **4.1** Dedicated, itemized Health & Sanitation budget line-items in the approved Barangay AIP (8 pts) | *Verification Source:* Approved Barangay AIP Document
          * **4.2** Adequate budget allocation for essential drugs, BHW honoraria, and emergency health response (6 pts) | *Verification Source:* Itemized Budget Breakdown
          * **4.3** Budget execution and liquidation status (>75% budget utilized for intended health programs) (6 pts) | *Verification Source:* Barangay Financial & Liquidation Reports
        * **Domain 5. Accomplishment Reports (Max: 15 pts)**
          * **5.1** Regular quarterly health tracking & epidemiological reports submitted on time to RHU/MHO (8 pts) | *Verification Source:* Submitted RHU/MHO Transmittals & Reports
          * **5.2** Presentation of Barangay Health Status & Progress during semi-annual Barangay Assemblies (4 pts) | *Verification Source:* Barangay Assembly Minutes / Slides
          * **5.3** Functional Barangay Health Information Board maintained at BHS / Barangay Hall (3 pts) | *Verification Source:* Updated BHS Data Board / Spot Map
        * **Domain 6. Committee Functionality (Max: 15 pts)**
          * **6.1** Functional Technical Working Committees created (e.g., Dengue Task Force, WASH Committee, Nutrition Committee) (6 pts) | *Verification Source:* TMC / Task Force Executive Orders
          * **6.2** Monthly/Regular operational meetings and activity implementation reports by committees (6 pts) | *Verification Source:* TMC Activity Reports & Logbooks
          * **6.3** Execution of community mobilization campaigns (e.g., Clean-up drives, Immunization, Operation Timbang) (3 pts) | *Verification Source:* Photo Documentation & Activity Logs
        
        ---
        ### III. GOVERNANCE FUNCTIONALITY RATING & CATEGORIZATION
        | Score Bracket | Category Level | Description & Operational Implications | Assessed Status |
        | :--- | :--- | :--- | :--- |
        | **80 – 100 Points** | **HIGH FUNCTIONING** | Fully compliant with legal, legislative, budgetary, and operational standards. Demonstrates proactive local health governance. | `[ ] HIGH FUNCTIONING` |
        | **50 – 79 Points** | **MODERATE FUNCTIONING** | Partially compliant. Basic structure exists but lacks consistency in meeting regularity, legislative output, or committee operations. | `[ ] MODERATE FUNCTIONING` |
        | **0 – 49 Points** | **LOW FUNCTIONING** | Non-compliant or severe operational gaps. Urgent technical assistance, reconstitution, and budgetary alignment required. | `[ ] LOW FUNCTIONING` |
        """)

    mode_p1 = st.radio("Select Operation", ["➕ New Scorecard Entry", "📂 Review, Edit & Delete Submitted Scorecards"], horizontal=True)

    if mode_p1 == "➕ New Scorecard Entry":
        with st.form("phase1_full_form"):
            t1, t2, t3, t4 = st.tabs(["📌 Metadata & Leadership", "🏛️ Legal, Meetings & Ordinances", "💰 AIP Budgeting & Reports", "🎯 Committee, Gaps & Action Plan"])

            with t1:
                c1, c2, c3 = st.columns(3)
                b_name = c1.selectbox("Barangay Name", PALO_BARANGAYS)
                city = c2.text_input("City / Municipality", "Palo")
                prov = c3.text_input("Province", "Leyte")

                c1, c2, c3 = st.columns(3)
                eval_date = c1.date_input("Date of Evaluation")
                pb_head = c2.text_input("Punong Barangay (BHB Chair)")
                health_lead = c3.text_input("Committee Lead on Health / BHW Lead")

            with t2:
                st.markdown("**Domain 1: Legal Reconstitution (Max 10 Points)**")
                c1, c2 = st.columns(2)
                g1_1 = c1.number_input("1.1 Signed Executive Order (EO) / Resolution reconstituting the BHB for current term (Max 5 pts)", 0, 5, 0, help="Verification: Signed EO / Barangay Resolution Copy")
                g1_2 = c2.number_input("1.2 Mandatory Multi-sectoral Representation present: NGO/CBO, Youth/SK, BHW/BNS, Senior Citizen, DepEd (Max 5 pts)", 0, 5, 0, help="Verification: Appointment Papers / Roster of Members")

                st.markdown("**Domain 2: Meeting Regularity (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g2_1 = c1.number_input("2.1 Conduct of Regular Quarterly BHB Meetings (3 pts per quarter conducted = 12 pts max)", 0, 12, 0, help="Verification: Minutes of Meeting & Attendance Sheets (Q1-Q4)")
                g2_2 = c2.number_input("2.2 Official Quorum (>50% member attendance) consistently documented in all meetings (Max 4 pts)", 0, 4, 0, help="Verification: Signed Attendance Logs")
                g2_3 = c3.number_input("2.3 Approved Action-Oriented Minutes with clear resolution/action point tracking (Max 4 pts)", 0, 4, 0, help="Verification: Approved BHB Minutes of Meetings")

                st.markdown("**Domain 3: Legislative Output (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g3_1 = c1.number_input("3.1 Enactment of specific local ordinances on Sanitation, WASH, Dengue, Rabies, or Tobacco/Vape Control (Max 10 pts)", 0, 10, 0, help="Verification: Official Barangay Ordinances")
                g3_2 = c2.number_input("3.2 Active enforcement mechanism, Task Force creation, or penalty/monitoring protocols (Max 5 pts)", 0, 5, 0, help="Verification: Enforcement Reports / Inspection Records")
                g3_3 = c3.number_input("3.3 Policy alignment with DOH Universal Health Care (UHC) & Municipal Health Priorities (Max 5 pts)", 0, 5, 0, help="Verification: Barangay Health Plan / Policy Framework")

            with t3:
                st.markdown("**Domain 4: AIP Budget Allocation (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g4_1 = c1.number_input("4.1 Dedicated, itemized Health & Sanitation budget line-items in approved Barangay AIP (Max 8 pts)", 0, 8, 0, help="Verification: Approved Barangay AIP Document")
                g4_2 = c2.number_input("4.2 Adequate budget allocation for essential drugs, BHW honoraria, and emergency health response (Max 6 pts)", 0, 6, 0, help="Verification: Itemized Budget Breakdown")
                g4_3 = c3.number_input("4.3 Budget execution and liquidation status (>75% budget utilized for intended health programs) (Max 6 pts)", 0, 6, 0, help="Verification: Barangay Financial & Liquidation Reports")

                st.markdown("**Domain 5: Accomplishment Reports (Max 15 Points)**")
                c1, c2, c3 = st.columns(3)
                g5_1 = c1.number_input("5.1 Regular quarterly health tracking & epidemiological reports submitted on time to RHU/MHO (Max 8 pts)", 0, 8, 0, help="Verification: Submitted RHU/MHO Transmittals & Reports")
                g5_2 = c2.number_input("5.2 Presentation of Barangay Health Status & Progress during semi-annual Barangay Assemblies (Max 4 pts)", 0, 4, 0, help="Verification: Barangay Assembly Minutes / Slides")
                g5_3 = c3.number_input("5.3 Functional Barangay Health Information Board maintained at BHS / Barangay Hall (Max 3 pts)", 0, 3, 0, help="Verification: Updated BHS Data Board / Spot Map")

            with t4:
                st.markdown("**Domain 6: Committee Functionality (Max 15 Points)**")
                c1, c2, c3 = st.columns(3)
                g6_1 = c1.number_input("6.1 Functional Technical Working Committees created (e.g., Dengue Task Force, WASH, Nutrition) (Max 6 pts)", 0, 6, 0, help="Verification: TMC / Task Force Executive Orders")
                g6_2 = c2.number_input("6.2 Monthly/Regular operational meetings and activity implementation reports by committees (Max 6 pts)", 0, 6, 0, help="Verification: TMC Activity Reports & Logbooks")
                g6_3 = c3.number_input("6.3 Execution of community mobilization campaigns (e.g., Clean-up drives, Immunization, Operation Timbang) (Max 3 pts)", 0, 3, 0, help="Verification: Photo Documentation & Activity Logs")

                gap_summary = st.text_area("Identify primary governance bottlenecks & legislative gaps:")
                action_plan = st.text_area("Recommended technical assistance & corrective intervention plan:")

            if st.form_submit_button("Submit & Save Governance Scorecard"):
                total_score = sum([g1_1, g1_2, g2_1, g2_2, g2_3, g3_1, g3_2, g3_3, g4_1, g4_2, g4_3, g5_1, g5_2, g5_3, g6_1, g6_2, g6_3])
                rating = "HIGH FUNCTIONING" if total_score >= 80 else ("MODERATE FUNCTIONING" if total_score >= 50 else "LOW FUNCTIONING / CRITICAL INTERVENTION REQUIRED")

                st.session_state.gov_records.append({
                    "Barangay": b_name, "City": city, "Province": prov, "Evaluation_Date": str(eval_date),
                    "Punong_Barangay": pb_head, "Health_Lead": health_lead, "Score": total_score, "Rating": rating,
                    "Gaps": gap_summary, "ActionPlan": action_plan,
                })
                save_session_to_disk()
                st.success(f"Scorecard Saved! Total Score: {total_score}/100 — Status: {rating}")

    else:
        st.markdown("### 📂 Submitted Governance Scorecards")
        if len(st.session_state.gov_records) == 0:
            st.info("No governance scorecard records found.")
        else:
            gov_options = [f"[{i+1}] {r.get('Barangay', 'Unnamed')} (Score: {r.get('Score', 0)})" for i, r in enumerate(st.session_state.gov_records)]
            selected_idx = st.selectbox("Select Record to Review / Edit", range(len(gov_options)), format_func=lambda x: gov_options[x])
            rec = st.session_state.gov_records[selected_idx]

            with st.form("edit_gov_form"):
                e_brgy = st.selectbox("Barangay Name", PALO_BARANGAYS, index=PALO_BARANGAYS.index(rec.get("Barangay")) if rec.get("Barangay") in PALO_BARANGAYS else 0)
                e_city = st.text_input("City / Municipality", value=rec.get("City", "Palo"))
                e_prov = st.text_input("Province", value=rec.get("Province", "Leyte"))
                e_score = st.number_input("Total Score (0–100)", 0, 100, int(rec.get("Score", 0)))
                e_rating = "HIGH FUNCTIONING" if e_score >= 80 else ("MODERATE FUNCTIONING" if e_score >= 50 else "LOW FUNCTIONING / CRITICAL INTERVENTION REQUIRED")
                e_gaps = st.text_area("Governance Bottlenecks", value=rec.get("Gaps", ""))
                e_action = st.text_area("Action Plan", value=rec.get("ActionPlan", ""))

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Changes"):
                        rec.update({"Barangay": e_brgy, "City": e_city, "Province": e_prov, "Score": e_score, "Rating": e_rating, "Gaps": e_gaps, "ActionPlan": e_action})
                        st.session_state.gov_records[selected_idx] = rec
                        save_session_to_disk()
                        st.success("Record updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Record"):
                        st.session_state.gov_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("Record deleted successfully!")
                        st.rerun()

# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader("Phase 2: Master Household Survey Instrument (Dynamic Profile Entry & Cross-Module Interpretation)")

    mode_p2 = st.radio(
        "Select Operation",
        [
            "➕ New Household Survey Entry",
            "📊 Phase 2 Interpreted Data & Individual Response Inspection",
            "📂 Review, Edit & Delete Submitted Household Surveys",
        ],
        horizontal=True,
    )

    if mode_p2 == "➕ New Household Survey Entry":
        st.markdown("#### ⚙️ Profile Roster Count Configuration & Controls")
        st.info("💡 Adjust the counters or click the buttons below to dynamically add profiling forms without submitting the overall survey record.")
        
        if "adult_count" not in st.session_state:
            st.session_state.adult_count = 1
        if "child_count" not in st.session_state:
            st.session_state.child_count = 0

        c_cnt1, c_cnt2, c_cnt3, c_cnt4 = st.columns(4)
        with c_cnt1:
            st.session_state.adult_count = st.number_input(
                "Adult Members Count", min_value=0, max_value=20, value=st.session_state.adult_count, step=1
            )
        with c_cnt2:
            if st.button("➕ Add Adult Form", use_container_width=True):
                st.session_state.adult_count += 1
                st.rerun()
        with c_cnt3:
            st.session_state.child_count = st.number_input(
                "Child Members Count (<5 yrs)", min_value=0, max_value=15, value=st.session_state.child_count, step=1
            )
        with c_cnt4:
            if st.button("➕ Add Child Form", use_container_width=True):
                st.session_state.child_count += 1
                st.rerun()

        num_adults = st.session_state.adult_count
        num_children = st.session_state.child_count

        with st.form("phase2_complete_form"):
            t_meta, t_vitals, t_socio, t_dec, t_morb, t_mch, t_child, t_yakap = st.tabs([
                "📋 Metadata & Roster",
                "🩺 Dynamic Adult Profiling & Vitals",
                "🌾 Socio-Econ, Food Security, Housing & WASH",
                "🤝 Decision-Making Patterns",
                "🤒 Morbidity & Chronic Care",
                "👩 Maternal, FP & Mortality",
                "👶 Dynamic Child Profiling & Immunization",
                "🏥 Health-Seeking Behavior & PhilHealth YAKAP",
            ])

            # --- TAB 1: METADATA & ROSTER ---
            with t_meta:
                st.markdown("**Survey Metadata Control Block**")
                c1, c2, c3, c4 = st.columns(4)
                hh_id = c1.text_input("Household ID", "HH-001")
                # UPDATED: PALO, LEYTE ALL BARANGAYS SELECTBOX
                brgy = c2.selectbox("Barangay Name (Palo, Leyte)", PALO_BARANGAYS)
                purok = c3.selectbox("Purok / Zone", [f"Purok {i}" for i in range(1, 8)])
                date_survey = c4.date_input("Date of Survey")

                c1, c2, c3, c4 = st.columns(4)
                lat = c1.number_input("Latitude", value=11.1560, format="%.4f")
                lon = c2.number_input("Longitude", value=124.9920, format="%.4f")
                # UPDATED: SPECIFIC 3 ENUMERATORS SELECTBOX
                enum_name = c3.selectbox("Enumerator Name", ENUMERATORS)
                resp_role = c4.selectbox("Respondent Role", ["Head", "Spouse", "Adult Member", "Other"])

                c1, c2, c3 = st.columns(3)
                surv_status = c1.selectbox("Survey Status", ["Completed", "Partially Completed", "Refused"])
                dialect = c2.selectbox("Primary Dialect Spoken at Home", ["Waray", "Tagalog", "English", "Mixed", "Cebuano / Bisaya", "Ilocano", "Bicolano", "Hiligaynon / Ilonggo", "Pangasinan", "Other Language"])
                religion = c3.selectbox("Religion", ["Roman Catholic", "Islam", "Iglesia ni Cristo (INC)", "Evangelical / Protestant", "Seventh-day Adventist", "Aglipayan (IFI)", "Jehovah's Witnesses", "Church of Jesus Christ of Latter-day Saints", "Born Again Christian", "None / Secular", "Other Religion"])

                st.markdown("---")
                st.markdown("**Household Demographic Roster**")
                c1, c2, c3, c4 = st.columns(4)
                tot_children = c1.number_input("No. of Children (<18 yrs)", 0, 20, 0)
                tot_dependents = c2.number_input("No. of Other Dependents", 0, 10, 0)
                hh_head_name = c3.text_input("Household Head Full Name")
                head_civil = c4.selectbox("Head Civil Status", ["Single", "Married", "Widowed", "Separated", "Cohabiting"])

            # --- TAB 2: DYNAMIC ADULT PROFILING ---
            with t_vitals:
                st.markdown(f"**Module B: Adult Profiling & Physical Screening ({num_adults} Adult(s) Active)**")
                
                adults_data = []
                for i in range(1, int(num_adults) + 1):
                    st.markdown(f"<div class='adult-card'><strong>Adult Member {i} Full Profile & Physical Screening</strong></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_name = c1.text_input(f"Adult {i} Name / Initials", key=f"a_name_{i}")
                    a_gender = c2.selectbox(f"Adult {i} Gender", ["Male", "Female", "Other"], key=f"a_gen_{i}")
                    a_age = c3.number_input(f"Adult {i} Age", 18, 120, 30, key=f"a_age_{i}")
                    a_edu = c4.selectbox(f"Adult {i} Education", ["No Formal Education", "Elementary Unfinished", "Elementary Graduate", "High School Unfinished", "High School Graduate", "Vocational / College Unfinished", "College Graduate", "Post-Graduate"], key=f"a_edu_{i}")
                    a_occ = c5.text_input(f"Adult {i} Primary Occupation", key=f"a_occ_{i}")

                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_ph_cat = c1.selectbox(f"Adult {i} PhilHealth", ["Indigent", "Formal", "Informal", "Dependent", "Unenrolled"], key=f"a_ph_{i}")
                    a_sys = c2.number_input(f"Adult {i} Systolic BP", 50, 250, 120, key=f"a_sys_{i}")
                    a_dia = c3.number_input(f"Adult {i} Diastolic BP", 30, 150, 80, key=f"a_dia_{i}")
                    a_spo2 = c4.number_input(f"Adult {i} SpO2 (%)", 50, 100, 98, key=f"a_spo2_{i}")
                    a_pulse = c5.number_input(f"Adult {i} Pulse (bpm)", 30, 200, 75, key=f"a_pulse_{i}")

                    c1, c2 = st.columns(2)
                    a_symptoms = c1.multiselect(
                        f"Adult {i} Current Complaints / Symptoms",
                        ["None", "Cough", "Fever / feeling feverish", "Headache", "Colds / runny nose", "Body aches / muscle pain", "Abdominal pain", "Diarrhea", "Back pain", "Dizziness", "Sore throat", "Others"],
                        default=["None"], key=f"a_sym_{i}"
                    )
                    a_risk = c2.selectbox(f"Adult {i} Risk Category", ["Normal", "Hypertensive Risk", "Hypoxemic (<95%)", "Fever / Febrile", "Tachycardic / Bradycardic"], key=f"a_risk_{i}")

                    a_action = st.multiselect(
                        f"🩺 Adult {i} Action Taken",
                        ["Referral to RHU / MHO Physician", "Referral to BHS / Barangay Midwife", "Health Education & Lifestyle Counseling", "Medication Compliance Check", "Follow-up Visit Scheduled", "Immediate Emergency Hospital Referral", "None / Normal Vitals"],
                        default=["None / Normal Vitals"] if a_risk == "Normal" else ["Referral to RHU / MHO Physician"],
                        key=f"a_action_{i}"
                    )

                    if a_name.strip() != "":
                        adults_data.append({
                            "ID": f"Adult {i}", "Name": a_name, "Gender": a_gender, "Age": a_age, "Edu": a_edu, "Occupation": a_occ,
                            "PhilHealth_Cat": a_ph_cat, "BP": f"{a_sys}/{a_dia}", "Sys": a_sys, "Dia": a_dia, "SpO2": a_spo2, "Pulse": a_pulse,
                            "Complaints": a_symptoms, "Risk": a_risk, "Action_Taken": a_action
                        })

            # --- TAB 3: SOCIO-ECON, FOOD INSECURITY, HOUSING & WASH ---
            with t_socio:
                st.markdown("**C1. Livelihood, Economic Stability & Domestic Assets**")
                c1, c2, c3 = st.columns(3)
                income_cat = c1.selectbox("Average Family Income / Month", ["≤ ₱10,000 (Q1)", "₱10,001–₱20,000 (Q2)", "₱20,001–₱35,000 (Q3)", "₱35,001–₱50,000 (Q4)", "> ₱50,000 (Q5)"])
                livelihood = c2.selectbox("Primary Livelihood Source", ["Farming (Owned)", "Farming (Tenanted)", "Laborer", "Carpentry", "Fishing", "Peddling", "Gov't Employee", "Small Industry/Sari-Sari", "Other"])
                food_prod = c3.selectbox("Engaged in Food Production?", ["Yes", "No"])

                c1, c2 = st.columns(2)
                emergency_5k = c1.selectbox("Emergency Cushion: Can raise ₱5,000 in 24 hrs?", ["Yes", "No"])
                p4ps_status = c2.selectbox("Active 4Ps Beneficiary?", ["Yes", "No"])

                st.markdown("**Domestic Assets, Utilities & Transportation Owned**")
                c1, c2, c3 = st.columns(3)
                transpo_owned = c1.multiselect("Type of Transportation Owned", ["None", "Bicycle", "Motorcycle / Tricycle", "Private Car / Van", "Motorized Banca / Boat"], default=["None"])
                utilities_avail = c2.multiselect("Utilities / Services Available", ["Grid Electricity", "Solar Power", "Piped Water Connection", "Cellular Signal", "Internet / Broadband", "Garbage Collection Service"], default=["Grid Electricity"])
                appliances_owned = c3.multiselect("Appliances Owned", ["Refrigerator", "Television", "Washing Machine", "Electric Fan", "Gas / Electric Stove", "Air Conditioner"], default=["Electric Fan"])

                st.markdown("---")
                st.markdown("**C2. Household Food Insecurity Assessment (Past 30 Days)**")
                c1, c2, c3 = st.columns(3)
                food_skip = c1.selectbox("Skipped meal / reduced portion size due to lack of money?", ["No", "Yes"])
                food_worry = c2.selectbox("Worried about running out of food before having money to buy?", ["No", "Yes"])
                food_fullday = c3.selectbox("Went a full day without eating due to lack of food/money?", ["No", "Yes"])

                st.markdown("---")
                st.markdown("**C3. Housing, Built Environment & Indoor Air Risk**")
                c1, c2, c3 = st.columns(3)
                tenure = c1.selectbox("Tenurial Status", ["Residential lot with house", "Residential House without Lot", "Renting", "Shared", "Farm Land", "Informal Settler / Caretaker"])
                house_type = c2.selectbox("Housing Construction Type", ["Light (Nipa, bamboo, cogon)", "Medium (Wooden floors/walls, G.I. roof)", "Heavy / Permanent (Concrete/hardwood)"])
                cook_fuel = c3.selectbox("Indoor Air Risk (Cooking Fuel)", ["LPG", "Charcoal", "Wood", "Kerosene", "Electric"])

                c1, c2 = st.columns(2)
                is_flood_prone = c1.selectbox("🌊 Is Household Located in a Flood-Prone Zone?", ["No", "Yes"])

                st.markdown("---")
                st.markdown("**C4. WASH Infrastructure & Environmental Health**")
                c1, c2, c3 = st.columns(3)
                water_source = c1.selectbox("Drinking Water Source Level", ["Level 1: Protected Well / Spring", "Level 2: Piped network & communal faucet", "Level 3: Individual household tap", "Unsafe: Shallow Well / River / Surface", "Commercial Refill Station"])
                toilet_type = c2.selectbox("Sanitation / Toilet Facility Type", ["Pour/Flush to Septic Tank", "Ventilated Improved Pit (VIP) Latrine", "Open Defecation / None"])
                solid_disposal = c3.selectbox("Solid Waste Disposal Method", ["Municipal/Barangay Collection", "Composting", "Burying", "Burning (Siga)", "Open Dumping", "River Disposal"])

            # --- TAB 4: DECISION-MAKING PATTERNS ---
            with t_dec:
                st.markdown("**Module D: Decision-Making Pattern & Community Participation**")
                c1, c2 = st.columns(2)
                dec_expenses = c1.multiselect("Who decides on Family Expenses?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Father", "Mother"])
                dec_health = c2.multiselect("Who decides on Health & Medical Care?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Mother"])

            # --- TAB 5: MORBIDITY & CHRONIC CARE ---
            with t_morb:
                st.markdown("**Module E1: Acute Infectious Diseases & Illnesses (Past 12 Months)**")
                c1, c2, c3 = st.columns(3)
                e_diarrhea = c1.selectbox("Diarrheal Episodes (>1 in past 12 mos in family)", ["No", "Yes"])
                e_urti = c2.selectbox("Severe Upper Respiratory Infections / Pneumonia", ["No", "Yes"])
                e_dengue = c3.selectbox("Suspected or Confirmed Dengue Cases", ["No", "Yes"])

                st.markdown("**Module E2: Physician-Diagnosed Chronic Conditions & Treatment Compliance**")
                c1, c2 = st.columns(2)
                htn_status = c1.selectbox("Hypertension Status in Household", ["No Member Diagnosed", "Diagnosed - Compliant with Meds Daily", "Diagnosed - Irregular Med Compliance", "Diagnosed - Unmedicated / Stopped"])
                dm_status = c2.selectbox("Type 2 Diabetes Status in Household", ["No Member Diagnosed", "Diagnosed - Compliant with Meds Daily", "Diagnosed - Irregular Med Compliance", "Diagnosed - Unmedicated / Stopped"])

                c1, c2 = st.columns(2)
                asthma_status = c1.selectbox("Bronchial Asthma / COPD Status", ["No Member Diagnosed", "Diagnosed - Active Maintenance Inhaler", "Diagnosed - Emergency Meds Only", "Diagnosed - Untreated"])
                tb_status = c2.selectbox("Tuberculosis (TB) History & DOTS Status", ["No Member Diagnosed", "Currently Enrolled in TB-DOTS", "Completed TB Treatment", "Defaulted / Interrupted DOTS"])

                c1, c2, c3 = st.columns(3)
                ckd_status = c1.selectbox("Chronic Kidney Disease (CKD)", ["No", "Yes - Stage 1-3", "Yes - Dialysis Dependent"])
                cvd_status = c2.selectbox("Cardiovascular Disease / History of Stroke", ["No", "Yes"])
                cancer_status = c3.selectbox("Active Malignancy / Cancer", ["No", "Yes"])

            # --- TAB 6: MATERNAL, FP & MORTALITY ---
            with t_mch:
                st.markdown("**Module F1: Maternal & Reproductive Health Protocols**")
                c1, c2, c3 = st.columns(3)
                is_preg = c1.selectbox("Currently Pregnant Member in Household?", ["No", "Yes"])
                anc_visits = c2.number_input("Antenatal Care (ANC) Visits (Target ≥4)", 0, 15, 0)
                anc_1st_tri = c3.selectbox("First ANC Visit in 1st Trimester?", ["N/A", "Yes", "No"])

                c1, c2, c3 = st.columns(3)
                ifa_tablets = c1.selectbox("Iron-Folic Acid (IFA) Tablets Received", ["N/A", "<180 Tablets", "≥180 Tablets (Completed)"])
                td_status = c2.selectbox("Tetanus Diphtheria (Td) Immunization", ["N/A", "Td1", "Td2", "Td3+", "Fully Immunized Mother"])
                postpartum_check = c3.selectbox("Postpartum Checkup within 72 hours", ["N/A", "Yes", "No"])

                st.markdown("---")
                st.markdown("**Module F2: Delivery & Family Planning**")
                c1, c2 = st.columns(2)
                deliv_personnel_yesno = c1.selectbox("Delivery handled by trained health personnel?", ["N/A", "Yes", "No"])
                deliv_facility_yesno = c2.selectbox("Delivery handled in an accredited Health Facility?", ["N/A", "Yes", "No"])

                c1, c2 = st.columns(2)
                fp_access = c1.selectbox("Couples with access to family planning services?", ["Yes", "No"])
                fp_practice = c2.selectbox("Couples practicing family planning?", ["Yes", "No"])

                st.markdown("---")
                st.markdown("**Module F3: Mortality Assessment (Jan–Dec)**")
                mortality_yesno = st.selectbox("With deaths in the family due to preventable diseases (Jan-Dec)?", ["No", "Yes"])

            # --- TAB 7: DYNAMIC CHILD PROFILING ---
            with t_child:
                st.markdown(f"**Module F4: Expanded Child Anthropometric & Immunization Record Profiling ({num_children} Child(ren) Active)**")
                
                children_records = []
                for c_i in range(1, int(num_children) + 1):
                    st.markdown(f"<div class='child-card'><strong>👶 Child Member {c_i} Profile & Immunization Screening</strong></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c_name = c1.text_input(f"Child {c_i} Name / Initials", key=f"c_name_{c_i}")
                    c_sex = c2.selectbox(f"Child {c_i} Sex", ["Male", "Female"], key=f"c_sex_{c_i}")
                    c_age_m = c3.number_input(f"Child {c_i} Age (Months)", 0, 59, 12, key=f"c_age_{c_i}")
                    c_wt_kg = c4.number_input(f"Child {c_i} Weight (kg)", 0.0, 35.0, 8.5, key=f"c_wt_{c_i}")
                    c_ht_cm = c5.number_input(f"Child {c_i} Height (cm)", 0.0, 120.0, 72.0, key=f"c_ht_{c_i}")

                    c_nutr = compute_child_nutrition(c_age_m, c_wt_kg, c_ht_cm)
                    st.caption(f"📊 **Outcome:** BMI: {c_nutr['BMI']} | Wasting: **{c_nutr['Wasting']}** | Stunting: **{c_nutr['Stunting']}** | Underweight: **{c_nutr['Underweight']}**")

                    st.markdown(f"**💉 Child {c_i} Immunization Card Check:**")
                    ic1, ic2, ic3, ic4, ic5, ic6 = st.columns(6)
                    imm_bcg = ic1.checkbox("BCG", key=f"bcg_{c_i}")
                    imm_hepb = ic2.checkbox("Hep B", key=f"hepb_{c_i}")
                    imm_penta = ic3.checkbox("Pentavalent 3x", key=f"penta_{c_i}")
                    imm_opv = ic4.checkbox("OPV/IPV 3x", key=f"opv_{c_i}")
                    imm_pcv = ic5.checkbox("PCV 3x", key=f"pcv_{c_i}")
                    imm_mmr = ic6.checkbox("MMR 2x", key=f"mmr_{c_i}")

                    is_fic = all([imm_bcg, imm_hepb, imm_penta, imm_opv, imm_pcv, imm_mmr])
                    fic_status = "Fully Immunized Child (FIC)" if is_fic else "Partially Immunized / Incomplete"

                    c_action = st.multiselect(
                        f"👶 Child {c_i} Action Taken",
                        ["Referral to RHU / Nutrition Officer", "Referral for Supplementary Feeding", "IYCF Counseling", "Immunization Catch-up", "Vitamin A Supplementation", "Deworming Administration", "None / Normal"],
                        default=["None / Normal"] if (is_fic and "Normal" in c_nutr["Wasting"]) else ["Referral to RHU / Nutrition Officer"],
                        key=f"c_action_{c_i}"
                    )

                    if c_name.strip() != "":
                        children_records.append({
                            "Child_Num": f"Child {c_i}", "Name": c_name, "Sex": c_sex, "Age_Months": c_age_m,
                            "Weight": c_wt_kg, "Height": c_ht_cm, "Nutr": c_nutr, "FIC_Status": fic_status,
                            "BCG": imm_bcg, "HepB": imm_hepb, "Penta": imm_penta, "OPV": imm_opv, "PCV": imm_pcv, "MMR": imm_mmr,
                            "Action_Taken": c_action
                        })

            # --- TAB 8: HEALTH-SEEKING BEHAVIOR & YAKAP ---
            with t_yakap:
                st.markdown("**Module G: Health-Seeking Behavior & PhilHealth YAKAP Access**")
                hsb_initial_actions = st.multiselect("Initial Actions When Unwell", ["Rest and wait", "Use home/herbal remedies", "Buy OTC medication", "Search symptoms online", "Ask family/friends", "Contact healthcare provider"], default=["Rest and wait"])
                hsb_providers_used = st.multiselect("Facilities/Providers Used", ["Public hospital", "Private clinic/hospital", "Community health center / RHU", "Local pharmacy", "Traditional practitioner", "Telehealth"], default=["Community health center / RHU"])
                hsb_travel_time = st.selectbox("Travel Time to Nearest Health Facility", ["Less than 15 minutes", "15 to 30 minutes", "30 minutes to 1 hour", "More than 1 hour"])
                hsb_barriers = st.multiselect("Barriers to Seeking Care", ["High cost of consultation/meds", "Long waiting times", "Distance / lack of transpo", "Work/caregiving responsibilities", "Fear of diagnosis", "Lack of insurance coverage"])
                hsb_influencers = st.multiselect("Key Influencers in Decisions", ["Spouse / Immediate family", "Parents / Relatives", "Friends / Peers", "Community / Religious leaders", "Independent decision"], default=["Independent decision"])
                hsb_criteria = st.multiselect("Criteria for Choosing Facility", ["Low cost / insurance", "Proximity", "Short waiting time", "Reputation", "Confidential & respectful staff", "Clean & supplied"])

                c1, c2 = st.columns(2)
                yakap_registered = c1.selectbox("Registered under PhilHealth YAKAP?", ["Yes", "No", "Uncertain"])
                yakap_availed = c2.selectbox("Availed FREE First Patient Encounter (FPE)?", ["Yes", "No", "N/A"])

            if st.form_submit_button("Submit & Save Complete Household Record"):
                primary_sys = adults_data[0]["Sys"] if len(adults_data) > 0 else 120
                primary_risk = adults_data[0]["Risk"] if len(adults_data) > 0 else "Normal"

                marker_color = [192, 38, 211, 230] if (is_flood_prone == "Yes" and primary_sys >= 140) else ([123, 17, 19, 220] if primary_sys >= 140 else ([37, 99, 235, 220] if is_flood_prone == "Yes" else [34, 197, 94, 200]))

                st.session_state.hh_records.append({
                    "HH_ID": hh_id, "Barangay": brgy, "Purok": purok, "Date": str(date_survey), "Lat": lat, "Lon": lon,
                    "Enumerator": enum_name, "Respondent_Role": resp_role, "Survey_Status": surv_status, "Dialect": dialect, "Religion": religion,
                    "Total_Children": tot_children, "Total_Dependents": tot_dependents, "Head_Name": hh_head_name, "Head_Civil_Status": head_civil,
                    "BP": f"{primary_sys}/80", "Risk": primary_risk, "Flood_Prone": is_flood_prone, "Color": marker_color,
                    "Adults": adults_data, "Children": children_records,
                    "Income": income_cat, "Livelihood": livelihood, "Food_Production": food_prod, "Emergency_5k": emergency_5k, "Four_Ps": p4ps_status,
                    "Transport_Owned": transpo_owned, "Utilities": utilities_avail, "Appliances": appliances_owned,
                    "Food_Skip": food_skip, "Food_Worry": food_worry, "Food_FullDay": food_fullday,
                    "Tenure": tenure, "House_Type": house_type, "Cook_Fuel": cook_fuel,
                    "Water": water_source, "Sanitation": toilet_type, "Solid_Disposal": solid_disposal,
                    "Decisions_Expenses": dec_expenses, "Decisions_Health": dec_health,
                    "Diarrhea": e_diarrhea, "URTI": e_urti, "Dengue": e_dengue,
                    "Hypertension_Status": htn_status, "Diabetes_Status": dm_status, "Asthma_Status": asthma_status, "TB_Status": tb_status, "CKD_Status": ckd_status, "CVD_Status": cvd_status, "Cancer_Status": cancer_status,
                    "Is_Pregnant": is_preg, "ANC_Visits": anc_visits, "ANC_1st_Tri": anc_1st_tri, "IFA_Tablets": ifa_tablets, "Td_Status": td_status, "Postpartum_Check": postpartum_check,
                    "Deliv_Personnel": deliv_personnel_yesno, "Deliv_Facility": deliv_facility_yesno, "FP_Access": fp_access, "FP_Practice": fp_practice, "Preventable_Mortality": mortality_yesno,
                    "HSB_Initial_Actions": hsb_initial_actions, "HSB_Providers_Used": hsb_providers_used, "HSB_Travel_Time": hsb_travel_time, "HSB_Barriers": hsb_barriers, "HSB_Influencers": hsb_influencers, "HSB_Criteria": hsb_criteria,
                    "Yakap": yakap_registered, "Yakap_Availed": yakap_availed,
                })
                save_session_to_disk()
                st.success(f"Household record '{hh_id}' saved successfully with dynamic individual profiles!")

    elif mode_p2 == "📊 Phase 2 Interpreted Data & Individual Response Inspection":
        st.markdown("### 📊 Comprehensive Cross-Module Aggregated Interpretation & Inspector")
        
        if len(st.session_state.hh_records) == 0:
            st.info("No household survey records found in Phase 2. Please add entries to view interpreted data.")
        else:
            tab_interp, tab_indiv = st.tabs([
                "📈 Aggregated Cross-Module Interpretation Dashboard", 
                "🔍 Individual Response Inspector (All Modules)"
            ])

            with tab_interp:
                total_hhs = len(st.session_state.hh_records)
                all_adults = [a for hh in st.session_state.hh_records for a in hh.get("Adults", [])]
                all_children = [c for hh in st.session_state.hh_records for c in hh.get("Children", [])]

                st.markdown(f"#### 🌐 Overview: Aggregate Coverage ({total_hhs} Households | {len(all_adults)} Adults Profiled | {len(all_children)} Children Profiled)")

                st.markdown("##### 1. Demographics, Dialect & Adult Physical Screening")
                col1, col2, col3, col4 = st.columns(4)
                
                dialects_cnt = Counter([hh.get("Dialect", "N/A") for hh in st.session_state.hh_records])
                top_dialect = dialects_cnt.most_common(1)[0][0] if dialects_cnt else "N/A"
                col1.metric("Primary Dialect", top_dialect)

                htn_cases = sum(1 for a in all_adults if a.get("Risk") == "Hypertensive Risk" or a.get("Sys", 0) >= 140 or a.get("Dia", 0) >= 90)
                col2.metric("Adult Hypertensive Risk", f"{htn_cases} / {len(all_adults)} ({(htn_cases/len(all_adults)*100 if len(all_adults) else 0):.1f}%)")

                hypox_cases = sum(1 for a in all_adults if a.get("Risk") == "Hypoxemic (<95%)" or (a.get("SpO2", 100) < 95 and a.get("SpO2", 0) > 0))
                col3.metric("Hypoxemia (<95% SpO2)", f"{hypox_cases} Adults")

                abnormal_vitals = sum(1 for a in all_adults if a.get("Risk") != "Normal")
                col4.metric("Abnormal Vitals Total", f"{abnormal_vitals} Adults")

                with st.expander("📌 View Symptoms, Age, Gender & Occupation Breakdown"):
                    c_sym, c_occ = st.columns(2)
                    all_symptoms = [sym for a in all_adults for sym in a.get("Complaints", []) if sym != "None"]
                    c_sym.markdown("**Top Adult Complaints / Symptoms:**")
                    c_sym.write(pd.Series(all_symptoms).value_counts().rename("Count") if all_symptoms else "No reported symptoms.")

                    all_occs = [a.get("Occupation") for a in all_adults if a.get("Occupation")]
                    c_occ.markdown("**Adult Primary Occupations:**")
                    c_occ.write(pd.Series(all_occs).value_counts().rename("Count") if all_occs else "No reported occupations.")

                st.markdown("---")
                st.markdown("##### 2. Socio-Economic Profile, Assets & Household Food Security")
                c1, c2, c3, c4, c5 = st.columns(5)

                food_prod_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Food_Production") == "Yes")
                c1.metric("Engaged in Food Prod.", f"{food_prod_cnt} ({(food_prod_cnt/total_hhs)*100:.1f}%)")

                emerg_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Emergency_5k") == "Yes")
                c2.metric("₱5k Emergency Cushion", f"{emerg_cnt} ({(emerg_cnt/total_hhs)*100:.1f}%)")

                p4ps_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Four_Ps") == "Yes")
                c3.metric("4Ps Beneficiaries", f"{p4ps_cnt} ({(p4ps_cnt/total_hhs)*100:.1f}%)")

                food_insec_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Food_Skip") == "Yes" or hh.get("Food_Worry") == "Yes" or hh.get("Food_FullDay") == "Yes")
                c4.metric("Food Insecure HHs", f"{food_insec_cnt} ({(food_insec_cnt/total_hhs)*100:.1f}%)")

                flood_hh_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Flood_Prone") == "Yes")
                c5.metric("Flood-Prone HHs", f"{flood_hh_cnt} ({(flood_hh_cnt/total_hhs)*100:.1f}%)")

                with st.expander("📌 View Income, Housing Built, Appliances & Transportation Details"):
                    ca, cb, cc = st.columns(3)
                    ca.markdown("**Income Category Distribution:**")
                    ca.write(pd.Series([hh.get("Income") for hh in st.session_state.hh_records]).value_counts())

                    cb.markdown("**Housing Construction Type:**")
                    cb.write(pd.Series([hh.get("House_Type") for hh in st.session_state.hh_records]).value_counts())

                    cc.markdown("**Indoor Cooking Fuel Risk:**")
                    cc.write(pd.Series([hh.get("Cook_Fuel") for hh in st.session_state.hh_records]).value_counts())

                st.markdown("---")
                st.markdown("##### 3. WASH Infrastructure & Decision-Making Patterns")
                w1, w2, w3, w4 = st.columns(4)

                unsafe_w = sum(1 for hh in st.session_state.hh_records if "Unsafe" in hh.get("Water", ""))
                w1.metric("Unsafe Drinking Water", f"{unsafe_w} HHs")

                open_def = sum(1 for hh in st.session_state.hh_records if "Open Defecation" in hh.get("Sanitation", ""))
                w2.metric("Open Defecation Risk", f"{open_def} HHs")

                siga_burn = sum(1 for hh in st.session_state.hh_records if "Burning" in hh.get("Solid_Disposal", ""))
                w3.metric("Waste Burning (Siga)", f"{siga_burn} HHs")

                health_dec_mom = sum(1 for hh in st.session_state.hh_records if "Mother" in hh.get("Decisions_Health", []))
                w4.metric("Health Decisions by Mother", f"{health_dec_mom} HHs")

                st.markdown("---")
                st.markdown("##### 4. Infectious Morbidity & Chronic Disease Compliance")
                m1, m2, m3, m4 = st.columns(4)

                diarrhea_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Diarrhea") == "Yes")
                m1.metric("Diarrheal Outbreaks", f"{diarrhea_cnt} HHs")

                dengue_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Dengue") == "Yes")
                m2.metric("Dengue Cases", f"{dengue_cnt} HHs")

                htn_diag_cnt = sum(1 for hh in st.session_state.hh_records if "Diagnosed" in hh.get("Hypertension_Status", ""))
                m3.metric("Diagnosed Hypertension", f"{htn_diag_cnt} HHs")

                dm_diag_cnt = sum(1 for hh in st.session_state.hh_records if "Diagnosed" in hh.get("Diabetes_Status", ""))
                m4.metric("Diagnosed Diabetes", f"{dm_diag_cnt} HHs")

                st.markdown("---")
                st.markdown("##### 5. Maternal Care, Child Anthropometrics & PhilHealth YAKAP Access")
                p1, p2, p3, p4, p5 = st.columns(5)

                preg_cnt = sum(1 for hh in st.session_state.hh_records if hh.get("Is_Pregnant") == "Yes")
                p1.metric("Active Pregnancies", f"{preg_cnt}")

                fic_cnt = sum(1 for c in all_children if c.get("FIC_Status") == "Fully Immunized Child (FIC)")
                p2.metric("Child FIC Rate", f"{fic_cnt} / {len(all_children)} ({(fic_cnt/len(all_children)*100 if len(all_children) else 0):.1f}%)")

                stunted_cnt = sum(1 for c in all_children if "Stunted" in c.get("Nutr", {}).get("Stunting", ""))
                p3.metric("Stunted Children", f"{stunted_cnt}")

                yakap_reg = sum(1 for hh in st.session_state.hh_records if hh.get("Yakap") == "Yes")
                p4.metric("PhilHealth YAKAP Reg.", f"{yakap_reg} ({(yakap_reg/total_hhs)*100:.1f}%)")

                yakap_avail = sum(1 for hh in st.session_state.hh_records if hh.get("Yakap_Availed") == "Yes")
                p5.metric("Availed YAKAP FPE", f"{yakap_avail}")

            with tab_indiv:
                hh_ids = [f"{r.get('HH_ID', 'N/A')} - {r.get('Barangay', 'N/A')} ({r.get('Head_Name', 'No Head')})" for r in st.session_state.hh_records]
                sel_hh_idx = st.selectbox("Select Household Record to Inspect", range(len(hh_ids)), format_func=lambda x: hh_ids[x])
                selected_record = st.session_state.hh_records[sel_hh_idx]
                
                st.markdown(f"### 🏠 Inspection for Record: `{selected_record.get('HH_ID', 'N/A')}`")
                
                i_t1, i_t2, i_t3, i_t4, i_t5 = st.tabs(["📌 Profile & Metadata", "🩺 Adult Profiling Data", "👶 Child Profiling Data", "🌾 WASH & Housing", "🏥 Health-Seeking & YAKAP"])
                
                with i_t1:
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Barangay:** {selected_record.get('Barangay', 'N/A')}")
                    c2.write(f"**Purok:** {selected_record.get('Purok', 'N/A')}")
                    c3.write(f"**Survey Date:** {selected_record.get('Date', 'N/A')}")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Head Name:** {selected_record.get('Head_Name', 'N/A')}")
                    c2.write(f"**Civil Status:** {selected_record.get('Head_Civil_Status', 'N/A')}")
                    c3.write(f"**Enumerator:** {selected_record.get('Enumerator', 'N/A')}")

                with i_t2:
                    st.markdown("#### 🩺 Dynamic Adult Profiling Data")
                    adults_list = selected_record.get("Adults", [])
                    if len(adults_list) == 0:
                        st.info("No detailed adult profile rows recorded for this household.")
                    else:
                        st.dataframe(pd.DataFrame(adults_list), use_container_width=True)

                with i_t3:
                    st.markdown("#### 👶 Dynamic Child Profiling & Immunization Data")
                    children_list = selected_record.get("Children", [])
                    if len(children_list) == 0:
                        st.info("No detailed child profile rows recorded for this household.")
                    else:
                        st.dataframe(pd.DataFrame(children_list), use_container_width=True)

                with i_t4:
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Monthly Income:** {selected_record.get('Income', 'N/A')}")
                    c2.write(f"**Water Source:** {selected_record.get('Water', 'N/A')}")
                    c3.write(f"**Sanitation/Toilet:** {selected_record.get('Sanitation', 'N/A')}")

                with i_t5:
                    c1, c2 = st.columns(2)
                    c1.write(f"**PhilHealth YAKAP Registered:** {selected_record.get('Yakap', 'N/A')}")
                    c2.write(f"**Availed FPE / Meds:** {selected_record.get('Yakap_Availed', 'N/A')}")

    else:
        st.markdown("### 📂 Submitted Household Survey Records")
        if len(st.session_state.hh_records) == 0:
            st.info("No household records found.")
        else:
            hh_options = [f"[{i+1}] {r.get('HH_ID', 'N/A')} - {r.get('Barangay', 'N/A')} ({r.get('Purok', 'N/A')})" for i, r in enumerate(st.session_state.hh_records)]
            selected_idx = st.selectbox("Select Household Record to Review / Edit", range(len(hh_options)), format_func=lambda x: hh_options[x])
            rec = st.session_state.hh_records[selected_idx]

            with st.form("edit_hh_form"):
                e_hh_id = st.text_input("Household ID", value=rec.get("HH_ID", ""))
                e_brgy = st.selectbox("Barangay Name", PALO_BARANGAYS, index=PALO_BARANGAYS.index(rec.get("Barangay")) if rec.get("Barangay") in PALO_BARANGAYS else 0)
                e_purok = st.text_input("Purok", value=rec.get("Purok", ""))

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Household Edits"):
                        rec.update({"HH_ID": e_hh_id, "Barangay": e_brgy, "Purok": e_purok})
                        st.session_state.hh_records[selected_idx] = rec
                        save_session_to_disk()
                        st.success("Household record updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Household Record"):
                        st.session_state.hh_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("Household record deleted successfully!")
                        st.rerun()

# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS (INTACT - UNCHANGED CONTENT)
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader("Phase 3: Qualitative Field Tools (KII & FGD Structured Guides)")

    tool_choice = st.selectbox(
        "Select Qualitative Tool Instrument",
        [
            "TOOL 3.1: KEY INFORMANT INTERVIEW (KII) GUIDE — GOVERNANCE & LEADERSHIP",
            "TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE PERSONNEL",
            "TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS",
        ],
    )

    if tool_choice == "TOOL 3.1: KEY INFORMANT INTERVIEW (KII) GUIDE — GOVERNANCE & LEADERSHIP":
        st.markdown("### 🏛️ TOOL 3.1: KEY INFORMANT INTERVIEW (KII) GUIDE — GOVERNANCE & LEADERSHIP")
        st.caption("**Target Respondents / Participants:** Punong Barangay, Committee Chair on Health, Municipal Health Officer (MHO)")
        st.caption("**Objective:** Assess political commitment, budget prioritization, legislative output, supply chain resilience, and health equity vision.")

        with st.form("kii_gov_form"):
            st.markdown("#### 📋 Respondent & Interview Administrative Metadata")
            c1, c2 = st.columns(2)
            resp_name = c1.text_input("Respondent Name")
            pos_desig = c2.multiselect("Position / Designation", ["Punong Barangay", "Health Chair", "MHO"], default=["Punong Barangay"])

            c1, c2 = st.columns(2)
            brgy_lgu = c1.selectbox("Barangay / LGU (Palo, Leyte)", PALO_BARANGAYS)
            date_time = c2.text_input("Date & Time of Interview", "09 / 07 / 2026 | 09:00 AM")

            c1, c2 = st.columns(2)
            interviewer = c1.selectbox("Interviewer Name", ENUMERATORS)
            note_taker = c2.text_input("Note-Taker Name")

            c1, c2 = st.columns(2)
            consent = c1.radio("Informed Consent Signed?", ["Yes", "No"], horizontal=True)
            audio_rec = c2.radio("Audio Recorded?", ["Yes (Permission Granted)", "No"], horizontal=True)

            st.markdown("---")
            st.markdown("#### 🗣️ Qualitative Interview Domains & Probing Prompts")

            st.markdown("**1. Resource Allocation & AIP Prioritization**")
            st.info("How does the Barangay Council prioritize health within the Annual Investment Plan (AIP)? What specific percentage of local revenue is earmarked for healthcare operations?")
            st.caption("• What specific health line-items were funded this year vs last year?\n• How are competing development priorities (e.g., roads, infrastructure vs health) negotiated during budget calls?\n• Is the health budget sufficient to meet actual community needs? If not, what gets cut?\n• Are discretionary or emergency contingency funds accessible for unexpected disease outbreaks?")
            q1_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 1)", key="kii_g_q1")

            st.markdown("**2. Policy Infrastructure & Enforcement**")
            st.info("What local health ordinances passed over the last 3 years have had the most direct impact on community health, and what are the key enforcement hurdles?")
            st.caption("• Which specific ordinances (e.g., Sanitation, Dengue, Anti-Smoking, WASH, Rabies Control) are actively enforced?\n• What are the main obstacles to enforcement (e.g., lack of enforcers, political friction, community resistance, lack of penalties)?\n• How is the Barangay Health Board involved in policy drafting and monitoring?")
            q2_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 2)", key="kii_g_q2")

            st.markdown("**3. Supply Chain Integrity & Emergency Procurement**")
            st.info("When the Barangay Health Station experiences stock-outs of essential medicines, what is the protocol for emergency procurement through the RHU or LGU?")
            st.caption("• What essential drugs or medical supplies suffer from frequent stock-outs (e.g., maintenance meds, vaccines, testing kits)?\n• How long does the emergency requisition process take from request to delivery?\n• Is there a dedicated barangay petty cash / buffer fund for urgent medical supply purchases?")
            q3_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 3)", key="kii_g_q3")

            st.markdown("**4. Health Inequity & Disadvantaged Populations**")
            st.info("In your view, which specific Purok or sub-population in this barangay suffers from the most severe health disadvantages, and why?")
            st.caption("• What drive these disparities (e.g., geographical isolation, informal settler status, lack of clean water, poverty, transport barriers)?\n• What targeted health programs or budget allocations are specifically directed at these vulnerable groups?\n• How are PWDs, senior citizens, and malnourished children tracked and prioritized?")
            q4_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 4)", key="kii_g_q4")

            st.markdown("**5. Strategic Governance Synthesis & Vision**")
            st.info("What single administrative or policy change at the Municipal / LGU level would most dramatically improve health governance in this barangay?")
            st.caption("• What support is most urgently needed from the Municipal Health Office (MHO) or Provincial Health Office (PHO)?\n• How can inter-local health zone cooperation or RHU-Barangay coordination be strengthened?")
            q5_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 5)", key="kii_g_q5")

            if st.form_submit_button("💾 Save TOOL 3.1 Interview Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.1: KII — Governance & Leadership",
                    "Respondent": resp_name, "Designation": pos_desig, "Barangay": brgy_lgu, "Date_Time": date_time,
                    "Interviewer": interviewer, "Note_Taker": note_taker, "Consent": consent, "Audio": audio_rec,
                    "D1_ResourceAllocation": q1_notes, "D2_PolicyEnforcement": q2_notes, "D3_SupplyChain": q3_notes,
                    "D4_HealthInequity": q4_notes, "D5_GovernanceVision": q5_notes
                })
                save_session_to_disk()
                st.success("TOOL 3.1 KII Governance Record Saved Successfully!")

    elif tool_choice == "TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE PERSONNEL":
        st.markdown("### 👩‍⚕️ TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE PERSONNEL")
        st.caption("**Target Respondents / Participants:** Rural Health Midwife, Barangay Health Worker (BHW) President, Barangay Nutrition Scholar (BNS)")
        st.caption("**Objective:** Uncover operational bottlenecks, clinical workload realities, supply deficits, emergency referral breakdowns, and treatment adherence barriers.")

        with st.form("kii_frontline_form"):
            st.markdown("#### 📋 Respondent & Administrative Metadata")
            c1, c2 = st.columns(2)
            resp_name = c1.text_input("Respondent Name")
            role = c2.multiselect("Frontline Role", ["Midwife", "BHW President", "BNS"], default=["Midwife"])

            c1, c2 = st.columns(2)
            bhs_name = c1.text_input("Barangay Health Station")
            date_time = c2.text_input("Date & Time", "09 / 07 / 2026 | 10:30 AM")

            c1, c2 = st.columns(2)
            interviewer = c1.selectbox("Interviewer Name", ENUMERATORS)
            years_service = c2.number_input("Years of Service in Barangay", 0, 50, 5)

            c1, c2 = st.columns(2)
            consent = c1.radio("Informed Consent Signed?", ["Yes", "No"], horizontal=True)
            audio_rec = c2.radio("Audio Recorded?", ["Yes", "No"], horizontal=True)

            st.markdown("---")
            st.markdown("#### 🗣️ Qualitative Interview Domains & Probing Prompts")

            st.markdown("**1. Clinical Workload & Essential Supply Deficits**")
            st.info("What are the top three health conditions you encounter daily among residents, and what medical supplies do you routinely lack to address them?")
            st.caption("• Which specific drugs, equipment, or diagnostic reagents are routinely missing at the BHS (e.g., BP apparatus, glucometer strips, prenatal vitamins, antibiotics)?\n• How do you manage patient care when essential supplies are unavailable?\n• What is the average daily patient load per frontline worker, and how does it impact care quality?")
            q1_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 1)", key="kii_f_q1")

            st.markdown("**2. Emergency Referral Pathway & Pipeline Breakdown**")
            st.info("Walk us through a critical patient emergency in a remote Purok. What breaks down in the transportation and referral pipeline to the RHU or Provincial Hospital?")
            st.caption("• Is a functional ambulance or barangay patrol vehicle available 24/7? Who pays for fuel and driver honoraria during emergencies?\n• What communication challenges exist between BHS workers and the RHU/hospital during pre-referral transfers?\n• How are financial barriers to emergency transport handled for indigent patients?")
            q2_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 2)", key="kii_f_q2")

            st.markdown("**3. Non-Medical Treatment Adherence Barriers**")
            st.info("How frequently do patients fail to adhere to chronic treatment (e.g., TB-DOTS, hypertension, diabetes) because they cannot afford food or transport fare?")
            st.caption("• What percentage of chronic disease patients drop out or skip medications due to poverty or inability to pay fare to RHU?\n• How do frontline workers perform home visits or follow-ups for non-compliant patients?\n• Are there supplementary food or transport assistance programs available for patients on long-term treatment?")
            q3_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 3)", key="kii_f_q3")

            st.markdown("**4. Systemic Worker Bottlenecks & Capacity Needs**")
            st.info("What structural or personal challenges (e.g., delayed honoraria, lack of training, personal safety, excessive reporting) affect your daily performance and morale?")
            st.caption("• Are BHW/BNS honoraria paid regularly and on time? If delayed, by how many months?\n• What specific clinical, record-keeping, or emergency management training do you feel you lack?\n• How adequate are the BHS facilities (electricity, clean water, privacy, waste management)?")
            q4_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 4)", key="kii_f_q4")

            if st.form_submit_button("💾 Save TOOL 3.2 Interview Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.2: KII — Frontline Personnel",
                    "Respondent": resp_name, "Role": role, "BHS": bhs_name, "Date_Time": date_time,
                    "Interviewer": interviewer, "Years_Service": years_service, "Consent": consent, "Audio": audio_rec,
                    "D1_SupplyDeficits": q1_notes, "D2_ReferralBreakdown": q2_notes, "D3_AdherenceBarriers": q3_notes, "D4_WorkerBottlenecks": q4_notes
                })
                save_session_to_disk()
                st.success("TOOL 3.2 KII Frontline Record Saved Successfully!")

    elif tool_choice == "TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS":
        st.markdown("### 👥 TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS")
        st.caption("**Target Respondents / Participants:** 6–10 Community Representatives (Mothers, Senior Citizens, Informal Settlers, PWDs, Youth Leaders)")
        st.caption("**Objective:** Capture community healthcare-seeking behavior, financial hardship, catastrophic expenses, provider interaction quality, and grassroots priorities.")

        with st.expander("📜 GROUND RULES FOR FACILITATOR", expanded=True):
            st.markdown("""
            1. Welcome participants, explain session purpose, and ensure all participants sign the informed consent form.
            2. Emphasize confidentiality: *'There are no right or wrong answers. What is shared here stays in this room.'*
            3. Encourage equal participation; ensure vocal participants do not dominate and quiet members are gently invited to speak.
            4. Maintain a neutral, non-judgmental tone throughout.
            """)

        with st.form("fgd_community_form"):
            st.markdown("#### 📋 Session Administrative & Group Composition Metadata")
            c1, c2 = st.columns(2)
            brgy_loc = c1.selectbox("Barangay / Location (Palo, Leyte)", PALO_BARANGAYS)
            grp_comp = c2.multiselect("Group Composition", ["Mothers", "Seniors", "PWDs", "Mixed"], default=["Mothers"])

            c1, c2, c3, c4 = st.columns(4)
            date_time = c1.text_input("Date & Time", "09 / 07 / 2026 | 02:00 PM")
            tot_parts = c2.number_input("Total Participants", 1, 20, 8)
            male_cnt = c3.number_input("Male Count", 0, 20, 2)
            female_cnt = c4.number_input("Female Count", 0, 20, 6)

            c1, c2 = st.columns(2)
            moderator = c1.selectbox("Moderator / Facilitator Name", ENUMERATORS)
            note_taker = c2.text_input("Note-Taker / Observer Name")

            c1, c2 = st.columns(2)
            consent = c1.radio("Informed Consent Granted by All?", ["Yes", "No"], horizontal=True)
            audio_rec = c2.radio("Audio Recorded?", ["Yes", "No"], horizontal=True)

            st.markdown("---")
            st.markdown("#### 🗣️ FGD Discussion Domains & Probing Prompts")

            st.markdown("**1. Health Seeking Decision Dynamics**")
            st.info("When someone in your family falls sick, how do you decide whether to go to the BHS, RHU, private clinic, or traditional healer (albularyo)?")
            st.caption("• What are the main deciding factors (e.g., travel cost, distance, waiting time, availability of doctor, trust, emergency severity)?\n• Who in the household makes the final decision regarding medical treatment?\n• Under what circumstances do residents bypass the BHS and go straight to hospital or private clinics?")
            q1_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 1)", key="fgd_q1")

            st.markdown("**2. Catastrophic Healthcare Expenses & Coping**")
            st.info("Have you ever been forced to choose between buying prescribed medicines/paying transport fare and purchasing food for your family? How did you manage?")
            st.caption("• How do families cope with sudden medical expenses (e.g., selling livestock/possessions, taking high-interest loans, seeking political favors)?\n• Are PhilHealth, MAIP, or local medical assistance programs accessible to informal settlers and poor residents?\n• Have medical expenses ever forced a child out of school or led to severe debt?")
            q2_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 2)", key="fgd_q2")

            st.markdown("**3. Provider-Patient Interaction & Quality Perception**")
            st.info("How do you feel treated when visiting public health facilities (BHS vs RHU)? Do you feel respected, listened to, and fully informed about your treatment plan?")
            st.caption("• Have you experienced long waiting times, harsh treatment, or lack of privacy during medical consultations?\n• Do facility operating hours accommodate working residents and agricultural laborers?\n• Do health workers explain medication instructions clearly in the local dialect?")
            q3_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 3)", key="fgd_q3")

            st.markdown("**4. Community Priorities & Grassroots Solutions**")
            st.info("If your community could fix ONE major health problem in this barangay today, what should it be and how should local leaders solve it?")
            st.caption("• What essential health service is most urgently missing in your barangay?\n• What concrete message or request do you want to convey directly to the Mayor and Barangay Captain regarding health services?")
            q4_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 4)", key="fgd_q4")

            if st.form_submit_button("💾 Save TOOL 3.3 FGD Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.3: FGD — Community Members",
                    "Barangay": brgy_loc, "Group_Composition": grp_comp, "Date_Time": date_time,
                    "Total_Participants": tot_parts, "Male": male_cnt, "Female": female_cnt,
                    "Moderator": moderator, "Note_Taker": note_taker, "Consent": consent, "Audio": audio_rec,
                    "D1_DecisionDynamics": q1_notes, "D2_CatastrophicExpenses": q2_notes, "D3_ProviderInteraction": q3_notes, "D4_CommunityPriorities": q4_notes
                })
                save_session_to_disk()
                st.success("TOOL 3.3 FGD Record Saved Successfully!")

    st.markdown("---")
    st.markdown("### 📂 Review Submitted Qualitative Records")
    if len(st.session_state.qual_records) == 0:
        st.info("No qualitative records logged yet.")
    else:
        q_options = [f"[{i+1}] {r.get('Tool', 'Qual Note')} - {r.get('Barangay', r.get('BHS', 'Location N/A'))}" for i, r in enumerate(st.session_state.qual_records)]
        sel_q_idx = st.selectbox("Select Record to Inspect / Delete", range(len(q_options)), format_func=lambda x: q_options[x])
        q_rec = st.session_state.qual_records[sel_q_idx]

        st.json(q_rec)
        if st.button("🗑️ Delete This Qualitative Record", key="del_qual"):
            st.session_state.qual_records.pop(sel_q_idx)
            save_session_to_disk()
            st.success("Qualitative record deleted!")
            st.rerun()

# MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader("Phase 4: Separated & Expanded Environmental Observation Matrices & PERI Index Manual")

    p4_tab1, p4_tab2, p4_tab3 = st.tabs([
        "📋 Field Survey Assessment Matrix",
        "📖 Comprehensive Result Interpretation & Manual",
        "📂 Review & Delete Saved Field Assessments"
    ])

    with p4_tab1:
        with st.form("phase4_expanded_observation_form"):
            st.markdown("### 📌 Field Survey Metadata")
            c1, c2, c3 = st.columns(3)
            purok_eval = c1.selectbox("Target Purok Evaluated", [f"Purok {i}" for i in range(1, 8)])
            eval_date = c2.date_input("Evaluation Date")
            evaluator_name = c3.selectbox("Lead Evaluator", ENUMERATORS)

            def render_rating(col1, col2, col3, label, choices, default_idx=0):
                rating = col2.radio(label, choices, index=default_idx, key=f"r_{label}")
                notes = col3.text_input("Hotspot / Landmark Notes", key=f"n_{label}")
                score_val = 1.0 if "1" in rating else (2.0 if "2" in rating else 3.0)
                return score_val, rating, notes

            # DOMAIN 1
            st.markdown("<div class='peri-domain-header'>Domain 1: Sanitation & Waste Management Assessment</div>", unsafe_allow_html=True)
            d1_scores = []
            d1_data = {}
            
            d1_params = [
                ("1.1 Uncollected Household Solid Waste", "Presence of uncollected trash piles, scattered plastic, household waste heaps on road shoulders or vacant lots.", ["Clean (1)", "Moderate (2)", "Severe Risk (3)"]),
                ("1.2 Open Drainage & Canal Integrity", "Condition of roadside canals: clogged with refuse, unpaved ditching, dark stagnant greywater, or uncovered open channels.", ["Adequate (1)", "Substandard (2)", "Hazardous (3)"]),
                ("1.3 Stagnant Water & Pooling", "Pools of standing water in road depressions, unpaved alleys, or tires/containers holding water >48 hrs (mosquito risk).", ["Low Risk (1)", "Moderate (2)", "Severe Risk (3)"]),
                ("1.4 Stray & Unattended Animals", "Free-roaming dogs, cats, or livestock (pigs/goats) scavenging around uncontained waste or public pathways.", ["Controlled (1)", "Moderate (2)", "Uncontrolled (3)"]),
                ("1.5 Material Recovery & Garbage Hubs", "Condition of Purok MRF or communal collection points: overflowing bins, lack of waste segregation, lack of covers.", ["Clean / Segregated (1)", "Overflowing (2)", "Dilapidated / None (3)"]),
                ("1.6 Open Waste Burning (Siga)", "Visual evidence or smell of open garbage/plastic/leaf burning in backyards, vacant plots, or road edges.", ["Absent (1)", "Occasional (2)", "Frequent/Severe (3)"]),
                ("1.7 Odor & Airborne Emissions", "Pungent or offensive odor emanating from decomposed waste, open sewage, or livestock pens near residential homes.", ["Odor-Free (1)", "Moderate Odor (2)", "Severe / Noxious (3)"]),
                ("1.8 Fecal Contamination Exposure", "Visible animal feces or human defecation marks along walkways, drainage channels, or play areas.", ["None Visible (1)", "Isolated (2)", "Widespread Risk (3)"]),
                ("1.9 Commercial / Market Waste", "Accumulation of rotting produce, fish water, or commercial trash around sari-sari stores, bakeries, or talipapa.", ["Sanitary (1)", "Substandard (2)", "Severe Risk (3)"])
            ]

            for param, indicator, options in d1_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d1_scores.append(s_val)
                d1_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 2
            st.markdown("<div class='peri-domain-header'>Domain 2: Food Environment & Nutritional Accessibility Assessment</div>", unsafe_allow_html=True)
            d2_scores = []
            d2_data = {}
            d2_params = [
                ("2.1 Fresh Produce Access (Talipapa / Markets)", "Presence of permanent or satellite fresh fruit, vegetable, and fresh protein (fish/meat) markets within 300m walking distance.", ["High Access (1)", "Limited Access (2)", "Food Desert (3)"]),
                ("2.2 Sari-Sari Store Food Profile", "Dominance of ultra-processed salty snacks, sugary carbonated beverages, and instant noodles displayed prominently at eye level.", ["Balanced / Healthy (1)", "Junk-Dominant (2)", "Unhealthy Swamp (3)"]),
                ("2.3 Produce Quality & Freshness", "Physical condition of available fruits/vegetables at local outlets: fresh, crisp vs. wilted, decaying, or insect-damaged.", ["High Quality (1)", "Mixed Quality (2)", "Poor / Spoiled (3)"]),
                ("2.4 Street Food Vending Hygiene", "Prepared street food stalls: use of food covers, glass displays, clean water for utensil washing, hairnets/gloves, fly presence.", ["Sanitary (1)", "Substandard (2)", "Unsanitary / High Risk (3)"]),
                ("2.5 Child-Targeted Marketing", "Prominent advertising banners or eye-level store displays targeting school children with sugary drinks, candies, and sodium snacks.", ["Low Exposure (1)", "Moderate (2)", "High / Aggressive (3)"]),
                ("2.6 Tobacco & Alcohol Visibility", "Prominent display and sale of cigarettes/e-cigarettes and alcoholic beverages near youth gathering points or school zones.", ["Restricted / Far (1)", "Moderate (2)", "Highly Visible (3)"]),
                ("2.7 Safe Drinking Water Refilling Outlets", "Availability and physical sanitary condition of commercial water refilling stations or public potable water taps in the Purok.", ["Accessible & Clean (1)", "Scarcely Available (2)", "Unsightly / Risky (3)"])
            ]

            for param, indicator, options in d2_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d2_scores.append(s_val)
                d2_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 3
            st.markdown("<div class='peri-domain-header'>Domain 3: Built Environment, Housing Quality & Infrastructure</div>", unsafe_allow_html=True)
            d3_scores = []
            d3_data = {}
            d3_params = [
                ("3.1 Housing Structural Integrity", "Proportion of concrete/permanent housing vs. makeshift, tarpaulin, light bamboo, or deteriorated wood structures.", ["Mostly Concrete (1)", "Mixed Structural (2)", "Predominantly Makeshift (3)"]),
                ("3.2 Pedestrian Walkways & Sidewalks", "Availability of paved, unblocked sidewalks or footpaths separated from vehicle traffic vs. pedestrians walking on main road shoulders.", ["Safe / Paved (1)", "Partial / Blocked (2)", "Absent / Dangerous (3)"]),
                ("3.3 Street Lighting & Night Safety", "Operational street lights every 30-50m along primary pathways to ensure safe pedestrian travel at night.", ["Well Lit (1)", "Partially Lit (2)", "Dark / Hazardous (3)"]),
                ("3.4 Green Spaces & Recreational Areas", "Access to maintained parks, open community spaces, trees, or sports grounds for physical activity.", ["Abundant (1)", "Limited (2)", "None / Concrete Desert (3)"]),
                ("3.5 Electrical Wiring & Fire Hazard", "Condition of overhead power lines: organized wiring vs. tangled 'spiderweb' illegal connections near residential roofs.", ["Organized / Safe (1)", "Moderate Risk (2)", "Hazardous Spiderwebs (3)"]),
                ("3.6 Road Conditions & Transit Access", "Paved concrete roads allowing smooth ambulance and vehicle access vs. unpaved, rutted, unpassable dirt pathways.", ["Fully Paved (1)", "Partially Paved (2)", "Unpaved / Impassable (3)"]),
                ("3.7 Noise & Industrial Pollution", "Proximity to high-decibel noise (highways, heavy machinery) or industrial smokestacks/workshops emitting particulates.", ["Quiet / Clean (1)", "Moderate Noise/Dust (2)", "Severe Industrial Nuisance (3)"])
            ]

            for param, indicator, options in d3_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d3_scores.append(s_val)
                d3_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 4
            st.markdown("<div class='peri-domain-header'>Domain 4: Healthcare Infrastructure & Emergency Referral Connectivity</div>", unsafe_allow_html=True)
            d4_scores = []
            d4_data = {}
            d4_params = [
                ("4.1 Proximity to BHS / RHU Facility", "Physical distance from Purok center to nearest functional Barangay Health Station or Rural Health Unit.", ["< 500 meters (1)", "500m - 1.5km (2)", "> 1.5km / Isolated (3)"]),
                ("4.2 Emergency Ambulance Access", "Ability of standard 4-wheel emergency ambulance to enter Purok alleys directly to patient doorstep.", ["Direct Access (1)", "Main Road Only (2)", "Inaccessible / Stretcher Only (3)"]),
                ("4.3 Cellular & Communication Signal", "Reliability of mobile phone coverage (Globe/Smart) for calling emergency services or BHWs.", ["Strong 4G/5G (1)", "Spotty Signal (2)", "Dead Zone / No Signal (3)"]),
                ("4.4 Local Health Information Postings", "Visibility of updated health bulletin boards, emergency hotlines, or clinic schedule posters in public areas.", ["Visible & Updated (1)", "Outdated / Faded (2)", "None Visible (3)"]),
                ("4.5 Pharmacy & Medicine Access", "Availability of accredited botika / pharmacy stocked with basic over-the-counter and maintenance meds within walking distance.", ["Accessible (1)", "Limited OTC Stock (2)", "No Pharmacy Access (3)"])
            ]

            for param, indicator, options in d4_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d4_scores.append(s_val)
                d4_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 5
            st.markdown("<div class='peri-domain-header'>Domain 5: Disaster Preparedness & Climate Hazard Vulnerability</div>", unsafe_allow_html=True)
            d5_scores = []
            d5_data = {}
            d5_params = [
                ("5.1 Flood Inundation Susceptibility", "Topographic vulnerability to waterlogging during heavy rain: low-lying riverbanks, coastal tidal surge, or poor run-off.", ["High Ground / Dry (1)", "Seasonal Puddling (2)", "Chronic Deep Flooding (3)"]),
                ("5.2 Evacuation Center Accessibility", "Distance and safe route accessibility to designated typhoon/disaster evacuation centers.", ["Safe & Nearby (1)", "Moderate Route (2)", "Distant / Treacherous (3)"]),
                ("5.3 Landslide & Soil Erosion Vulnerability", "Proximity of houses to unstable soil slopes, cliff edges, or unfortified riverbanks prone to collapsing.", ["Stable Ground (1)", "Moderate Slope (2)", "High Landslide Zone (3)"]),
                ("5.4 Disaster Warning System Visibility", "Presence of functional emergency warning sirens, hazard signages, or flood gauge markers in key Purok locations.", ["Functional & Visible (1)", "Partial / Damaged (2)", "Absent (3)"])
            ]

            for param, indicator, options in d5_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d5_scores.append(s_val)
                d5_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 6
            st.markdown("<div class='peri-domain-header'>Domain 6: Vector & Pest Vector Risk Identification</div>", unsafe_allow_html=True)
            d6_scores = []
            d6_data = {}
            d6_params = [
                ("6.1 Mosquito Breeding Site Proliferation", "Presence of uncontained water receptors: discarded coconut shells, tires, open drums, unmaintained gutters holding rainwater.", ["Minimal (1)", "Moderate (2)", "High Breeding Risk (3)"]),
                ("6.2 Rodent & Cockroach Harborage", "Visual evidence of rat burrows, rodent dropping trails, or cockroach infestation near food stalls and homes.", ["Controlled (1)", "Noticeable (2)", "Infested (3)"]),
                ("6.3 Stray Rabies Vector Presence", "Number of unvaccinated, free-roaming dogs and cats exhibiting aggressive behavior or scavenging behavior.", ["Low Vector Risk (1)", "Moderate (2)", "High Rabies Threat (3)"])
            ]

            for param, indicator, options in d6_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d6_scores.append(s_val)
                d6_data[param] = {"Rating": r_txt, "Notes": n_txt}

            if st.form_submit_button("💾 Calculate & Save Expanded PERI Index"):
                m1 = np.mean(d1_scores)
                m2 = np.mean(d2_scores)
                m3 = np.mean(d3_scores)
                m4 = np.mean(d4_scores)
                m5 = np.mean(d5_scores)
                m6 = np.mean(d6_scores)
                overall_peri = np.mean([m1, m2, m3, m4, m5, m6])

                cat_level = "Category A: Low Environmental Risk" if overall_peri < 1.5 else ("Category B: Moderate Environmental Concern" if overall_peri < 2.3 else "Category C: High Environmental Hazard Zone")

                st.session_state.windshield_records.append({
                    "Purok": purok_eval, "Date": str(eval_date), "Evaluator": evaluator_name,
                    "DS1_Sanitation": m1, "DS2_Food": m2, "DS3_BuiltEnv": m3,
                    "DS4_HealthInfra": m4, "DS5_DRR": m5, "DS6_Vector": m6,
                    "PERI_Index": overall_peri, "Category": cat_level,
                    "Details": {"D1": d1_data, "D2": d2_data, "D3": d3_data, "D4": d4_data, "D5": d5_data, "D6": d6_data}
                })
                save_session_to_disk()
                st.success(f"PERI Evaluation Saved for {purok_eval}! Index: {overall_peri:.2f} — {cat_level}")

    with p4_tab2:
        st.markdown("### 📖 PERI Result Interpretation Manual & Score Guide")
        st.markdown("""
        | PERI Index Range | Risk Classification | Operational Meaning & Field Priority |
        | :--- | :--- | :--- |
        | **1.00 – 1.49** | **Category A: Low Risk** | Environmental hazards are well-managed. Continue routine monitoring and standard sanitation maintenance. |
        | **1.50 – 2.29** | **Category B: Moderate Concern** | Noticeable environmental vulnerabilities present (e.g. uncollected trash, open canals). Requires targeted barangay interventions. |
        | **2.30 – 3.00** | **Category C: High Hazard Zone** | Critical multi-domain risk (flood, waste accumulation, vector breeding). Immediate municipal DRRMO and MHO referral mandated. |
        """)

    with p4_tab3:
        st.markdown("### 📂 Saved PERI Windshield Records")
        if len(st.session_state.windshield_records) == 0:
            st.info("No windshield evaluation records saved yet.")
        else:
            for i, p_rec in enumerate(st.session_state.windshield_records):
                with st.expander(f"[{i+1}] {p_rec.get('Purok')} - PERI Index: {p_rec.get('PERI_Index', 0):.2f} ({p_rec.get('Category')})"):
                    st.write(f"**Evaluator:** {p_rec.get('Evaluator')} | **Date:** {p_rec.get('Date')}")
                    st.json(p_rec.get("Details"))
                    if st.button(f"🗑️ Delete Record {i+1}", key=f"del_peri_{i}"):
                        st.session_state.windshield_records.pop(i)
                        save_session_to_disk()
                        st.success("Record deleted!")
                        st.rerun()

# MODULE 6: PHASE 5 STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("📈 Phase 5: Cross-Module Correlation Engine & Advanced Statistical Analytics")

    if len(st.session_state.hh_records) == 0:
        st.info("No household survey records available for analytics. Please complete Phase 2 entries.")
    else:
        st.markdown("### 📊 Cross-Tabulation & Chi-Square Association Testing")
        
        flat_data = []
        for h in st.session_state.hh_records:
            flat_data.append({
                "Barangay": h.get("Barangay"),
                "Purok": h.get("Purok"),
                "Water_Safety": "Unsafe Water" if "Unsafe" in h.get("Water", "") else "Safe Water",
                "Diarrhea_History": h.get("Diarrhea", "No"),
                "Hypertension_Risk": "High BP Risk" if h.get("Risk") == "Hypertensive Risk" else "Normal BP",
                "Flood_Prone": h.get("Flood_Prone", "No"),
                "Food_Insecurity": "Food Insecure" if (h.get("Food_Skip") == "Yes" or h.get("Food_Worry") == "Yes") else "Food Secure",
                "Income_Group": h.get("Income", "Q1")
            })
        
        df_analytics = pd.DataFrame(flat_data)

        c1, c2 = st.columns(2)
        var1 = c1.selectbox("Select Primary Factor Variable (X)", ["Water_Safety", "Flood_Prone", "Income_Group", "Food_Insecurity"])
        var2 = c2.selectbox("Select Health Outcome Variable (Y)", ["Diarrhea_History", "Hypertension_Risk"])

        ct = pd.crosstab(df_analytics[var1], df_analytics[var2], margins=True)
        st.markdown(f"#### 📋 Cross-Tabulation Table: `{var1}` vs `{var2}`")
        st.dataframe(ct, use_container_width=True)

        st.bar_chart(pd.crosstab(df_analytics[var1], df_analytics[var2]))

# MODULE 7: PHASE 6 ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("📋 Phase 6: Priority Community Diagnosis & Action Planning Matrix")

    with st.form("action_plan_form"):
        st.markdown("### 📌 Community Health Diagnosis Entry")
        c1, c2 = st.columns(2)
        target_brgy = c1.selectbox("Target Barangay (Palo, Leyte)", PALO_BARANGAYS)
        diag_title = c2.text_input("Priority Diagnosis / Identified Health Problem", "High Prevalence of Adult Hypertension & NCD Non-Compliance")

        st.markdown("---")
        st.markdown("### 🎯 Strategic Intervention Plan")
        c1, c2 = st.columns(2)
        obj_target = c1.text_area("Measurable Goal / Objective", "Reduce unmonitored hypertension rates by 30% over 6 months through weekly BHW home monitoring.")
        act_steps = c2.text_area("Key Interventions & Activities", "1. Deploy BHW home BP screening teams.\n2. Conduct RHU physician consultation drives.\n3. Establish barangay medicine buffer stock.")

        c1, c2, c3 = st.columns(3)
        res_needed = c1.text_input("Resources & Budget Needed", "₱25,000 (AIP Health Line-Item)")
        resp_party = c2.text_input("Responsible Lead / Team", "Barangay Midwife & BHW President")
        target_timeline = c3.text_input("Target Completion Timeline", "Q3 - Q4 2026")

        if st.form_submit_button("💾 Save Community Action Plan"):
            st.session_state.diag_records.append({
                "Barangay": target_brgy, "Diagnosis": diag_title, "Objective": obj_target,
                "Activities": act_steps, "Resources": res_needed, "Lead": resp_party, "Timeline": target_timeline
            })
            save_session_to_disk()
            st.success("Community Action Plan Saved Successfully!")

    st.markdown("---")
    st.markdown("### 📂 Saved Community Diagnosis & Action Plans")
    if len(st.session_state.diag_records) == 0:
        st.info("No action plans created yet.")
    else:
        for idx, d_rec in enumerate(st.session_state.diag_records):
            with st.expander(f"[{idx+1}] {d_rec.get('Barangay')} - {d_rec.get('Diagnosis')}"):
                st.write(f"**Goal:** {d_rec.get('Objective')}")
                st.write(f"**Activities:**\n{d_rec.get('Activities')}")
                st.write(f"**Resources:** {d_rec.get('Resources')} | **Lead:** {d_rec.get('Lead')} | **Timeline:** {d_rec.get('Timeline')}")

# MODULE 8: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Data Management, Storage & Multi-Format Export")
    st.caption("Export compiled multi-phase survey datasets for permanent offline storage, LGU reporting, and statistical analysis.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### 🏠 Master Household Surveys (Phase 2)")
        if len(st.session_state.hh_records) > 0:
            df_hh_exp = pd.DataFrame(st.session_state.hh_records)
            st.download_button("📥 Export Household Data (CSV)", df_hh_exp.to_csv(index=False), "phase2_household_records.csv", "text/csv", use_container_width=True)
        else:
            st.info("No household records to export.")

    with c2:
        st.markdown("#### 🏛️ Governance Scorecards (Phase 1)")
        if len(st.session_state.gov_records) > 0:
            df_gov_exp = pd.DataFrame(st.session_state.gov_records)
            st.download_button("📥 Export Governance Data (CSV)", df_gov_exp.to_csv(index=False), "phase1_governance_scorecards.csv", "text/csv", use_container_width=True)
        else:
            st.info("No governance records to export.")

    with c3:
        st.markdown("#### 🔍 PERI Windshield Surveys (Phase 4)")
        if len(st.session_state.windshield_records) > 0:
            df_peri_exp = pd.DataFrame(st.session_state.windshield_records)
            st.download_button("📥 Export PERI Data (CSV)", df_peri_exp.to_csv(index=False), "phase4_peri_windshield_records.csv", "text/csv", use_container_width=True)
        else:
            st.info("No PERI records to export.")
