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

                # Research Table Construction for All Master Survey Questions
                tables_data = []

                # Module 1: Survey Metadata & Demographics
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

                # Module 2: Adult Profiling & Screening
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

                # Module 3: Socio-Economic & Domestic Assets
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

                # Module 4: Food Insecurity
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

                # Module 5: Housing & WASH
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

                # Module 6: Morbidity & Chronic Care
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

                # Module 7: Health Seeking & YAKAP
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
            st.info(
                "How does the Barangay Council prioritize health within the"
                " Annual Investment Plan (AIP)? What specific percentage of"
                " local revenue is earmarked for healthcare operations?"
            )
            st.caption(
                "• What specific health line-items were funded this year vs"
                " last year?\n• How are competing development priorities (e.g.,"
                " roads, infrastructure vs health) negotiated during budget"
                " calls?\n• Is the health budget sufficient to meet actual"
                " community needs? If not, what gets cut?\n• Are discretionary"
                " or emergency contingency funds accessible for unexpected"
                " disease outbreaks?"
            )
            q1_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 1)", key="kii_g_q1"
            )

            st.markdown("**2. Policy Infrastructure & Enforcement**")
            st.info(
                "What local health ordinances passed over the last 3 years"
                " have had the most direct impact on community health, and what"
                " are the key enforcement hurdles?"
            )
            st.caption(
                "• Which specific ordinances (e.g., Sanitation, Dengue,"
                " Anti-Smoking, WASH, Rabies Control) are actively enforced?\n•"
                " What are the main obstacles to enforcement (e.g., lack of"
                " enforcers, political friction, community resistance, lack of"
                " penalties)?\n• How is the Barangay Health Board involved in"
                " policy drafting and monitoring?"
            )
            q2_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 2)", key="kii_g_q2"
            )

            st.markdown(
                "**3. Supply Chain Integrity & Emergency Procurement**"
            )
            st.info(
                "When the Barangay Health Station experiences stock-outs of"
                " essential medicines, what is the protocol for emergency"
                " procurement through the RHU or LGU?"
            )
            st.caption(
                "• What essential drugs or medical supplies suffer from"
                " frequent stock-outs (e.g., maintenance meds, vaccines,"
                " testing kits)?\n• How long does the emergency requisition"
                " process take from request to delivery?\n• Is there a dedicated"
                " barangay petty cash / buffer fund for urgent medical supply"
                " purchases?"
            )
            q3_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 3)", key="kii_g_q3"
            )

            st.markdown("**4. Health Inequity & Disadvantaged Populations**")
            st.info(
                "In your view, which specific Purok or sub-population in this"
                " barangay suffers from the most severe health disadvantages,"
                " and why?"
            )
            st.caption(
                "• What drive these disparities (e.g., geographical isolation,"
                " informal settler status, lack of clean water, poverty,"
                " transport barriers)?\n• What targeted health programs or"
                " budget allocations are specifically directed at these"
                " vulnerable groups?\n• How are PWDs, senior citizens, and"
                " malnourished children tracked and prioritized?"
            )
            q4_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 4)", key="kii_g_q4"
            )

            st.markdown("**5. Strategic Governance Synthesis & Vision**")
            st.info(
                "What single administrative or policy change at the Municipal /"
                " LGU level would most dramatically improve health governance"
                " in this barangay?"
            )
            st.caption(
                "• What support is most urgently needed from the Municipal"
                " Health Office (MHO) or Provincial Health Office (PHO)?\n• How"
                " can inter-local health zone cooperation or RHU-Barangay"
                " coordination be strengthened?"
            )
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
        st.caption(
            "**Objective:** Uncover operational bottlenecks, clinical"
            " workload realities, supply deficits, emergency referral"
            " breakdowns, and treatment adherence barriers."
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
            years_service = c2.number_input(
                "Years of Service in Barangay", 0, 50, 5
            )

            c1, c2 = st.columns(2)
            consent = c1.radio(
                "Informed Consent Signed?", ["Yes", "No"], horizontal=True
            )
            audio_rec = c2.radio(
                "Audio Recorded?", ["Yes", "No"], horizontal=True
            )

            st.markdown("---")
            st.markdown(
                "#### 🗣️ Qualitative Interview Domains & Probing Prompts"
            )

            st.markdown("**1. Clinical Workload & Essential Supply Deficits**")
            st.info(
                "What are the top three health conditions you encounter daily"
                " among residents, and what medical supplies do you routinely"
                " lack to address them?"
            )
            st.caption(
                "• Which specific drugs, equipment, or diagnostic reagents are"
                " routinely missing at the BHS (e.g., BP apparatus, glucometer"
                " strips, prenatal vitamins, antibiotics)?\n• How do you manage"
                " patient care when essential supplies are unavailable?\n• What"
                " is the average daily patient load per frontline worker, and"
                " how does it impact care quality?"
            )
            q1_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 1)", key="kii_f_q1"
            )

            st.markdown(
                "**2. Emergency Referral Pathway & Pipeline Breakdown**"
            )
            st.info(
                "Walk us through a critical patient emergency in a remote"
                " Purok. What breaks down in the transportation and referral"
                " pipeline to the RHU or Provincial Hospital?"
            )
            st.caption(
                "• Is a functional ambulance or barangay patrol vehicle"
                " available 24/7? Who pays for fuel and driver honoraria"
                " during emergencies?\n• What communication challenges exist"
                " between BHS workers and the RHU/hospital during pre-referral"
                " transfers?\n• How are financial barriers to emergency"
                " transport handled for indigent patients?"
            )
            q2_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 2)", key="kii_f_q2"
            )

            st.markdown("**3. Non-Medical Treatment Adherence Barriers**")
            st.info(
                "How frequently do patients fail to adhere to chronic treatment"
                " (e.g., TB-DOTS, hypertension, diabetes) because they cannot"
                " afford food or transport fare?"
            )
            st.caption(
                "• What percentage of chronic disease patients drop out or"
                " skip medications due to poverty or inability to pay fare to"
                " RHU?\n• How do frontline workers perform home visits or"
                " follow-ups for non-compliant patients?\n• Are there"
                " supplementary food or transport assistance programs"
                " available for patients on long-term treatment?"
            )
            q3_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 3)", key="kii_f_q3"
            )

            st.markdown("**4. Systemic Worker Bottlenecks & Capacity Needs**")
            st.info(
                "What structural or personal challenges (e.g., delayed"
                " honoraria, lack of training, personal safety, excessive"
                " reporting) affect your daily performance and morale?"
            )
            st.caption(
                "• Are BHW/BNS honoraria paid regularly and on time? If"
                " delayed, by how many months?\n• What specific clinical,"
                " record-keeping, or emergency management training do you feel"
                " you lack?\n• How adequate are the BHS facilities"
                " (electricity, clean water, privacy, waste management)?"
            )
            q4_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 4)", key="kii_f_q4"
            )

            if st.form_submit_button("💾 Save TOOL 3.2 Interview Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.2: KII — Frontline Personnel",
                    "Respondent": resp_name,
                    "Role": role,
                    "BHS": bhs_name,
                    "Date_Time": date_time,
                    "Interviewer": interviewer,
                    "Years_Service": years_service,
                    "Consent": consent,
                    "Audio": audio_rec,
                    "D1_SupplyDeficits": q1_notes,
                    "D2_ReferralBreakdown": q2_notes,
                    "D3_AdherenceBarriers": q3_notes,
                    "D4_WorkerBottlenecks": q4_notes,
                })
                save_session_to_disk()
                st.success(
                    "TOOL 3.2 KII Frontline Record Saved Successfully!"
                )

    elif (
        tool_choice
        == "TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS"
    ):
        st.markdown(
            "### 👥 TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY"
            " MEMBERS"
        )
        st.caption(
            "**Target Respondents / Participants:** 6–10 Community"
            " Representatives (Mothers, Senior Citizens, Informal Settlers,"
            " PWDs, Youth Leaders)"
        )
        st.caption(
            "**Objective:** Capture community healthcare-seeking behavior,"
            " financial hardship, catastrophic expenses, provider interaction"
            " quality, and grassroots priorities."
        )

        with st.expander("📜 GROUND RULES FOR FACILITATOR", expanded=True):
            st.markdown("""
            1. Welcome participants, explain session purpose, and ensure all participants sign the informed consent form.
            2. Emphasize confidentiality: *'There are no right or wrong answers. What is shared here stays in this room.'*
            3. Encourage equal participation; ensure vocal participants do not dominate and quiet members are gently invited to speak.
            4. Maintain a neutral, non-judgmental tone throughout.
            """)

        with st.form("fgd_community_form"):
            st.markdown(
                "#### 📋 Session Administrative & Group Composition Metadata"
            )
            c1, c2 = st.columns(2)
            brgy_loc = c1.text_input("Barangay / Location")
            grp_comp = c2.multiselect(
                "Group Composition",
                ["Mothers", "Seniors", "PWDs", "Mixed"],
                default=["Mothers"],
            )

            c1, c2, c3, c4 = st.columns(4)
            date_time = c1.text_input("Date & Time", "09 / 07 / 2026 | 02:00 PM")
            tot_parts = c2.number_input("Total Participants", 1, 20, 8)
            male_cnt = c3.number_input("Male Count", 0, 20, 2)
            female_cnt = c4.number_input("Female Count", 0, 20, 6)

            c1, c2 = st.columns(2)
            moderator = c1.text_input("Moderator / Facilitator Name")
            note_taker = c2.text_input("Note-Taker / Observer Name")

            c1, c2 = st.columns(2)
            consent = c1.radio(
                "Informed Consent Granted by All?", ["Yes", "No"], horizontal=True
            )
            audio_rec = c2.radio(
                "Audio Recorded?", ["Yes", "No"], horizontal=True
            )

            st.markdown("---")
            st.markdown(
                "#### 🗣️ FGD Discussion Domains & Probing Prompts"
            )

            st.markdown("**1. Health Seeking Decision Dynamics**")
            st.info(
                "When someone in your family falls sick, how do you decide"
                " whether to go to the BHS, RHU, private clinic, or traditional"
                " healer (albularyo)?"
            )
            st.caption(
                "• What are the main deciding factors (e.g., travel cost,"
                " distance, waiting time, availability of doctor, trust,"
                " emergency severity)?\n• Who in the household makes the final"
                " decision regarding medical treatment?\n• Under what"
                " circumstances do residents bypass the BHS and go straight to"
                " hospital or private clinics?"
            )
            q1_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 1)", key="fgd_q1"
            )

            st.markdown("**2. Catastrophic Healthcare Expenses & Coping**")
            st.info(
                "Have you ever been forced to choose between buying prescribed"
                " medicines/paying transport fare and purchasing food for your"
                " family? How did you manage?"
            )
            st.caption(
                "• How do families cope with sudden medical expenses (e.g.,"
                " selling livestock/possessions, taking high-interest loans,"
                " seeking political favors)?\n• Are PhilHealth, MAIP, or local"
                " medical assistance programs accessible to informal settlers"
                " and poor residents?\n• Have medical expenses ever forced a"
                " child out of school or led to severe debt?"
            )
            q2_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 2)", key="fgd_q2"
            )

            st.markdown(
                "**3. Provider-Patient Interaction & Quality Perception**"
            )
            st.info(
                "How do you feel treated when visiting public health facilities"
                " (BHS vs RHU)? Do you feel respected, listened to, and fully"
                " informed about your treatment plan?"
            )
            st.caption(
                "• Have you experienced long waiting times, harsh treatment,"
                " or lack of privacy during medical consultations?\n• Do"
                " facility operating hours accommodate working residents and"
                " agricultural laborers?\n• Do health workers explain"
                " medication instructions clearly in the local dialect?"
            )
            q3_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 3)", key="fgd_q3"
            )

            st.markdown("**4. Community Priorities & Grassroots Solutions**")
            st.info(
                "If your community could fix ONE major health problem in this"
                " barangay today, what should it be and how should local"
                " leaders solve it?"
            )
            st.caption(
                "• What essential health service is most urgently missing in"
                " your barangay?\n• What concrete message or request do you"
                " want to convey directly to the Mayor and Barangay Captain"
                " regarding health services?"
            )
            q4_notes = st.text_area(
                "Qualitative Notes / Key Quotations (Domain 4)", key="fgd_q4"
            )

            if st.form_submit_button("💾 Save TOOL 3.3 FGD Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.3: FGD — Community Members",
                    "Barangay": brgy_loc,
                    "Group_Composition": grp_comp,
                    "Date_Time": date_time,
                    "Total_Participants": tot_parts,
                    "Male": male_cnt,
                    "Female": female_cnt,
                    "Moderator": moderator,
                    "Note_Taker": note_taker,
                    "Consent": consent,
                    "Audio": audio_rec,
                    "D1_DecisionDynamics": q1_notes,
                    "D2_CatastrophicExpenses": q2_notes,
                    "D3_ProviderInteraction": q3_notes,
                    "D4_CommunityPriorities": q4_notes,
                })
                save_session_to_disk()
                st.success("TOOL 3.3 FGD Record Saved Successfully!")

    st.markdown("---")
    st.markdown("### 📂 Review Submitted Qualitative Records")
    if len(st.session_state.qual_records) == 0:
        st.info("No qualitative records logged yet.")
    else:
        q_options = [
            f"[{i+1}] {r.get('Tool', 'Qual Note')} -"
            f" {r.get('Barangay', r.get('BHS', 'Location N/A'))}"
            for i, r in enumerate(st.session_state.qual_records)
        ]
        sel_q_idx = st.selectbox(
            "Select Record to Inspect / Delete",
            range(len(q_options)),
            format_func=lambda x: q_options[x],
        )
        q_rec = st.session_state.qual_records[sel_q_idx]

        st.json(q_rec)
        if st.button("🗑️ Delete This Qualitative Record", key="del_qual"):
            st.session_state.qual_records.pop(sel_q_idx)
            save_session_to_disk()
            st.success("Qualitative record deleted!")
            st.rerun()

# MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader(
        "Phase 4: Separated & Expanded Environmental Observation Matrices &"
        " PERI Index Manual"
    )

    p4_tab1, p4_tab2, p4_tab3 = st.tabs([
        "📋 Field Survey Assessment Matrix",
        "📖 Comprehensive Result Interpretation & Manual",
        "📂 Review & Delete Saved Field Assessments",
    ])

    with p4_tab1:
        with st.form("phase4_expanded_observation_form"):
            st.markdown("### 📌 Field Survey Metadata")
            c1, c2, c3 = st.columns(3)
            purok_eval = c1.selectbox(
                "Target Purok Evaluated", [f"Purok {i}" for i in range(1, 8)]
            )
            eval_date = c2.date_input("Evaluation Date")
            evaluator_name = c3.text_input("Lead Evaluator", "Field Inspector")

            def render_rating(
                col1, col2, col3, label, choices, default_idx=0
            ):
                rating = col2.radio(
                    label, choices, index=default_idx, key=f"r_{label}"
                )
                notes = col3.text_input(
                    "Hotspot / Landmark Notes", key=f"n_{label}"
                )
                score_val = (
                    1.0 if "1" in rating else (2.0 if "2" in rating else 3.0)
                )
                return score_val, rating, notes

            # DOMAIN 1
            st.markdown(
                "<div class='peri-domain-header'>Domain 1: Sanitation & Waste"
                " Management Assessment</div>",
                unsafe_allow_html=True,
            )
            d1_scores = []
            d1_data = {}

            d1_params = [
                (
                    "1.1 Uncollected Household Solid Waste",
                    (
                        "Presence of uncollected trash piles, scattered"
                        " plastic, household waste heaps on road shoulders or"
                        " vacant lots."
                    ),
                    ["Clean (1)", "Moderate (2)", "Severe Risk (3)"],
                ),
                (
                    "1.2 Open Drainage & Canal Integrity",
                    (
                        "Condition of roadside canals: clogged with refuse,"
                        " unpaved ditching, dark stagnant greywater, or"
                        " uncovered open channels."
                    ),
                    ["Adequate (1)", "Substandard (2)", "Hazardous (3)"],
                ),
                (
                    "1.3 Stagnant Water & Pooling",
                    (
                        "Pools of standing water in road depressions, unpaved"
                        " alleys, or tires/containers holding water >48 hrs"
                        " (mosquito risk)."
                    ),
                    ["Low Risk (1)", "Moderate (2)", "Severe Risk (3)"],
                ),
                (
                    "1.4 Stray & Unattended Animals",
                    (
                        "Free-roaming dogs, cats, or livestock (pigs/goats)"
                        " scavenging around uncontained waste or public"
                        " pathways."
                    ),
                    ["Controlled (1)", "Moderate (2)", "Uncontrolled (3)"],
                ),
                (
                    "1.5 Material Recovery & Garbage Hubs",
                    (
                        "Condition of Purok MRF or communal collection points:"
                        " overflowing bins, lack of waste segregation, lack of"
                        " covers."
                    ),
                    [
                        "Clean / Segregated (1)",
                        "Overflowing (2)",
                        "Dilapidated / None (3)",
                    ],
                ),
                (
                    "1.6 Open Waste Burning (Siga)",
                    (
                        "Visual evidence or smell of open garbage/plastic/leaf"
                        " burning in backyards, vacant plots, or road edges."
                    ),
                    ["Absent (1)", "Occasional (2)", "Frequent/Severe (3)"],
                ),
                (
                    "1.7 Odor & Airborne Emissions",
                    (
                        "Pungent or offensive odor emanating from decomposed"
                        " waste, open sewage, or livestock pens near"
                        " residential homes."
                    ),
                    [
                        "Odor-Free (1)",
                        "Moderate Odor (2)",
                        "Severe / Noxious (3)",
                    ],
                ),
                (
                    "1.8 Fecal Contamination Exposure",
                    (
                        "Visible animal feces or human defecation marks along"
                        " walkways, drainage channels, or play areas."
                    ),
                    ["None Visible (1)", "Isolated (2)", "Widespread Risk (3)"],
                ),
                (
                    "1.9 Commercial / Market Waste",
                    (
                        "Accumulation of rotting produce, fish water, or"
                        " commercial trash around sari-sari stores, bakeries,"
                        " or talipapa."
                    ),
                    ["Sanitary (1)", "Substandard (2)", "Severe Risk (3)"],
                ),
            ]

            for param, indicator, options in d1_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(
                    c1, c2, c3, param, options
                )
                d1_scores.append(s_val)
                d1_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 2
            st.markdown(
                "<div class='peri-domain-header'>Domain 2: Food Environment &"
                " Nutritional Accessibility Assessment</div>",
                unsafe_allow_html=True,
            )
            d2_scores = []
            d2_data = {}
            d2_params = [
                (
                    "2.1 Fresh Produce Access (Talipapa / Markets)",
                    (
                        "Presence of permanent or satellite fresh fruit,"
                        " vegetable, and fresh protein (fish/meat) markets"
                        " within 300m walking distance."
                    ),
                    ["High Access (1)", "Limited Access (2)", "Food Desert (3)"],
                ),
                (
                    "2.2 Sari-Sari Store Food Profile",
                    (
                        "Dominance of ultra-processed salty snacks, sugary"
                        " carbonated beverages, and instant noodles displayed"
                        " prominently at eye level."
                    ),
                    [
                        "Balanced / Healthy (1)",
                        "Junk-Dominant (2)",
                        "Unhealthy Swamp (3)",
                    ],
                ),
                (
                    "2.3 Produce Quality & Freshness",
                    (
                        "Physical condition of available fruits/vegetables at"
                        " local outlets: fresh, crisp vs. wilted, decaying, or"
                        " insect-damaged."
                    ),
                    [
                        "High Quality (1)",
                        "Mixed Quality (2)",
                        "Poor / Spoiled (3)",
                    ],
                ),
                (
                    "2.4 Street Food Vending Hygiene",
                    (
                        "Prepared street food stalls: use of food covers, glass"
                        " displays, clean water for utensil washing,"
                        " hairnets/gloves, fly presence."
                    ),
                    [
                        "Sanitary (1)",
                        "Substandard (2)",
                        "Unsanitary / High Risk (3)",
                    ],
                ),
                (
                    "2.5 Child-Targeted Marketing",
                    (
                        "Prominent advertising banners or eye-level store"
                        " displays targeting school children with sugary drinks,"
                        " candies, and sodium snacks."
                    ),
                    [
                        "Low Exposure (1)",
                        "Moderate (2)",
                        "High / Aggressive (3)",
                    ],
                ),
                (
                    "2.6 Tobacco & Alcohol Visibility",
                    (
                        "Prominent display and sale of cigarettes/e-cigarettes"
                        " and alcoholic beverages near youth gathering points"
                        " or school zones."
                    ),
                    [
                        "Restricted / Far (1)",
                        "Moderate (2)",
                        "Highly Visible (3)",
                    ],
                ),
                (
                    "2.7 Safe Drinking Water Refilling Outlets",
                    (
                        "Availability and physical sanitary condition of"
                        " commercial water refilling stations or public potable"
                        " water taps in the Purok."
                    ),
                    [
                        "Accessible & Clean (1)",
                        "Scarcely Available (2)",
                        "Unsightly / Risky (3)",
                    ],
                ),
            ]

            for param, indicator, options in d2_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(
                    c1, c2, c3, param, options
                )
                d2_scores.append(s_val)
                d2_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 3
            st.markdown(
                "<div class='peri-domain-header'>Domain 3: Built Environment,"
                " Housing Quality & Infrastructure</div>",
                unsafe_allow_html=True,
            )
            d3_scores = []
            d3_data = {}
            d3_params = [
                (
                    "3.1 Housing Structural Integrity",
                    (
                        "Proportion of concrete/permanent housing vs."
                        " makeshift, tarpaulin, light bamboo, or deteriorated"
                        " wood structures."
                    ),
                    [
                        "Mostly Concrete (1)",
                        "Mixed Structural (2)",
                        "Predominantly Makeshift (3)",
                    ],
                ),
                (
                    "3.2 Pedestrian Walkways & Sidewalks",
                    (
                        "Availability of paved, unblocked sidewalks or"
                        " footpaths separated from vehicle traffic vs."
                        " pedestrians walking on main road shoulders."
                    ),
                    [
                        "Safe / Paved (1)",
                        "Partial / Blocked (2)",
                        "Absent / Dangerous (3)",
                    ],
                ),
                (
                    "3.3 Street Lighting & Night Safety",
                    (
                        "Operational street lights every 30-50m along primary"
                        " pathways to ensure safe pedestrian travel at night."
                    ),
                    [
                        "Well Lit (1)",
                        "Partially Lit (2)",
                        "Dark / Hazardous (3)",
                    ],
                ),
                (
                    "3.4 Green Spaces & Recreational Areas",
                    (
                        "Access to maintained parks, open community spaces,"
                        " trees, or sports grounds for physical activity."
                    ),
                    [
                        "Abundant (1)",
                        "Limited (2)",
                        "None / Concrete Desert (3)",
                    ],
                ),
                (
                    "3.5 Electrical Wiring & Fire Hazard",
                    (
                        "Condition of overhead power lines: organized wiring vs."
                        " tangled 'spider webs', illegal connections, or fire"
                        " hazard exposures."
                    ),
                    [
                        "Safe / Neat (1)",
                        "Moderate Tangle (2)",
                        "Hazardous 'Spiderweb' (3)",
                    ],
                ),
            ]

            for param, indicator, options in d3_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(
                    c1, c2, c3, param, options
                )
                d3_scores.append(s_val)
                d3_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 4
            st.markdown(
                "<div class='peri-domain-header'>Domain 4: Health"
                " Infrastructure Access & Service Physical Accessibility</div>",
                unsafe_allow_html=True,
            )
            d4_scores = []
            d4_data = {}
            d4_params = [
                (
                    "4.1 Physical Proximity to BHS / Barangay Health Center",
                    (
                        "Distance and walking time from Purok center to the"
                        " nearest functional Barangay Health Station."
                    ),
                    ["<10 mins (1)", "10-25 mins (2)", ">25 mins / Far (3)"],
                ),
                (
                    "4.2 Public Transport Availability to Health Facilities",
                    (
                        "Frequency and cost of public transport (tricycles,"
                        " jeepneys) connecting Purok residents to RHU or"
                        " Hospital."
                    ),
                    [
                        "Frequent & Low Cost (1)",
                        "Moderate Cost/Wait (2)",
                        "Rare / Expensive (3)",
                    ],
                ),
                (
                    "4.3 Facility Signage & Health Information Boards",
                    (
                        "Visibility of health advisories, BHS operating hours,"
                        " and emergency referral phone numbers posted in"
                        " public areas."
                    ),
                    [
                        "Clear & Updated (1)",
                        "Faded / Partial (2)",
                        "Absent (3)",
                    ],
                ),
            ]

            for param, indicator, options in d4_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(
                    c1, c2, c3, param, options
                )
                d4_scores.append(s_val)
                d4_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 5
            st.markdown(
                "<div class='peri-domain-header'>Domain 5: Disaster Preparedness"
                " & Climate Resilience Vector</div>",
                unsafe_allow_html=True,
            )
            d5_scores = []
            d5_data = {}
            d5_params = [
                (
                    "5.1 Flood & Landslide Vulnerability Exposure",
                    (
                        "Proximity of residential clusters to riverbanks,"
                        " low-lying flood basins, or steep erosion-prone slopes."
                    ),
                    ["Low Exposure (1)", "Moderate (2)", "High Hazard (3)"],
                ),
                (
                    "5.2 Evacuation Center Accessibility & Route Signage",
                    (
                        "Clear directional markers pointing to safe designated"
                        " evacuation assembly points."
                    ),
                    [
                        "Marked & Clear (1)",
                        "Unmarked / Far (2)",
                        "No Signage / Inaccessible (3)",
                    ],
                ),
            ]

            for param, indicator, options in d5_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(
                    c1, c2, c3, param, options
                )
                d5_scores.append(s_val)
                d5_data[param] = {"Rating": r_txt, "Notes": n_txt}

            # DOMAIN 6
            st.markdown(
                "<div class='peri-domain-header'>Domain 6: Vector & Zoonotic"
                " Disease Exposure Risks</div>",
                unsafe_allow_html=True,
            )
            d6_scores = []
            d6_data = {}
            d6_params = [
                (
                    "6.1 Mosquito Breeding Site Proliferation",
                    (
                        "Density of uncontained water drums, discarded tires,"
                        " coconut shells, or clogged gutters holding stagnant"
                        " water."
                    ),
                    ["Minimal (1)", "Moderate (2)", "Severe Density (3)"],
                ),
                (
                    "6.2 Rodent & Pest Harbage Areas",
                    (
                        "Presence of dense overgrown vegetation, uncollected"
                        " timber/scrap piles, or open grain storage harboring"
                        " rodents."
                    ),
                    ["Low (1)", "Moderate (2)", "High Infestation (3)"],
                ),
            ]

            for param, indicator, options in d6_params:
                c1, c2, c3 = st.columns([2, 1.2, 1.8])
                c1.markdown(f"**{param}**\n\n*{indicator}*")
                s_val, r_txt, n_txt = render_rating(
                    c1, c2, c3, param, options
                )
                d6_scores.append(s_val)
                d6_data[param] = {"Rating": r_txt, "Notes": n_txt}

            if st.form_submit_button(
                "Submit & Save Phase 4 Expanded PERI Assessment"
            ):
                avg_d1 = float(np.mean(d1_scores))
                avg_d2 = float(np.mean(d2_scores))
                avg_d3 = float(np.mean(d3_scores))
                avg_d4 = float(np.mean(d4_scores))
                avg_d5 = float(np.mean(d5_scores))
                avg_d6 = float(np.mean(d6_scores))

                overall_peri = float(
                    np.mean([avg_d1, avg_d2, avg_d3, avg_d4, avg_d5, avg_d6])
                )
                risk_cat = (
                    "CATEGORY C: CRITICAL HIGH RISK (>= 2.30)"
                    if overall_peri >= 2.3
                    else (
                        "CATEGORY B: MODERATE RISK CONCERN (1.50 - 2.29)"
                        if overall_peri >= 1.5
                        else "CATEGORY A: LOW RISK / SANITARY (1.00 - 1.49)"
                    )
                )

                st.session_state.windshield_records.append({
                    "Purok": purok_eval,
                    "Date": str(eval_date),
                    "Evaluator": evaluator_name,
                    "DS1_Sanitation": avg_d1,
                    "DS2_Food": avg_d2,
                    "DS3_BuiltEnv": avg_d3,
                    "DS4_HealthInfra": avg_d4,
                    "DS5_DRR": avg_d5,
                    "DS6_Vector": avg_d6,
                    "PERI_Index": overall_peri,
                    "Category": risk_cat,
                    "D1_Details": d1_data,
                    "D2_Details": d2_data,
                    "D3_Details": d3_data,
                    "D4_Details": d4_data,
                    "D5_Details": d5_data,
                    "D6_Details": d6_data,
                })
                save_session_to_disk()
                st.success(
                    f"Assessment Saved for {purok_eval}! Overall PERI Index:"
                    f" {overall_peri:.2f} — {risk_cat}"
                )

    with p4_tab2:
        st.markdown("### 📖 PERI Score Interpretation Manual & Action Thresholds")
        st.markdown("""
        #### 📊 Rating Scale & Mathematical Index Construction
        * **1.00 – 1.49 (Category A: Low Environmental Risk / Sanitary):** Environment is generally well-maintained. Standard preventive monitoring recommended.
        * **1.50 – 2.29 (Category B: Moderate Environmental Risk / Concern):** Noticeable environmental degradation or infrastructure bottlenecks. Targeted sanitation and WASH interventions required.
        * **2.30 – 3.00 (Category C: Critical High Environmental Risk):** Severe environmental hazards, uncontrolled vector breeding, or flood vulnerability. Immediate inter-agency remediation mandated.
        """)

    with p4_tab3:
        st.markdown("### 📂 Saved Field Observations")
        if len(st.session_state.windshield_records) == 0:
            st.info("No windshield assessment records stored.")
        else:
            for i, p_rec in enumerate(st.session_state.windshield_records):
                with st.expander(
                    f"📌 [{p_rec.get('Purok')}] - Evaluation Date:"
                    f" {p_rec.get('Date')} (PERI Index:"
                    f" {p_rec.get('PERI_Index', 0):.2f})"
                ):
                    st.write(f"**Evaluator:** {p_rec.get('Evaluator')}")
                    st.write(
                        f"**Category Status:** `{p_rec.get('Category')}`"
                    )
                    st.json({
                        "Sanitation (D1)": p_rec.get("DS1_Sanitation"),
                        "Food Environment (D2)": p_rec.get("DS2_Food"),
                        "Built Environment (D3)": p_rec.get("DS3_BuiltEnv"),
                        "Health Infra (D4)": p_rec.get("DS4_HealthInfra"),
                        "DRR & Climate (D5)": p_rec.get("DS5_DRR"),
                        "Vector Exposure (D6)": p_rec.get("DS6_Vector"),
                    })
                    if st.button("🗑️ Delete Assessment", key=f"del_peri_{i}"):
                        st.session_state.windshield_records.pop(i)
                        save_session_to_disk()
                        st.success("Assessment deleted!")
                        st.rerun()

# MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader(
        "Phase 5: Integrated Spatial, Epidemiological & Research Analytics"
        " Engine"
    )

    hh_data = st.session_state.hh_records
    peri_data = st.session_state.windshield_records

    if len(hh_data) == 0:
        st.info("No household survey data available for Phase 5 analytics.")
    else:
        st.markdown(
            "#### 📊 Comprehensive Statistical Breakdown of All Asked Survey"
            " Questions"
        )

        total_hhs = len(hh_data)
        all_adults = [a for hh in hh_data for a in hh.get("Adults", [])]
        all_children = [c for hh in hh_data for c in hh.get("Children", [])]

        st.markdown(
            f"**Total Sample Size:** $N = {total_hhs}$ Households | $n ="
            f" {len(all_adults)}$ Adults Profiled | $n = {len(all_children)}$"
            " Children Profiled"
        )

        res_tab1, res_tab2, res_tab3 = st.tabs([
            "📋 Full Research Frequency & Percentage Tables (All Items)",
            "📊 Environmental PERI Correlations",
            "🗺️ Spatial Cluster & Vulnerability Mapping",
        ])

        with res_tab1:
            st.markdown(
                "##### Research Analytics: Complete Itemized Frequency ($n$) &"
                " Percentage ($\%$) Table"
            )

            # Build full research table
            all_tables = []

            # 1. Respondent & Dialect
            all_tables.append(
                generate_research_table(
                    [r.get("Respondent_Role") for r in hh_data],
                    total_hhs,
                    "Demographics: Respondent Role",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Dialect") for r in hh_data],
                    total_hhs,
                    "Demographics: Primary Spoken Dialect",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Religion") for r in hh_data],
                    total_hhs,
                    "Demographics: Household Religion",
                )
            )

            # 2. Income & Economic Stability
            all_tables.append(
                generate_research_table(
                    [r.get("Income") for r in hh_data],
                    total_hhs,
                    "Economics: Monthly Family Income Quintile",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Livelihood") for r in hh_data],
                    total_hhs,
                    "Economics: Primary Livelihood Source",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Emergency_5k") for r in hh_data],
                    total_hhs,
                    "Economics: ₱5k Emergency Cushion Access",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Four_Ps") for r in hh_data],
                    total_hhs,
                    "Economics: Active 4Ps Beneficiary",
                )
            )

            # 3. Food Security
            all_tables.append(
                generate_research_table(
                    [r.get("Food_Skip") for r in hh_data],
                    total_hhs,
                    "Food Security: Skipped Meals / Reduced Portion",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Food_Worry") for r in hh_data],
                    total_hhs,
                    "Food Security: Worried About Food Outage",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Food_FullDay") for r in hh_data],
                    total_hhs,
                    "Food Security: Full Day Without Food",
                )
            )

            # 4. Housing & Environmental WASH
            all_tables.append(
                generate_research_table(
                    [r.get("Tenure") for r in hh_data],
                    total_hhs,
                    "WASH & Housing: Housing Tenurial Status",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("House_Type") for r in hh_data],
                    total_hhs,
                    "WASH & Housing: Housing Structure Type",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Cook_Fuel") for r in hh_data],
                    total_hhs,
                    "WASH & Housing: Indoor Cooking Fuel Risk",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Water") for r in hh_data],
                    total_hhs,
                    "WASH & Housing: Drinking Water Source Level",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Sanitation") for r in hh_data],
                    total_hhs,
                    "WASH & Housing: Toilet / Sanitation Facility",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Solid_Disposal") for r in hh_data],
                    total_hhs,
                    "WASH & Housing: Solid Waste Disposal Method",
                )
            )

            # 5. Morbidity & Compliance
            all_tables.append(
                generate_research_table(
                    [r.get("Hypertension_Status") for r in hh_data],
                    total_hhs,
                    "Morbidity: Hypertension Status & Med Adherence",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Diabetes_Status") for r in hh_data],
                    total_hhs,
                    "Morbidity: Diabetes Status & Med Adherence",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("TB_Status") for r in hh_data],
                    total_hhs,
                    "Morbidity: Tuberculosis (TB-DOTS) History",
                )
            )

            # 6. PhilHealth YAKAP
            all_tables.append(
                generate_research_table(
                    [r.get("Yakap") for r in hh_data],
                    total_hhs,
                    "Health Systems: PhilHealth YAKAP Registration",
                )
            )
            all_tables.append(
                generate_research_table(
                    [r.get("Yakap_Availed") for r in hh_data],
                    total_hhs,
                    "Health Systems: Availed First Patient Encounter (FPE)",
                )
            )

            full_res_table = pd.concat(all_tables, ignore_index=True)
            st.dataframe(full_res_table, use_container_width=True)

            # Download CSV option for researchers
            csv_data = full_res_table.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Publication-Ready Research Analytics (CSV)",
                csv_data,
                "Master_Household_Survey_Research_Analytics.csv",
                "text/csv",
            )

        with res_tab2:
            st.markdown(
                "##### Environmental Risk Index (PERI) vs Household Morbidity"
            )
            if len(peri_data) > 0:
                p_df = pd.DataFrame(peri_data)
                st.dataframe(p_df, use_container_width=True)
            else:
                st.info(
                    "No Phase 4 PERI evaluation data available for correlation."
                )

        with res_tab3:
            st.markdown(
                "##### Spatial Vulnerability & High-Risk Cluster Analysis"
            )
            df_map = pd.DataFrame(hh_data)
            st.map(df_map[["Lat", "Lon"]])

# MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS & ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("Phase 6: Community Diagnosis & COPAR Action Planning Portal")

    with st.form("phase6_action_form"):
        st.markdown("### 🎯 Formulate Priority Community Health Action Plan")
        c1, c2 = st.columns(2)
        target_brgy = c1.text_input("Barangay Target Name")
        plan_date = c2.date_input("Planning Date")

        prio_problem = st.text_input(
            "Priority Diagnosed Health / Environmental Problem",
            "High Adult Hypertensive Risk (32.4%) & Unsafe Drinking Water",
        )

        c1, c2 = st.columns(2)
        target_pop = c1.text_input(
            "Target Population / Beneficiaries", "Adults >40 yrs & Flood HHs"
        )
        lead_dept = c2.text_input(
            "Lead Implementing Agency / Committee", "BHB & BHS Midwife/BHWs"
        )

        st.markdown("---")
        st.markdown("#### 🛠️ COPAR Strategic Intervention Matrix")
        strat_obj = st.text_area(
            "1. Strategic Objectives & Key Performance Indicators (KPIs):"
        )
        activities = st.text_area(
            "2. Concrete Community Mobilization Activities:"
        )

        c1, c2 = st.columns(2)
        budget_req = c1.number_input(
            "Required Budget Allocation (₱)", 0, 1000000, 25000
        )
        timeframe = c2.text_input("Implementation Timeframe", "3 Months (Q4)")

        if st.form_submit_button("💾 Save & Finalize Action Plan"):
            st.session_state.diag_records.append({
                "Barangay": target_brgy,
                "Date": str(plan_date),
                "Problem": prio_problem,
                "Target": target_pop,
                "Lead": lead_dept,
                "Objectives": strat_obj,
                "Activities": activities,
                "Budget": budget_req,
                "Timeframe": timeframe,
            })
            save_session_to_disk()
            st.success("Community Action Plan Saved Permanently!")

    st.markdown("---")
    st.markdown("### 📂 Saved Community Action Plans")
    if len(st.session_state.diag_records) == 0:
        st.info("No action plans created yet.")
    else:
        for i, plan in enumerate(st.session_state.diag_records):
            with st.expander(
                f"🎯 Plan #{i+1}: {plan.get('Barangay')} -"
                f" {plan.get('Problem')}"
            ):
                st.write(f"**Lead:** {plan.get('Lead')}")
                st.write(f"**Budget:** ₱{plan.get('Budget'):,}")
                st.write(f"**Objectives:** {plan.get('Objectives')}")
                st.write(f"**Activities:** {plan.get('Activities')}")
                if st.button("🗑️ Delete Plan", key=f"del_plan_{i}"):
                    st.session_state.diag_records.pop(i)
                    save_session_to_disk()
                    st.success("Plan deleted!")
                    st.rerun()

# MODULE 8: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Persistent Data Storage & Multi-Format Export Engine")

    st.markdown("### 📊 Current Database Record Counts")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Governance Scorecards", len(st.session_state.gov_records))
    c2.metric("Household Surveys", len(st.session_state.hh_records))
    c3.metric("Qualitative Notes", len(st.session_state.qual_records))
    c4.metric("PERI Windshield", len(st.session_state.windshield_records))
    c5.metric("Action Plans", len(st.session_state.diag_records))

    st.markdown("---")
    st.markdown("### 📥 Download Shared Persistent Data")

    col1, col2 = st.columns(2)
    with col1:
        full_json_str = json.dumps(load_shared_data(), indent=4)
        st.download_button(
            "📥 Download Complete System JSON Backup",
            data=full_json_str,
            file_name="UPManila_Clerks_Portal_Master_Backup.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        if len(st.session_state.hh_records) > 0:
            df_hh_export = pd.DataFrame(st.session_state.hh_records)
            csv_hh = df_hh_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Master Household Survey CSV",
                data=csv_hh,
                file_name="Master_Household_Survey_Records.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No household records available for CSV export.")
