import json
import math
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
            width: 4.5in !important;
            max-width: 4.5in !important;
            margin: 50px auto;
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
        '<div class="login-sub">Field Enumerators & Lead Developers:<br>Jan Art'
        " A. Serna, RMT | Leila Projima, PTRP | Aubrey Maye Aurietta</div>",
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
    font-size: 14px !important;
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
    <div class="up-navbar-detail">Integrated System: Spatial Mapping, Geocoding, Analytics & Action Planning (Phases 1–6)</div>
    <div class="up-navbar-lead">Field Enumerators & Developers: Jan Art A. Serna, RMT | Leila Projima, PTRP | Aubrey Maye Aurietta</div>
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


def generate_research_table(
    data_list, denominator, var_title, label_col="Response Category"
):
    """Generates a research-grade frequency and percentage distribution table."""
    if not data_list or denominator == 0:
        return pd.DataFrame(
            columns=[
                "Variable Category",
                label_col,
                "Frequency (n)",
                "Percentage (%)",
            ]
        )

    flat_items = []
    for item in data_list:
        if isinstance(item, list):
            flat_items.extend([str(x) for x in item if str(x).strip() != ""])
        elif item is not None and str(item).strip() != "":
            flat_items.append(str(item))

    counts = Counter(flat_items)
    rows = []
    for category, count in counts.most_common():
        pct = (count / denominator) * 100.0
        rows.append({
            "Variable Category": var_title,
            label_col: category,
            "Frequency (n)": count,
            "Percentage (%)": f"{pct:.2f}%",
        })
    return pd.DataFrame(rows)


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
    st.write(
        f"{'✅' if p1_status else '🔴'} **Phase 1 (Governance):**"
        f" {'100%' if p1_status else '0%'}"
    )
    st.write(
        f"{'✅' if p2_status else '🔴'} **Phase 2 (Master Survey):**"
        f" {'100%' if p2_status else '0%'}"
    )
    st.write(
        f"{'✅' if p3_status else '🔴'} **Phase 3 (Qualitative):**"
        f" {'100%' if p3_status else '0%'}"
    )
    st.write(
        f"{'✅' if p4_status else '🔴'} **Phase 4 (Expanded PERI):**"
        f" {'100%' if p4_status else '0%'}"
    )
    st.write(
        f"{'✅' if p5_status else '🔴'} **Phase 5 (Analytics):**"
        f" {'100%' if p5_status else '0%'}"
    )
    st.write(
        f"{'✅' if p6_status else '🔴'} **Phase 6 (Action Plan):**"
        f" {'100%' if p6_status else '0%'}"
    )

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
    st.subheader(
        "📊 Executive Field Intelligence Dashboard & Automated Risk Engine"
    )
    st.caption(
        "Real-Time Multi-Phase Field Analytics, Epidemiological Insights &"
        " Automated Public Health Risk Prediction"
    )

    hh_data = st.session_state.hh_records
    gov_data = st.session_state.gov_records
    peri_data = st.session_state.windshield_records
    qual_data = st.session_state.qual_records
    diag_data = st.session_state.diag_records

    all_adults = [a for hh in hh_data for a in hh.get("Adults", [])]
    all_children = [c for hh in hh_data for c in hh.get("Children", [])]

    tot_hh = len(hh_data)
    tot_pop = len(all_adults) + len(all_children)

    htn_count = sum(
        1
        for a in all_adults
        if a.get("Risk") == "Hypertensive Risk"
        or a.get("Sys", 0) >= 140
        or a.get("Dia", 0) >= 90
    )
    htn_rate = (
        (htn_count / len(all_adults) * 100) if len(all_adults) > 0 else 0.0
    )

    avg_peri = (
        np.mean([p.get("PERI_Index", 0) for p in peri_data])
        if len(peri_data) > 0
        else 0.0
    )
    latest_gov = gov_data[-1].get("Score", 0) if len(gov_data) > 0 else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(
        "Total Surveyed HHs",
        f"{tot_hh}",
        delta=f"{tot_pop} People Profiled" if tot_pop > 0 else None,
    )
    m2.metric(
        "Adult Hypertensive Risk",
        f"{htn_rate:.1f}%",
        delta=f"{htn_count} High BP Adults",
        delta_color="inverse",
    )
    m3.metric(
        "Avg PERI Risk Index",
        f"{avg_peri:.2f}",
        delta=(
            "Cat C Critical"
            if avg_peri >= 2.3
            else ("Cat B Concern" if avg_peri >= 1.5 else "Cat A Low Risk")
        ),
        delta_color="inverse",
    )
    m4.metric(
        "BHB Governance Score",
        f"{latest_gov}/100",
        delta="High Functioning" if latest_gov >= 80 else "Needs Action",
        delta_color="normal",
    )
    m5.metric(
        "Action Plans Saved",
        f"{len(diag_data)} Plans",
        delta=f"{len(qual_data)} Qualitative Notes",
    )

    st.markdown("---")

    st.markdown("### 🤖 Automated Community Health Risk & Vulnerability Predictor")
    st.caption(
        "Dynamically evaluates multi-phase field vectors and generates priority"
        " public health interventions."
    )

    risk_triggers = []

    if htn_rate > 25.0:
        risk_triggers.append({
            "type": "high",
            "title": "🚨 Severe Adult Cardiovascular & Hypertension Surge",
            "desc": (
                f"Hyper-prevalence detected: **{htn_rate:.1f}%** of screened"
                " adults present with high BP (≥140/90 mmHg). Urgent community"
                " NCD screening and BHS compliance monitoring required."
            ),
            "action": (
                "Deploy BHWs for immediate home BP monitoring & RHU physician"
                " referral."
            ),
        })

    flood_hhs = sum(1 for hh in hh_data if hh.get("Flood_Prone") == "Yes")
    if tot_hh > 0 and (flood_hhs / tot_hh) >= 0.3:
        risk_triggers.append({
            "type": "high",
            "title": "🌊 Critical Climate & Flood Vector Exposure",
            "desc": (
                f"**{(flood_hhs/tot_hh*100):.1f}%** of surveyed households are"
                " located directly within severe flood-prone zones."
            ),
            "action": (
                "Coordinate with Municipal DRRMO for pre-disaster evacuation"
                " protocols and waterborne infection prophylaxis."
            ),
        })

    stunted_cnt = sum(
        1
        for c in all_children
        if "Stunted" in c.get("Nutr", {}).get("Stunting", "")
    )
    if len(all_children) > 0 and (stunted_cnt / len(all_children)) >= 0.2:
        risk_triggers.append({
            "type": "warn",
            "title": "👶 Elevated Child Malnutrition & Stunting Cluster",
            "desc": (
                "Child anthropometric screening reveals"
                f" **{(stunted_cnt/len(all_children)*100):.1f}%** stunting rate"
                " among profiled children under 5 years."
            ),
            "action": (
                "Enroll affected households in RHU supplementary feeding and"
                " IYCF nutrition education."
            ),
        })

    unsafe_water = sum(
        1 for hh in hh_data if "Unsafe" in hh.get("Water", "")
    )
    if unsafe_water > 0:
        risk_triggers.append({
            "type": "warn",
            "title": "🚰 Environmental WASH Vulnerability (Unsafe Water)",
            "desc": (
                f"**{unsafe_water}** household(s) rely on shallow wells or"
                " unprotected water sources, heightening diarrheal disease"
                " risk."
            ),
            "action": (
                "Distribute chlorine tablets / point-of-use water disinfection"
                " units and inspect water sources."
            ),
        })

    if not risk_triggers:
        st.markdown(
            """<div class="insight-alert-good">
            <strong>✅ Low Baseline Risk Detected:</strong> Current field data indicates manageable community health indicators. Continue quarterly monitoring and standard BHS preventive interventions.
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        for trig in risk_triggers:
            box_cls = (
                "insight-alert-high"
                if trig["type"] == "high"
                else "insight-alert-warn"
            )
            st.markdown(
                f"""<div class="{box_cls}">
                <strong>{trig['title']}</strong><br>
                {trig['desc']}<br>
                <em>🎯 Recommended Action: {trig['action']}</em>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    dash_tab1, dash_tab2, dash_tab3 = st.tabs([
        "📈 Disease & Vitals Analytics",
        "🌍 Environmental & PERI Breakdown",
        "🔍 Real-Time Master Household Roster",
    ])

    with dash_tab1:
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("**Adult Systolic BP Distribution**")
            if len(all_adults) > 0:
                sys_vals = [
                    a.get("Sys", 120) for a in all_adults if a.get("Sys", 0) > 0
                ]
                df_sys = pd.DataFrame({"Systolic BP": sys_vals})
                st.bar_chart(df_sys["Systolic BP"].value_counts().sort_index())
            else:
                st.info("No adult BP vitals recorded yet.")

        with c_right:
            st.markdown("**Chronic Disease Prevalence in Households**")
            if tot_hh > 0:
                htn_hhs = sum(
                    1
                    for hh in hh_data
                    if "Diagnosed" in hh.get("Hypertension_Status", "")
                )
                dm_hhs = sum(
                    1
                    for hh in hh_data
                    if "Diagnosed" in hh.get("Diabetes_Status", "")
                )
                asthma_hhs = sum(
                    1
                    for hh in hh_data
                    if "Diagnosed" in hh.get("Asthma_Status", "")
                )
                tb_hhs = sum(
                    1 for hh in hh_data if "DOTS" in hh.get("TB_Status", "")
                )

                df_chronic = pd.DataFrame({
                    "Condition": [
                        "Hypertension",
                        "Diabetes",
                        "Asthma/COPD",
                        "Tuberculosis",
                    ],
                    "Diagnosed HH Count": [
                        htn_hhs,
                        dm_hhs,
                        asthma_hhs,
                        tb_hhs,
                    ],
                }).set_index("Condition")
                st.bar_chart(df_chronic)
            else:
                st.info("No household morbidity records available.")

    with dash_tab2:
        if len(peri_data) > 0:
            st.markdown(
                "**Purok Environmental Risk Index (PERI) Domain Breakdown**"
            )
            peri_df = pd.DataFrame(peri_data)[[
                "Purok",
                "DS1_Sanitation",
                "DS2_Food",
                "DS3_BuiltEnv",
                "DS4_HealthInfra",
                "DS5_DRR",
                "DS6_Vector",
                "PERI_Index",
            ]]
            st.dataframe(peri_df, use_container_width=True)
            st.bar_chart(
                peri_df.set_index("Purok")[[
                    "DS1_Sanitation",
                    "DS2_Food",
                    "DS3_BuiltEnv",
                    "DS4_HealthInfra",
                    "DS5_DRR",
                    "DS6_Vector",
                ]]
            )
        else:
            st.info("No Phase 4 PERI windshield evaluations stored yet.")

    with dash_tab3:
        st.markdown("**Live Master Household Explorer**")
        if tot_hh > 0:
            search_query = st.text_input(
                "🔎 Search by Household ID, Barangay, or Head Name", ""
            )
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
                    "Water Source": h.get("Water"),
                })
            df_display = pd.DataFrame(flat_hhs)
            if search_query:
                df_display = df_display[
                    df_display.apply(
                        lambda r: search_query.lower() in str(r).lower(), axis=1
                    )
                ]
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No household data logged.")

# MODULE 1: INTERACTIVE SPOT MAP
elif menu == "🗺️ Interactive Spot Map":
    st.subheader(
        "📍 Interactive Barangay Health & Environmental Hazard Spot Map"
    )

    if len(st.session_state.hh_records) == 0:
        st.info(
            "No household survey records stored yet. Showing baseline map with"
            " simulated hazard markers."
        )
        map_df = pd.DataFrame([
            {
                "HH_ID": "HH-001",
                "Purok": "Purok 1",
                "Lat": 11.1562,
                "Lon": 124.9912,
                "BP": "145/92",
                "Risk": "Hypertensive Risk",
                "Flood_Prone": "Yes",
                "Color": [192, 38, 211, 230],
            },
            {
                "HH_ID": "HH-002",
                "Purok": "Purok 1",
                "Lat": 11.1568,
                "Lon": 124.9918,
                "BP": "118/78",
                "Risk": "Normal",
                "Flood_Prone": "No",
                "Color": [34, 197, 94, 200],
            },
            {
                "HH_ID": "HH-003",
                "Purok": "Purok 2",
                "Lat": 11.1555,
                "Lon": 124.9905,
                "BP": "120/80",
                "Risk": "Normal",
                "Flood_Prone": "Yes",
                "Color": [37, 99, 235, 220],
            },
            {
                "HH_ID": "HH-004",
                "Purok": "Purok 3",
                "Lat": 11.1570,
                "Lon": 124.9930,
                "BP": "150/98",
                "Risk": "Hypertensive Risk",
                "Flood_Prone": "No",
                "Color": [123, 17, 19, 220],
            },
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_m, col_f = st.columns([3, 1])

    with col_f:
        st.markdown("**Map Controls & Filters**")
        puroks = list(map_df["Purok"].unique())
        sel_puroks = st.multiselect(
            "Filter Puroks", options=puroks, default=puroks
        )
        flood_filter = st.selectbox("Flood Risk Filter", [
            "Show All Households",
            "Flood-Prone Zones Only",
            "Non-Flood Zones Only",
        ])

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
    flood_detected = sum(
        1 for _, r in filt_df.iterrows() if r.get("Flood_Prone") == "Yes"
    )

    st.markdown(
        f"📊 **Detected Summary:** Showing **{total_map_hh}** households | ⚠️"
        f" **{flood_detected}** located in detected **Flood-Prone Zones**."
    )

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
                tooltip={
                    "text": (
                        "HH: {HH_ID}\nPurok: {Purok}\nBP: {BP}\nHealth Risk:"
                        " {Risk}\nFlood Prone: {Flood_Prone}"
                    )
                },
            )
        )

# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD
elif menu == "📋 Phase 1: Full Governance Scorecard":
    st.subheader(
        "Phase 1: Barangay Health Board (BHB) Governance Scorecard (100-Point"
        " Instrument)"
    )

    with st.expander(
        "📖 View Formal Scoring Criteria Matrix & Governance Categorization"
        " Guide",
        expanded=False,
    ):
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

    mode_p1 = st.radio(
        "Select Operation",
        [
            "➕ New Scorecard Entry",
            "📂 Review, Edit & Delete Submitted Scorecards",
        ],
        horizontal=True,
    )

    if mode_p1 == "➕ New Scorecard Entry":
        with st.form("phase1_full_form"):
            t1, t2, t3, t4 = st.tabs([
                "📌 Metadata & Leadership",
                "🏛️ Legal, Meetings & Ordinances",
                "💰 AIP Budgeting & Reports",
                "🎯 Committee, Gaps & Action Plan",
            ])

            with t1:
                c1, c2, c3 = st.columns(3)
                b_name = c1.text_input("Barangay Name")
                city = c2.text_input("City / Municipality")
                prov = c3.text_input("Province")

                c1, c2, c3 = st.columns(3)
                eval_date = c1.date_input("Date of Evaluation")
                pb_head = c2.text_input("Punong Barangay (BHB Chair)")
                health_lead = c3.text_input(
                    "Committee Lead on Health / BHW Lead"
                )

            with t2:
                st.markdown(
                    "**Domain 1: Legal Reconstitution (Max 10 Points)**"
                )
                c1, c2 = st.columns(2)
                g1_1 = c1.number_input(
                    "1.1 Signed Executive Order (EO) / Resolution reconstituting"
                    " the BHB for current term (Max 5 pts)",
                    0,
                    5,
                    0,
                    help="Verification: Signed EO / Barangay Resolution Copy",
                )
                g1_2 = c2.number_input(
                    "1.2 Mandatory Multi-sectoral Representation present:"
                    " NGO/CBO, Youth/SK, BHW/BNS, Senior Citizen, DepEd (Max 5"
                    " pts)",
                    0,
                    5,
                    0,
                    help=(
                        "Verification: Appointment Papers / Roster of Members"
                    ),
                )

                st.markdown("**Domain 2: Meeting Regularity (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g2_1 = c1.number_input(
                    "2.1 Conduct of Regular Quarterly BHB Meetings (3 pts per"
                    " quarter conducted = 12 pts max)",
                    0,
                    12,
                    0,
                    help=(
                        "Verification: Minutes of Meeting & Attendance Sheets"
                        " (Q1-Q4)"
                    ),
                )
                g2_2 = c2.number_input(
                    "2.2 Official Quorum (>50% member attendance) consistently"
                    " documented in all meetings (Max 4 pts)",
                    0,
                    4,
                    0,
                    help="Verification: Signed Attendance Logs",
                )
                g2_3 = c3.number_input(
                    "2.3 Approved Action-Oriented Minutes with clear"
                    " resolution/action point tracking (Max 4 pts)",
                    0,
                    4,
                    0,
                    help="Verification: Approved BHB Minutes of Meetings",
                )

                st.markdown("**Domain 3: Legislative Output (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g3_1 = c1.number_input(
                    "3.1 Enactment of specific local ordinances on Sanitation,"
                    " WASH, Dengue, Rabies, or Tobacco/Vape Control (Max 10"
                    " pts)",
                    0,
                    10,
                    0,
                    help="Verification: Official Barangay Ordinances",
                )
                g3_2 = c2.number_input(
                    "3.2 Active enforcement mechanism, Task Force creation, or"
                    " penalty/monitoring protocols (Max 5 pts)",
                    0,
                    5,
                    0,
                    help="Verification: Enforcement Reports / Inspection Records",
                )
                g3_3 = c3.number_input(
                    "3.3 Policy alignment with DOH Universal Health Care (UHC)"
                    " & Municipal Health Priorities (Max 5 pts)",
                    0,
                    5,
                    0,
                    help=(
                        "Verification: Barangay Health Plan / Policy Framework"
                    ),
                )

            with t3:
                st.markdown(
                    "**Domain 4: AIP Budget Allocation (Max 20 Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g4_1 = c1.number_input(
                    "4.1 Dedicated, itemized Health & Sanitation budget"
                    " line-items in approved Barangay AIP (Max 8 pts)",
                    0,
                    8,
                    0,
                    help="Verification: Approved Barangay AIP Document",
                )
                g4_2 = c2.number_input(
                    "4.2 Adequate budget allocation for essential drugs, BHW"
                    " honoraria, and emergency health response (Max 6 pts)",
                    0,
                    6,
                    0,
                    help="Verification: Itemized Budget Breakdown",
                )
                g4_3 = c3.number_input(
                    "4.3 Budget execution and liquidation status (>75% budget"
                    " utilized for intended health programs) (Max 6 pts)",
                    0,
                    6,
                    0,
                    help=(
                        "Verification: Barangay Financial & Liquidation Reports"
                    ),
                )

                st.markdown(
                    "**Domain 5: Accomplishment Reports (Max 15 Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g5_1 = c1.number_input(
                    "5.1 Regular quarterly health tracking & epidemiological"
                    " reports submitted on time to RHU/MHO (Max 8 pts)",
                    0,
                    8,
                    0,
                    help=(
                        "Verification: Submitted RHU/MHO Transmittals & Reports"
                    ),
                )
                g5_2 = c2.number_input(
                    "5.2 Presentation of Barangay Health Status & Progress"
                    " during semi-annual Barangay Assemblies (Max 4 pts)",
                    0,
                    4,
                    0,
                    help="Verification: Barangay Assembly Minutes / Slides",
                )
                g5_3 = c3.number_input(
                    "5.3 Functional Barangay Health Information Board"
                    " maintained at BHS / Barangay Hall (Max 3 pts)",
                    0,
                    3,
                    0,
                    help="Verification: Updated BHS Data Board / Spot Map",
                )

            with t4:
                st.markdown(
                    "**Domain 6: Committee Functionality (Max 15 Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g6_1 = c1.number_input(
                    "6.1 Functional Technical Working Committees created (e.g.,"
                    " Dengue Task Force, WASH, Nutrition) (Max 6 pts)",
                    0,
                    6,
                    0,
                    help="Verification: TMC / Task Force Executive Orders",
                )
                g6_2 = c2.number_input(
                    "6.2 Monthly/Regular operational meetings and activity"
                    " implementation reports by committees (Max 6 pts)",
                    0,
                    6,
                    0,
                    help="Verification: TMC Activity Reports & Logbooks",
                )
                g6_3 = c3.number_input(
                    "6.3 Execution of community mobilization campaigns (e.g.,"
                    " Clean-up drives, Immunization, Operation Timbang) (Max 3"
                    " pts)",
                    0,
                    3,
                    0,
                    help="Verification: Photo Documentation & Activity Logs",
                )

                gap_summary = st.text_area(
                    "Identify primary governance bottlenecks & legislative"
                    " gaps:"
                )
                action_plan = st.text_area(
                    "Recommended technical assistance & corrective intervention"
                    " plan:"
                )

            if st.form_submit_button("Submit & Save Governance Scorecard"):
                total_score = sum([
                    g1_1,
                    g1_2,
                    g2_1,
                    g2_2,
                    g2_3,
                    g3_1,
                    g3_2,
                    g3_3,
                    g4_1,
                    g4_2,
                    g4_3,
                    g5_1,
                    g5_2,
                    g5_3,
                    g6_1,
                    g6_2,
                    g6_3,
                ])
                rating = (
                    "HIGH FUNCTIONING"
                    if total_score >= 80
                    else (
                        "MODERATE FUNCTIONING"
                        if total_score >= 50
                        else "LOW FUNCTIONING / CRITICAL INTERVENTION REQUIRED"
                    )
                )

                st.session_state.gov_records.append({
                    "Barangay": b_name,
                    "City": city,
                    "Province": prov,
                    "Evaluation_Date": str(eval_date),
                    "Punong_Barangay": pb_head,
                    "Health_Lead": health_lead,
                    "Score": total_score,
                    "Rating": rating,
                    "Gaps": gap_summary,
                    "ActionPlan": action_plan,
                })
                save_session_to_disk()
                st.success(
                    f"Scorecard Saved! Total Score: {total_score}/100 — Status:"
                    f" {rating}"
                )

    else:
        st.markdown("### 📂 Submitted Governance Scorecards")
        if len(st.session_state.gov_records) == 0:
            st.info("No governance scorecard records found.")
        else:
            gov_options = [
                f"[{i+1}] {r.get('Barangay', 'Unnamed')} (Score:"
                f" {r.get('Score', 0)})"
                for i, r in enumerate(st.session_state.gov_records)
            ]
            selected_idx = st.selectbox(
                "Select Record to Review / Edit",
                range(len(gov_options)),
                format_func=lambda x: gov_options[x],
            )
            rec = st.session_state.gov_records[selected_idx]

            with st.form("edit_gov_form"):
                e_brgy = st.text_input(
                    "Barangay Name", value=rec.get("Barangay", "")
                )
                e_city = st.text_input(
                    "City / Municipality", value=rec.get("City", "")
                )
                e_prov = st.text_input("Province", value=rec.get("Province", ""))
                e_score = st.number_input(
                    "Total Score (0–100)", 0, 100, int(rec.get("Score", 0))
                )
                e_rating = (
                    "HIGH FUNCTIONING"
                    if e_score >= 80
                    else (
                        "MODERATE FUNCTIONING"
                        if e_score >= 50
                        else "LOW FUNCTIONING / CRITICAL INTERVENTION REQUIRED"
                    )
                )
                e_gaps = st.text_area(
                    "Governance Bottlenecks", value=rec.get("Gaps", "")
                )
                e_action = st.text_area(
                    "Action Plan", value=rec.get("ActionPlan", "")
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Changes"):
                        rec.update({
                            "Barangay": e_brgy,
                            "City": e_city,
                            "Province": e_prov,
                            "Score": e_score,
                            "Rating": e_rating,
                            "Gaps": e_gaps,
                            "ActionPlan": e_action,
                        })
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
    st.subheader(
        "Phase 2: Master Household Survey Instrument (Dynamic Profile Entry &"
        " Cross-Module Interpretation)"
    )

    mode_p2 = st.radio(
        "Select Operation",
        [
            "➕ New Household Survey Entry",
            (
                "📊 Phase 2 Interpreted Data & Research Analytics Table"
                " Inspector"
            ),
            "📂 Review, Edit & Delete Submitted Household Surveys",
        ],
        horizontal=True,
    )

    if mode_p2 == "➕ New Household Survey Entry":
        st.markdown(
            "#### ⚙️ Enumerator Identification & Profile Roster Count"
            " Configuration"
        )
        st.info(
            "💡 **Multi-Enumerator Collision Prevention:** Select your"
            " Enumerator ID below. The Household ID automatically uses an"
            " enumerator-specific prefix (e.g., HH-E1-001, HH-E2-001) so all"
            " team members (Jan Art A. Serna, Leila Projima, Aubrey Maye"
            " Aurietta) can collect data concurrently without duplicate ID"
            " collisions."
        )

        if "adult_count" not in st.session_state:
            st.session_state.adult_count = 1
        if "child_count" not in st.session_state:
            st.session_state.child_count = 0

        c_cnt1, c_cnt2, c_cnt3, c_cnt4 = st.columns(4)
        with c_cnt1:
            st.session_state.adult_count = st.number_input(
                "Adult Members Count",
                min_value=0,
                max_value=20,
                value=st.session_state.adult_count,
                step=1,
            )
        with c_cnt2:
            if st.button("➕ Add Adult Form", use_container_width=True):
                st.session_state.adult_count += 1
                st.rerun()
        with c_cnt3:
            st.session_state.child_count = st.number_input(
                "Child Members Count (<5 yrs)",
                min_value=0,
                max_value=15,
                value=st.session_state.child_count,
                step=1,
            )
        with c_cnt4:
            if st.button("➕ Add Child Form", use_container_width=True):
                st.session_state.child_count += 1
                st.rerun()

        num_adults = st.session_state.adult_count
        num_children = st.session_state.child_count

        c_e1, c_e2 = st.columns(2)
        enum_select = c_e1.selectbox(
            "👤 Enumerator Identifier",
            [
                "Jan Art A. Serna, RMT (Code: E1)",
                "Leila Projima, PTRP (Code: E2)",
                "Aubrey Maye Aurietta (Code: E3)",
            ],
            index=0,
        )
        enum_code = (
            "E1"
            if "E1" in enum_select
            else ("E2" if "E2" in enum_select else "E3")
        )

        existing_hh_ids = [
            r.get("HH_ID", "") for r in st.session_state.hh_records
        ]
        enum_existing_count = (
            sum(
                1
                for r in st.session_state.hh_records
                if r.get("Enumerator_Code") == enum_code
                or r.get("HH_ID", "").startswith(f"HH-{enum_code}-")
            )
            + 1
        )
        auto_suggested_id = f"HH-{enum_code}-{enum_existing_count:03d}"

        with st.form("phase2_complete_form"):
            t_meta, t_vitals, t_socio, t_dec, t_morb, t_mch, t_child, t_yakap = (
                st.tabs([
                    "📋 Metadata & Roster",
                    "🩺 Dynamic Adult Profiling & Vitals",
                    "🌾 Socio-Econ, Food Security, Housing & WASH",
                    "🤝 Decision-Making Patterns",
                    "🤒 Morbidity & Chronic Care",
                    "👩 Maternal, FP & Mortality",
                    "👶 Dynamic Child Profiling & Immunization",
                    "🏥 Health-Seeking Behavior & PhilHealth YAKAP",
                ])
            )

            # --- TAB 1: METADATA & ROSTER ---
            with t_meta:
                st.markdown("**Survey Metadata & Unique Household Identification**")
                c1, c2, c3, c4 = st.columns(4)
                hh_id = c1.text_input(
                    "Household ID (Enumerator Prefixed)", value=auto_suggested_id
                )
                brgy = c2.text_input("Barangay Name")
                purok = c3.selectbox(
                    "Purok / Zone", [f"Purok {i}" for i in range(1, 8)]
                )
                date_survey = c4.date_input("Date of Survey")

                if hh_id in existing_hh_ids:
                    st.error(
                        f"⛔ CRITICAL COLLISION WARNING: Household ID '{hh_id}'"
                        " ALREADY EXISTS in persistent storage! Change the ID"
                        " to ensure uniqueness."
                    )

                c1, c2, c3, c4 = st.columns(4)
                lat = c1.number_input(
                    "Latitude", value=11.1560, format="%.4f"
                )
                lon = c2.number_input(
                    "Longitude", value=124.9920, format="%.4f"
                )
                enum_name = c3.text_input(
                    "Enumerator Full Name",
                    enum_select.split("(")[0].strip(),
                )
                resp_role = c4.selectbox(
                    "Respondent Role",
                    ["Head", "Spouse", "Adult Member", "Other"],
                )

                c1, c2, c3 = st.columns(3)
                surv_status = c1.selectbox(
                    "Survey Status",
                    ["Completed", "Partially Completed", "Refused"],
                )
                dialect = c2.selectbox(
                    "Primary Dialect Spoken at Home",
                    [
                        "Waray",
                        "Tagalog",
                        "English",
                        "Mixed",
                        "Cebuano / Bisaya",
                        "Ilocano",
                        "Bicolano",
                        "Hiligaynon / Ilonggo",
                        "Pangasinan",
                        "Other Language",
                    ],
                )
                religion = c3.selectbox(
                    "Religion",
                    [
                        "Roman Catholic",
                        "Islam",
                        "Iglesia ni Cristo (INC)",
                        "Evangelical / Protestant",
                        "Seventh-day Adventist",
                        "Aglipayan (IFI)",
                        "Jehovah's Witnesses",
                        "Church of Jesus Christ of Latter-day Saints",
                        "Born Again Christian",
                        "None / Secular",
                        "Other Religion",
                    ],
                )

                st.markdown("---")
                st.markdown("**Household Demographic Roster**")
                c1, c2, c3, c4 = st.columns(4)
                tot_children = c1.number_input(
                    "No. of Children (<18 yrs)", 0, 20, 0
                )
                tot_dependents = c2.number_input(
                    "No. of Other Dependents", 0, 10, 0
                )
                hh_head_name = c3.text_input("Household Head Full Name")
                head_civil = c4.selectbox(
                    "Head Civil Status",
                    ["Single", "Married", "Widowed", "Separated", "Cohabiting"],
                )

            # --- TAB 2: DYNAMIC ADULT PROFILING ---
            with t_vitals:
                st.markdown(
                    "**Module B: Adult Profiling & Physical Screening"
                    f" ({num_adults} Adult(s) Active)**"
                )

                adults_data = []
                for i in range(1, int(num_adults) + 1):
                    st.markdown(
                        "<div class='adult-card'><strong>Adult Member"
                        f" {i} Full Profile & Physical Screening</strong></div>",
                        unsafe_allow_html=True,
                    )
                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_name = c1.text_input(
                        f"Adult {i} Name / Initials", key=f"a_name_{i}"
                    )
                    a_gender = c2.selectbox(
                        f"Adult {i} Gender",
                        ["Male", "Female", "Other"],
                        key=f"a_gen_{i}",
                    )
                    a_age = c3.number_input(
                        f"Adult {i} Age", 18, 120, 30, key=f"a_age_{i}"
                    )
                    a_edu = c4.selectbox(
                        f"Adult {i} Education",
                        [
                            "No Formal Education",
                            "Elementary Unfinished",
                            "Elementary Graduate",
                            "High School Unfinished",
                            "High School Graduate",
                            "Vocational / College Unfinished",
                            "College Graduate",
                            "Post-Graduate",
                        ],
                        key=f"a_edu_{i}",
                    )
                    a_occ = c5.text_input(
                        f"Adult {i} Primary Occupation", key=f"a_occ_{i}"
                    )

                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_ph_cat = c1.selectbox(
                        f"Adult {i} PhilHealth",
                        [
                            "Indigent",
                            "Formal",
                            "Informal",
                            "Dependent",
                            "Unenrolled",
                        ],
                        key=f"a_ph_{i}",
                    )
                    a_sys = c2.number_input(
                        f"Adult {i} Systolic BP", 50, 250, 120, key=f"a_sys_{i}"
                    )
                    a_dia = c3.number_input(
                        f"Adult {i} Diastolic BP", 30, 150, 80, key=f"a_dia_{i}"
                    )
                    a_spo2 = c4.number_input(
                        f"Adult {i} SpO2 (%)", 50, 100, 98, key=f"a_spo2_{i}"
                    )
                    a_pulse = c5.number_input(
                        f"Adult {i} Pulse (bpm)", 30, 200, 75, key=f"a_pulse_{i}"
                    )

                    c1, c2 = st.columns(2)
                    a_symptoms = c1.multiselect(
                        f"Adult {i} Current Complaints / Symptoms",
                        [
                            "None",
                            "Cough",
                            "Fever / feeling feverish",
                            "Headache",
                            "Colds / runny nose",
                            "Body aches / muscle pain",
                            "Abdominal pain",
                            "Diarrhea",
                            "Back pain",
                            "Dizziness",
                            "Sore throat",
                            "Others",
                        ],
                        default=["None"],
                        key=f"a_sym_{i}",
                    )
                    a_risk = c2.selectbox(
                        f"Adult {i} Risk Category",
                        [
                            "Normal",
                            "Hypertensive Risk",
                            "Hypoxemic (<95%)",
                            "Fever / Febrile",
                            "Tachycardic / Bradycardic",
                        ],
                        key=f"a_risk_{i}",
                    )

                    a_action = st.multiselect(
                        f"🩺 Adult {i} Action Taken",
                        [
                            "Referral to RHU / MHO Physician",
                            "Referral to BHS / Barangay Midwife",
                            "Health Education & Lifestyle Counseling",
                            "Medication Compliance Check",
                            "Follow-up Visit Scheduled",
                            "Immediate Emergency Hospital Referral",
                            "None / Normal Vitals",
                        ],
                        default=(
                            ["None / Normal Vitals"]
                            if a_risk == "Normal"
                            else ["Referral to RHU / MHO Physician"]
                        ),
                        key=f"a_action_{i}",
                    )

                    if a_name.strip() != "":
                        adults_data.append({
                            "ID": f"Adult {i}",
                            "Name": a_name,
                            "Gender": a_gender,
                            "Age": a_age,
                            "Edu": a_edu,
                            "Occupation": a_occ,
                            "PhilHealth_Cat": a_ph_cat,
                            "BP": f"{a_sys}/{a_dia}",
                            "Sys": a_sys,
                            "Dia": a_dia,
                            "SpO2": a_spo2,
                            "Pulse": a_pulse,
                            "Complaints": a_symptoms,
                            "Risk": a_risk,
                            "Action_Taken": a_action,
                        })

            # --- TAB 3: SOCIO-ECON, FOOD INSECURITY, HOUSING & WASH ---
            with t_socio:
                st.markdown(
                    "**C1. Livelihood, Economic Stability & Domestic Assets**"
                )
                c1, c2, c3 = st.columns(3)
                income_cat = c1.selectbox(
                    "Average Family Income / Month",
                    [
                        "≤ ₱10,000 (Q1)",
                        "₱10,001–₱20,000 (Q2)",
                        "₱20,001–₱35,000 (Q3)",
                        "₱35,001–₱50,000 (Q4)",
                        "> ₱50,000 (Q5)",
                    ],
                )
                livelihood = c2.selectbox(
                    "Primary Livelihood Source",
                    [
                        "Farming (Owned)",
                        "Farming (Tenanted)",
                        "Laborer",
                        "Carpentry",
                        "Fishing",
                        "Peddling",
                        "Gov't Employee",
                        "Small Industry/Sari-Sari",
                        "Other",
                    ],
                )
                food_prod = c3.selectbox(
                    "Engaged in Food Production?", ["Yes", "No"]
                )

                c1, c2 = st.columns(2)
                emergency_5k = c1.selectbox(
                    "Emergency Cushion: Can raise ₱5,000 in 24 hrs?",
                    ["Yes", "No"],
                )
                p4ps_status = c2.selectbox(
                    "Active 4Ps Beneficiary?", ["Yes", "No"]
                )

                st.markdown(
                    "**Domestic Assets, Utilities & Transportation Owned**"
                )
                c1, c2, c3 = st.columns(3)
                transpo_owned = c1.multiselect(
                    "Type of Transportation Owned",
                    [
                        "None",
                        "Bicycle",
                        "Motorcycle / Tricycle",
                        "Private Car / Van",
                        "Motorized Banca / Boat",
                    ],
                    default=["None"],
                )
                utilities_avail = c2.multiselect(
                    "Utilities / Services Available",
                    [
                        "Grid Electricity",
                        "Solar Power",
                        "Piped Water Connection",
                        "Cellular Signal",
                        "Internet / Broadband",
                        "Garbage Collection Service",
                    ],
                    default=["Grid Electricity"],
                )
                appliances_owned = c3.multiselect(
                    "Appliances Owned",
                    [
                        "Refrigerator",
                        "Television",
                        "Washing Machine",
                        "Electric Fan",
                        "Gas / Electric Stove",
                        "Air Conditioner",
                    ],
                    default=["Electric Fan"],
                )

                st.markdown("---")
                st.markdown(
                    "**C2. Household Food Insecurity Assessment (Past 30"
                    " Days)**"
                )
                c1, c2, c3 = st.columns(3)
                food_skip = c1.selectbox(
                    "Skipped meal / reduced portion size due to lack of money?",
                    ["No", "Yes"],
                )
                food_worry = c2.selectbox(
                    "Worried about running out of food before having money to"
                    " buy?",
                    ["No", "Yes"],
                )
                food_fullday = c3.selectbox(
                    "Went a full day without eating due to lack of food/money?",
                    ["No", "Yes"],
                )

                st.markdown("---")
                st.markdown(
                    "**C3. Housing, Built Environment & Indoor Air Risk**"
                )
                c1, c2, c3 = st.columns(3)
                tenure = c1.selectbox(
                    "Tenurial Status",
                    [
                        "Residential lot with house",
                        "Residential House without Lot",
                        "Renting",
                        "Shared",
                        "Farm Land",
                        "Informal Settler / Caretaker",
                    ],
                )
                house_type = c2.selectbox(
                    "Housing Construction Type",
                    [
                        "Light (Nipa, bamboo, cogon)",
                        "Medium (Wooden floors/walls, G.I. roof)",
                        "Heavy / Permanent (Concrete/hardwood)",
                    ],
                )
                cook_fuel = c3.selectbox(
                    "Indoor Air Risk (Cooking Fuel)",
                    ["LPG", "Charcoal", "Wood", "Kerosene", "Electric"],
                )

                c1, c2 = st.columns(2)
                is_flood_prone = c1.selectbox(
                    "🌊 Is Household Located in a Flood-Prone Zone?",
                    ["No", "Yes"],
                )

                st.markdown("---")
                st.markdown(
                    "**C4. WASH Infrastructure & Environmental Health**"
                )
                c1, c2, c3 = st.columns(3)
                water_source = c1.selectbox(
                    "Drinking Water Source Level",
                    [
                        "Level 1: Protected Well / Spring",
                        "Level 2: Piped network & communal faucet",
                        "Level 3: Individual household tap",
                        "Unsafe: Shallow Well / River / Surface",
                        "Commercial Refill Station",
                    ],
                )
                toilet_type = c2.selectbox(
                    "Sanitation / Toilet Facility Type",
                    [
                        "Pour/Flush to Septic Tank",
                        "Ventilated Improved Pit (VIP) Latrine",
                        "Open Defecation / None",
                    ],
                )
                solid_disposal = c3.selectbox(
                    "Solid Waste Disposal Method",
                    [
                        "Municipal/Barangay Collection",
                        "Composting",
                        "Burying",
                        "Burning (Siga)",
                        "Open Dumping",
                        "River Disposal",
                    ],
                )

            # --- TAB 4: DECISION-MAKING PATTERNS ---
            with t_dec:
                st.markdown(
                    "**Module D: Decision-Making Pattern & Community"
                    " Participation**"
                )
                c1, c2 = st.columns(2)
                dec_expenses = c1.multiselect(
                    "Who decides on Family Expenses?",
                    ["Father", "Mother", "Children", "Single Member", "Others"],
                    default=["Father", "Mother"],
                )
                dec_health = c2.multiselect(
                    "Who decides on Health & Medical Care?",
                    ["Father", "Mother", "Children", "Single Member", "Others"],
                    default=["Mother"],
                )

            # --- TAB 5: MORBIDITY & CHRONIC CARE ---
            with t_morb:
                st.markdown(
                    "**Module E1: Acute Infectious Diseases & Illnesses (Past 12"
                    " Months)**"
                )
                c1, c2, c3 = st.columns(3)
                e_diarrhea = c1.selectbox(
                    "Diarrheal Episodes (>1 in past 12 mos in family)",
                    ["No", "Yes"],
                )
                e_urti = c2.selectbox(
                    "Severe Upper Respiratory Infections / Pneumonia",
                    ["No", "Yes"],
                )
                e_dengue = c3.selectbox(
                    "Suspected or Confirmed Dengue Cases", ["No", "Yes"]
                )

                st.markdown(
                    "**Module E2: Physician-Diagnosed Chronic Conditions &"
                    " Treatment Compliance**"
                )
                c1, c2 = st.columns(2)
                htn_status = c1.selectbox(
                    "Hypertension Status in Household",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Compliant with Meds Daily",
                        "Diagnosed - Irregular Med Compliance",
                        "Diagnosed - Unmedicated / Stopped",
                    ],
                )
                dm_status = c2.selectbox(
                    "Type 2 Diabetes Status in Household",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Compliant with Meds Daily",
                        "Diagnosed - Irregular Med Compliance",
                        "Diagnosed - Unmedicated / Stopped",
                    ],
                )

                c1, c2 = st.columns(2)
                asthma_status = c1.selectbox(
                    "Bronchial Asthma / COPD Status",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Active Maintenance Inhaler",
                        "Diagnosed - Emergency Meds Only",
                        "Diagnosed - Untreated",
                    ],
                )
                tb_status = c2.selectbox(
                    "Tuberculosis (TB) History & DOTS Status",
                    [
                        "No Member Diagnosed",
                        "Currently Enrolled in TB-DOTS",
                        "Completed TB Treatment",
                        "Defaulted / Interrupted DOTS",
                    ],
                )

                c1, c2, c3 = st.columns(3)
                ckd_status = c1.selectbox(
                    "Chronic Kidney Disease (CKD)",
                    ["No", "Yes - Stage 1-3", "Yes - Dialysis Dependent"],
                )
                cvd_status = c2.selectbox(
                    "Cardiovascular Disease / History of Stroke", ["No", "Yes"]
                )
                cancer_status = c3.selectbox(
                    "Active Malignancy / Cancer", ["No", "Yes"]
                )

            # --- TAB 6: MATERNAL, FP & MORTALITY ---
            with t_mch:
                st.markdown(
                    "**Module F1: Maternal & Reproductive Health Protocols**"
                )
                c1, c2, c3 = st.columns(3)
                is_preg = c1.selectbox(
                    "Currently Pregnant Member in Household?", ["No", "Yes"]
                )
                anc_visits = c2.number_input(
                    "Antenatal Care (ANC) Visits (Target ≥4)", 0, 15, 0
                )
                anc_1st_tri = c3.selectbox(
                    "First ANC Visit in 1st Trimester?", ["N/A", "Yes", "No"]
                )

                c1, c2, c3 = st.columns(3)
                ifa_tablets = c1.selectbox(
                    "Iron-Folic Acid (IFA) Tablets Received",
                    ["N/A", "<180 Tablets", "≥180 Tablets (Completed)"],
                )
                td_status = c2.selectbox(
                    "Tetanus Diphtheria (Td) Immunization",
                    ["N/A", "Td1", "Td2", "Td3+", "Fully Immunized Mother"],
                )
                postpartum_check = c3.selectbox(
                    "Postpartum Checkup within 72 hours", ["N/A", "Yes", "No"]
                )

                st.markdown("---")
                st.markdown("**Module F2: Delivery & Family Planning**")
                c1, c2 = st.columns(2)
                deliv_personnel_yesno = c1.selectbox(
                    "Delivery handled by trained health personnel?",
                    ["N/A", "Yes", "No"],
                )
                deliv_facility_yesno = c2.selectbox(
                    "Delivery handled in an accredited Health Facility?",
                    ["N/A", "Yes", "No"],
                )

                c1, c2 = st.columns(2)
                fp_access = c1.selectbox(
                    "Couples with access to family planning services?",
                    ["Yes", "No"],
                )
                fp_practice = c2.selectbox(
                    "Couples practicing family planning?", ["Yes", "No"]
                )

                st.markdown("---")
                st.markdown("**Module F3: Mortality Assessment (Jan–Dec)**")
                mortality_yesno = st.selectbox(
                    "With deaths in the family due to preventable diseases"
                    " (Jan-Dec)?",
                    ["No", "Yes"],
                )

            # --- TAB 7: DYNAMIC CHILD PROFILING ---
            with t_child:
                st.markdown(
                    "**Module F4: Expanded Child Anthropometric & Immunization"
                    f" Record Profiling ({num_children} Child(ren) Active)**"
                )

                children_records = []
                for c_i in range(1, int(num_children) + 1):
                    st.markdown(
                        f"<div class='child-card'><strong>👶 Child Member {c_i}"
                        " Profile & Immunization Screening</strong></div>",
                        unsafe_allow_html=True,
                    )
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c_name = c1.text_input(
                        f"Child {c_i} Name / Initials", key=f"c_name_{c_i}"
                    )
                    c_sex = c2.selectbox(
                        f"Child {c_i} Sex",
                        ["Male", "Female"],
                        key=f"c_sex_{c_i}",
                    )
                    c_age_m = c3.number_input(
                        f"Child {c_i} Age (Months)", 0, 59, 12, key=f"c_age_{c_i}"
                    )
                    c_wt_kg = c4.number_input(
                        f"Child {c_i} Weight (kg)",
                        0.0,
                        35.0,
                        8.5,
                        key=f"c_wt_{c_i}",
                    )
                    c_ht_cm = c5.number_input(
                        f"Child {c_i} Height (cm)",
                        0.0,
                        120.0,
                        72.0,
                        key=f"c_ht_{c_i}",
                    )

                    c_nutr = compute_child_nutrition(c_age_m, c_wt_kg, c_ht_cm)
                    st.caption(
                        f"📊 **Outcome:** BMI: {c_nutr['BMI']} | Wasting:"
                        f" **{c_nutr['Wasting']}** | Stunting:"
                        f" **{c_nutr['Stunting']}** | Underweight:"
                        f" **{c_nutr['Underweight']}**"
                    )

                    st.markdown(
                        f"**💉 Child {c_i} Immunization Card Check:**"
                    )
                    ic1, ic2, ic3, ic4, ic5, ic6 = st.columns(6)
                    imm_bcg = ic1.checkbox("BCG", key=f"bcg_{c_i}")
                    imm_hepb = ic2.checkbox("Hep B", key=f"hepb_{c_i}")
                    imm_penta = ic3.checkbox("Pentavalent 3x", key=f"penta_{c_i}")
                    imm_opv = ic4.checkbox("OPV/IPV 3x", key=f"opv_{c_i}")
                    imm_pcv = ic5.checkbox("PCV 3x", key=f"pcv_{c_i}")
                    imm_mmr = ic6.checkbox("MMR 2x", key=f"mmr_{c_i}")

                    is_fic = all([
                        imm_bcg,
                        imm_hepb,
                        imm_penta,
                        imm_opv,
                        imm_pcv,
                        imm_mmr,
                    ])
                    fic_status = (
                        "Fully Immunized Child (FIC)"
                        if is_fic
                        else "Partially Immunized / Incomplete"
                    )

                    c_action = st.multiselect(
                        f"👶 Child {c_i} Action Taken",
                        [
                            "Referral to RHU / Nutrition Officer",
                            "Referral for Supplementary Feeding",
                            "IYCF Counseling",
                            "Immunization Catch-up",
                            "Vitamin A Supplementation",
                            "Deworming Administration",
                            "None / Normal",
                        ],
                        default=(
                            ["None / Normal"]
                            if (is_fic and "Normal" in c_nutr["Wasting"])
                            else ["Referral to RHU / Nutrition Officer"]
                        ),
                        key=f"c_action_{c_i}",
                    )

                    if c_name.strip() != "":
                        children_records.append({
                            "Child_Num": f"Child {c_i}",
                            "Name": c_name,
                            "Sex": c_sex,
                            "Age_Months": c_age_m,
                            "Weight": c_wt_kg,
                            "Height": c_ht_cm,
                            "Nutr": c_nutr,
                            "FIC_Status": fic_status,
                            "BCG": imm_bcg,
                            "HepB": imm_hepb,
                            "Penta": imm_penta,
                            "OPV": imm_opv,
                            "PCV": imm_pcv,
                            "MMR": imm_mmr,
                            "Action_Taken": c_action,
                        })

            # --- TAB 8: HEALTH-SEEKING BEHAVIOR & YAKAP ---
            with t_yakap:
                st.markdown(
                    "**Module G: Health-Seeking Behavior & PhilHealth YAKAP"
                    " Access**"
                )
                hsb_initial_actions = st.multiselect(
                    "Initial Actions When Unwell",
                    [
                        "Rest and wait",
                        "Use home/herbal remedies",
                        "Buy OTC medication",
                        "Search symptoms online",
                        "Ask family/friends",
                        "Contact healthcare provider",
                    ],
                    default=["Rest and wait"],
                )
                hsb_providers_used = st.multiselect(
                    "Facilities/Providers Used",
                    [
                        "Public hospital",
                        "Private clinic/hospital",
                        "Community health center / RHU",
                        "Local pharmacy",
                        "Traditional practitioner",
                        "Telehealth",
                    ],
                    default=["Community health center / RHU"],
                )
                hsb_travel_time = st.selectbox(
                    "Travel Time to Nearest Health Facility",
                    [
                        "Less than 15 minutes",
                        "15 to 30 minutes",
                        "30 minutes to 1 hour",
                        "More than 1 hour",
                    ],
                )
                hsb_barriers = st.multiselect(
                    "Barriers to Seeking Care",
                    [
                        "High cost of consultation/meds",
                        "Long waiting times",
                        "Distance / lack of transpo",
                        "Work/caregiving responsibilities",
                        "Fear of diagnosis",
                        "Lack of insurance coverage",
                    ],
                )
                hsb_influencers = st.multiselect(
                    "Key Influencers in Decisions",
                    [
                        "Spouse / Immediate family",
                        "Parents / Relatives",
                        "Friends / Peers",
                        "Community / Religious leaders",
                        "Independent decision",
                    ],
                    default=["Independent decision"],
                )
                hsb_criteria = st.multiselect(
                    "Criteria for Choosing Facility",
                    [
                        "Low cost / insurance",
                        "Proximity",
                        "Short waiting time",
                        "Reputation",
                        "Confidential & respectful staff",
                        "Clean & supplied",
                    ],
                )

                c1, c2 = st.columns(2)
                yakap_registered = c1.selectbox(
                    "Registered under PhilHealth YAKAP?",
                    ["Yes", "No", "Uncertain"],
                )
                yakap_availed = c2.selectbox(
                    "Availed FREE First Patient Encounter (FPE)?",
                    ["Yes", "No", "N/A"],
                )

            if st.form_submit_button("Submit & Save Complete Household Record"):
                if hh_id in existing_hh_ids:
                    st.error(
                        f"Cannot save: Household ID '{hh_id}' already exists"
                        " in persistent storage! Please change the Household ID."
                    )
                else:
                    primary_sys = (
                        adults_data[0]["Sys"] if len(adults_data) > 0 else 120
                    )
                    primary_risk = (
                        adults_data[0]["Risk"]
                        if len(adults_data) > 0
                        else "Normal"
                    )

                    marker_color = (
                        [192, 38, 211, 230]
                        if (is_flood_prone == "Yes" and primary_sys >= 140)
                        else (
                            [123, 17, 19, 220]
                            if primary_sys >= 140
                            else (
                                [37, 99, 235, 220]
                                if is_flood_prone == "Yes"
                                else [34, 197, 94, 200]
                            )
                        )
                    )

                    st.session_state.hh_records.append({
                        "HH_ID": hh_id,
                        "Enumerator_Code": enum_code,
                        "Barangay": brgy,
                        "Purok": purok,
                        "Date": str(date_survey),
                        "Lat": lat,
                        "Lon": lon,
                        "Enumerator": enum_name,
                        "Respondent_Role": resp_role,
                        "Survey_Status": surv_status,
                        "Dialect": dialect,
                        "Religion": religion,
                        "Total_Children": tot_children,
                        "Total_Dependents": tot_dependents,
                        "Head_Name": hh_head_name,
                        "Head_Civil_Status": head_civil,
                        "BP": f"{primary_sys}/80",
                        "Risk": primary_risk,
                        "Flood_Prone": is_flood_prone,
                        "Color": marker_color,
                        "Adults": adults_data,
                        "Children": children_records,
                        "Income": income_cat,
                        "Livelihood": livelihood,
                        "Food_Production": food_prod,
                        "Emergency_5k": emergency_5k,
                        "Four_Ps": p4ps_status,
                        "Transport_Owned": transpo_owned,
                        "Utilities": utilities_avail,
                        "Appliances": appliances_owned,
                        "Food_Skip": food_skip,
                        "Food_Worry": food_worry,
                        "Food_FullDay": food_fullday,
                        "Tenure": tenure,
                        "House_Type": house_type,
                        "Cook_Fuel": cook_fuel,
                        "Water": water_source,
                        "Sanitation": toilet_type,
                        "Solid_Disposal": solid_disposal,
                        "Decisions_Expenses": dec_expenses,
                        "Decisions_Health": dec_health,
                        "Diarrhea": e_diarrhea,
                        "URTI": e_urti,
                        "Dengue": e_dengue,
                        "Hypertension_Status": htn_status,
                        "Diabetes_Status": dm_status,
                        "Asthma_Status": asthma_status,
                        "TB_Status": tb_status,
                        "CKD_Status": ckd_status,
                        "CVD_Status": cvd_status,
                        "Cancer_Status": cancer_status,
                        "Is_Pregnant": is_preg,
                        "ANC_Visits": anc_visits,
                        "ANC_1st_Tri": anc_1st_tri,
                        "IFA_Tablets": ifa_tablets,
                        "Td_Status": td_status,
                        "Postpartum_Check": postpartum_check,
                        "Deliv_Personnel": deliv_personnel_yesno,
                        "Deliv_Facility": deliv_facility_yesno,
                        "FP_Access": fp_access,
                        "FP_Practice": fp_practice,
                        "Preventable_Mortality": mortality_yesno,
                        "HSB_Initial_Actions": hsb_initial_actions,
                        "HSB_Providers_Used": hsb_providers_used,
                        "HSB_Travel_Time": hsb_travel_time,
                        "HSB_Barriers": hsb_barriers,
                        "HSB_Influencers": hsb_influencers,
                        "HSB_Criteria": hsb_criteria,
                        "Yakap": yakap_registered,
                        "Yakap_Availed": yakap_availed,
                    })
                    save_session_to_disk()
                    st.success(
                        f"Household record '{hh_id}' saved successfully with"
                        " dynamic individual profiles!"
                    )

    elif (
        mode_p2
        == "📊 Phase 2 Interpreted Data & Research Analytics Table Inspector"
    ):
        st.markdown(
            "### 📊 Comprehensive Research Interpretation & Master Survey"
            " Variable Tables"
        )

        if len(st.session_state.hh_records) == 0:
            st.info(
                "No household survey records found in Phase 2. Please add"
                " entries to view interpreted research analytics."
            )
        else:
            tab_interp, tab_research, tab_indiv = st.tabs([
                "📈 Aggregated Cross-Module Dashboard",
                "🔬 Master Survey Questions Research Tables (n & %)",
                "🔍 Individual Response Inspector",
            ])

            with tab_interp:
                total_hhs = len(st.session_state.hh_records)
                all_adults = [
                    a
                    for hh in st.session_state.hh_records
                    for a in hh.get("Adults", [])
                ]
                all_children = [
                    c
                    for hh in st.session_state.hh_records
                    for c in hh.get("Children", [])
                ]

                st.markdown(
                    f"#### 🌐 Overview: Aggregate Coverage ({total_hhs}"
                    f" Households | {len(all_adults)} Adults Profiled |"
                    f" {len(all_children)} Children Profiled)"
                )

                st.markdown(
                    "##### 1. Demographics, Dialect & Adult Physical Screening"
                )
                col1, col2, col3, col4 = st.columns(4)

                dialects_cnt = Counter([
                    hh.get("Dialect", "N/A")
                    for hh in st.session_state.hh_records
                ])
                top_dialect = (
                    dialects_cnt.most_common(1)[0][0] if dialects_cnt else "N/A"
                )
                col1.metric("Primary Dialect", top_dialect)

                htn_cases = sum(
                    1
                    for a in all_adults
                    if a.get("Risk") == "Hypertensive Risk"
                    or a.get("Sys", 0) >= 140
                    or a.get("Dia", 0) >= 90
                )
                col2.metric(
                    "Adult Hypertensive Risk",
                    f"{htn_cases} / {len(all_adults)}"
                    f" ({(htn_cases/len(all_adults)*100 if len(all_adults) else 0):.1f}%)",
                )

                hypox_cases = sum(
                    1
                    for a in all_adults
                    if a.get("Risk") == "Hypoxemic (<95%)"
                    or (a.get("SpO2", 100) < 95 and a.get("SpO2", 0) > 0)
                )
                col3.metric("Hypoxemia (<95% SpO2)", f"{hypox_cases} Adults")

                abnormal_vitals = sum(
                    1 for a in all_adults if a.get("Risk") != "Normal"
                )
                col4.metric("Abnormal Vitals Total", f"{abnormal_vitals} Adults")

            with tab_research:
                st.markdown(
                    "#### 🔬 Complete Research Interpretation Tables (All"
                    " Master Survey Variables)"
                )
                st.caption(
                    "Presents frequency counts (n) and percentage"
                    " distributions (%) for all asked items across all 10"
                    " survey domains."
                )

                total_hhs = len(st.session_state.hh_records)
                all_adults = [
                    a
                    for hh in st.session_state.hh_records
                    for a in hh.get("Adults", [])
                ]
                all_children = [
                    c
                    for hh in st.session_state.hh_records
                    for c in hh.get("Children", [])
                ]
                tot_adults = len(all_adults)
                tot_kids = len(all_children)

                tables_data = []

                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Survey_Status")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module A. Survey Completion Status",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [r.get("Dialect") for r in st.session_state.hh_records],
                        total_hhs,
                        "Module A. Primary Dialect Spoken at Home",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Religion")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module A. Religious Affiliation",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Head_Civil_Status")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module A. Head of Household Civil Status",
                    )
                )

                if tot_adults > 0:
                    tables_data.append(
                        generate_research_table(
                            [a.get("Gender") for a in all_adults],
                            tot_adults,
                            "Module B. Adult Member Sex / Gender Distribution",
                        )
                    )
                    tables_data.append(
                        generate_research_table(
                            [a.get("Edu") for a in all_adults],
                            tot_adults,
                            "Module B. Adult Educational Attainment",
                        )
                    )
                    tables_data.append(
                        generate_research_table(
                            [a.get("PhilHealth_Cat") for a in all_adults],
                            tot_adults,
                            "Module B. Adult PhilHealth Category",
                        )
                    )
                    tables_data.append(
                        generate_research_table(
                            [a.get("Risk") for a in all_adults],
                            tot_adults,
                            "Module B. Adult Clinical Risk Classification",
                        )
                    )

                tables_data.append(
                    generate_research_table(
                        [r.get("Income") for r in st.session_state.hh_records],
                        total_hhs,
                        "Module C1. Monthly Household Income Quintile",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Livelihood")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C1. Primary Household Livelihood",
                    )
                )

                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Food_Skip")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C2. Skipped Meal / Reduced Portion (Past 30d)",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [r.get("Water") for r in st.session_state.hh_records],
                        total_hhs,
                        "Module C4. Drinking Water Source Level",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Sanitation")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C4. Toilet & Sanitation Facility",
                    )
                )

                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Hypertension_Status")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module E2. Household Hypertension Status & Compliance",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [r.get("Yakap") for r in st.session_state.hh_records],
                        total_hhs,
                        "Module G. PhilHealth YAKAP Registration Rate",
                    )
                )

                master_research_df = pd.concat(tables_data, ignore_index=True)
                st.dataframe(master_research_df, use_container_width=True)

            with tab_indiv:
                hh_ids = [
                    f"{r.get('HH_ID', 'N/A')} - {r.get('Barangay', 'N/A')}"
                    f" ({r.get('Head_Name', 'No Head')})"
                    for r in st.session_state.hh_records
                ]
                sel_hh_idx = st.selectbox(
                    "Select Household Record to Inspect",
                    range(len(hh_ids)),
                    format_func=lambda x: hh_ids[x],
                )
                selected_record = st.session_state.hh_records[sel_hh_idx]

                st.markdown(
                    "### 🏠 Inspection for Record:"
                    f" `{selected_record.get('HH_ID', 'N/A')}`"
                )

                i_t1, i_t2, i_t3, i_t4, i_t5 = st.tabs([
                    "📌 Profile & Metadata",
                    "🩺 Adult Profiling Data",
                    "👶 Child Profiling Data",
                    "🌾 WASH & Housing",
                    "🏥 Health-Seeking & YAKAP",
                ])

                with i_t1:
                    c1, c2, c3 = st.columns(3)
                    c1.write(
                        "**Barangay:**"
                        f" {selected_record.get('Barangay', 'N/A')}"
                    )
                    c2.write(
                        f"**Purok:** {selected_record.get('Purok', 'N/A')}"
                    )
                    c3.write(
                        f"**Survey Date:** {selected_record.get('Date', 'N/A')}"
                    )

                with i_t2:
                    st.markdown("#### 🩺 Dynamic Adult Profiling Data")
                    adults_list = selected_record.get("Adults", [])
                    if len(adults_list) == 0:
                        st.info(
                            "No detailed adult profile rows recorded for this"
                            " household."
                        )
                    else:
                        st.dataframe(
                            pd.DataFrame(adults_list), use_container_width=True
                        )

                with i_t3:
                    st.markdown(
                        "#### 👶 Dynamic Child Profiling & Immunization Data"
                    )
                    children_list = selected_record.get("Children", [])
                    if len(children_list) == 0:
                        st.info(
                            "No detailed child profile rows recorded for this"
                            " household."
                        )
                    else:
                        st.dataframe(
                            pd.DataFrame(children_list),
                            use_container_width=True,
                        )

                with i_t4:
                    c1, c2, c3 = st.columns(3)
                    c1.write(
                        "**Monthly Income:**"
                        f" {selected_record.get('Income', 'N/A')}"
                    )
                    c2.write(
                        "**Water Source:**"
                        f" {selected_record.get('Water', 'N/A')}"
                    )
                    c3.write(
                        "**Sanitation/Toilet:**"
                        f" {selected_record.get('Sanitation', 'N/A')}"
                    )

                with i_t5:
                    c1, c2 = st.columns(2)
                    c1.write(
                        "**PhilHealth YAKAP Registered:**"
                        f" {selected_record.get('Yakap', 'N/A')}"
                    )
                    c2.write(
                        "**Availed FPE / Meds:**"
                        f" {selected_record.get('Yakap_Availed', 'N/A')}"
                    )

    else:
        st.markdown("### 📂 Submitted Household Survey Records")
        if len(st.session_state.hh_records) == 0:
            st.info("No household records found.")
        else:
            hh_options = [
                f"[{i+1}] {r.get('HH_ID', 'N/A')} -"
                f" {r.get('Barangay', 'N/A')} ({r.get('Purok', 'N/A')})"
                for i, r in enumerate(st.session_state.hh_records)
            ]
            selected_idx = st.selectbox(
                "Select Household Record to Review / Edit",
                range(len(hh_options)),
                format_func=lambda x: hh_options[x],
            )
            rec = st.session_state.hh_records[selected_idx]

            with st.form("edit_hh_form"):
                e_hh_id = st.text_input(
                    "Household ID", value=rec.get("HH_ID", "")
                )
                e_brgy = st.text_input(
                    "Barangay Name", value=rec.get("Barangay", "")
                )
                e_purok = st.text_input("Purok", value=rec.get("Purok", ""))

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Household Edits"):
                        rec.update({
                            "HH_ID": e_hh_id,
                            "Barangay": e_brgy,
                            "Purok": e_purok,
                        })
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
    st.subheader(
        "Phase 3: Qualitative Field Tools (KII & FGD Structured Guides)"
    )

    tool_choice = st.selectbox(
        "Select Qualitative Tool Instrument",
        [
            (
                "TOOL 3.1: KEY INFORMANT INTERVIEW (KII) GUIDE — GOVERNANCE &"
                " LEADERSHIP"
            ),
            (
                "TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE"
                " PERSONNEL"
            ),
            (
                "TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY"
                " MEMBERS"
            ),
        ],
    )

    if (
        tool_choice
        == "TOOL 3.1: KEY INFORMANT INTERVIEW (KII) GUIDE — GOVERNANCE &"
        " LEADERSHIP"
    ):
        st.markdown(
            "### 🏛️ TOOL 3.1: KEY INFORMANT INTERVIEW (KII) GUIDE — GOVERNANCE"
            " & LEADERSHIP"
        )
        st.caption(
            "**Target Respondents / Participants:** Punong Barangay, Committee"
            " Chair on Health, Municipal Health Officer (MHO)"
        )

        with st.form("kii_gov_form"):
            st.markdown("#### 📋 Respondent & Administrative Metadata")
            c1, c2 = st.columns(2)
            resp_name = c1.text_input("Respondent Name")
            pos_desig = c2.multiselect(
                "Position / Designation",
                ["Punong Barangay", "Health Chair", "MHO"],
                default=["Punong Barangay"],
            )

            c1, c2 = st.columns(2)
            brgy_lgu = c1.text_input("Barangay / LGU")
            date_time = c2.text_input(
                "Date & Time of Interview", "09 / 07 / 2026 | 09:00 AM"
            )

            c1, c2 = st.columns(2)
            interviewer = c1.text_input("Interviewer Name")
            note_taker = c2.text_input("Note-Taker Name")

            c1, c2 = st.columns(2)
            consent = c1.radio(
                "Informed Consent Signed?", ["Yes", "No"], horizontal=True
            )
            audio_rec = c2.radio(
                "Audio Recorded?",
                ["Yes (Permission Granted)", "No"],
                horizontal=True,
            )

            st.markdown("---")
            q1_notes = st.text_area(
                "1. Resource Allocation & AIP Prioritization Qualitative"
                " Notes",
                key="kii_g_q1",
            )
            q2_notes = st.text_area(
                "2. Policy Infrastructure & Enforcement Notes", key="kii_g_q2"
            )
            q3_notes = st.text_area(
                "3. Supply Chain Integrity & Emergency Procurement Notes",
                key="kii_g_q3",
            )
            q4_notes = st.text_area(
                "4. Health Inequity & Disadvantaged Populations Notes",
                key="kii_g_q4",
            )

            if st.form_submit_button("💾 Save TOOL 3.1 Interview Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.1: KII — Governance & Leadership",
                    "Respondent": resp_name,
                    "Designation": pos_desig,
                    "Barangay": brgy_lgu,
                    "Date_Time": date_time,
                    "Interviewer": interviewer,
                    "Note_Taker": note_taker,
                    "Consent": consent,
                    "Audio": audio_rec,
                    "D1_ResourceAllocation": q1_notes,
                    "D2_PolicyEnforcement": q2_notes,
                    "D3_SupplyChain": q3_notes,
                    "D4_HealthInequity": q4_notes,
                })
                save_session_to_disk()
                st.success(
                    "TOOL 3.1 KII Governance Record Saved Successfully!"
                )

    elif (
        tool_choice
        == "TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE PERSONNEL"
    ):
        st.markdown(
            "### 👩‍⚕️ TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE"
            " PERSONNEL"
        )
        with st.form("kii_frontline_form"):
            resp_name = st.text_input("Respondent Name")
            role = st.multiselect(
                "Frontline Role",
                ["Midwife", "BHW President", "BNS"],
                default=["Midwife"],
            )
            notes_frontline = st.text_area(
                "Qualitative Field Observations & Challenges"
            )
            if st.form_submit_button("💾 Save TOOL 3.2 Interview Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.2: KII — Frontline Personnel",
                    "Respondent": resp_name,
                    "Role": role,
                    "Notes": notes_frontline,
                })
                save_session_to_disk()
                st.success("TOOL 3.2 Record Saved!")

    else:
        st.markdown(
            "### 👥 TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY"
            " MEMBERS"
        )
        with st.form("fgd_form"):
            group_desc = st.text_input(
                "Participant Group Description (e.g. Mothers, Farmers, Senior"
                " Citizens)"
            )
            num_part = st.number_input("Number of Participants", 1, 30, 8)
            fgd_notes = st.text_area(
                "Key Themes & Community Perception Findings"
            )
            if st.form_submit_button("💾 Save TOOL 3.3 FGD Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.3: FGD — Community Members",
                    "Group": group_desc,
                    "Participants": num_part,
                    "Notes": fgd_notes,
                })
                save_session_to_disk()
                st.success("TOOL 3.3 FGD Record Saved!")

# MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader(
        "Phase 4: Expanded Purok Environmental Risk Index (PERI) Windshield"
        " Tool"
    )

    with st.form("peri_windshield_form"):
        purok_name = st.text_input("Purok / Zone Evaluated", "Purok 1")
        evaluator = st.text_input("Evaluator Name(s)")

        st.markdown(
            "<div class='peri-domain-header'>Domain 1: Sanitation & WASH"
            " Infrastructure (Max 5 pts)</div>",
            unsafe_allow_html=True,
        )
        ds1 = st.slider(
            "Open defecation evidence, stagnant sewage, uncollected waste"
            " risk",
            1,
            5,
            2,
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 2: Food Environment &"
            " Security (Max 5 pts)</div>",
            unsafe_allow_html=True,
        )
        ds2 = st.slider(
            "Unsanitary food stalls, lack of fresh produce markets risk",
            1,
            5,
            2,
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 3: Built Environment &"
            " Housing Vulnerability (Max 5 pts)</div>",
            unsafe_allow_html=True,
        )
        ds3 = st.slider(
            "Dilapidated light housing materials, overcrowded structure risk",
            1,
            5,
            3,
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 4: Health Infrastructure"
            " Access (Max 5 pts)</div>",
            unsafe_allow_html=True,
        )
        ds4 = st.slider(
            "Distance barrier to BHS/RHU, unpaved muddy road risk", 1, 5, 2
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 5: Disaster & Climate"
            " Hazard Resilience (Max 5 pts)</div>",
            unsafe_allow_html=True,
        )
        ds5 = st.slider(
            "Proximity to flood prone rivers, landslide zones, lack of evacuation",
            1,
            5,
            3,
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 6: Vector Control &"
            " Environmental Hazards (Max 5 pts)</div>",
            unsafe_allow_html=True,
        )
        ds6 = st.slider(
            "Stagnant water pools (dengue risk), stray animals, indoor smoke",
            1,
            5,
            2,
        )

        if st.form_submit_button("💾 Calculate & Save PERI Windshield Evaluation"):
            peri_index = np.mean([ds1, ds2, ds3, ds4, ds5, ds6])
            cat = (
                "Category C: Critical Risk (≥2.3)"
                if peri_index >= 2.3
                else (
                    "Category B: Concern (1.5–2.29)"
                    if peri_index >= 1.5
                    else "Category A: Low Risk (<1.5)"
                )
            )

            st.session_state.windshield_records.append({
                "Purok": purok_name,
                "Evaluator": evaluator,
                "DS1_Sanitation": ds1,
                "DS2_Food": ds2,
                "DS3_BuiltEnv": ds3,
                "DS4_HealthInfra": ds4,
                "DS5_DRR": ds5,
                "DS6_Vector": ds6,
                "PERI_Index": float(peri_index),
                "Category": cat,
            })
            save_session_to_disk()
            st.success(
                f"PERI Evaluation Saved for {purok_name}! Index:"
                f" {peri_index:.2f} — {cat}"
            )

# MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS (6.3 IMPLEMENTATION)
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader(
        "Phase 5: Spatial Analytics & Advanced Statistical Modeling Engine"
    )
    st.caption(
        "Automated Execution of Section 6.3: Statistical Analysis & Advanced"
        " Analytical Modeling Plan"
    )

    # Reference Plan Table 6.3
    st.markdown(
        "#### 📑 6.3 Statistical Analysis & Advanced Analytical Modeling Plan"
        " Framework"
    )
    plan_matrix = [
        {
            "Statistical Method": "Descriptive Cross-Tabulation & Odds Ratios",
            "Input Variables (Survey/GIS)": (
                "Income Quintiles × Hypertension / Diabetes Prevalence"
            ),
            "Target Public Health Output": (
                "Quantifies the slope of the social gradient in health across"
                " income tiers."
            ),
        },
        {
            "Statistical Method": "Factor Analysis (PCA)",
            "Input Variables (Survey/GIS)": (
                "Housing materials, WASH level, Income, Cooking fuel"
            ),
            "Target Public Health Output": (
                "Generates a composite 'Barangay Socio-Economic Vulnerability"
                " Index'."
            ),
        },
        {
            "Statistical Method": "Latent Class Analysis (LCA)",
            "Input Variables (Survey/GIS)": (
                "Co-occurring food insecurity, housing instability, distance"
                " barrier"
            ),
            "Target Public Health Output": (
                "Identifies multi-risk household clusters requiring integrated"
                " LGU social protection."
            ),
        },
    ]
    st.table(pd.DataFrame(plan_matrix))

    st.markdown("---")

    hh_records = st.session_state.hh_records

    if len(hh_records) == 0:
        st.warning(
            "⚠️ No household survey records available in storage. Please add"
            " survey entries under Phase 2 to run automated dynamic"
            " statistical computations."
        )
    else:
        p5_tab1, p5_tab2, p5_tab3 = st.tabs([
            "A. Descriptive Analysis (Social Gradient, OR & RR)",
            "B1. Factor Analysis & Deprivation Index (PCA)",
            "B2. Latent Class Analysis (LCA Risk Clustering)",
        ])

        # --- SECTION 6.3 A: DESCRIPTIVE ANALYSIS (SOCIAL GRADIENT, OR, RR) ---
        with p5_tab1:
            st.markdown(
                "### A. Descriptive Analysis: Measuring the Social Gradient"
            )
            st.caption(
                "Cross-tabulate clinical health outcomes across socio-economic"
                " tiers (income quintiles, education) and geographic zones."
                " Calculates Odds Ratios (OR) and Relative Risks (RR) with 95%"
                " Confidence Intervals."
            )

            c_exp, c_out = st.columns(2)
            with c_exp:
                exp_var = st.selectbox(
                    "Select Socio-Economic Exposure Vector",
                    [
                        "Income Tier: Low Income (Q1/Q2) vs Higher Income",
                        "WASH Access: Unsafe Water vs Safe Level 1-3",
                        "Housing Risk: Light Construction vs Medium/Heavy",
                        "Climate Hazard: Flood-Prone Zone vs Non-Flood Zone",
                        "Food Insecurity: Skipped Meals vs Secured",
                    ],
                )
            with c_out:
                out_var = st.selectbox(
                    "Select Target Health Outcome",
                    [
                        "Hypertension Prevalence (Diagnosed / Sys ≥140)",
                        "Diabetes Prevalence (Diagnosed)",
                        "Asthma / Respiratory Morbidity",
                        "Combined Chronic Disease Burden",
                    ],
                )

            # Compute Exposure & Outcome Flags for each household
            exp_flags = []
            out_flags = []

            for h in hh_records:
                # Exposure definition
                if "Income Tier" in exp_var:
                    is_exp = h.get("Income") in [
                        "≤ ₱10,000 (Q1)",
                        "₱10,001–₱20,000 (Q2)",
                    ]
                elif "WASH Access" in exp_var:
                    is_exp = "Unsafe" in str(h.get("Water", ""))
                elif "Housing Risk" in exp_var:
                    is_exp = "Light" in str(h.get("House_Type", ""))
                elif "Climate Hazard" in exp_var:
                    is_exp = h.get("Flood_Prone") == "Yes"
                else:  # Food Insecurity
                    is_exp = h.get("Food_Skip") == "Yes"

                # Outcome definition
                if "Hypertension" in out_var:
                    is_out = "Diagnosed" in str(
                        h.get("Hypertension_Status", "")
                    ) or "Hypertensive" in str(h.get("Risk", ""))
                elif "Diabetes" in out_var:
                    is_out = "Diagnosed" in str(h.get("Diabetes_Status", ""))
                elif "Asthma" in out_var:
                    is_out = "Diagnosed" in str(h.get("Asthma_Status", ""))
                else:  # Combined Chronic Disease Burden
                    is_out = (
                        "Diagnosed" in str(h.get("Hypertension_Status", ""))
                        or "Diagnosed" in str(h.get("Diabetes_Status", ""))
                        or "Diagnosed" in str(h.get("Asthma_Status", ""))
                    )

                exp_flags.append(is_exp)
                out_flags.append(is_out)

            exp_arr = np.array(exp_flags)
            out_arr = np.array(out_flags)

            # 2x2 Contingency Matrix
            # a: Exposed, Outcome Present
            # b: Exposed, Outcome Absent
            # c: Unexposed, Outcome Present
            # d: Unexposed, Outcome Absent
            a = sum(exp_arr & out_arr)
            b = sum(exp_arr & ~out_arr)
            c = sum(~exp_arr & out_arr)
            d = sum(~exp_arr & ~out_arr)

            st.markdown("#### 📊 2 × 2 Contingency Matrix")
            df_2x2 = pd.DataFrame(
                [[a, b, a + b], [c, d, c + d], [a + c, b + d, a + b + c + d]],
                columns=[
                    "Outcome Present (+)",
                    "Outcome Absent (-)",
                    "Total",
                ],
                index=["Exposed (+)", "Unexposed (-)", "Total"],
            )
            st.dataframe(df_2x2, use_container_width=True)

            # Epidemiological Risk Calculation Engine (OR & RR)
            # Haldane-Anscombe correction if zero cell present
            a_c, b_c, c_c, d_c = (
                (a + 0.5, b + 0.5, c + 0.5, d + 0.5)
                if (a == 0 or b == 0 or c == 0 or d == 0)
                else (a, b, c, d)
            )

            risk_exp = a_c / (a_c + b_c)
            risk_unexp = c_c / (c_c + d_c)

            rr = risk_exp / risk_unexp if risk_unexp > 0 else 1.0
            se_ln_rr = math.sqrt(
                (1 / a_c) - (1 / (a_c + b_c)) + (1 / c_c) - (1 / (c_c + d_c))
            )
            rr_ci_low = math.exp(math.log(rr) - (1.96 * se_ln_rr))
            rr_ci_high = math.exp(math.log(rr) + (1.96 * se_ln_rr))

            or_val = (a_c * d_c) / (b_c * c_c) if (b_c * c_c) > 0 else 1.0
            se_ln_or = math.sqrt(
                (1 / a_c) + (1 / b_c) + (1 / c_c) + (1 / d_c)
            )
            or_ci_low = math.exp(math.log(or_val) - (1.96 * se_ln_or))
            or_ci_high = math.exp(math.log(or_val) + (1.96 * se_ln_or))

            col_or, col_rr, col_grad = st.columns(3)
            col_or.metric(
                "Odds Ratio (OR)",
                f"{or_val:.2f}",
                delta=f"95% CI: [{or_ci_low:.2f} – {or_ci_high:.2f}]",
                delta_color="inverse" if or_val > 1.0 else "normal",
            )
            col_rr.metric(
                "Relative Risk (RR)",
                f"{rr:.2f}",
                delta=f"95% CI: [{rr_ci_low:.2f} – {rr_ci_high:.2f}]",
                delta_color="inverse" if rr > 1.0 else "normal",
            )
            col_grad.metric(
                "Exposed Burden Rate",
                f"{(risk_exp*100):.1f}%",
                delta=f"vs Baseline: {(risk_unexp*100):.1f}%",
            )

            st.markdown("#### 📈 Social Gradient Slope across Income Quintiles")
            income_tiers = [
                "≤ ₱10,000 (Q1)",
                "₱10,001–₱20,000 (Q2)",
                "₱20,001–₱35,000 (Q3)",
                "₱35,001–₱50,000 (Q4)",
                "> ₱50,000 (Q5)",
            ]
            gradient_data = []

            for tier in income_tiers:
                tier_hhs = [
                    h for h in hh_records if h.get("Income") == tier
                ]
                n_tier = len(tier_hhs)
                if n_tier > 0:
                    dis_cnt = sum(
                        1
                        for h in tier_hhs
                        if "Diagnosed"
                        in str(h.get("Hypertension_Status", ""))
                        or "Diagnosed" in str(h.get("Diabetes_Status", ""))
                        or "Hypertensive" in str(h.get("Risk", ""))
                    )
                    rate = (dis_cnt / n_tier) * 100.0
                else:
                    rate = 0.0
                gradient_data.append({
                    "Income Tier": tier,
                    "Disease Burden Rate (%)": rate,
                    "Sample (n)": n_tier,
                })

            df_gradient = pd.DataFrame(gradient_data)
            st.bar_chart(
                df_gradient.set_index("Income Tier")["Disease Burden Rate (%)"]
            )

        # --- SECTION 6.3 B1: FACTOR ANALYSIS (PCA & HOUSEHOLD DEPRIVATION INDEX) ---
        with p5_tab2:
            st.markdown(
                "### B1. Factor Analysis & Principal Component Index (PCA)"
            )
            st.caption(
                "Collapse correlated environmental and economic variables"
                " into latent factor scores to create a composite Household"
                " Deprivation Index (0–100 Score) and Barangay Socio-Economic"
                " Vulnerability Index."
            )

            # Construct indicator matrix for each household
            pca_features = []
            hh_labels = []

            for h in hh_records:
                # Code variables: higher value = higher structural vulnerability
                v1_income = (
                    1.0
                    if h.get("Income") == "≤ ₱10,000 (Q1)"
                    else (0.75 if h.get("Income") == "₱10,001–₱20,000 (Q2)" else 0.25)
                )
                v2_water = (
                    1.0
                    if "Unsafe" in str(h.get("Water", ""))
                    else (0.6 if "Level 1" in str(h.get("Water", "")) else 0.1)
                )
                v3_toilet = (
                    1.0
                    if "Open Defecation" in str(h.get("Sanitation", ""))
                    else (
                        0.5
                        if "Pit" in str(h.get("Sanitation", ""))
                        else 0.1
                    )
                )
                v4_housing = (
                    1.0
                    if "Light" in str(h.get("House_Type", ""))
                    else (0.5 if "Medium" in str(h.get("House_Type", "")) else 0.1)
                )
                v5_fuel = (
                    1.0
                    if h.get("Cook_Fuel") in ["Charcoal", "Wood"]
                    else 0.2
                )
                v6_food = 1.0 if h.get("Food_Skip") == "Yes" else 0.0

                pca_features.append([
                    v1_income,
                    v2_water,
                    v3_toilet,
                    v4_housing,
                    v5_fuel,
                    v6_food,
                ])
                hh_labels.append(h.get("HH_ID", "HH"))

            X = np.array(pca_features)

            # Compute standardized scores and First Principal Component / Latent Factor Weights
            X_mean = np.mean(X, axis=0)
            X_std = np.std(X, axis=0) + 1e-5
            X_norm = (X - X_mean) / X_std

            # Eigen-decomposition of correlation matrix
            cov_matrix = np.cov(X_norm, rowvar=False)
            eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

            # First principal component vector
            pc1_vector = eigenvectors[:, np.argmax(eigenvalues)]
            pc1_scores = np.dot(X_norm, pc1_vector)

            # Rescale PC1 score to 0–100 Household Deprivation Index
            min_score, max_score = np.min(pc1_scores), np.max(pc1_scores)
            if max_score > min_score:
                deprivation_index = (
                    (pc1_scores - min_score) / (max_score - min_score)
                ) * 100.0
            else:
                deprivation_index = np.full_like(pc1_scores, 50.0)

            # Store scores in records
            for idx, h in enumerate(hh_records):
                h["Deprivation_Score"] = round(float(deprivation_index[idx]), 1)

            df_pca_res = pd.DataFrame({
                "HH ID": hh_labels,
                "Barangay": [h.get("Barangay") for h in hh_records],
                "Purok": [h.get("Purok") for h in hh_records],
                "Income Tier": [h.get("Income") for h in hh_records],
                "Water Level": [h.get("Water") for h in hh_records],
                "Household Deprivation Index (0-100)": np.round(
                    deprivation_index, 1
                ),
            })

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(
                    "#### 📊 Component Loadings (Latent Factor Weights)"
                )
                loadings_df = pd.DataFrame({
                    "Vulnerability Indicator": [
                        "Income Poverty (Q1/Q2)",
                        "Unsafe Drinking Water",
                        "Unimproved Sanitation",
                        "Light Housing Material",
                        "Solid Cooking Fuel (Wood/Charcoal)",
                        "Severe Food Insecurity",
                    ],
                    "PCA Weight Loading": np.round(pc1_vector, 3),
                })
                st.dataframe(loadings_df, use_container_width=True)

            with col_p2:
                st.markdown(
                    "#### 🏘️ Barangay Socio-Economic Vulnerability Index by"
                    " Purok"
                )
                purok_vuln = (
                    df_pca_res.groupby("Purok")[
                        "Household Deprivation Index (0-100)"
                    ]
                    .mean()
                    .reset_index()
                )
                st.dataframe(purok_vuln, use_container_width=True)

            st.markdown(
                "#### 🔍 Household Deprivation Index Ranking Explorer"
            )
            st.dataframe(
                df_pca_res.sort_values(
                    by="Household Deprivation Index (0-100)", ascending=False
                ),
                use_container_width=True,
            )

        # --- SECTION 6.3 B2: LATENT CLASS ANALYSIS (LCA VULNERABILITY CLUSTERING) ---
        with p5_tab3:
            st.markdown("### B2. Latent Class Analysis (LCA)")
            st.caption(
                "Groups households into discrete latent vulnerability classes"
                " based on overlapping social risks (e.g. Food insecurity,"
                " housing instability, water access). Models direct probability"
                " of chronic disease prevalence per class."
            )

            # Rule-based LCA Cluster Assignment Model
            lca_classes = []
            for h in hh_records:
                r_food = h.get("Food_Skip") == "Yes"
                r_water = "Unsafe" in str(h.get("Water", ""))
                r_house = "Light" in str(h.get("House_Type", ""))
                r_income = h.get("Income") in [
                    "≤ ₱10,000 (Q1)",
                    "₱10,001–₱20,000 (Q2)",
                ]

                risk_sum = sum([r_food, r_water, r_house, r_income])

                if risk_sum >= 3:
                    c_class = "Class 3: Severe Multi-Risk Vulnerability"
                elif risk_sum >= 1:
                    c_class = "Class 2: Moderate / Transitional Risk"
                else:
                    c_class = "Class 1: High Income / High Access (Low Risk)"

                h["LCA_Class"] = c_class
                lca_classes.append(c_class)

            df_lca = pd.DataFrame(hh_records)

            lca_summary = []
            for cls_name in [
                "Class 1: High Income / High Access (Low Risk)",
                "Class 2: Moderate / Transitional Risk",
                "Class 3: Severe Multi-Risk Vulnerability",
            ]:
                cls_hhs = [
                    h for h in hh_records if h.get("LCA_Class") == cls_name
                ]
                n_cls = len(cls_hhs)
                if n_cls > 0:
                    htn_p = (
                        sum(
                            1
                            for h in cls_hhs
                            if "Diagnosed"
                            in str(h.get("Hypertension_Status", ""))
                            or "Hypertensive" in str(h.get("Risk", ""))
                        )
                        / n_cls
                    ) * 100.0
                    dm_p = (
                        sum(
                            1
                            for h in cls_hhs
                            if "Diagnosed"
                            in str(h.get("Diabetes_Status", ""))
                        )
                        / n_cls
                    ) * 100.0
                    food_p = (
                        sum(1 for h in cls_hhs if h.get("Food_Skip") == "Yes")
                        / n_cls
                    ) * 100.0
                else:
                    htn_p, dm_p, food_p = 0.0, 0.0, 0.0

                lca_summary.append({
                    "Latent Vulnerability Class": cls_name,
                    "Household Count (n)": n_cls,
                    "Class Share (%)": f"{(n_cls/len(hh_records)*100):.1f}%",
                    "Hypertension Prob (%)": f"{htn_p:.1f}%",
                    "Diabetes Prob (%)": f"{dm_p:.1f}%",
                    "Severe Food Insecurity (%)": f"{food_p:.1f}%",
                })

            st.markdown("#### 🧩 Latent Class Model Profiles & Outputs")
            st.dataframe(pd.DataFrame(lca_summary), use_container_width=True)

            st.markdown(
                "#### 🎯 Direct Probability of Chronic Disease Prevalence per"
                " Class"
            )
            df_chart_lca = pd.DataFrame(lca_summary).set_index(
                "Latent Vulnerability Class"
            )
            st.bar_chart(
                df_chart_lca[
                    ["Hypertension Prob (%)", "Diabetes Prob (%)"]
                ].applymap(lambda x: float(str(x).replace("%", "")))
            )

# MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS & ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader(
        "Phase 6: Comprehensive Community Health Diagnosis & Integrated Action"
        " Plan"
    )

    with st.form("action_plan_form"):
        st.markdown("#### 🎯 Priority Community Health Problem Identification")
        c1, c2 = st.columns(2)
        target_brgy = c1.text_input("Target Barangay", "Barangay San Jose")
        prob_title = c2.text_input(
            "Primary Health Problem / Vulnerability",
            "High Cardiovascular & Hypertensive Disease Surge",
        )

        st.markdown("---")
        st.markdown("#### 🛠️ Comprehensive Strategic Intervention Matrix")

        obj_desc = st.text_area(
            "Program Objectives (SMART)",
            "Reduce uncontrolled adult hypertension prevalence by 25% over 12"
            " months through monthly BHS screening, BHW home visits, and RHU"
            " drug access.",
        )
        interv_activities = st.text_area(
            "Key Interventions & Field Activities",
            "1. Deploy mobile BP screening teams across all Puroks.\n2."
            " Establish BHS compliance monitoring logbooks for anti-hypertensive"
            " maintenance drugs.\n3. Conduct community salt-reduction and"
            " dietary educational workshops.",
        )

        c1, c2, c3 = st.columns(3)
        lead_agency = c1.text_input(
            "Lead Responsible Office", "MHO / RHU / Barangay Health Board"
        )
        timeline = c2.text_input("Implementation Timeline", "Q4 2026 – Q3 2027")
        est_budget = c3.text_input("Estimated Budget Allocation", "₱150,000.00")

        kpi_metrics = st.text_area(
            "Monitoring & Evaluation Success Indicators",
            "• 85% of adult residents screened for BP.\n• 100% of diagnosed"
            " hypertensive patients enrolled in BHS maintenance program.",
        )

        if st.form_submit_button("💾 Save Integrated Action Plan"):
            st.session_state.diag_records.append({
                "Barangay": target_brgy,
                "Problem": prob_title,
                "Objectives": obj_desc,
                "Interventions": interv_activities,
                "Lead": lead_agency,
                "Timeline": timeline,
                "Budget": est_budget,
                "KPIs": kpi_metrics,
            })
            save_session_to_disk()
            st.success("Action Plan saved successfully!")

    if len(st.session_state.diag_records) > 0:
        st.markdown("---")
        st.markdown("### 📜 Saved Community Action Plans")
        st.dataframe(
            pd.DataFrame(st.session_state.diag_records),
            use_container_width=True,
        )

# MODULE 8: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Multi-Phase Master Data Management & Export Hub")

    st.markdown("#### 📤 Export Complete Survey Datasets (JSON / CSV)")

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.markdown("**Phase 2 Master Surveys**")
        st.write(f"Count: {len(st.session_state.hh_records)}")
        if len(st.session_state.hh_records) > 0:
            df_hh = pd.DataFrame(st.session_state.hh_records)
            st.download_button(
                "⬇️ Download CSV",
                data=df_hh.to_csv(index=False),
                file_name="Phase2_Master_Household_Survey.csv",
                mime="text/csv",
            )

    with d2:
        st.markdown("**Phase 1 Governance**")
        st.write(f"Count: {len(st.session_state.gov_records)}")
        if len(st.session_state.gov_records) > 0:
            df_gov = pd.DataFrame(st.session_state.gov_records)
            st.download_button(
                "⬇️ Download CSV",
                data=df_gov.to_csv(index=False),
                file_name="Phase1_Governance_Scorecards.csv",
                mime="text/csv",
            )

    with d3:
        st.markdown("**Phase 4 PERI Tools**")
        st.write(f"Count: {len(st.session_state.windshield_records)}")
        if len(st.session_state.windshield_records) > 0:
            df_peri = pd.DataFrame(st.session_state.windshield_records)
            st.download_button(
                "⬇️ Download CSV",
                data=df_peri.to_csv(index=False),
                file_name="Phase4_PERI_Windshield_Evaluations.csv",
                mime="text/csv",
            )

    with d4:
        st.markdown("**Phase 6 Action Plans**")
        st.write(f"Count: {len(st.session_state.diag_records)}")
        if len(st.session_state.diag_records) > 0:
            df_diag = pd.DataFrame(st.session_state.diag_records)
            st.download_button(
                "⬇️ Download CSV",
                data=df_diag.to_csv(index=False),
                file_name="Phase6_Action_Plans.csv",
                mime="text/csv",
            )

    st.markdown("---")
    st.markdown("#### ⚙️ Maintenance & System Reset")
    if st.button("🚨 System Reset: Wipe Persistent Disk Data"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.session_state.hh_records = []
        st.session_state.gov_records = []
        st.session_state.qual_records = []
        st.session_state.windshield_records = []
        st.session_state.diag_records = []
        st.success("All persistent survey data reset successfully!")
        st.rerun()
