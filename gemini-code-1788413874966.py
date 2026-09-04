import json
import os
from collections import Counter
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="UP Manila - Community Clerks Portal (Dev: Jan Art Serna, RMT)",
    page_icon="🩺",
    layout="wide",
)

# ================= SHARED MULTI-ENUMERATOR DATA PERSISTENCE =================
DATA_FILE = "shared_survey_data.json"


def load_shared_data():
    """Reads shared survey records from disk for multi-enumerator sync."""
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
    """Saves shared survey records to disk."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error persisting shared data: {e}")


def sync_session_from_disk():
    """Syncs local Streamlit session state with the shared data file."""
    shared = load_shared_data()
    st.session_state.hh_records = shared.get("hh_records", [])
    st.session_state.gov_records = shared.get("gov_records", [])
    st.session_state.qual_records = shared.get("qual_records", [])
    st.session_state.windshield_records = shared.get("windshield_records", [])
    st.session_state.diag_records = shared.get("diag_records", [])


def save_session_to_disk():
    """Writes session state records into the shared data file."""
    shared = {
        "hh_records": st.session_state.get("hh_records", []),
        "gov_records": st.session_state.get("gov_records", []),
        "qual_records": st.session_state.get("qual_records", []),
        "windshield_records": st.session_state.get("windshield_records", []),
        "diag_records": st.session_state.get("diag_records", []),
    }
    save_shared_data(shared)


# Always sync latest data on rerun
sync_session_from_disk()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


def show_login_screen():
    st.markdown(
        """
        <style>
        .login-box {
            max-width: 420px;
            margin: 60px auto;
            padding: 30px;
            background-color: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #CBD5E1;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .login-title {
            color: #7B1113;
            font-weight: 800;
            font-size: 22px;
            margin-bottom: 4px;
        }
        .login-sub {
            color: #475569;
            font-size: 13px;
            margin-bottom: 15px;
        }
        .dev-badge-login {
            background-color: #FEF3C7;
            border: 1px solid #F59E0B;
            color: #92400E;
            font-size: 12px;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 20px;
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
        '<div class="login-sub">Comprehensive Community Health Field Portal</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="dev-badge-login">⭐ Lead developer Jan Art A. Serna, RMT</div>',
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

# ================= MAIN APPLICATION LOGIC =================

CSS_STYLE = """<style>
.sticky-progress-container {
    position: sticky;
    top: 0;
    z-index: 99999;
    background-color: #F1F5F9;
    padding: 14px 10px;
    margin-bottom: 15px;
    border-bottom: 2px solid #CBD5E1;
    border-radius: 0 0 8px 8px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
}
.up-navbar {
    background-color: #7B1113;
    border-bottom: 4px solid #1E4D2B;
    padding: 20px 24px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
}
.up-navbar-title {
    color: #FFFFFF !important;
    font-size: 24px !important;
    font-weight: 800 !important;
    margin: 0 !important;
    line-height: 1.2;
    letter-spacing: 0.5px;
}
.up-navbar-sub {
    color: #FACC15 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin: 4px 0 0 0 !important;
}
.up-navbar-detail {
    color: #E2E8F0 !important;
    font-size: 12px !important;
    margin-top: 4px !important;
}
.dev-honor-banner {
    background: linear-gradient(90deg, #1E4D2B 0%, #064E3B 100%);
    border: 1px solid #10B981;
    color: #ECFDF5;
    padding: 8px 16px;
    border-radius: 8px;
    text-align: center;
    font-size: 13px;
    font-weight: 700;
    margin-top: 10px;
    letter-spacing: 0.4px;
}
div[data-testid="stForm"] {
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    background-color: #FFFFFF;
    padding: 24px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
}
section[data-testid="stSidebar"] {
    background-color: #F1F5F9;
    border-right: 1px solid #E2E8F0;
}
.adult-card {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #7B1113;
    padding: 12px 15px;
    border-radius: 6px;
    margin-bottom: 12px;
}
.child-card {
    background-color: #F0FDF4;
    border: 1px solid #DCFCE7;
    border-left: 4px solid #16A34A;
    padding: 12px 15px;
    border-radius: 6px;
    margin-bottom: 12px;
}
.peri-domain-header {
    background-color: #7B1113;
    color: #FFFFFF;
    padding: 8px 14px;
    border-radius: 6px;
    font-weight: 700;
    margin-bottom: 12px;
}
.dash-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
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
    color: #64748B;
    text-transform: uppercase;
}
.insight-alert-high {
    background-color: #FEF2F2;
    border-left: 5px solid #EF4444;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 10px;
    color: #991B1B;
}
.insight-alert-warn {
    background-color: #FFFBEB;
    border-left: 5px solid #F59E0B;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 10px;
    color: #92400E;
}
.insight-alert-good {
    background-color: #F0FDF4;
    border-left: 5px solid #22C55E;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 10px;
    color: #166534;
}
</style>"""

st.markdown(CSS_STYLE, unsafe_allow_html=True)

col_header, col_logout = st.columns([8, 2])

with col_header:
    HEADER_HTML = """<div class="up-navbar">
    <div class="up-navbar-title">UNIVERSITY OF THE PHILIPPINES MANILA</div>
    <div class="up-navbar-sub">School of Health Sciences — Comprehensive Community Health Field Portal</div>
    <div class="up-navbar-detail">Integrated System: Spatial Mapping, Geocoding, Analytics & Action Planning (Phases 1–6)</div>
    <div class="dev-honor-banner">Lead developer Jan Art A. Serna, RMT</div>
    </div>"""
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

with col_logout:
    st.write("")
    st.write("")
    if st.button("🚪 Log Out System", use_container_width=True, type="secondary"):
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
    <div style="font-weight: 700; color: #1E293B; font-size: 14px; margin-bottom: 4px;">📊 Phase Completion Tracker</div>
    <div style="font-weight: 800; color: #7B1113; font-size: 18px; margin-bottom: 4px;">{overall_progress_pct}% Completed</div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.progress(overall_progress_pct / 100)

if st.sidebar.button(
    "🔄 Sync / Refresh Shared Data",
    use_container_width=True,
    help="Fetch live submissions from all active enumerators",
):
    sync_session_from_disk()
    st.sidebar.success("Data synced with shared storage!")
    st.rerun()

with st.sidebar.expander("🔍 View Detailed Phase Status", expanded=False):
    st.write(f"{'✅' if p1_status else '🔴'} **Phase 1 (Governance):** {'100%' if p1_status else '0%'}")
    st.write(f"{'✅' if p2_status else '🔴'} **Phase 2 (Master Survey):** {'100%' if p2_status else '0%'}")
    st.write(f"{'✅' if p3_status else '🔴'} **Phase 3 (Qualitative):** {'100%' if p3_status else '0%'}")
    st.write(f"{'✅' if p4_status else '🔴'} **Phase 4 (Expanded PERI):** {'100%' if p4_status else '0%'}")
    st.write(f"{'✅' if p5_status else '🔴'} **Phase 5 (Analytics):** {'100%' if p5_status else '0%'}")
    st.write(f"{'✅' if p6_status else '🔴'} **Phase 6 (Action Plan):** {'100%' if p6_status else '0%'}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Portal Navigation")
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

st.sidebar.caption("👨‍💻 **Lead Developer:** Jan Art Serna, RMT")

# ================= MODULE 0: EXECUTIVE DASHBOARD & SMART RISK ENGINE (NEW MODERN FEATURE) =================
if menu == "📊 Executive Health Dashboard & Smart Risk Engine":
    st.subheader("📊 Executive Field Intelligence Dashboard & Automated Risk Engine")
    st.caption("Real-Time Multi-Phase Field Analytics, Epidemiological Insights & Automated Public Health Risk Prediction | Lead Dev: Jan Art A. Serna, RMT")

    # Metrics aggregation
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

    # Modern KPI Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Surveyed HHs", f"{tot_hh}", delta=f"{tot_pop} People Profiled" if tot_pop > 0 else None)
    m2.metric("Adult Hypertensive Risk", f"{htn_rate:.1f}%", delta=f"{htn_count} Adults High BP", delta_color="inverse")
    m3.metric("Avg PERI Risk Index", f"{avg_peri:.2f}", delta="Cat C Critical" if avg_peri >= 2.3 else ("Cat B Concern" if avg_peri >= 1.5 else "Cat A Low Risk"), delta_color="inverse")
    m4.metric("BHB Governance Score", f"{latest_gov}/100", delta="High Functioning" if latest_gov >= 80 else "Needs Action", delta_color="normal")
    m5.metric("Action Plans Saved", f"{len(diag_data)} Plans", delta=f"{len(qual_data)} Qualitative Notes")

    st.markdown("---")

    # modern Feature: Automated AI/Rule-based Community Risk & Vulnerability Predictor
    st.markdown("### 🤖 Automated Community Health Risk & Vulnerability Predictor")
    st.caption("Engineered by Jan Art A. Serna, RMT to dynamically evaluate multi-phase field vectors and generate priority interventions.")

    # Risk evaluation logic
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

    # Visual Analytics & Data Distribution Tabs
    dash_tab1, dash_tab2, dash_tab3 = st.tabs(["📈 Disease & Vitals Analytics", "🌍 Environmental & PERI Breakdown", "🔍 Real-Time Master Household Roster"])

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

    with dash_tab2:
        if len(peri_data) > 0:
            st.markdown("**Purok Environmental Risk Index (PERI) Domain Breakdown**")
            peri_df = pd.DataFrame(peri_data)[["Purok", "DS1_Sanitation", "DS2_Food", "DS3_BuiltEnv", "DS4_HealthInfra", "DS5_DRR", "DS6_Vector", "PERI_Index"]]
            st.dataframe(peri_df, use_container_width=True)
            st.bar_chart(peri_df.set_index("Purok")[["DS1_Sanitation", "DS2_Food", "DS3_BuiltEnv", "DS4_HealthInfra", "DS5_DRR", "DS6_Vector"]])
        else:
            st.info("No Phase 4 PERI windshield evaluations stored yet.")

    with dash_tab3:
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
elif menu == "🗺️ Interactive Spot Map":
    st.subheader("📍 Interactive Barangay Health & Environmental Hazard Spot Map")

    if len(st.session_state.hh_records) == 0:
        st.info("No household survey records stored yet. Showing baseline map with simulated hazard markers.")
        map_df = pd.DataFrame([
            {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk": "Hypertensive Risk", "Flood_Prone": "Yes", "Color": [192, 38, 211, 230]},
            {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk": "Normal", "Flood_Prone": "No", "Color": [34, 197, 94, 200]},
            {"HH_ID": "HH-003", "Purok": "Purok 2", "Lat": 11.1555, "Lon": 124.9905, "BP": "120/80", "Risk": "Normal", "Flood_Prone": "Yes", "Color": [37, 99, 235, 220]},
            {"HH_ID": "HH-004", "Purok": "Purok 3", "Lat": 11.1570, "Lon": 124.9930, "BP": "150/98", "Risk": "Hypertensive Risk", "Flood_Prone": "No", "Color": [123, 17, 19, 220]},
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_m, col_f = st.columns([3, 1])

    with col_f:
        st.markdown("**Map Controls & Filters**")
        puroks = list(map_df["Purok"].unique())
        sel_puroks = st.multiselect("Filter Puroks", options=puroks, default=puroks)
        flood_filter = st.selectbox("Flood Risk Filter", ["Show All Households", "Flood-Prone Zones Only", "Non-Flood Zones Only"])

        st.markdown("---")
        st.markdown("**Map Marker Legend:**")
        st.markdown("🔵 **Blue:** Flood-Prone Zone Only")
        st.markdown("🔴 **Maroon:** Hypertensive Health Risk Only")
        st.markdown("🟣 **Purple:** Dual Hazard (Flood + Health Risk)")
        st.markdown("🟢 **Green:** Normal / Low Risk")

    filt_df = map_df[map_df["Purok"].isin(sel_puroks)]
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
                tooltip={"text": "HH: {HH_ID}\nPurok: {Purok}\nBP: {BP}\nHealth Risk: {Risk}\nFlood Prone: {Flood_Prone}"},
            )
        )

# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD
elif menu == "📋 Phase 1: Full Governance Scorecard":
    st.subheader("Phase 1: Barangay Health Board (BHB) Governance Scorecard (100-Point Instrument)")

    mode_p1 = st.radio("Select Operation", ["➕ New Scorecard Entry", "📂 Review, Edit & Delete Submitted Scorecards"], horizontal=True)

    if mode_p1 == "➕ New Scorecard Entry":
        with st.form("phase1_full_form"):
            t1, t2, t3, t4 = st.tabs(["📌 Metadata & Leadership", "🏛️ Structure, Meetings & Ordinances", "💰 AIP Budgeting & Reporting", "🎯 Gaps & Action Planning"])

            with t1:
                c1, c2, c3 = st.columns(3)
                b_name = c1.text_input("Barangay Name")
                city = c2.text_input("City / Municipality")
                prov = c3.text_input("Province")

                c1, c2, c3 = st.columns(3)
                eval_date = c1.date_input("Date of Evaluation")
                pb_head = c2.text_input("Punong Barangay (BHB Chair)")
                health_lead = c3.text_input("Committee Lead on Health / BHW Lead")

            with t2:
                st.markdown("**Domain 1: Legal Structure & Reconstitution (Max 10 Points)**")
                c1, c2 = st.columns(2)
                g1_1 = c1.number_input("1.1 Updated Executive Order reconstituting BHB with mandate terms (0–5 pts)", 0, 5, 0)
                g1_2 = c2.number_input("1.2 Mandatory multi-sectoral reps active (0–5 pts)", 0, 5, 0)

                st.markdown("**Domain 2: Meeting Regularity & Quorum Compliance (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g2_1 = c1.number_input("2.1 Quarterly meetings in past 12 mos (0–12 pts)", 0, 12, 0)
                g2_2 = c2.number_input("2.2 Official quorum met during every meeting (0–4 pts)", 0, 4, 0)
                g2_3 = c3.number_input("2.3 Signed minutes and attendance records filed (0–4 pts)", 0, 4, 0)

                st.markdown("**Domain 3: Health Policies & Ordinance Enactment (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g3_1 = c1.number_input("3.1 Local health/sanitation ordinances enacted (0–10 pts)", 0, 10, 0)
                g3_2 = c2.number_input("3.2 Active task force enforcing local health laws (0–5 pts)", 0, 5, 0)
                g3_3 = c3.number_input("3.3 Local policies aligned with DOH UHC mandates (0–5 pts)", 0, 5, 0)

            with t3:
                st.markdown("**Domain 4: AIP Budget Allocation & Financial Execution (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g4_1 = c1.number_input("4.1 Dedicated health line-items in AIP (0–8 pts)", 0, 8, 0)
                g4_2 = c2.number_input("4.2 Budget for BHW honoraria, emergency response (0–6 pts)", 0, 6, 0)
                g4_3 = c3.number_input("4.3 Health budget execution rate >75% last fiscal year (0–6 pts)", 0, 6, 0)

                st.markdown("**Domain 5: Health Reporting & Transparency (Max 15 Points)**")
                c1, c2, c3 = st.columns(3)
                g5_1 = c1.number_input("5.1 Quarterly health reports submitted to MHO/RHU (0–8 pts)", 0, 8, 0)
                g5_2 = c2.number_input("5.2 Health status presented during Barangay Assemblies (0–4 pts)", 0, 4, 0)
                g5_3 = c3.number_input("5.3 Barangay Health Spot Map maintained at BHS (0–3 pts)", 0, 3, 0)

                st.markdown("**Domain 6: Working Committees & Mobilization (Max 15 Points)**")
                c1, c2, c3 = st.columns(3)
                g6_1 = c1.number_input("6.1 Active technical working committees (0–6 pts)", 0, 6, 0)
                g6_2 = c2.number_input("6.2 Monthly committee reports to BHB (0–6 pts)", 0, 6, 0)
                g6_3 = c3.number_input("6.3 Community health mobilization events completed (0–3 pts)", 0, 3, 0)

            with t4:
                gap_summary = st.text_area("Identify primary governance bottlenecks & legislative gaps:")
                action_plan = st.text_area("Recommended technical assistance & corrective intervention plan:")

            if st.form_submit_button("Submit & Save Complete Governance Scorecard"):
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
                e_brgy = st.text_input("Barangay Name", value=rec.get("Barangay", ""))
                e_city = st.text_input("City / Municipality", value=rec.get("City", ""))
                e_prov = st.text_input("Province", value=rec.get("Province", ""))
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
        st.markdown("#### ⚙️ Profile Roster Count Configuration & Non-Submitting Add Controls")
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
                brgy = c2.text_input("Barangay Name")
                purok = c3.selectbox("Purok / Zone", [f"Purok {i}" for i in range(1, 8)])
                date_survey = c4.date_input("Date of Survey")

                c1, c2, c3, c4 = st.columns(4)
                lat = c1.number_input("Latitude", value=11.1560, format="%.4f")
                lon = c2.number_input("Longitude", value=124.9920, format="%.4f")
                enum_name = c3.selectbox("Enumerator Name", ["Jan Art Serna, RMT", "Aubrey Maye Arrieta", "Leila Projimo, PTRP"])
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

            # --- TAB 1: ALL-VARIABLE AGGREGATED CROSS-MODULE INTERPRETATION ---
            with tab_interp:
                total_hhs = len(st.session_state.hh_records)
                all_adults = [a for hh in st.session_state.hh_records for a in hh.get("Adults", [])]
                all_children = [c for hh in st.session_state.hh_records for c in hh.get("Children", [])]

                st.markdown(f"#### 🌐 Overview: Aggregate Coverage ({total_hhs} Households | {len(all_adults)} Adults Profiled | {len(all_children)} Children Profiled)")

                # Section 1: Demographics, Language & Vitals
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

                # Symptom Breakdown & Occupations
                with st.expander("📌 View Symptoms, Age, Gender & Occupation Breakdown"):
                    c_sym, c_occ = st.columns(2)
                    all_symptoms = [sym for a in all_adults for sym in a.get("Complaints", []) if sym != "None"]
                    c_sym.markdown("**Top Adult Complaints / Symptoms:**")
                    c_sym.write(pd.Series(all_symptoms).value_counts().rename("Count") if all_symptoms else "No reported symptoms.")

                    all_occs = [a.get("Occupation") for a in all_adults if a.get("Occupation")]
                    c_occ.markdown("**Adult Primary Occupations:**")
                    c_occ.write(pd.Series(all_occs).value_counts().rename("Count") if all_occs else "No reported occupations.")

                st.markdown("---")
                # Section 2: Socio-Economic, Food Insecurity, Housing & Assets
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
                # Section 3: WASH Infrastructure & Environmental Health
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
                # Section 4: Morbidity & Chronic Disease Compliance
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
                # Section 5: Maternal Care, Child Anthropometrics & PhilHealth YAKAP
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

            # --- TAB 2: INDIVIDUAL RESPONSE INSPECTOR ---
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
                e_brgy = st.text_input("Barangay Name", value=rec.get("Barangay", ""))
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

# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader("Phase 3: Community Qualitative Data Collection (KII & FGD Tools)")

    mode_p3 = st.radio("Select Operation", ["➕ New Qualitative Entry", "📂 Review, Edit & Delete Submitted Qualitative Records"], horizontal=True)

    if mode_p3 == "➕ New Qualitative Entry":
        with st.form("phase3_qual_form"):
            c1, c2, c3 = st.columns(3)
            tool_type = c1.selectbox("Tool Type", ["Key Informant Interview (KII)", "Focus Group Discussion (FGD)"])
            informant_type = c2.selectbox("Informant Category", ["Barangay Official", "BHW / BNS", "Barangay Midwife", "Senior Citizens", "4Ps Mothers", "Farmers/Fisherfolk Association"])
            purok_loc = c3.selectbox("Purok Conducted", [f"Purok {i}" for i in range(1, 8)])

            health_perceptions = st.text_area("1. Perceived Top Health Bottlenecks & Risks:")
            barriers_care = st.text_area("2. Barriers to Accessing Local RHU/BHS Services:")
            indigenous_practices = st.text_area("3. Local Health Seeking Practices & Beliefs:")

            if st.form_submit_button("Submit & Save Qualitative Record"):
                st.session_state.qual_records.append({
                    "Type": tool_type, "Informant": informant_type, "Purok": purok_loc,
                    "Perceptions": health_perceptions, "Barriers": barriers_care, "Beliefs": indigenous_practices,
                })
                save_session_to_disk()
                st.success("Qualitative field notes saved successfully!")

    else:
        st.markdown("### 📂 Submitted Qualitative Records")
        if len(st.session_state.qual_records) == 0:
            st.info("No qualitative records found.")
        else:
            qual_options = [f"[{i+1}] {r.get('Type', 'N/A')} - {r.get('Informant', 'N/A')}" for i, r in enumerate(st.session_state.qual_records)]
            selected_idx = st.selectbox("Select Record", range(len(qual_options)), format_func=lambda x: qual_options[x])
            rec = st.session_state.qual_records[selected_idx]

            with st.form("edit_qual_form"):
                e_informant = st.text_input("Informant Category", value=rec.get("Informant", ""))
                e_perceptions = st.text_area("Perceptions", value=rec.get("Perceptions", ""))

                if st.form_submit_button("🗑️ Delete Record"):
                    st.session_state.qual_records.pop(selected_idx)
                    save_session_to_disk()
                    st.success("Record deleted!")
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
            evaluator_name = c3.selectbox("Lead Evaluator", ["Jan Art Serna, RMT", "Aubrey Maye Arrieta", "Leila Projimo, PTRP"])

            def render_rating(col1, col2, col3, label, choices, default_idx=0):
                rating = col2.radio(label, choices, index=default_idx, key=f"r_{label}")
                notes = col3.text_input("Hotspot / Landmark Notes", key=f"n_{label}")
                score_val = 1.0 if "1" in rating else (2.0 if "2" in rating else 3.0)
                return score_val, rating, notes

            # DOMAIN 1
            st.markdown("<div class='peri-domain-header'>Domain 1: Sanitation & Waste Management Assessment</div>", unsafe_allow_html=True)
            st.caption("Evaluates solid waste collection efficiency, drainage cleanliness, wastewater pooling, vector hazards, and overall public hygiene across target Puroks.")
            
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
            st.caption("Evaluates the physical accessibility and ratio of nutrient-dense fresh foods vs. highly processed, ultra-palatable junk foods (identifying 'Food Deserts' and 'Food Swamps').")
            
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
            st.caption("Assesses structural housing vulnerability, pedestrian safety, public illumination, electrical hazards, and recreational space adequacy.")
            
            d3_scores = []
            d3_data = {}
            d3_params = [
                ("3.1 Housing Structural Integrity", "Proportion of concrete/permanent housing vs. makeshift, tarpaulin, light bamboo, or deteriorated wood structures.", ["Mostly Concrete (1)", "Mixed Structural (2)", "Predominantly Makeshift (3)"]),
                ("3.2 Pedestrian Walkways & Sidewalks", "Availability of paved, unblocked sidewalks or footpaths separated from vehicle traffic vs. pedestrians walking on main road shoulders.", ["Safe / Paved (1)", "Partial / Blocked (2)", "Absent / Dangerous (3)"]),
                ("3.3 Street Lighting & Night Illumination", "Density and functioning status of streetlights along primary thoroughfares, inner alleyways, and public footbridges.", ["Fully Lit (1)", "Dim / Partial (2)", "Dark / Unlit Alleys (3)"]),
                ("3.4 Public Open Spaces & Youth Parks", "Presence of safe, clean public plazas, basketball courts, or green parks free from trash, broken glass, or structural hazards.", ["Safe & Accessible (1)", "Dilapidated / Unkept (2)", "None / Unsafe (3)"]),
                ("3.5 Universal Physical Accessibility", "Presence of smooth ramps, unblocked curb cuts, and level walkways for PWDs, senior citizens, wheelchairs, and strollers.", ["Barrier-Free (1)", "Partially Barrier-Free (2)", "Severe Barriers (3)"]),
                ("3.6 Electrical Wiring & Power Line Safety", "Condition of overhead utility wires: neatly bundled vs. entangled 'octopus' wiring, low-hanging lines, or sparking transformers.", ["Orderly / Safe (1)", "Cluttered / Low (2)", "Hazardous 'Octopus' (3)"]),
                ("3.7 Road Surface & Speed Management", "Quality of road paving (paved concrete vs. potholed/muddy dirt roads) and presence of speed humps near pedestrian areas.", ["Well-Paved / Safe (1)", "Unpaved / Potholes (2)", "Severely Broken / Muddy (3)"])
            ]

            for param, indicator, options in d3_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d3_scores.append(s_val)
                d3_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 4
            st.markdown("<div class='peri-domain-header'>Domain 4: Health Infrastructure & Primary Care Accessibility</div>", unsafe_allow_html=True)
            st.caption("Evaluates physical state, operational transparency, emergency accessibility, and visibility of primary healthcare facilities.")
            
            d4_scores = []
            d4_data = {}
            d4_params = [
                ("4.1 Barangay Health Station (BHS) State", "Physical appearance of BHS/Health Center: clean, repainted, intact roof/windows vs. cracked walls, rust, water leaks, or clutter.", ["Well-Maintained (1)", "Substandard / Wear (2)", "Dilapidated / Blighted (3)"]),
                ("4.2 Facility Visibility & Operational Signage", "Prominent signage outside BHS detailing facility name, list of free health services, operating hours, and emergency contacts.", ["Clear & Complete (1)", "Faded / Incomplete (2)", "Missing / No Signage (3)"]),
                ("4.3 Public Transport Proximity (<100m)", "Distance from BHS entrance to nearest tricycle terminal, jeepney stop, or paved road where public transport is readily available.", ["High Access (<50m) (1)", "Moderate (50-150m) (2)", "Isolated (>150m) (3)"]),
                ("4.4 Pharmacy / Essential Medicine Access", "Proximity of BHS dispensing room or private community pharmacy (Botika) stocking essential maintenance and emergency drugs.", ["Co-located / Nearby (1)", "Limited / Distant (2)", "Absent in Zone (3)"]),
                ("4.5 Emergency Vehicle Access Corridors", "Width and clarity of access roads leading to BHS or deep Puroks to allow full-sized ambulance or fire truck entry without blocking.", ["Unobstructed Wide (1)", "Narrow / Tight Turn (2)", "Blocked / Inaccessible (3)"]),
                ("4.6 Health Promotion Advisory Display", "Visibility of outdoor bulletin boards displaying updated health warnings (Dengue, TB, Maternal Health, COVID, Immunization dates).", ["Updated & Visible (1)", "Outdated Posters (2)", "Blank / Damaged (3)"]),
                ("4.7 BHS Sanitation & Basic Utilities", "Presence of functioning handwashing sink with soap, clean patient toilet facility, running water, and reliable power at BHS.", ["Fully Functional (1)", "Partial / Defective (2)", "Non-Functional / None (3)"])
            ]

            for param, indicator, options in d4_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d4_scores.append(s_val)
                d4_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 5
            st.markdown("<div class='peri-domain-header'>Domain 5: Disaster Risk Reduction & Climate Environmental Safety</div>", unsafe_allow_html=True)
            st.caption("Evaluates physical vulnerability of residential clusters to natural hazards (floods, landslides, coastal surges) and readiness of escape corridors.")
            
            d5_scores = []
            d5_data = {}
            d5_params = [
                ("5.1 High-Hazard Proximity (Geohazards)", "Residential dwellings constructed directly along steep unstable slopes, active riverbanks, sea walls, or landslide easements.", ["Low Exposure (1)", "Moderate Buffer (2)", "High Hazard Zone (3)"]),
                ("5.2 Flood Vulnerability & High-Water Marks", "Visible watermark lines on house walls, recent mud silt on pavements, or low-lying basin topography prone to rapid inundation.", ["Flood-Free / High (1)", "Ankle-Deep / Slow (2)", "Rapid Deep Inundation (3)"]),
                ("5.3 Evacuation Route Signage & Clarity", "Presence of reflectorized, clearly marked evacuation directional signs along major Purok footpaths and intersections.", ["Clearly Marked (1)", "Faded / Sparse (2)", "No Signage Found (3)"]),
                ("5.4 Evacuation Center Readiness", "Structural condition, roof integrity, and accessibility of designated evacuation hubs (e.g., Covered Court, Barangay Hall, School).", ["Ready & Accessible (1)", "Minor Maintenance (2)", "Unsafe / Restricted (3)"]),
                ("5.5 Major Drainage Outfalls & Waterways", "Condition of river outlets, major creek channels, or floodgates: free-flowing vs. choked with thick silt, water hyacinths, or trash.", ["Clear Outflow (1)", "Moderately Clogged (2)", "Severely Choked (3)"]),
                ("5.6 Urban Fire Hazard & Density", "Extremely dense wooden housing clusters separated by narrow (<1.5m) alleys preventing fire tender hose penetration.", ["Low Fire Risk (1)", "Moderate Density (2)", "High Fire Trap (3)"]),
                ("5.7 Slope Protection & Retaining Walls", "Presence and structural condition of concrete retaining walls, gabions, or vegetation cover along steep roadside cuts or embankments.", ["Intact Protection (1)", "Cracking / Eroded (2)", "Unprotected Slope (3)"])
            ]

            for param, indicator, options in d5_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d5_scores.append(s_val)
                d5_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 6
            st.markdown("<div class='peri-domain-header'>Domain 6: Vector Control & Environmental Exposure Hazards</div>", unsafe_allow_html=True)
            st.caption("Evaluates micro-environmental exposure factors including mosquito breeding reservoirs, rodent activity, and localized industrial/noise pollution.")
            
            d6_scores = []
            d6_data = {}
            d6_params = [
                ("6.1 Dengue Vector Breeding Sites", "Density of discarded motor vehicle tires, uncovered rain barrels, open tin cans, or plastic containers containing stagnant water.", ["Rare / Clean (1)", "Moderate Sites (2)", "Prolific Breeding (3)"]),
                ("6.2 Rodent & Fly Infestation Signs", "Visible signs of rat burrows along canal banks, swarms of flies near open waste or food stalls, or pest damage to structures.", ["Low / Unnoticed (1)", "Moderate Signs (2)", "Severe Infestation (3)"]),
                ("6.3 Commercial / Workshop Pollution", "Proximity of residential homes to auto-repair shops dumping waste motor oil, junk yards, welding shops, or noisy small factories.", ["Buffer Compliant (1)", "Moderate Nuisance (2)", "Severe Toxic Exposure (3)"]),
                ("6.4 Dust, Exhaust & Air Quality", "Heavy airborne dust generated by unpaved dirt roads or intense diesel exhaust fumes along congested transport stops.", ["Clean Air (1)", "Moderate Dust/Fumes (2)", "High Particulate Dust (3)"])
            ]

            for param, indicator, options in d6_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(c1, c2, c3, param, options)
                d6_scores.append(s_val)
                d6_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN SCORE CALCULATIONS
            ds1 = sum(d1_scores) / len(d1_scores)
            ds2 = sum(d2_scores) / len(d2_scores)
            ds3 = sum(d3_scores) / len(d3_scores)
            ds4 = sum(d4_scores) / len(d4_scores)
            ds5 = sum(d5_scores) / len(d5_scores)
            ds6 = sum(d6_scores) / len(d6_scores)

            peri_index = (ds1 + ds2 + ds3 + ds4 + ds5 + ds6) / 6.0
            
            if peri_index >= 2.30:
                tier_cat = "CATEGORY C: Critical Hazard (Red)"
            elif peri_index >= 1.50:
                tier_cat = "CATEGORY B: Moderate Concern (Amber)"
            else:
                tier_cat = "CATEGORY A: Low Risk (Green)"

            st.markdown("---")
            st.markdown("### 📊 Calculated PERI Assessment Index")
            st.metric("Composite Purok Environmental Risk Index (PERI)", f"{peri_index:.2f}", tier_cat)

            if st.form_submit_button("Submit & Save PERI Assessment Record"):
                st.session_state.windshield_records.append({
                    "Purok": purok_eval, "Date": str(eval_date), "Evaluator": evaluator_name,
                    "DS1_Sanitation": ds1, "DS2_Food": ds2, "DS3_BuiltEnv": ds3, "DS4_HealthInfra": ds4, "DS5_DRR": ds5, "DS6_Vector": ds6,
                    "PERI_Index": peri_index, "Tier_Category": tier_cat,
                    "Details": {"D1": d1_data, "D2": d2_data, "D3": d3_data, "D4": d4_data, "D5": d5_data, "D6": d6_data}
                })
                save_session_to_disk()
                st.success(f"Complete PERI Assessment for {purok_eval} successfully saved!")

    with p4_tab2:
        st.markdown("## 3. Comprehensive Result Interpretation & Field Scoring Manual")
        st.write("To translate windshield observation field findings into actionable public health policies, disaster mitigation plans, and LGU budget allocations, field teams must apply the standardized scoring, index calculation, and risk categorization framework detailed below.")

        st.markdown("### 3.1 Quantitative Scoring & Index Calculation Methodology")
        st.markdown("""
        Each evaluated parameter within a domain receives a discrete rating score based on field observation:
        * **Score 1.0 (Optimal / Clean / Low Risk):** Parameter meets sanitary and structural standards. Minimal or no hazard observed.
        * **Score 2.0 (Moderate Risk / Substandard):** Parameter displays noticeable deficiencies, wear, or moderate sanitation gaps requiring targeted routine maintenance.
        * **Score 3.0 (Severe Hazard / Critical):** Parameter presents acute, severe environmental hazards, extreme infrastructure decay, or immediate health risks requiring urgent intervention.
        """)

        st.markdown("#### Mathematical Calculation Steps:")
        st.markdown("""
        **1. Step 1 - Calculate Domain Score (DS):** For each domain, sum the numerical scores of all evaluated items and divide by the total number of items evaluated in that domain.
        
        $$\\text{Domain Score (DS)} = \\frac{\\sum \\text{Item Ratings in Domain}}{\\text{Total Number of Evaluated Items in Domain}}$$
        
        *Example: If Domain 1 (Sanitation) has 9 items and the sum of scores is 18, then $DS = \\frac{18}{9} = 2.00$ (Moderate Risk).*
        
        **2. Step 2 - Calculate Purok Environmental Risk Index (PERI):** Sum the Domain Scores across all 6 domains and divide by 6 to determine the overall composite risk index for the specific Purok.
        
        $$\\text{PERI} = \\frac{DS_1 + DS_2 + DS_3 + DS_4 + DS_5 + DS_6}{6}$$
        
        The PERI provides a single, comparative composite score ranging from **1.00 (Lowest Risk)** to **3.00 (Highest Risk)**.
        """)

        st.markdown("---")
        st.markdown("### 3.2 Risk Level Classification Matrix & Priority Tiers")
        risk_matrix_df = pd.DataFrame([
            {"PERI Score Range": "1.00 – 1.49", "Risk Tier Category": "CATEGORY A: Low Risk (Green)", "Environmental Health Description": "Environment is generally clean, structurally stable, and well-serviced. Minimal health hazard exposure.", "Required Operational Response": "Routine quarterly monitoring; maintain existing Barangay sanitation services."},
            {"PERI Score Range": "1.50 – 2.29", "Risk Tier Category": "CATEGORY B: Moderate Concern (Amber)", "Environmental Health Description": "Noticeable environmental deficits (e.g., clogged canals, junk food dominance, dim lighting). Moderate risk of localized outbreak.", "Required Operational Response": "Targeted 30-day intervention; schedule clean-up drives, BHW health education, minor repairs."},
            {"PERI Score Range": "2.30 – 3.00", "Risk Tier Category": "CATEGORY C: Critical Hazard (Red)", "Environmental Health Description": "Severe contamination, acute disaster vulnerability, food desert conditions, or dilapidated health access. Severe threat.", "Required Operational Response": "Immediate Emergency Action (<7 days); escalate to Municipal Mayor, LGU Health Officer, DRRMO."}
        ])
        st.table(risk_matrix_df)

        st.markdown("---")
        st.markdown("### 3.3 Hotspot Spatial Mapping & Analysis Instructions")
        st.markdown("""
        1. **Color-Coded Community Base Maps:** Transpose the PERI scores onto an official Barangay base map using green, yellow/amber, and red highlighters for each Purok boundary.
        2. **Multi-Domain Hotspot Identification:** Identify 'Double Red' or 'Triple Red' Puroks—zones where multiple domains (e.g., Sanitation + Flood Risk + Food Desert) simultaneously score above 2.30. These represent priority zones for integrated socio-economic interventions.
        3. **Micro-Hotspot Pinpointing:** Utilize the field notes column to physically plot point locations of severe hazards (e.g., 'Octopus' power pole #4 at Purok 3; Clogged canal junction at Purok 1) for direct referral to maintenance teams.
        """)

        st.markdown("---")
        st.markdown("### 3.4 Domain-Specific Action Pathways & Trigger Thresholds")
        st.markdown("""
        When specific individual domain scores ($DS$) exceed **2.00**, execute the following standardized operational responses:
        * **Sanitation Trigger ($DS_1 > 2.00$):** Deploy Barangay Tanods and BHWs for a mandatory weekend Purok Clean-Up Drive; issue compliance notices to households with illegal open dumping; request additional garbage truck pickups from LGU solid waste office.
        * **Food Environment Trigger ($DS_2 > 2.00$):** Partner with local farmers to establish weekly mobile vegetable markets ('Talipapa on Wheels'); conduct nutritional counselling in sari-sari store owner forums to encourage stocking fresh produce.
        * **Built Environment Trigger ($DS_3 > 2.00$):** Reallocate Barangay Development Funds (BDF) for streetlight solar replacement, footpath concrete paving, and immediate utility pole hazard reporting to local power co-ops.
        * **Health Access Trigger ($DS_4 > 2.00$):** Re-evaluate BHS operational hours; establish satellite BHW consultation posts in isolated Puroks; request ambulance access lane clearing from barangay council.
        * **Disaster Safety Trigger ($DS_5 > 2.00$):** Conduct immediate localized evacuation drills; install bright reflectorized signage along escape routes; clear major river outfalls using heavy equipment prior to rainy season.
        """)

        st.markdown("---")
        st.markdown("### 3.5 Data Triangulation with Secondary Health Indicators")
        st.markdown("""
        Windshield survey findings should not stand alone. Cross-validate field results with the following official health records:
        1. **Triangulate Sanitation & Vector Scores (Domains 1 & 6)** with BHS FHSIS records on Diarrhea cases, Dengue incidence, and Skin Infection consultations.
        2. **Triangulate Food Environment Scores (Domain 2)** with Operation Timbang (OPT) Child Malnutrition and Stunting prevalence data.
        3. **Triangulate Disaster & Built Environment Scores (Domains 3 & 5)** with historical DRRMO casualty and flood damage reports.
        """)

    with p4_tab3:
        st.markdown("### 📂 Submitted PERI Assessment Records")
        if len(st.session_state.windshield_records) == 0:
            st.info("No PERI records found.")
        else:
            peri_options = [f"[{i+1}] {r.get('Purok', 'N/A')} - PERI Index: {r.get('PERI_Index', 0.0):.2f} ({r.get('Tier_Category', 'N/A')})" for i, r in enumerate(st.session_state.windshield_records)]
            selected_idx = st.selectbox("Select Assessment Record", range(len(peri_options)), format_func=lambda x: peri_options[x])
            rec = st.session_state.windshield_records[selected_idx]

            st.write(f"**Evaluator:** {rec.get('Evaluator')}")
            st.write(f"**Date:** {rec.get('Date')}")
            st.write(f"**Domain Scores:** Sanitation: {rec.get('DS1_Sanitation'):.2f} | Food: {rec.get('DS2_Food'):.2f} | Built: {rec.get('DS3_BuiltEnv'):.2f} | Health Infra: {rec.get('DS4_HealthInfra'):.2f} | DRR: {rec.get('DS5_DRR'):.2f} | Vector: {rec.get('DS6_Vector'):.2f}")

            if st.button("🗑️ Delete Selected PERI Record"):
                st.session_state.windshield_records.pop(selected_idx)
                save_session_to_disk()
                st.success("PERI record deleted!")
                st.rerun()

# MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial Mapping, Geocoding, & Statistical Analytics")
    st.write("To transform raw community assessment data into high-impact public health intelligence, assessment teams must integrate spatial visualization (GIS) with advanced statistical modeling.")

    p5_tab1, p5_tab2, p5_tab3 = st.tabs([
        "6.1 Spot Mapping & Geocoding Protocol",
        "6.2 Multi-Layer GIS Visualization Framework",
        "6.3 Statistical Analysis & Modeling Plan"
    ])

    with p5_tab1:
        st.markdown("### 6.1 Spot Mapping & Mobile Address Geocoding Protocol")
        st.markdown("""
        * **Step 1: Participatory BHW Spot Mapping:** Mobilize BHWs to draw baseline community spot maps capturing every residential structure, water source, and health facility.
        * **Step 2: GPS Mobile Geocoding:** Utilizing handheld GPS devices or mobile survey software (KoboToolbox), capture exact latitude and longitude coordinates $(x, y)$ for every surveyed household.
        * **Step 3: GIS Layering:** Upload geocoded survey points into QGIS or ArcGIS to convert static addresses into spatial shapefiles.
        """)

        st.markdown("---")
        st.markdown("#### 📍 Geocoded Survey Coordinates Preview")
        if len(st.session_state.hh_records) > 0:
            geo_df = pd.DataFrame(st.session_state.hh_records)[["HH_ID", "Purok", "Lat", "Lon", "Risk", "Flood_Prone"]]
            st.dataframe(geo_df, use_container_width=True)
        else:
            st.info("No household geocodes stored yet. Complete Phase 2 entries to populate spatial layers.")

    with p5_tab2:
        st.markdown("### 6.2 Multi-Layer GIS Visualization Framework")
        st.markdown("""
        * **Layer 1: Disease Hotspot Mapping:** Apply Kernel Density Estimation (KDE) to plot heatmaps of chronic hypertension, diabetes, and active TB clusters across Puroks.
        * **Layer 2: Environmental SDOH Overlay:** Superimpose disease hot spots over layers of unsafe water sources (Level I/unprotected), flood risk zones, and open waste dumping areas.
        * **Layer 3: Food Desert Identification:** Perform buffer analysis (500-meter walking radius) around fresh food markets versus sari-sari store density to map food deserts against childhood malnutrition.
        * **Layer 4: Catchment Isochrone Modeling:** Generate 15-minute and 30-minute travel time contours around the BHS/RHU to identify geographically isolated and disadvantaged areas (GIDAs).
        """)

        # Interactive Spatial Visualizer for Layer Overlays
        st.markdown("---")
        st.markdown("#### 🗺️ Multi-Layer Overlay Engine")
        selected_layer = st.selectbox("Select GIS Overlay Simulation Layer", [
            "Layer 1: Disease Hotspot Mapping (KDE Density)",
            "Layer 2: Environmental SDOH Overlay (Flood & Waste)",
            "Layer 3: Food Desert Identification (500m Buffers)",
            "Layer 4: Catchment Isochrone Modeling (15/30-min Travel contours)"
        ])

        if len(st.session_state.hh_records) > 0:
            m_df = pd.DataFrame(st.session_state.hh_records)
            st.pydeck_chart(pdk.Deck(
                layers=[
                    pdk.Layer(
                        "HexagonLayer" if "Layer 1" in selected_layer else "ScatterplotLayer",
                        data=m_df,
                        get_position=["Lon", "Lat"],
                        get_color="Color" if "Layer 1" not in selected_layer else None,
                        get_radius=20,
                        elevation_scale=4,
                        elevation_range=[0, 1000],
                        pickable=True,
                        extruded=True,
                    )
                ],
                initial_view_state=pdk.ViewState(
                    latitude=m_df["Lat"].mean(),
                    longitude=m_df["Lon"].mean(),
                    zoom=15, pitch=40
                )
            ))
        else:
            st.info("Add household coordinates in Phase 2 to render interactive GIS Spatial layers.")

    with p5_tab3:
        st.markdown("### 6.3 Statistical Analysis & Advanced Analytical Modeling Plan")
        
        st.markdown("#### A. Descriptive Analysis (Measuring the Social Gradient)")
        st.write("Cross-tabulate clinical health outcomes across income quintiles, educational attainment levels, and geographic zones. Calculate Odds Ratios (OR) and Relative Risks (RR) to quantify how disease burdens increase along lower socio-economic tiers.")

        st.markdown("#### B. Advanced Multivariate Modeling (Factor Analysis & Latent Class Analysis)")
        st.write("Social determinants rarely occur in isolation; compounding social risks produce exponential health detriments. Two advanced statistical techniques are deployed:")
        st.markdown("""
        * **1. Principal Component & Factor Analysis:** Collapse correlated environmental and economic variables (e.g., wall material, toilet type, income, water level) into latent factor scores (e.g., Household Deprivation Index) to measure overall structural vulnerability.
        * **2. Latent Class Analysis (LCA):** Group households into discrete vulnerability classes based on overlapping social risks (e.g., Class 1: High Income/High Access; Class 2: Severe Food Insecurity + Housing Instability + No Piped Water). Model the direct probability of chronic disease prevalence per class.
        """)

        st.markdown("---")
        st.markdown("#### 📊 Statistical Modeling Matrix")
        stat_plan_df = pd.DataFrame([
            {
                "Statistical Method": "Descriptive Cross-Tabulation & Odds Ratios",
                "Input Variables (Survey/GIS)": "Income Quintiles × Hypertension / Diabetes Prevalence",
                "Target Public Health Output": "Quantifies the slope of the social gradient in health across income tiers."
            },
            {
                "Statistical Method": "Factor Analysis (PCA)",
                "Input Variables (Survey/GIS)": "Housing materials, WASH level, Income, Cooking fuel",
                "Target Public Health Output": "Generates a composite 'Barangay Socio-Economic Vulnerability Index'."
            },
            {
                "Statistical Method": "Latent Class Analysis (LCA)",
                "Input Variables (Survey/GIS)": "Co-occurring food insecurity, housing instability, distance barrier",
                "Target Public Health Output": "Identifies multi-risk household clusters requiring integrated LGU social protection."
            }
        ])
        st.table(stat_plan_df)

# MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS & ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("Phase 6: Community Diagnosis Prioritization & Action Planning Matrix")

    with st.form("phase6_diag_form"):
        diag_title = st.text_input("Community Health Diagnosis Title", "High Hypertension Risk Burden Compounded by Seasonal Flooding")
        priority_puroks = st.multiselect("Priority Target Puroks", [f"Purok {i}" for i in range(1, 8)], default=["Purok 1", "Purok 3"])
        target_obj = st.text_area("Target Strategic Objectives & Outcomes")
        activities = st.text_area("Recommended Community Health Action Plans & BHS Interventions")

        if st.form_submit_button("Save Diagnosis & Action Plan"):
            st.session_state.diag_records.append({
                "Title": diag_title, "Puroks": priority_puroks, "Objectives": target_obj, "Activities": activities
            })
            save_session_to_disk()
            st.success("Action Plan saved successfully!")

# MODULE 8: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Shared Master Data Management, Backup & JSON Export")

    st.json({
        "Total_HH_Records": len(st.session_state.hh_records),
        "Total_Governance_Records": len(st.session_state.gov_records),
        "Total_Qualitative_Records": len(st.session_state.qual_records),
        "Total_PERI_Records": len(st.session_state.windshield_records),
        "Total_Diagnosis_Records": len(st.session_state.diag_records),
    })

    full_data_str = json.dumps({
        "hh_records": st.session_state.hh_records,
        "gov_records": st.session_state.gov_records,
        "qual_records": st.session_state.qual_records,
        "windshield_records": st.session_state.windshield_records,
        "diag_records": st.session_state.diag_records,
    }, indent=4)

    st.download_button("📥 Download All Compiled Survey Data (JSON)", data=full_data_str, file_name="shared_survey_data.json", mime="application/json")
