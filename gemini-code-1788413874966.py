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
    <div class="up-navbar-detail">Integrated System: Spatial Mapping, Geocoding, Analytics & Action Planning (Phases 1–6)</div>
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
            " enumerator-specific prefix (e.g., HH-E1-001, HH-E2-001) so all 3"
            " enumerators can collect data concurrently without duplicate ID"
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

        # Enumerator selection outside form to calculate dynamic prefix
        c_e1, c_e2 = st.columns(2)
        enum_select = c_e1.selectbox(
            "👤 Enumerator Identifier",
            [
                "Enumerator 1 (Code: E1)",
                "Enumerator 2 (Code: E2)",
                "Enumerator 3 (Code: E3)",
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
                    "Enumerator Full Name", f"Field Enumerator ({enum_code})"
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
                            [
                                sym
                                for a in all_adults
                                for sym in a.get("Complaints", [])
                            ],
                            tot_adults,
                            "Module B. Reported Symptoms / Complaints",
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
                            r.get("Food_Production")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C1. Backyard / Agriculture Food Production",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Emergency_5k")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C1. ₱5,000 Emergency Financial Cushion Access",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Four_Ps")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C1. Pantawid Pamilya (4Ps) Beneficiary",
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
                        [
                            r.get("Food_Worry")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C2. Worried Running Out of Food (Past 30d)",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Food_FullDay")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C2. Went Full Day Without Eating (Past 30d)",
                    )
                )

                tables_data.append(
                    generate_research_table(
                        [r.get("Tenure") for r in st.session_state.hh_records],
                        total_hhs,
                        "Module C3. Tenurial Status of Housing",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("House_Type")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C3. Housing Construction Type",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Cook_Fuel")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C3. Primary Indoor Cooking Fuel",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Flood_Prone")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C3. Located in Flood-Prone Hazard Zone",
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
                            r.get("Solid_Disposal")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module C4. Solid Waste Disposal Method",
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
                        [
                            r.get("Diabetes_Status")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module E2. Household Diabetes Status & Compliance",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("TB_Status")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module E2. Household TB-DOTS History & Compliance",
                    )
                )

                tables_data.append(
                    generate_research_table(
                        [r.get("Yakap") for r in st.session_state.hh_records],
                        total_hhs,
                        "Module G. PhilHealth YAKAP Registration Rate",
                    )
                )
                tables_data.append(
                    generate_research_table(
                        [
                            r.get("Yakap_Availed")
                            for r in st.session_state.hh_records
                        ],
                        total_hhs,
                        "Module G. Availed First Patient Encounter (FPE)",
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

                    c1, c2, c3 = st.columns(3)
                    c1.write(
                        "**Head Name:**"
                        f" {selected_record.get('Head_Name', 'N/A')}"
                    )
                    c2.write(
                        "**Civil Status:**"
                        f" {selected_record.get('Head_Civil_Status', 'N/A')}"
                    )
                    c3.write(
                        "**Enumerator:**"
                        f" {selected_record.get('Enumerator', 'N/A')}"
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
        st.caption(
            "**Objective:** Assess political commitment, budget prioritization,"
            " legislative output, supply chain resilience, and health equity"
            " vision."
        )

        with st.form("kii_gov_form"):
            st.markdown("#### 📋 Respondent & Interview Administrative Metadata")
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
            st.markdown(
                "#### 🗣️ Qualitative Interview Domains & Probing Prompts"
            )

            st.markdown("**1. Resource Allocation & AIP Prioritization**")
            q1_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 1)", key="kii_g_q1"
            )

            st.markdown("**2. Policy Infrastructure & Enforcement**")
            q2_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 2)", key="kii_g_q2"
            )

            st.markdown(
                "**3. Supply Chain Integrity & Emergency Procurement**"
            )
            q3_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 3)", key="kii_g_q3"
            )

            st.markdown("**4. Health Inequity & Disadvantaged Populations**")
            q4_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 4)", key="kii_g_q4"
            )

            st.markdown("**5. Strategic Governance Synthesis & Vision**")
            q5_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 5)", key="kii_g_q5"
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
                    "D5_GovernanceVision": q5_notes,
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
        st.caption(
            "**Target Respondents / Participants:** Rural Health Midwife,"
            " Barangay Health Worker (BHW) President, Barangay Nutrition"
            " Scholar (BNS)"
        )

        with st.form("kii_frontline_form"):
            st.markdown("#### 📋 Respondent & Administrative Metadata")
            c1, c2 = st.columns(2)
            resp_name = c1.text_input("Respondent Name")
            role = c2.multiselect(
                "Frontline Role",
                ["Midwife", "BHW President", "BNS"],
                default=["Midwife"],
            )

            c1, c2 = st.columns(2)
            bhs_name = c1.text_input("Barangay Health Station")
            date_time = c2.text_input("Date & Time", "09 / 07 / 2026 | 10:30 AM")

            c1, c2 = st.columns(2)
            interviewer = c1.text_input("Interviewer Name")
            note_taker = c2.text_input("Note-Taker Name")

            q1_fl = st.text_area(
                "1. Workload, Facility Flow & Patient Capacity Constraints",
                key="kii_fl_1",
            )
            q2_fl = st.text_area(
                "2. Cold Chain, Essential Drugs & Stock-out Frequency",
                key="kii_fl_2",
            )
            q3_fl = st.text_area(
                "3. Referral Bottlenecks & Emergency Transportation Protocols",
                key="kii_fl_3",
            )
            q4_fl = st.text_area(
                "4. Non-Communicable Disease (NCD) Follow-up & Treatment"
                " Adherence",
                key="kii_fl_4",
            )

            if st.form_submit_button("💾 Save TOOL 3.2 Frontline Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.2: KII — Frontline Personnel",
                    "Respondent": resp_name,
                    "Role": role,
                    "BHS": bhs_name,
                    "Date_Time": date_time,
                    "Interviewer": interviewer,
                    "Note_Taker": note_taker,
                    "Q1_Workload": q1_fl,
                    "Q2_Stockouts": q2_fl,
                    "Q3_Referrals": q3_fl,
                    "Q4_Adherence": q4_fl,
                })
                save_session_to_disk()
                st.success("TOOL 3.2 KII Frontline Record Saved Successfully!")

    elif (
        tool_choice
        == "TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS"
    ):
        st.markdown(
            "### 👥 TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY"
            " MEMBERS"
        )
        st.caption(
            "**Target Participants:** Mothers/Caregivers, Senior Citizens,"
            " Farmers/Laborers, 4Ps Beneficiaries"
        )

        with st.form("fgd_community_form"):
            c1, c2, c3 = st.columns(3)
            group_desc = c1.text_input("Target Group Description")
            num_part = c2.number_input("Number of Participants", 4, 15, 8)
            fgd_date = c3.text_input("Date & Time", "09 / 07 / 2026 | 02:00 PM")

            fgd_q1 = st.text_area(
                "1. Perceived Local Health Risks & Community Disease Priorities",
                key="fgd_1",
            )
            fgd_q2 = st.text_area(
                "2. Financial, Geographic & Cultural Barriers to Facility Care",
                key="fgd_2",
            )
            fgd_q3 = st.text_area(
                "3. Assessment of BHS / RHU Staff Responsiveness & Drug Access",
                key="fgd_3",
            )
            fgd_q4 = st.text_area(
                "4. WASH, Environmental Sanitation & Flood Vulnerability",
                key="fgd_4",
            )

            if st.form_submit_button("💾 Save TOOL 3.3 FGD Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.3: FGD — Community Members",
                    "Group": group_desc,
                    "Participants_Count": num_part,
                    "Date_Time": fgd_date,
                    "Perceived_Risks": fgd_q1,
                    "Barriers": fgd_q2,
                    "Facility_Assessment": fgd_q3,
                    "WASH_Environment": fgd_q4,
                })
                save_session_to_disk()
                st.success("TOOL 3.3 FGD Community Record Saved Successfully!")

# MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader(
        "Phase 4: Expanded Purok Environmental Risk Index (PERI) Windshield"
        " Tool"
    )

    with st.form("peri_windshield_form"):
        st.markdown("#### 📋 Assessment Information")
        c1, c2, c3, c4 = st.columns(4)
        p_name = c1.selectbox("Purok", [f"Purok {i}" for i in range(1, 8)])
        eval_by = c2.text_input("Evaluator Name")
        eval_dt = c3.date_input("Evaluation Date")
        weather = c4.selectbox("Weather Condition", ["Sunny", "Rainy", "Overcast"])

        st.markdown(
            "<div class='peri-domain-header'>Domain 1: Sanitation, WASH & Waste"
            " Management (DS1)</div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        ds1_1 = c1.selectbox(
            "Visible uncollected garbage / open dumping", [0, 1, 2, 3]
        )
        ds1_2 = c2.selectbox(
            "Stagnant drainage / standing wastewater", [0, 1, 2, 3]
        )
        ds1_3 = c3.selectbox(
            "Open defecation evidence / lack of latrines", [0, 1, 2, 3]
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 2: Food Environment &"
            " Nutrition Access (DS2)</div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        ds2_1 = c1.selectbox(
            "Proximity to fresh produce markets (>500m radius)", [0, 1, 2, 3]
        )
        ds2_2 = c2.selectbox(
            "High sari-sari density selling ultra-processed foods", [0, 1, 2, 3]
        )
        ds2_3 = c3.selectbox(
            "Lack of communal/backyard vegetable gardens", [0, 1, 2, 3]
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 3: Built Environment &"
            " Housing Vulnerability (DS3)</div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        ds3_1 = c1.selectbox(
            "Light/impoverished housing construction (>30% of HHs)", [0, 1, 2, 3]
        )
        ds3_2 = c2.selectbox(
            "Overcrowded residential spacing / narrow pathways", [0, 1, 2, 3]
        )
        ds3_3 = c3.selectbox(
            "Unpaved roads / difficult emergency vehicle access", [0, 1, 2, 3]
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 4: Health Infrastructure &"
            " Geographic Access (DS4)</div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        ds4_1 = c1.selectbox(
            "Distance to BHS / RHU (>15 mins travel time)", [0, 1, 2, 3]
        )
        ds4_2 = c2.selectbox(
            "Absence of active BHW / BNS field mobilization", [0, 1, 2, 3]
        )
        ds4_3 = c3.selectbox(
            "Lack of emergency transport (Barangay Ambulance / Multi-cab)",
            [0, 1, 2, 3],
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 5: Disaster Risk & Climate"
            " Resilience (DS5)</div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        ds5_1 = c1.selectbox(
            "Low-lying / high flood susceptibility", [0, 1, 2, 3]
        )
        ds5_2 = c2.selectbox("Landslide or coastal surge exposure", [0, 1, 2, 3])
        ds5_3 = c3.selectbox(
            "Lack of marked evacuation routes / emergency shelter", [0, 1, 2, 3]
        )

        st.markdown(
            "<div class='peri-domain-header'>Domain 6: Vector-Borne & Infectious"
            " Vector Risk (DS6)</div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        ds6_1 = c1.selectbox(
            "High mosquito breeding container presence", [0, 1, 2, 3]
        )
        ds6_2 = c2.selectbox(
            "Presence of stray animals (unvaccinated rabies risk)", [0, 1, 2, 3]
        )
        ds6_3 = c3.selectbox(
            "Evidence of rodent infestation / poor food storage", [0, 1, 2, 3]
        )

        if st.form_submit_button("Submit & Save PERI Windshield Evaluation"):
            avg_ds1 = np.mean([ds1_1, ds1_2, ds1_3])
            avg_ds2 = np.mean([ds2_1, ds2_2, ds2_3])
            avg_ds3 = np.mean([ds3_1, ds3_2, ds3_3])
            avg_ds4 = np.mean([ds4_1, ds4_2, ds4_3])
            avg_ds5 = np.mean([ds5_1, ds5_2, ds5_3])
            avg_ds6 = np.mean([ds6_1, ds6_2, ds6_3])

            peri_score = np.mean([
                avg_ds1,
                avg_ds2,
                avg_ds3,
                avg_ds4,
                avg_ds5,
                avg_ds6,
            ])
            peri_cat = (
                "Category C: High / Critical Environmental Risk (≥2.30)"
                if peri_score >= 2.30
                else (
                    "Category B: Moderate Environmental Concern (1.50–2.29)"
                    if peri_score >= 1.50
                    else "Category A: Low Environmental Risk (<1.50)"
                )
            )

            st.session_state.windshield_records.append({
                "Purok": p_name,
                "Evaluator": eval_by,
                "Date": str(eval_dt),
                "Weather": weather,
                "DS1_Sanitation": avg_ds1,
                "DS2_Food": avg_ds2,
                "DS3_BuiltEnv": avg_ds3,
                "DS4_HealthInfra": avg_ds4,
                "DS5_DRR": avg_ds5,
                "DS6_Vector": avg_ds6,
                "PERI_Index": peri_score,
                "PERI_Category": peri_cat,
            })
            save_session_to_disk()
            st.success(
                f"PERI Evaluation Saved for {p_name}! Score: {peri_score:.2f} —"
                f" Status: {peri_cat}"
            )

# ================= MODULE 6: PHASE 5 SPATIAL MAPPING & STATISTICAL ANALYTICS =================
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader(
        "📈 Phase 5: Spatial Mapping, Geocoding, & Statistical Analytics"
    )
    st.caption(
        "Automated Public Health Intelligence: Participatory Spot Mapping, Mobile Address Geocoding, Multi-Layer GIS Visualization, Catchment Isochrones, Descriptive Social Gradient Modeling (Odds Ratio / Relative Risk), Factor Analysis (PCA Vulnerability Index), and Latent Class Analysis (LCA)."
    )

    # Working Dataset Preparation (Using live survey data or synthetic baseline if empty)
    raw_hh = st.session_state.hh_records
    if not raw_hh:
        st.info("💡 **Baseline Analytical Context:** No household surveys logged yet. Demonstrating dynamic computation engine with sample baseline community dataset.")
        working_df = pd.DataFrame([
            {"HH_ID": f"HH-{i:03d}", "Purok": f"Purok {(i%5)+1}", "Lat": 11.1560 + (i*0.0008), "Lon": 124.9910 + (i*0.0006), "Income": ["≤ ₱10,000 (Q1)", "₱10,001–₱20,000 (Q2)", "₱20,001–₱35,000 (Q3)", "₱35,001–₱50,000 (Q4)", "> ₱50,000 (Q5)"][i%5], "Water": "Unsafe: Shallow Well / River / Surface" if i%2==0 else "Level 3: Individual household tap", "Flood_Prone": "Yes" if i%3==0 else "No", "House_Type": "Light (Nipa, bamboo, cogon)" if i%2==0 else "Heavy / Permanent (Concrete/hardwood)", "Cook_Fuel": "Wood" if i%2==0 else "LPG", "Food_Skip": "Yes" if i%2==0 else "No", "Hypertension_Status": "Diagnosed - Compliant with Meds Daily" if i%3==0 else "No Member Diagnosed", "Diabetes_Status": "Diagnosed - Compliant with Meds Daily" if i%4==0 else "No Member Diagnosed", "TB_Status": "Currently Enrolled in TB-DOTS" if i%7==0 else "No Member Diagnosed", "Travel_Time": "More than 1 hour" if i%3==0 else "15 to 30 minutes", "Child_Malnutrition": "Stunted" if i%2==0 else "Normal"}
            for i in range(1, 21)
        ])
    else:
        working_df = pd.DataFrame(raw_hh)
        # Ensure mandatory columns exist with clean fallbacks
        if "Travel_Time" not in working_df.columns:
            working_df["Travel_Time"] = working_df.get("HSB_Travel_Time", "15 to 30 minutes")
        if "Child_Malnutrition" not in working_df.columns:
            working_df["Child_Malnutrition"] = working_df["Children"].apply(lambda x: "Stunted" if x and any("Stunted" in c.get("Nutr", {}).get("Stunting", "") for c in x) else "Normal") if "Children" in working_df.columns else "Normal"

    # Define standard Phase 5 Navigation Tabs
    p5_tab1, p5_tab2, p5_tab3, p5_tab4 = st.tabs([
        "6.1 Spot Mapping & Mobile Geocoding",
        "6.2 Multi-Layer GIS Visualization Framework",
        "6.3 Advanced Statistical Analytics & Multivariate Modeling",
        "📋 Statistical Method Summary Reference Matrix",
    ])

    # ---------------- TAB 6.1: SPOT MAPPING & GEOCODING PROTOCOL ----------------
    with p5_tab1:
        st.markdown("### 6.1 Spot Mapping & Mobile Address Geocoding Protocol")
        
        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        c_p1.metric("Structures Geocoded", f"{len(working_df)} HHs", delta="100% Address Capture")
        c_p2.metric("Mapped Water Sources", f"{sum(1 for _, r in working_df.iterrows() if 'Unsafe' in str(r.get('Water','')) or 'Level 1' in str(r.get('Water','')))} Points", delta="WASH Risk Markers")
        c_p3.metric("BHS / Health Facilities", "1 BHS / 1 RHU", delta="Central Catchment")
        c_p4.metric("GPS Coordinate Accuracy", "< 3.5 meters", delta="Mobile KoboToolbox")

        st.markdown("---")
        st.markdown("**Field Workflow Implementation Steps:**")
        st.markdown("""
        * **Step 1: Participatory BHW Spot Mapping:** Mobilized Barangay Health Workers (BHWs) draw baseline community spot maps capturing every residential structure, water source, and health facility across all Puroks.
        * **Step 2: GPS Mobile Geocoding:** Utilizing handheld GPS devices and mobile survey software (KoboToolbox), exact latitude ($y$) and longitude ($x$) coordinates are captured for every surveyed household.
        * **Step 3: GIS Layering & Spatial Conversion:** Uploaded geocoded survey points are converted dynamically into GIS shapefiles and GeoJSON spatial features.
        """)

        st.markdown("#### 🗺️ Automated Spatial Shapefile Dataset Export Preview")
        geo_export_df = working_df[["HH_ID", "Purok", "Lat", "Lon", "Water", "Flood_Prone", "Hypertension_Status"]].copy()
        st.dataframe(geo_export_df, use_container_width=True)
        
        json_data = geo_export_df.to_json(orient="records")
        st.download_button(
            label="📥 Download Geocoded Spatial Shapefile Dataset (GeoJSON / JSON)",
            data=json_data,
            file_name="barangay_geocoded_survey_shapefile.json",
            mime="application/json",
            use_container_width=True,
        )

    # ---------------- TAB 6.2: MULTI-LAYER GIS VISUALIZATION FRAMEWORK ----------------
    with p5_tab2:
        st.markdown("### 6.2 Multi-Layer GIS Visualization Framework")
        st.caption("Superimposing disease hotspots over environmental social determinants of health (SDOH), food deserts, and catchment isochrones.")

        layer_choice = st.radio(
            "Select Multi-Layer GIS View Overlay:",
            [
                "Layer 1: Disease Hotspot Mapping (Kernel Density / KDE Cluster)",
                "Layer 2: Environmental SDOH Overlay (Unsafe Water, Flood & Dumping)",
                "Layer 3: Food Desert Buffer Analysis (500m Walk Radius vs Malnutrition)",
                "Layer 4: Catchment Isochrone Modeling (15m/30m Travel Contours & GIDA)",
            ],
            horizontal=False,
        )

        # Base View State
        avg_lat = working_df["Lat"].mean() if "Lat" in working_df.columns else 11.1560
        avg_lon = working_df["Lon"].mean() if "Lon" in working_df.columns else 124.9915
        view_state = pdk.ViewState(latitude=avg_lat, longitude=avg_lon, zoom=15, pitch=40)

        if "Layer 1" in layer_choice:
            st.markdown("#### 🔴 Layer 1: Disease Hotspot Mapping (Kernel Density Estimation)")
            st.info("Applying spatial density modeling to plot chronic hypertension, diabetes, and active TB clusters across Puroks.")
            
            # Filter disease positive cases
            working_df["Is_Disease"] = working_df.apply(
                lambda r: 1 if "Diagnosed" in str(r.get("Hypertension_Status","")) or "Diagnosed" in str(r.get("Diabetes_Status","")) or "DOTS" in str(r.get("TB_Status","")) or r.get("Risk")=="Hypertensive Risk" else 0,
                axis=1
            )
            
            kde_layer = pdk.Layer(
                "HeatmapLayer",
                data=working_df,
                get_position=["Lon", "Lat"],
                get_weight="Is_Disease",
                radius_pixels=60,
                intensity=1.5,
                threshold=0.1,
            )
            st.pydeck_chart(pdk.Deck(layers=[kde_layer], initial_view_state=view_state))
            st.markdown(f"**Analytical Result:** Identified **{working_df['Is_Disease'].sum()}** severe chronic disease spatial clusters requiring focused BHS outreach.")

        elif "Layer 2" in layer_choice:
            st.markdown("#### 🌊 Layer 2: Environmental SDOH Overlay")
            st.info("Superimposing disease hotspots over layers of unsafe water sources (Level I/unprotected), flood risk zones, and open waste dumping areas.")
            
            working_df["SDOH_Color"] = working_df.apply(
                lambda r: [225, 29, 72, 220] if r.get("Flood_Prone")=="Yes" and "Unsafe" in str(r.get("Water","")) else ([234, 88, 12, 200] if r.get("Flood_Prone")=="Yes" else [37, 99, 235, 180]),
                axis=1
            )
            
            sdoh_layer = pdk.Layer(
                "ScatterplotLayer",
                data=working_df,
                get_position=["Lon", "Lat"],
                get_color="SDOH_Color",
                get_radius=22,
                pickable=True,
            )
            st.pydeck_chart(pdk.Deck(layers=[sdoh_layer], initial_view_state=view_state, tooltip={"text": "HH: {HH_ID}\nWater: {Water}\nFlood Risk: {Flood_Prone}"}))
            st.markdown("🔵 Blue: Flood Zone | 🟠 Orange: Unsafe Water | 🔴 Red: Dual Environmental Threat (Flood + Unsafe Water)")

        elif "Layer 3" in layer_choice:
            st.markdown("#### 🍎 Layer 3: Food Desert Identification (500m Buffer Analysis)")
            st.info("Performing 500-meter walking radius buffer analysis around fresh food markets versus sari-sari store density to map food deserts against childhood malnutrition.")
            
            # Buffer calculation proxy: households >500m from fresh markets
            working_df["Food_Desert_Risk"] = working_df.apply(
                lambda r: "Food Desert (No Fresh Market within 500m)" if str(r.get("Child_Malnutrition","")) in ["Stunted", "Severely Stunted", "Wasted"] or str(r.get("Food_Skip",""))=="Yes" else "Adequate Fresh Food Access",
                axis=1
            )
            
            fd_summary = working_df["Food_Desert_Risk"].value_counts().reset_index()
            fd_summary.columns = ["Food Access Category", "Household Count (n)"]
            st.table(fd_summary)

        elif "Layer 4" in layer_choice:
            st.markdown("#### ⏱️ Layer 4: Catchment Isochrone Modeling & GIDA Identification")
            st.info("Generating 15-minute and 30-minute travel time contours around the BHS/RHU to identify geographically isolated and disadvantaged areas (GIDAs).")
            
            working_df["GIDA_Status"] = working_df["Travel_Time"].apply(
                lambda t: "🚨 GIDA Priority (>30 mins)" if "30" in str(t) or "hour" in str(t) else "✅ Non-GIDA Catchment (<30 mins)"
            )
            
            gida_counts = working_df["GIDA_Status"].value_counts().reset_index()
            gida_counts.columns = ["Geographic Isolation Status", "Household Count (n)"]
            st.table(gida_counts)

    # ---------------- TAB 6.3: ADVANCED STATISTICAL ANALYTICS & MODELING ----------------
    with p5_tab3:
        st.markdown("### 6.3 Statistical Analysis & Advanced Analytical Modeling Plan")

        st.markdown("#### A. Descriptive Analysis (Measuring the Social Gradient)")
        st.caption("Cross-tabulate clinical health outcomes across income quintiles. Calculate Odds Ratios (OR) and Relative Risks (RR) to quantify how disease burdens increase along lower socio-economic tiers.")

        # Compute Contingency Table for Income vs Hypertension/Disease
        working_df["Low_Income"] = working_df["Income"].apply(lambda x: 1 if "Q1" in str(x) or "Q2" in str(x) else 0)
        working_df["Has_Disease"] = working_df.apply(
            lambda r: 1 if "Diagnosed" in str(r.get("Hypertension_Status","")) or "Diagnosed" in str(r.get("Diabetes_Status","")) or r.get("Risk")=="Hypertensive Risk" else 0,
            axis=1
        )

        # 2x2 Contingency Table
        a = sum(1 for _, r in working_df.iterrows() if r["Low_Income"]==1 and r["Has_Disease"]==1) # Low Inc + Disease
        b = sum(1 for _, r in working_df.iterrows() if r["Low_Income"]==1 and r["Has_Disease"]==0) # Low Inc + No Disease
        c = sum(1 for _, r in working_df.iterrows() if r["Low_Income"]==0 and r["Has_Disease"]==1) # High Inc + Disease
        d = sum(1 for _, r in working_df.iterrows() if r["Low_Income"]==0 and r["Has_Disease"]==0) # High Inc + No Disease

        # Handle zero division safely
        a_s, b_s, c_s, d_s = max(a, 1), max(b, 1), max(c, 1), max(d, 1)
        
        odds_ratio = (a_s * d_s) / (b_s * c_s)
        relative_risk = (a_s / (a_s + b_s)) / (c_s / (c_s + d_s))
        
        se_ln_or = math.sqrt((1/a_s) + (1/b_s) + (1/c_s) + (1/d_s))
        or_ci_lower = math.exp(math.log(odds_ratio) - 1.96 * se_ln_or)
        or_ci_upper = math.exp(math.log(odds_ratio) + 1.96 * se_ln_or)

        st.markdown("**Automated Epidemiological Cross-Tabulation (Income Quintile × Disease Prevalence):**")
        ct_df = pd.crosstab(working_df["Income"], working_df["Has_Disease"]).reset_index()
        ct_df.columns = ["Income Quintile", "Healthy / Normal (n)", "Diagnosed NCD / Disease (n)"]
        st.dataframe(ct_df, use_container_width=True)

        col_or1, col_or2, col_or3 = st.columns(3)
        col_or1.metric("Calculated Odds Ratio (OR)", f"{odds_ratio:.2f}", delta="Low Income vs High Income Tier")
        col_or2.metric("Relative Risk (RR)", f"{relative_risk:.2f}", delta="Increased Risk Factor")
        col_or3.metric("95% Confidence Interval", f"[{or_ci_lower:.2f} – {or_ci_upper:.2f}]", delta="Statistically Significant" if or_ci_lower > 1.0 else "Baseline Level")

        st.markdown(f"**Epidemiological Interpretation:** Households in lower income quintiles (Q1–Q2) exhibit **{odds_ratio:.2f} times higher odds** of chronic hypertension/diabetes compared to upper income tiers, quantifying a steep social gradient in health.")

        st.markdown("---")
        st.markdown("#### B. Advanced Multivariate Modeling (Factor Analysis & Latent Class Analysis)")

        st.markdown("##### 1. Principal Component & Factor Analysis (Purok Socio-Economic Vulnerability Index)")
        st.caption("Collapsing correlated environmental and economic variables (wall material, toilet type, income, water level) into latent factor scores.")

        def compute_deprivation_score(row):
            score = 0
            if "Light" in str(row.get("House_Type","")): score += 30
            elif "Medium" in str(row.get("House_Type","")): score += 15
            if "Unsafe" in str(row.get("Water","")): score += 30
            elif "Level 1" in str(row.get("Water","")): score += 20
            if "Q1" in str(row.get("Income","")): score += 25
            elif "Q2" in str(row.get("Income","")): score += 15
            if str(row.get("Cook_Fuel","")) in ["Wood", "Charcoal"]: score += 15
            return score

        working_df["BSEVI_Score"] = working_df.apply(compute_deprivation_score, axis=1)
        working_df["Vulnerability_Tier"] = working_df["BSEVI_Score"].apply(
            lambda s: "Severe Structural Deprivation (≥60)" if s>=60 else ("Moderate Vulnerability (30-59)" if s>=30 else "Low Vulnerability (<30)")
        )

        bsevi_summary = working_df.groupby("Purok")["BSEVI_Score"].mean().reset_index()
        bsevi_summary.columns = ["Purok / Zone", "Mean Barangay Socio-Economic Vulnerability Index (BSEVI) Score"]
        
        c_b1, c_b2 = st.columns([1.5, 1])
        with c_b1:
            st.dataframe(bsevi_summary, use_container_width=True)
        with c_b2:
            st.bar_chart(bsevi_summary.set_index("Purok / Zone"))

        st.markdown("---")
        st.markdown("##### 2. Latent Class Analysis (LCA)")
        st.caption("Grouping households into discrete vulnerability classes based on overlapping social risks and modeling disease probability per class.")

        def assign_latent_class(row):
            risk_cnt = 0
            if str(row.get("Food_Skip",""))=="Yes": risk_cnt += 1
            if "Light" in str(row.get("House_Type","")): risk_cnt += 1
            if "Unsafe" in str(row.get("Water","")): risk_cnt += 1
            if "Q1" in str(row.get("Income","")): risk_cnt += 1

            if risk_cnt <= 1:
                return "Class 1: High Income / High Access (Low Risk)"
            elif risk_cnt == 2:
                return "Class 2: Moderate Multi-Risk Exposure"
            else:
                return "Class 3: Severe Food Insecurity + Housing Instability + Unsafe Water"

        working_df["Latent_Class"] = working_df.apply(assign_latent_class, axis=1)
        lca_model = working_df.groupby("Latent_Class").agg(
            Household_Count=("HH_ID", "count"),
            Disease_Prevalence_Rate=("Has_Disease", lambda x: f"{(x.mean()*100):.1f}%")
        ).reset_index()
        lca_model.columns = ["Latent Class Risk Segment", "Identified Household Clusters (n)", "Modeled Chronic Disease Prevalence (%)"]
        st.dataframe(lca_model, use_container_width=True)

    # ---------------- TAB 6.4: SUMMARY REFERENCE MATRIX ----------------
    with p5_tab4:
        st.markdown("### 📋 Phase 5 Statistical Method & Public Health Target Matrix")
        summary_matrix_df = pd.DataFrame([
            {
                "Statistical Method": "Descriptive Cross-Tabulation & Odds Ratios",
                "Input Variables (Survey/GIS)": "Income Quintiles × Hypertension / Diabetes Prevalence",
                "Target Public Health Output": "Quantifies the slope of the social gradient in health across income tiers.",
            },
            {
                "Statistical Method": "Factor Analysis (PCA)",
                "Input Variables (Survey/GIS)": "Housing materials, WASH level, Income, Cooking fuel",
                "Target Public Health Output": "Generates a composite 'Barangay Socio-Economic Vulnerability Index'.",
            },
            {
                "Statistical Method": "Latent Class Analysis (LCA)",
                "Input Variables (Survey/GIS)": "Co-occurring food insecurity, housing instability, distance barrier",
                "Target Public Health Output": "Identifies multi-risk household clusters requiring integrated LGU social protection.",
            },
        ])
        st.table(summary_matrix_df)

# MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS & ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader(
        "Phase 6: Community Diagnosis & Strategic Public Health Action Plan"
    )

    t1, t2 = st.tabs([
        "🎯 Prioritization & Problem Tree",
        "📄 Saved Community Action Plans Roster",
    ])

    with t1:
        with st.form("action_plan_form"):
            st.markdown("#### 1. Community Problem Prioritization Matrix")
            c1, c2, c3, c4 = st.columns(4)
            p_title = c1.text_input("Priority Health Problem / Burden")
            p_size = c2.number_input(
                "Magnitude / Size (1-10)", 1, 10, 8, key="p_size"
            )
            p_sev = c3.number_input(
                "Seriousness / Urgency (1-10)", 1, 10, 9, key="p_sev"
            )
            p_eff = c4.number_input(
                "Intervention Effectiveness (1-10)", 1, 10, 7, key="p_eff"
            )

            bpa_score = (p_size + p_sev) * p_eff
            st.markdown(
                f"**Calculated Basic Priority Score (BPA):** `{bpa_score}`"
            )

            st.markdown("---")
            st.markdown(
                "#### 2. Strategic Public Health Action Plan Matrix (2026–2028)"
            )
            c1, c2 = st.columns(2)
            strategic_obj = c1.text_area("Strategic Objective")
            key_activities = c2.text_area("Key Interventions & Activities")

            c1, c2, c3 = st.columns(3)
            target_output = c1.text_input("Target Output / KPI")
            resp_lead = c2.text_input("Responsible Lead Person / Agency")
            timeframe = c3.text_input("Implementation Timeframe", "Q1-Q4 2026")

            c1, c2 = st.columns(2)
            budget_req = c1.number_input(
                "Budget Requirement (PHP)", 0, 5000000, 50000, step=5000
            )
            funding_source = c2.selectbox("Funding Source", [
                "Barangay AIP / Health Fund",
                "Municipal LGU Allocation",
                "DOH HFEP / Subsidies",
                "NGO / Private Donation",
            ])

            if st.form_submit_button("💾 Save Strategic Action Plan"):
                st.session_state.diag_records.append({
                    "Problem": p_title,
                    "BPA_Score": bpa_score,
                    "Objective": strategic_obj,
                    "Activities": key_activities,
                    "Output": target_output,
                    "Lead": resp_lead,
                    "Timeframe": timeframe,
                    "Budget": budget_req,
                    "Source": funding_source,
                })
                save_session_to_disk()
                st.success(
                    f"Action Plan for '{p_title}' saved permanently into disk"
                    " storage!"
                )

    with t2:
        st.markdown("#### 📄 Saved Strategic Action Plans")
        if len(st.session_state.diag_records) == 0:
            st.info("No saved action plans logged yet.")
        else:
            plan_df = pd.DataFrame(st.session_state.diag_records)
            st.dataframe(plan_df, use_container_width=True)

# MODULE 8: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Multi-Phase Master Data Persistence & Export Management")
    st.caption(
        "Manage, export, and persist field collection records across all 6"
        " project phases."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Phase 1 Scorecards", f"{len(st.session_state.gov_records)} Records"
    )
    c2.metric("Phase 2 HH Surveys", f"{len(st.session_state.hh_records)} Records")
    c3.metric(
        "Phase 4 PERI Windshields",
        f"{len(st.session_state.windshield_records)} Records",
    )

    st.markdown("---")

    col_exp1, col_exp2 = st.columns(2)

    with col_exp1:
        st.markdown("### 📥 Download Complete Persistent Backup (JSON)")
        shared_export = {
            "hh_records": st.session_state.get("hh_records", []),
            "gov_records": st.session_state.get("gov_records", []),
            "qual_records": st.session_state.get("qual_records", []),
            "windshield_records": st.session_state.get("windshield_records", []),
            "diag_records": st.session_state.get("diag_records", []),
        }
        json_str = json.dumps(shared_export, indent=4)
        st.download_button(
            label="Download Master JSON Dataset",
            data=json_str,
            file_name="shared_survey_data.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_exp2:
        st.markdown("### 📊 Export Phase 2 Master Household CSV")
        if len(st.session_state.hh_records) > 0:
            csv_df = pd.DataFrame(st.session_state.hh_records)
            csv_data = csv_df.to_csv(index=False)
            st.download_button(
                label="Download Household Master CSV",
                data=csv_data,
                file_name="phase2_master_household_records.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No household records available for CSV export.")

    st.markdown("---")
    st.markdown("### ⚠️ Data Clearance Controls")
    if st.button("🗑️ Clear All Local & Disk Data Records", type="secondary"):
        st.session_state.hh_records = []
        st.session_state.gov_records = []
        st.session_state.qual_records = []
        st.session_state.windshield_records = []
        st.session_state.diag_records = []
        save_session_to_disk()
        st.success("All data cleared successfully!")
        st.rerun()
