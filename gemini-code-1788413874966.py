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

# ================= MODULE 1: INTERACTIVE SPOT MAP =================
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

# ================= MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD =================
elif menu == "📋 Phase 1: Full Governance Scorecard":
    st.subheader(
        "Phase 1: Barangay Health Board (BHB) Governance Scorecard (100-Point"
        " Instrument)"
    )

    with st.expander(
        "📖 View Formal Scoring Criteria Matrix & Governance Categorization Guide",
        expanded=False,
    ):
        st.markdown("""
        ### Official Scoring Matrix & Verification Guide
        * **Domain 1. Legal Reconstitution (Max: 10 pts)**
          * **1.1** Signed Executive Order (EO) / Resolution reconstituting the BHB for the current term (5 pts)
          * **1.2** Mandatory Multi-sectoral Representation present: NGO/CBO, Youth/SK, BHW/BNS, Senior Citizen, DepEd (5 pts)
        * **Domain 2. Meeting Regularity (Max: 20 pts)**
          * **2.1** Conduct of Regular Quarterly BHB Meetings (3 pts per quarter conducted = 12 pts max)
          * **2.2** Official Quorum (>50% member attendance) consistently documented (4 pts)
          * **2.3** Approved Action-Oriented Minutes with resolution tracking (4 pts)
        * **Domain 3. Legislative Output (Max: 20 pts)**
          * **3.1** Enactment of specific local health ordinances (10 pts)
          * **3.2** Active enforcement mechanism & Task Force creation (5 pts)
          * **3.3** Policy alignment with UHC & Municipal Health Priorities (5 pts)
        * **Domain 4. AIP Budget Allocation (Max: 20 pts)**
          * **4.1** Dedicated Health & Sanitation budget line-items in AIP (8 pts)
          * **4.2** Adequate budget for drugs, honoraria, emergency response (6 pts)
          * **4.3** Budget execution & utilization >75% (6 pts)
        * **Domain 5. Accomplishment Reports (Max: 15 pts)**
          * **5.1** Regular quarterly health reports submitted to RHU/MHO (8 pts)
          * **5.2** Presentation of Health Status during Barangay Assemblies (4 pts)
          * **5.3** Functional Health Information Board maintained (3 pts)
        * **Domain 6. Committee Functionality (Max: 15 pts)**
          * **6.1** Functional Working Committees created (6 pts)
          * **6.2** Regular operational meetings and reports (6 pts)
          * **6.3** Community mobilization campaigns executed (3 pts)
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
                health_lead = c3.text_input("Committee Lead on Health")

            with t2:
                st.markdown("**Domain 1: Legal Reconstitution (Max 10 Points)**")
                c1, c2 = st.columns(2)
                g1_1 = c1.number_input("1.1 Signed EO / Resolution (Max 5 pts)", 0, 5, 0)
                g1_2 = c2.number_input("1.2 Multi-sectoral Representation (Max 5 pts)", 0, 5, 0)

                st.markdown("**Domain 2: Meeting Regularity (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g2_1 = c1.number_input("2.1 Quarterly Meetings (Max 12 pts)", 0, 12, 0)
                g2_2 = c2.number_input("2.2 Official Quorum (Max 4 pts)", 0, 4, 0)
                g2_3 = c3.number_input("2.3 Action-Oriented Minutes (Max 4 pts)", 0, 4, 0)

                st.markdown("**Domain 3: Legislative Output (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g3_1 = c1.number_input("3.1 Health Ordinances (Max 10 pts)", 0, 10, 0)
                g3_2 = c2.number_input("3.2 Active Enforcement (Max 5 pts)", 0, 5, 0)
                g3_3 = c3.number_input("3.3 UHC Policy Alignment (Max 5 pts)", 0, 5, 0)

            with t3:
                st.markdown("**Domain 4: AIP Budget Allocation (Max 20 Points)**")
                c1, c2, c3 = st.columns(3)
                g4_1 = c1.number_input("4.1 Health Budget in AIP (Max 8 pts)", 0, 8, 0)
                g4_2 = c2.number_input("4.2 Medicine & Honoraria Budget (Max 6 pts)", 0, 6, 0)
                g4_3 = c3.number_input("4.3 Budget Utilization >75% (Max 6 pts)", 0, 6, 0)

                st.markdown("**Domain 5: Accomplishment Reports (Max 15 Points)**")
                c1, c2, c3 = st.columns(3)
                g5_1 = c1.number_input("5.1 RHU/MHO Reports Submitted (Max 8 pts)", 0, 8, 0)
                g5_2 = c2.number_input("5.2 Barangay Assembly Reporting (Max 4 pts)", 0, 4, 0)
                g5_3 = c3.number_input("5.3 Active Health Info Board (Max 3 pts)", 0, 3, 0)

            with t4:
                st.markdown("**Domain 6: Committee Functionality (Max 15 Points)**")
                c1, c2, c3 = st.columns(3)
                g6_1 = c1.number_input("6.1 Active Working Committees (Max 6 pts)", 0, 6, 0)
                g6_2 = c2.number_input("6.2 Monthly Committee Meetings (Max 6 pts)", 0, 6, 0)
                g6_3 = c3.number_input("6.3 Community Campaigns Executed (Max 3 pts)", 0, 3, 0)

                gap_summary = st.text_area("Identify primary governance bottlenecks:")
                action_plan = st.text_area("Recommended technical assistance plan:")

            if st.form_submit_button("Submit & Save Governance Scorecard"):
                total_score = sum([
                    g1_1, g1_2, g2_1, g2_2, g2_3, g3_1, g3_2, g3_3,
                    g4_1, g4_2, g4_3, g5_1, g5_2, g5_3, g6_1, g6_2, g6_3
                ])
                rating = (
                    "HIGH FUNCTIONING"
                    if total_score >= 80
                    else ("MODERATE FUNCTIONING" if total_score >= 50 else "LOW FUNCTIONING")
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
                st.success(f"Scorecard Saved! Total Score: {total_score}/100 — Rating: {rating}")

    else:
        st.markdown("### 📂 Submitted Governance Scorecards")
        if len(st.session_state.gov_records) == 0:
            st.info("No governance scorecard records found.")
        else:
            gov_options = [
                f"[{i+1}] {r.get('Barangay', 'Unnamed')} (Score: {r.get('Score', 0)})"
                for i, r in enumerate(st.session_state.gov_records)
            ]
            selected_idx = st.selectbox("Select Record to Review / Edit", range(len(gov_options)), format_func=lambda x: gov_options[x])
            rec = st.session_state.gov_records[selected_idx]

            with st.form("edit_gov_form"):
                e_brgy = st.text_input("Barangay Name", value=rec.get("Barangay", ""))
                e_city = st.text_input("City / Municipality", value=rec.get("City", ""))
                e_prov = st.text_input("Province", value=rec.get("Province", ""))
                e_score = st.number_input("Total Score (0–100)", 0, 100, int(rec.get("Score", 0)))
                e_gaps = st.text_area("Governance Bottlenecks", value=rec.get("Gaps", ""))
                e_action = st.text_area("Action Plan", value=rec.get("ActionPlan", ""))

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Changes"):
                        rec.update({"Barangay": e_brgy, "City": e_city, "Province": e_prov, "Score": e_score, "Gaps": e_gaps, "ActionPlan": e_action})
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

# ================= MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY =================
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader("Phase 2: Master Household Survey Instrument")

    mode_p2 = st.radio(
        "Select Operation",
        [
            "➕ New Household Survey Entry",
            "📊 Phase 2 Interpreted Data & Research Analytics Table Inspector",
            "📂 Review, Edit & Delete Submitted Household Surveys",
        ],
        horizontal=True,
    )

    if mode_p2 == "➕ New Household Survey Entry":
        if "adult_count" not in st.session_state:
            st.session_state.adult_count = 1
        if "child_count" not in st.session_state:
            st.session_state.child_count = 0

        c_cnt1, c_cnt2, c_cnt3, c_cnt4 = st.columns(4)
        with c_cnt1:
            st.session_state.adult_count = st.number_input("Adult Members Count", 0, 20, st.session_state.adult_count, 1)
        with c_cnt2:
            if st.button("➕ Add Adult Form", use_container_width=True):
                st.session_state.adult_count += 1
                st.rerun()
        with c_cnt3:
            st.session_state.child_count = st.number_input("Child Members Count (<5 yrs)", 0, 15, st.session_state.child_count, 1)
        with c_cnt4:
            if st.button("➕ Add Child Form", use_container_width=True):
                st.session_state.child_count += 1
                st.rerun()

        num_adults = st.session_state.adult_count
        num_children = st.session_state.child_count

        c_e1, c_e2 = st.columns(2)
        enum_select = c_e1.selectbox("👤 Enumerator Identifier", ["Enumerator 1 (Code: E1)", "Enumerator 2 (Code: E2)", "Enumerator 3 (Code: E3)"], index=0)
        enum_code = "E1" if "E1" in enum_select else ("E2" if "E2" in enum_select else "E3")

        existing_hh_ids = [r.get("HH_ID", "") for r in st.session_state.hh_records]
        enum_existing_count = sum(1 for r in st.session_state.hh_records if r.get("Enumerator_Code") == enum_code or r.get("HH_ID", "").startswith(f"HH-{enum_code}-")) + 1
        auto_suggested_id = f"HH-{enum_code}-{enum_existing_count:03d}"

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

            with t_meta:
                c1, c2, c3, c4 = st.columns(4)
                hh_id = c1.text_input("Household ID", value=auto_suggested_id)
                brgy = c2.text_input("Barangay Name")
                purok = c3.selectbox("Purok / Zone", [f"Purok {i}" for i in range(1, 8)])
                date_survey = c4.date_input("Date of Survey")

                c1, c2, c3, c4 = st.columns(4)
                lat = c1.number_input("Latitude", value=11.1560, format="%.4f")
                lon = c2.number_input("Longitude", value=124.9920, format="%.4f")
                enum_name = c3.text_input("Enumerator Full Name", f"Field Enumerator ({enum_code})")
                resp_role = c4.selectbox("Respondent Role", ["Head", "Spouse", "Adult Member", "Other"])

                c1, c2, c3 = st.columns(3)
                surv_status = c1.selectbox("Survey Status", ["Completed", "Partially Completed", "Refused"])
                dialect = c2.selectbox("Primary Dialect", ["Waray", "Tagalog", "English", "Cebuano / Bisaya", "Other"])
                religion = c3.selectbox("Religion", ["Roman Catholic", "Islam", "Iglesia ni Cristo", "Evangelical", "Other"])

                st.markdown("---")
                c1, c2, c3, c4 = st.columns(4)
                tot_children = c1.number_input("No. of Children (<18 yrs)", 0, 20, 0)
                tot_dependents = c2.number_input("No. of Other Dependents", 0, 10, 0)
                hh_head_name = c3.text_input("Household Head Full Name")
                head_civil = c4.selectbox("Head Civil Status", ["Single", "Married", "Widowed", "Separated", "Cohabiting"])

            with t_vitals:
                st.markdown(f"**Adult Profiling ({num_adults} Adult(s))**")
                adults_data = []
                for i in range(1, int(num_adults) + 1):
                    st.markdown(f"<div class='adult-card'><strong>Adult Member {i} Profile</strong></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_name = c1.text_input(f"Adult {i} Name", key=f"a_name_{i}")
                    a_gender = c2.selectbox(f"Adult {i} Gender", ["Male", "Female", "Other"], key=f"a_gen_{i}")
                    a_age = c3.number_input(f"Adult {i} Age", 18, 120, 30, key=f"a_age_{i}")
                    a_edu = c4.selectbox(f"Adult {i} Education", ["No Formal", "Elementary", "High School", "College"], key=f"a_edu_{i}")
                    a_occ = c5.text_input(f"Adult {i} Occupation", key=f"a_occ_{i}")

                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_ph_cat = c1.selectbox(f"Adult {i} PhilHealth", ["Indigent", "Formal", "Informal", "Unenrolled"], key=f"a_ph_{i}")
                    a_sys = c2.number_input(f"Adult {i} Systolic BP", 50, 250, 120, key=f"a_sys_{i}")
                    a_dia = c3.number_input(f"Adult {i} Diastolic BP", 30, 150, 80, key=f"a_dia_{i}")
                    a_spo2 = c4.number_input(f"Adult {i} SpO2 (%)", 50, 100, 98, key=f"a_spo2_{i}")
                    a_pulse = c5.number_input(f"Adult {i} Pulse", 30, 200, 75, key=f"a_pulse_{i}")

                    c1, c2 = st.columns(2)
                    a_symptoms = c1.multiselect(f"Adult {i} Complaints", ["None", "Cough", "Fever", "Headache", "Diarrhea", "Dizziness"], default=["None"], key=f"a_sym_{i}")
                    a_risk = c2.selectbox(f"Adult {i} Risk Category", ["Normal", "Hypertensive Risk", "Hypoxemic (<95%)", "Fever / Febrile"], key=f"a_risk_{i}")

                    a_action = st.multiselect(f"Adult {i} Action Taken", ["Referral to RHU", "BHS Check", "Counseling", "None"], default=["None"] if a_risk == "Normal" else ["Referral to RHU"], key=f"a_action_{i}")

                    if a_name.strip() != "":
                        adults_data.append({
                            "ID": f"Adult {i}", "Name": a_name, "Gender": a_gender, "Age": a_age, "Edu": a_edu,
                            "Occupation": a_occ, "PhilHealth_Cat": a_ph_cat, "BP": f"{a_sys}/{a_dia}",
                            "Sys": a_sys, "Dia": a_dia, "SpO2": a_spo2, "Pulse": a_pulse,
                            "Complaints": a_symptoms, "Risk": a_risk, "Action_Taken": a_action
                        })

            with t_socio:
                c1, c2, c3 = st.columns(3)
                income_cat = c1.selectbox("Monthly Family Income", ["≤ ₱10,000", "₱10,001–₱20,000", "₱20,001–₱35,000", "> ₱35,000"])
                livelihood = c2.selectbox("Primary Livelihood", ["Farming", "Laborer", "Fishing", "Govt", "Sari-Sari", "Other"])
                food_prod = c3.selectbox("Engaged in Food Production?", ["Yes", "No"])

                c1, c2 = st.columns(2)
                emergency_5k = c1.selectbox("Can raise ₱5k in 24 hrs?", ["Yes", "No"])
                p4ps_status = c2.selectbox("4Ps Beneficiary?", ["Yes", "No"])

                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                food_skip = c1.selectbox("Skipped meals due to lack of money?", ["No", "Yes"])
                food_worry = c2.selectbox("Worried running out of food?", ["No", "Yes"])
                food_fullday = c3.selectbox("Full day without eating?", ["No", "Yes"])

                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                tenure = c1.selectbox("Tenurial Status", ["Owned Lot & House", "Renting", "Shared", "Informal Settler"])
                house_type = c2.selectbox("Housing Type", ["Light", "Medium", "Heavy / Concrete"])
                cook_fuel = c3.selectbox("Indoor Cooking Fuel", ["LPG", "Wood / Charcoal", "Electric", "Kerosene"])

                c1, c2 = st.columns(2)
                is_flood_prone = c1.selectbox("🌊 Located in Flood-Prone Zone?", ["No", "Yes"])

                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                water_source = c1.selectbox("Water Source", ["Level 1: Protected Well", "Level 2: Faucet", "Level 3: Household Tap", "Unsafe Source", "Refill Station"])
                toilet_type = c2.selectbox("Toilet Facility", ["Flush to Septic", "VIP Latrine", "Open Defecation / None"])
                solid_disposal = c3.selectbox("Garbage Disposal", ["Municipal Collection", "Composting", "Burning", "Open Dumping"])

            with t_dec:
                c1, c2 = st.columns(2)
                dec_expenses = c1.multiselect("Who decides on Expenses?", ["Father", "Mother", "Both", "Children"], default=["Father", "Mother"])
                dec_health = c2.multiselect("Who decides on Health Care?", ["Father", "Mother", "Both", "Children"], default=["Mother"])

            with t_morb:
                c1, c2, c3 = st.columns(3)
                e_diarrhea = c1.selectbox("Diarrheal Episodes (>1 in past yr)", ["No", "Yes"])
                e_urti = c2.selectbox("Respiratory Illnesses / Pneumonia", ["No", "Yes"])
                e_dengue = c3.selectbox("Dengue Suspected/Confirmed", ["No", "Yes"])

                c1, c2 = st.columns(2)
                htn_status = c1.selectbox("Hypertension Status", ["No Member", "Diagnosed - Compliant", "Diagnosed - Irregular", "Diagnosed - Untreated"])
                dm_status = c2.selectbox("Diabetes Status", ["No Member", "Diagnosed - Compliant", "Diagnosed - Irregular", "Diagnosed - Untreated"])

                c1, c2 = st.columns(2)
                asthma_status = c1.selectbox("Asthma / COPD Status", ["No Member", "Active Maintenance", "Emergency Meds Only"])
                tb_status = c2.selectbox("TB Status", ["No Member", "Enrolled in DOTS", "Completed DOTS"])

                c1, c2, c3 = st.columns(3)
                ckd_status = c1.selectbox("CKD", ["No", "Yes"])
                cvd_status = c2.selectbox("CVD / Stroke", ["No", "Yes"])
                cancer_status = c3.selectbox("Cancer", ["No", "Yes"])

            with t_mch:
                c1, c2, c3 = st.columns(3)
                is_preg = c1.selectbox("Pregnant Member?", ["No", "Yes"])
                anc_visits = c2.number_input("ANC Visits", 0, 15, 0)
                anc_1st_tri = c3.selectbox("1st ANC in 1st Tri?", ["N/A", "Yes", "No"])

                c1, c2, c3 = st.columns(3)
                ifa_tablets = c1.selectbox("IFA Tablets", ["N/A", "<180", "≥180"])
                td_status = c2.selectbox("Td Status", ["N/A", "Td1/2", "Fully Immunized"])
                postpartum_check = c3.selectbox("Postpartum Check <72h", ["N/A", "Yes", "No"])

                c1, c2 = st.columns(2)
                deliv_personnel_yesno = c1.selectbox("Handled by Skilled Personnel?", ["N/A", "Yes", "No"])
                deliv_facility_yesno = c2.selectbox("Handled in Accredited Facility?", ["N/A", "Yes", "No"])

                c1, c2 = st.columns(2)
                fp_access = c1.selectbox("FP Access?", ["Yes", "No"])
                fp_practice = c2.selectbox("FP Practice?", ["Yes", "No"])

                mortality_yesno = st.selectbox("Preventable Death in Family (Past Yr)?", ["No", "Yes"])

            with t_child:
                st.markdown(f"**Child Profiling ({num_children} Child(ren))**")
                children_records = []
                for c_i in range(1, int(num_children) + 1):
                    st.markdown(f"<div class='child-card'><strong>👶 Child Member {c_i} Profile</strong></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c_name = c1.text_input(f"Child {c_i} Name", key=f"c_name_{c_i}")
                    c_sex = c2.selectbox(f"Child {c_i} Sex", ["Male", "Female"], key=f"c_sex_{c_i}")
                    c_age_m = c3.number_input(f"Child {c_i} Age (Mos)", 0, 59, 12, key=f"c_age_{c_i}")
                    c_wt_kg = c4.number_input(f"Child {c_i} Weight (kg)", 0.0, 35.0, 8.5, key=f"c_wt_{c_i}")
                    c_ht_cm = c5.number_input(f"Child {c_i} Height (cm)", 0.0, 120.0, 72.0, key=f"c_ht_{c_i}")

                    c_nutr = compute_child_nutrition(c_age_m, c_wt_kg, c_ht_cm)
                    st.caption(f"BMI: {c_nutr['BMI']} | Wasting: {c_nutr['Wasting']} | Stunting: {c_nutr['Stunting']}")

                    ic1, ic2, ic3, ic4, ic5, ic6 = st.columns(6)
                    imm_bcg = ic1.checkbox("BCG", key=f"bcg_{c_i}")
                    imm_hepb = ic2.checkbox("Hep B", key=f"hepb_{c_i}")
                    imm_penta = ic3.checkbox("Penta 3x", key=f"penta_{c_i}")
                    imm_opv = ic4.checkbox("OPV 3x", key=f"opv_{c_i}")
                    imm_pcv = ic5.checkbox("PCV 3x", key=f"pcv_{c_i}")
                    imm_mmr = ic6.checkbox("MMR 2x", key=f"mmr_{c_i}")

                    is_fic = all([imm_bcg, imm_hepb, imm_penta, imm_opv, imm_pcv, imm_mmr])
                    fic_status = "Fully Immunized Child (FIC)" if is_fic else "Incomplete"

                    c_action = st.multiselect(f"Child {c_i} Action", ["RHU Referral", "Supplementary Feeding", "IYCF", "Catch-up Imm", "None"], default=["None"] if is_fic else ["RHU Referral"], key=f"c_action_{c_i}")

                    if c_name.strip() != "":
                        children_records.append({
                            "Child_Num": f"Child {c_i}", "Name": c_name, "Sex": c_sex, "Age_Months": c_age_m,
                            "Weight": c_wt_kg, "Height": c_ht_cm, "Nutr": c_nutr, "FIC_Status": fic_status,
                            "Action_Taken": c_action
                        })

            with t_yakap:
                hsb_initial_actions = st.multiselect("Initial Actions When Unwell", ["Rest and wait", "Herbal remedies", "Buy OTC meds", "Contact healthcare provider"], default=["Rest and wait"])
                hsb_providers_used = st.multiselect("Facilities Used", ["Public hospital", "Private clinic", "RHU / BHS", "Pharmacy"], default=["RHU / BHS"])
                hsb_travel_time = st.selectbox("Travel Time to Facility", ["< 15 mins", "15-30 mins", "30-60 mins", "> 1 hour"])
                hsb_barriers = st.multiselect("Barriers to Seeking Care", ["High cost", "Waiting times", "Distance", "Lack of insurance"])

                c1, c2 = st.columns(2)
                yakap_registered = c1.selectbox("Registered under PhilHealth YAKAP?", ["Yes", "No", "Uncertain"])
                yakap_availed = c2.selectbox("Availed First Patient Encounter (FPE)?", ["Yes", "No", "N/A"])

            if st.form_submit_button("Submit & Save Complete Household Record"):
                primary_sys = adults_data[0]["Sys"] if len(adults_data) > 0 else 120
                primary_risk = adults_data[0]["Risk"] if len(adults_data) > 0 else "Normal"

                marker_color = [192, 38, 211, 230] if (is_flood_prone == "Yes" and primary_sys >= 140) else ([123, 17, 19, 220] if primary_sys >= 140 else ([37, 99, 235, 220] if is_flood_prone == "Yes" else [34, 197, 94, 200]))

                st.session_state.hh_records.append({
                    "HH_ID": hh_id, "Enumerator_Code": enum_code, "Barangay": brgy, "Purok": purok,
                    "Date": str(date_survey), "Lat": lat, "Lon": lon, "Enumerator": enum_name,
                    "Respondent_Role": resp_role, "Survey_Status": surv_status, "Dialect": dialect,
                    "Religion": religion, "Total_Children": tot_children, "Total_Dependents": tot_dependents,
                    "Head_Name": hh_head_name, "Head_Civil_Status": head_civil, "BP": f"{primary_sys}/80",
                    "Risk": primary_risk, "Flood_Prone": is_flood_prone, "Color": marker_color,
                    "Adults": adults_data, "Children": children_records, "Income": income_cat,
                    "Livelihood": livelihood, "Food_Production": food_prod, "Emergency_5k": emergency_5k,
                    "Four_Ps": p4ps_status, "Food_Skip": food_skip, "Food_Worry": food_worry,
                    "Food_FullDay": food_fullday, "Tenure": tenure, "House_Type": house_type,
                    "Cook_Fuel": cook_fuel, "Water": water_source, "Sanitation": toilet_type,
                    "Solid_Disposal": solid_disposal, "Decisions_Expenses": dec_expenses,
                    "Decisions_Health": dec_health, "Diarrhea": e_diarrhea, "URTI": e_urti,
                    "Dengue": e_dengue, "Hypertension_Status": htn_status, "Diabetes_Status": dm_status,
                    "Asthma_Status": asthma_status, "TB_Status": tb_status, "CKD_Status": ckd_status,
                    "CVD_Status": cvd_status, "Cancer_Status": cancer_status, "Is_Pregnant": is_preg,
                    "ANC_Visits": anc_visits, "ANC_1st_Tri": anc_1st_tri, "IFA_Tablets": ifa_tablets,
                    "Td_Status": td_status, "Postpartum_Check": postpartum_check, "Deliv_Personnel": deliv_personnel_yesno,
                    "Deliv_Facility": deliv_facility_yesno, "FP_Access": fp_access, "FP_Practice": fp_practice,
                    "Preventable_Mortality": mortality_yesno, "HSB_Initial_Actions": hsb_initial_actions,
                    "HSB_Providers_Used": hsb_providers_used, "HSB_Travel_Time": hsb_travel_time,
                    "HSB_Barriers": hsb_barriers, "Yakap": yakap_registered, "Yakap_Availed": yakap_availed,
                })
                save_session_to_disk()
                st.success(f"Household record '{hh_id}' saved successfully!")

    elif mode_p2 == "📊 Phase 2 Interpreted Data & Research Analytics Table Inspector":
        st.markdown("### 📊 Research Interpretation & Master Survey Variable Tables")
        if len(st.session_state.hh_records) == 0:
            st.info("No household records found in Phase 2.")
        else:
            total_hhs = len(st.session_state.hh_records)
            all_adults = [a for hh in st.session_state.hh_records for a in hh.get("Adults", [])]
            tot_adults = len(all_adults)

            tables_data = []
            tables_data.append(generate_research_table([r.get("Survey_Status") for r in st.session_state.hh_records], total_hhs, "Survey Completion Status"))
            tables_data.append(generate_research_table([r.get("Dialect") for r in st.session_state.hh_records], total_hhs, "Primary Dialect"))
            tables_data.append(generate_research_table([r.get("Income") for r in st.session_state.hh_records], total_hhs, "Monthly Income"))
            tables_data.append(generate_research_table([r.get("Water") for r in st.session_state.hh_records], total_hhs, "Water Source Level"))
            tables_data.append(generate_research_table([r.get("Sanitation") for r in st.session_state.hh_records], total_hhs, "Toilet Facility"))
            tables_data.append(generate_research_table([r.get("Hypertension_Status") for r in st.session_state.hh_records], total_hhs, "Hypertension Status"))
            if tot_adults > 0:
                tables_data.append(generate_research_table([a.get("Risk") for a in all_adults], tot_adults, "Adult Clinical Risk Category"))

            master_research_df = pd.concat(tables_data, ignore_index=True)
            st.dataframe(master_research_df, use_container_width=True)

    else:
        st.markdown("### 📂 Submitted Household Survey Records")
        if len(st.session_state.hh_records) == 0:
            st.info("No household records found.")
        else:
            hh_options = [f"[{i+1}] {r.get('HH_ID', 'N/A')} - {r.get('Barangay', 'N/A')} ({r.get('Purok', 'N/A')})" for i, r in enumerate(st.session_state.hh_records)]
            selected_idx = st.selectbox("Select Record to Review / Edit", range(len(hh_options)), format_func=lambda x: hh_options[x])
            rec = st.session_state.hh_records[selected_idx]

            with st.form("edit_hh_form"):
                e_hh_id = st.text_input("Household ID", value=rec.get("HH_ID", ""))
                e_brgy = st.text_input("Barangay Name", value=rec.get("Barangay", ""))
                e_purok = st.text_input("Purok", value=rec.get("Purok", ""))

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Edits"):
                        rec.update({"HH_ID": e_hh_id, "Barangay": e_brgy, "Purok": e_purok})
                        st.session_state.hh_records[selected_idx] = rec
                        save_session_to_disk()
                        st.success("Record updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Record"):
                        st.session_state.hh_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("Record deleted successfully!")
                        st.rerun()

# ================= MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS =================
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader("Phase 3: Qualitative Field Tools (KII & FGD Guides)")

    tool_choice = st.selectbox(
        "Select Qualitative Tool Instrument",
        [
            "TOOL 3.1: KII GUIDE — GOVERNANCE & LEADERSHIP",
            "TOOL 3.2: KII GUIDE — FRONTLINE PERSONNEL",
            "TOOL 3.3: FGD GUIDE — COMMUNITY MEMBERS",
        ],
    )

    with st.form("qual_tool_form"):
        c1, c2 = st.columns(2)
        resp_name = c1.text_input("Respondent / Group ID")
        brgy_name = c2.text_input("Barangay / Location")

        st.markdown("#### Qualitative Key Findings & Transcripts")
        findings = st.text_area("Key Interview / Discussion Themes & Notes", height=180)
        quotes = st.text_area("Verbatim Quotes / Highlight Statements", height=120)

        if st.form_submit_button("💾 Save Qualitative Field Record"):
            st.session_state.qual_records.append({
                "Tool": tool_choice,
                "Respondent": resp_name,
                "Barangay": brgy_name,
                "Findings": findings,
                "Quotes": quotes,
            })
            save_session_to_disk()
            st.success("Qualitative Record Saved Successfully!")

# ================= MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL =================
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader("Phase 4: Expanded Purok Environmental Risk Index (PERI) Windshield Evaluation Tool")

    mode_p4 = st.radio("Select Operation", ["➕ New PERI Evaluation", "📂 Review Saved PERI Evaluations"], horizontal=True)

    if mode_p4 == "➕ New PERI Evaluation":
        with st.form("peri_form"):
            c1, c2, c3 = st.columns(3)
            purok_name = c1.selectbox("Purok Evaluated", [f"Purok {i}" for i in range(1, 8)])
            eval_date = c2.date_input("Evaluation Date")
            evaluator = c3.text_input("Evaluator Name")

            st.markdown("<div class='peri-domain-header'>Domain 1: Water, Sanitation & Hygiene (WASH)</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            ds1_1 = c1.slider("Open Defecation / Latrine Deficits (1-3)", 1, 3, 1)
            ds1_2 = c2.slider("Unprotected Water / Stagnant Water Risk (1-3)", 1, 3, 1)

            st.markdown("<div class='peri-domain-header'>Domain 2: Food Safety & Market Environment</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            ds2_1 = c1.slider("Uncovered Food Stalls / Food Hazard (1-3)", 1, 3, 1)
            ds2_2 = c2.slider("Lack of Fresh Produce Access (1-3)", 1, 3, 1)

            st.markdown("<div class='peri-domain-header'>Domain 3: Built Environment & Housing Density</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            ds3_1 = c1.slider("Overcrowded Construction / Narrow Access (1-3)", 1, 3, 1)
            ds3_2 = c2.slider("Poor Ventilation & Indoor Air Risk (1-3)", 1, 3, 1)

            st.markdown("<div class='peri-domain-header'>Domain 4: Health Infrastructure & Accessibility</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            ds4_1 = c1.slider("Distance / Barrier to BHS (1-3)", 1, 3, 1)
            ds4_2 = c2.slider("Lack of Emergency Transport (1-3)", 1, 3, 1)

            st.markdown("<div class='peri-domain-header'>Domain 5: Disaster Vulnerability & Climate Risk</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            ds5_1 = c1.slider("Flood Prone / Low-Lying Vulnerability (1-3)", 1, 3, 1)
            ds5_2 = c2.slider("Landslide / Coastal Hazard Risk (1-3)", 1, 3, 1)

            st.markdown("<div class='peri-domain-header'>Domain 6: Vector & Pest Proliferation Risk</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            ds6_1 = c1.slider("Uncollected Garbage / Stray Animals (1-3)", 1, 3, 1)
            ds6_2 = c2.slider("Mosquito Breeding Sites / Clogged Drains (1-3)", 1, 3, 1)

            if st.form_submit_button("Submit & Compute PERI Score"):
                d1 = (ds1_1 + ds1_2) / 2.0
                d2 = (ds2_1 + ds2_2) / 2.0
                d3 = (ds3_1 + ds3_2) / 2.0
                d4 = (ds4_1 + ds4_2) / 2.0
                d5 = (ds5_1 + ds5_2) / 2.0
                d6 = (ds6_1 + ds6_2) / 2.0

                peri_index = np.mean([d1, d2, d3, d4, d5, d6])
                risk_cat = "Category C: Critical Hazard Zone" if peri_index >= 2.3 else ("Category B: Moderate Environmental Risk" if peri_index >= 1.5 else "Category A: Low Environmental Risk")

                st.session_state.windshield_records.append({
                    "Purok": purok_name,
                    "Date": str(eval_date),
                    "Evaluator": evaluator,
                    "DS1_Sanitation": d1,
                    "DS2_Food": d2,
                    "DS3_BuiltEnv": d3,
                    "DS4_HealthInfra": d4,
                    "DS5_DRR": d5,
                    "DS6_Vector": d6,
                    "PERI_Index": float(peri_index),
                    "Category": risk_cat,
                })
                save_session_to_disk()
                st.success(f"PERI Evaluation Saved! Composite Index: {peri_index:.2f} — {risk_cat}")

    else:
        st.markdown("### 📂 Saved PERI Windshield Records")
        if len(st.session_state.windshield_records) == 0:
            st.info("No PERI evaluation records found.")
        else:
            st.dataframe(pd.DataFrame(st.session_state.windshield_records), use_container_width=True)

# ================= MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS =================
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial Cluster Mapping & Statistical Analytics Engine")
    st.caption("Epidemiological Correlation Analysis, Bivariate Hypothesis Testing & Multi-Factor Spatial Risk Clustering")

    hh_records = st.session_state.hh_records
    peri_records = st.session_state.windshield_records

    tab_corr, tab_spatial, tab_cross, tab_rank = st.tabs([
        "📊 PERI vs. Morbidity Correlation",
        "🗺️ Spatial Cluster Vulnerability Mapping",
        "📈 Bivariate Cross-Tabulation & Risk Analysis",
        "🏆 Purok Environmental Risk Ranking",
    ])

    # ---------------- TAB 1: PERI vs MORBIDITY CORRELATION ----------------
    with tab_corr:
        st.markdown("### 📊 Correlation: Environmental Risk (PERI) vs. Disease Morbidity Rate")
        st.caption("Evaluates the linear association between Purok Environmental Risk Index (PERI) scores and community disease prevalence.")

        purok_list = [f"Purok {i}" for i in range(1, 8)]
        
        # Build Purok PERI lookup map
        peri_map = {}
        for p in peri_records:
            peri_map[p.get("Purok")] = p.get("PERI_Index", 1.0)

        # Build Purok Morbidity & Health Risk lookup
        purok_stats = []
        for p_name in purok_list:
            p_hhs = [h for h in hh_records if h.get("Purok") == p_name]
            p_adults = [a for h in p_hhs for a in h.get("Adults", [])]
            p_children = [c for h in p_hhs for c in h.get("Children", [])]
            
            n_hh = len(p_hhs)
            n_adults = len(p_adults)
            
            # Disease indicators
            htn_cases = sum(1 for a in p_adults if a.get("Risk") == "Hypertensive Risk" or a.get("Sys", 0) >= 140)
            htn_rate = (htn_cases / n_adults * 100.0) if n_adults > 0 else 0.0
            
            diarrhea_hhs = sum(1 for h in p_hhs if h.get("Diarrhea") == "Yes")
            diarrhea_rate = (diarrhea_hhs / n_hh * 100.0) if n_hh > 0 else 0.0

            stunted_kids = sum(1 for c in p_children if "Stunted" in c.get("Nutr", {}).get("Stunting", ""))
            stunting_rate = (stunted_kids / len(p_children) * 100.0) if len(p_children) > 0 else 0.0

            p_peri = peri_map.get(p_name, 1.2 if n_hh == 0 else (1.5 + (diarrhea_rate * 0.03)))

            purok_stats.append({
                "Purok": p_name,
                "Total HHs": n_hh,
                "PERI Index": round(float(p_peri), 2),
                "Hypertension Rate (%)": round(htn_rate, 2),
                "Diarrhea Rate (%)": round(diarrhea_rate, 2),
                "Child Stunting Rate (%)": round(stunting_rate, 2),
            })

        df_corr_purok = pd.DataFrame(purok_stats)

        col_sel, col_stat = st.columns([2, 1])

        with col_sel:
            selected_morbidity = st.selectbox(
                "Select Morbidity Vector to Correlate with PERI Index",
                ["Hypertension Rate (%)", "Diarrhea Rate (%)", "Child Stunting Rate (%)"]
            )

        # Pearson Correlation Coefficient Calculation
        x_peri = df_corr_purok["PERI Index"].values
        y_morb = df_corr_purok[selected_morbidity].values

        if len(x_peri) > 1 and np.std(x_peri) > 0 and np.std(y_morb) > 0:
            corr_coef = float(np.corrcoef(x_peri, y_morb)[0, 1])
        else:
            corr_coef = 0.00

        with col_stat:
            st.metric(
                "Pearson Correlation (r)",
                f"{corr_coef:+.3f}",
                delta="Strong Association" if abs(corr_coef) >= 0.6 else ("Moderate Association" if abs(corr_coef) >= 0.3 else "Weak / Low Association")
            )

        st.markdown("#### 📉 Interactive Correlation Scatter & Trend Representation")
        st.dataframe(df_corr_purok, use_container_width=True)

        st.bar_chart(df_corr_purok.set_index("Purok")[["PERI Index", selected_morbidity]])

        if abs(corr_coef) >= 0.5:
            st.markdown(
                f"""<div class="insight-alert-high">
                <strong>💡 Epidemiological Interpretation:</strong> A high correlation coefficient (<strong>r = {corr_coef:+.3f}</strong>) indicates that environmental risks measured by the PERI tool strongly drive increases in community <strong>{selected_morbidity}</strong>. Priorities should focus on environmental sanitation and structural hazard mitigation in high PERI puroks.
                </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""<div class="insight-alert-good">
                <strong>💡 Epidemiological Interpretation:</strong> A correlation coefficient of <strong>r = {corr_coef:+.3f}</strong> indicates a mild or multi-factorial association. Continue gathering longitudinal survey samples across all puroks.
                </div>""",
                unsafe_allow_html=True,
            )

    # ---------------- TAB 2: SPATIAL CLUSTER VULNERABILITY MAPPING ----------------
    with tab_spatial:
        st.markdown("### 🗺️ Multi-Factor Spatial Vulnerability Cluster Mapping")
        st.caption("Geospatial risk clustering evaluating composite vulnerability (PERI Index + Flood Zone + WASH Deficit + Clinical Health Risk).")

        if len(hh_records) == 0:
            st.info("No household entries found. Displaying baseline spatial cluster simulation.")
            cluster_data = [
                {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "Vuln_Score": 0.85, "Tier": "Critical Vulnerability", "Color": [180, 0, 0, 220]},
                {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "Vuln_Score": 0.30, "Tier": "Low Vulnerability", "Color": [34, 197, 94, 200]},
                {"HH_ID": "HH-003", "Purok": "Purok 2", "Lat": 11.1555, "Lon": 124.9905, "Vuln_Score": 0.65, "Tier": "Moderate Vulnerability", "Color": [220, 120, 0, 220]},
                {"HH_ID": "HH-004", "Purok": "Purok 3", "Lat": 11.1570, "Lon": 124.9930, "Vuln_Score": 0.90, "Tier": "Critical Vulnerability", "Color": [180, 0, 0, 220]},
            ]
            df_cluster = pd.DataFrame(cluster_data)
        else:
            cluster_rows = []
            for h in hh_records:
                score = 0.1
                if h.get("Flood_Prone") == "Yes":
                    score += 0.25
                if "Unsafe" in h.get("Water", ""):
                    score += 0.25
                if "≤ ₱10,000" in h.get("Income", ""):
                    score += 0.20
                if h.get("Risk") == "Hypertensive Risk":
                    score += 0.20

                score = min(score, 1.0)

                if score >= 0.70:
                    tier = "Critical Vulnerability"
                    col = [180, 0, 0, 220]
                elif score >= 0.40:
                    tier = "Moderate Vulnerability"
                    col = [220, 120, 0, 220]
                else:
                    tier = "Low Vulnerability"
                    col = [34, 197, 94, 200]

                cluster_rows.append({
                    "HH_ID": h.get("HH_ID"),
                    "Purok": h.get("Purok"),
                    "Lat": h.get("Lat", 11.1560),
                    "Lon": h.get("Lon", 124.9915),
                    "Vuln_Score": round(score, 2),
                    "Tier": tier,
                    "Color": col,
                })
            df_cluster = pd.DataFrame(cluster_rows)

        c_map, c_legend = st.columns([3, 1])

        with c_legend:
            st.markdown("**Spatial Cluster Legend:**")
            st.markdown("🔴 **Red:** Critical Vulnerability (Score ≥ 0.70)")
            st.markdown("🟠 **Orange:** Moderate Vulnerability (Score 0.40 - 0.69)")
            st.markdown("🟢 **Green:** Low Vulnerability (Score < 0.40)")

            crit_cnt = sum(1 for _, r in df_cluster.iterrows() if r["Tier"] == "Critical Vulnerability")
            st.metric("Critical Spatial Hotspots", f"{crit_cnt} HHs")

        with c_map:
            view = pdk.ViewState(
                latitude=df_cluster["Lat"].mean() if len(df_cluster) > 0 else 11.1560,
                longitude=df_cluster["Lon"].mean() if len(df_cluster) > 0 else 124.9915,
                zoom=15,
                pitch=35,
            )
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_cluster,
                get_position=["Lon", "Lat"],
                get_color="Color",
                get_radius=20,
                pickable=True,
            )
            st.pydeck_chart(
                pdk.Deck(
                    layers=[layer],
                    initial_view_state=view,
                    tooltip={
                        "text": "HH ID: {HH_ID}\nPurok: {Purok}\nVulnerability Score: {Vuln_Score}\nTier: {Tier}"
                    },
                )
            )

        st.markdown("#### 📋 Cluster Analysis Summary Table")
        st.dataframe(df_cluster, use_container_width=True)

    # ---------------- TAB 3: BIVARIATE CROSS-TABULATION ----------------
    with tab_cross:
        st.markdown("### 📈 Cross-Tabulation & Bivariate Risk Analysis")
        st.caption("Examines key social determinant interactions and disease risk distributions.")

        if len(hh_records) > 0:
            df_hh = pd.DataFrame(hh_records)
            st.markdown("#### 1. Water Source vs. Diarrheal Illness Frequency")
            ct_water = pd.crosstab(df_hh["Water"], df_hh["Diarrhea"], margins=True)
            st.dataframe(ct_water, use_container_width=True)

            st.markdown("#### 2. Income Level vs. Hypertension Status")
            ct_inc = pd.crosstab(df_hh["Income"], df_hh["Hypertension_Status"], margins=True)
            st.dataframe(ct_inc, use_container_width=True)
        else:
            st.info("No household data logged yet for cross-tabulation.")

    # ---------------- TAB 4: PUROK RISK RANKING ----------------
    with tab_rank:
        st.markdown("### 🏆 Comprehensive Purok Environmental & Health Risk Ranking")
        if len(hh_records) > 0 or len(peri_records) > 0:
            st.dataframe(df_corr_purok.sort_values(by="PERI Index", ascending=False), use_container_width=True)
        else:
            st.info("No data available to rank puroks.")

# ================= MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS & ACTION PLAN =================
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("Phase 6: Priority Community Diagnosis & SMART Public Health Action Plan")

    with st.form("diag_form"):
        st.markdown("#### 🎯 Community Health Problem Formulation")
        p_title = st.text_input("Community Health Diagnosis Title", "High Prevalence of Adult Hypertension Secondary to Unhealthy Lifestyle & Low BHS Screening")
        p_domain = st.selectbox("Health Domain Category", ["Cardiovascular / NCD", "WASH & Infectious Disease", "Maternal & Child Health", "Nutrition & Stunting", "Environmental / DRR"])
        p_target = st.text_input("Target Purok / Vulnerable Population", "Purok 1 & Purok 3 Adults")

        st.markdown("#### 📝 SMART Intervention Action Plan")
        c1, c2 = st.columns(2)
        obj_smart = c1.text_area("SMART Objective", "Reduce unmonitored hypertension by 30% within 6 months.")
        activities = c2.text_area("Core Strategic Interventions", "Conduct weekly BHW home BP visits, establish BHS hypertension registry, provide free maintenance meds.")

        c1, c2, c3 = st.columns(3)
        lead_agency = c1.text_input("Lead Agency / Person", "BHB Chair & RHU Physician")
        budget_req = c2.text_input("Required AIP Budget (₱)", "₱45,000")
        indicator = c3.text_input("Evaluation Indicator", "100% screened adults with BP logs")

        if st.form_submit_button("💾 Save Action Plan"):
            st.session_state.diag_records.append({
                "Title": p_title,
                "Domain": p_domain,
                "Target": p_target,
                "Objective": obj_smart,
                "Activities": activities,
                "Lead": lead_agency,
                "Budget": budget_req,
                "Indicator": indicator,
            })
            save_session_to_disk()
            st.success("Community Action Plan Saved Successfully!")

    st.markdown("---")
    st.markdown("### 📂 Saved Community Diagnosis & Action Plans")
    if len(st.session_state.diag_records) == 0:
        st.info("No saved action plans found.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.diag_records), use_container_width=True)

# ================= MODULE 8: DATA MANAGEMENT & EXPORT =================
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Multi-Phase Shared Data Management & Export Console")

    st.markdown("#### 📤 Export Survey Data Records")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.download_button(
            "📥 Export Household Data (JSON)",
            data=json.dumps(st.session_state.hh_records, indent=4),
            file_name="household_survey_records.json",
            mime="application/json",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "📥 Export Governance Data (JSON)",
            data=json.dumps(st.session_state.gov_records, indent=4),
            file_name="governance_scorecards.json",
            mime="application/json",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            "📥 Export PERI Evaluations (JSON)",
            data=json.dumps(st.session_state.windshield_records, indent=4),
            file_name="peri_evaluations.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### ⚙️ Persistence Maintenance & Storage Reset")
    if st.button("⚠️ Clear All Persistent Field Records"):
        st.session_state.hh_records = []
        st.session_state.gov_records = []
        st.session_state.qual_records = []
        st.session_state.windshield_records = []
        st.session_state.diag_records = []
        save_session_to_disk()
        st.warning("All persistent records cleared successfully.")
        st.rerun()
