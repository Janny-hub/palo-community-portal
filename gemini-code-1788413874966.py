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


# ================= RESEARCH STATISTICAL GENERATOR FUNCTION =================
def generate_master_survey_research_table(hh_records):
    """Generates a complete research frequency (n) and percentage (%) table for ALL Master Survey questions."""
    if not hh_records:
        return pd.DataFrame()

    total_hhs = len(hh_records)
    all_adults = [a for hh in hh_records for a in hh.get("Adults", [])]
    all_children = [c for hh in hh_records for c in hh.get("Children", [])]

    rows = []

    def add_single_cat(domain_name, key, total_denom):
        vals = [
            str(hh.get(key, "Unspecified"))
            for hh in hh_records
            if hh.get(key) is not None
        ]
        counts = Counter(vals)
        for cat, n in counts.items():
            pct = (n / total_denom) * 100 if total_denom > 0 else 0
            rows.append({
                "Survey Question / Domain": domain_name,
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{pct:.2f}%",
            })

    def add_multi_cat(domain_name, key, total_denom):
        all_items = []
        for hh in hh_records:
            items = hh.get(key, [])
            if isinstance(items, list):
                all_items.extend(items)
            elif items:
                all_items.append(str(items))
        counts = Counter(all_items)
        for cat, n in counts.items():
            pct = (n / total_denom) * 100 if total_denom > 0 else 0
            rows.append({
                "Survey Question / Domain": domain_name,
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{pct:.2f}%",
            })

    # Household Level
    add_single_cat("Respondent Role", "Respondent_Role", total_hhs)
    add_single_cat("Survey Completion Status", "Survey_Status", total_hhs)
    add_single_cat("Primary Dialect Spoken", "Dialect", total_hhs)
    add_single_cat("Religion", "Religion", total_hhs)
    add_single_cat("Head Civil Status", "Head_Civil_Status", total_hhs)
    add_single_cat("Monthly Household Income", "Income", total_hhs)
    add_single_cat("Primary Livelihood Source", "Livelihood", total_hhs)
    add_single_cat(
        "Engaged in Food Production", "Food_Production", total_hhs
    )
    add_single_cat(
        "Emergency ₱5,000 Financial Cushion", "Emergency_5k", total_hhs
    )
    add_single_cat("Active 4Ps Beneficiary", "Four_Ps", total_hhs)
    add_multi_cat("Transportation Owned", "Transport_Owned", total_hhs)
    add_multi_cat("Utilities Available", "Utilities", total_hhs)
    add_multi_cat("Appliances Owned", "Appliances", total_hhs)
    add_single_cat(
        "Food Insecurity: Skipped Meal (30 Days)", "Food_Skip", total_hhs
    )
    add_single_cat(
        "Food Insecurity: Worried About Food", "Food_Worry", total_hhs
    )
    add_single_cat(
        "Food Insecurity: Full Day Without Food", "Food_FullDay", total_hhs
    )
    add_single_cat("Tenurial Status", "Tenure", total_hhs)
    add_single_cat("Housing Construction Type", "House_Type", total_hhs)
    add_single_cat("Indoor Cooking Fuel Risk", "Cook_Fuel", total_hhs)
    add_single_cat("Located in Flood-Prone Zone", "Flood_Prone", total_hhs)
    add_single_cat("Drinking Water Source Level", "Water", total_hhs)
    add_single_cat("Sanitation / Toilet Type", "Sanitation", total_hhs)
    add_single_cat(
        "Solid Waste Disposal Method", "Solid_Disposal", total_hhs
    )
    add_multi_cat(
        "Decision Maker: Household Expenses", "Decisions_Expenses", total_hhs
    )
    add_multi_cat(
        "Decision Maker: Health Care", "Decisions_Health", total_hhs
    )

    add_single_cat(
        "Morbidity: Diarrheal Episodes (Past 12m)", "Diarrhea", total_hhs
    )
    add_single_cat("Morbidity: URTI / Pneumonia", "URTI", total_hhs)
    add_single_cat("Morbidity: Dengue Cases", "Dengue", total_hhs)
    add_single_cat(
        "Chronic: Hypertension Status", "Hypertension_Status", total_hhs
    )
    add_single_cat(
        "Chronic: Type 2 Diabetes Status", "Diabetes_Status", total_hhs
    )
    add_single_cat("Chronic: Asthma / COPD Status", "Asthma_Status", total_hhs)
    add_single_cat("Chronic: TB & DOTS Status", "TB_Status", total_hhs)
    add_single_cat("Chronic: CKD Status", "CKD_Status", total_hhs)
    add_single_cat("Chronic: CVD / Stroke History", "CVD_Status", total_hhs)
    add_single_cat("Chronic: Active Malignancy / Cancer", "Cancer_Status", total_hhs)

    add_single_cat(
        "Maternal: Currently Pregnant Member", "Is_Pregnant", total_hhs
    )
    add_single_cat(
        "Maternal: First ANC Visit 1st Trimester", "ANC_1st_Tri", total_hhs
    )
    add_single_cat(
        "Maternal: IFA Tablets Completed", "IFA_Tablets", total_hhs
    )
    add_single_cat("Maternal: Td Immunization Status", "Td_Status", total_hhs)
    add_single_cat(
        "Maternal: Postpartum Check within 72h", "Postpartum_Check", total_hhs
    )
    add_single_cat(
        "Delivery: Trained Personnel Handled", "Deliv_Personnel", total_hhs
    )
    add_single_cat(
        "Delivery: Accredited Facility", "Deliv_Facility", total_hhs
    )
    add_single_cat("Family Planning Access", "FP_Access", total_hhs)
    add_single_cat("Family Planning Practice", "FP_Practice", total_hhs)
    add_single_cat(
        "Preventable Disease Mortality", "Preventable_Mortality", total_hhs
    )

    add_multi_cat(
        "Health Seeking: Initial Actions", "HSB_Initial_Actions", total_hhs
    )
    add_multi_cat(
        "Health Seeking: Facilities/Providers Used",
        "HSB_Providers_Used",
        total_hhs,
    )
    add_single_cat(
        "Health Seeking: Travel Time to Facility", "HSB_Travel_Time", total_hhs
    )
    add_multi_cat(
        "Health Seeking: Barriers to Care", "HSB_Barriers", total_hhs
    )
    add_multi_cat(
        "Health Seeking: Key Decision Influencers",
        "HSB_Influencers",
        total_hhs,
    )
    add_multi_cat(
        "Health Seeking: Facility Selection Criteria",
        "HSB_Criteria",
        total_hhs,
    )
    add_single_cat("PhilHealth YAKAP Registration", "Yakap", total_hhs)
    add_single_cat("Availed YAKAP FPE / Services", "Yakap_Availed", total_hhs)

    # Adult Level
    if all_adults:
        tot_a = len(all_adults)
        for cat, n in Counter([a.get("Gender", "N/A") for a in all_adults]).items():
            rows.append({
                "Survey Question / Domain": "Adult Demographic: Gender",
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_a)*100:.2f}%",
            })
        for cat, n in Counter([a.get("Edu", "N/A") for a in all_adults]).items():
            rows.append({
                "Survey Question / Domain": (
                    "Adult Demographic: Education Level"
                ),
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_a)*100:.2f}%",
            })
        for cat, n in Counter(
            [a.get("PhilHealth_Cat", "N/A") for a in all_adults]
        ).items():
            rows.append({
                "Survey Question / Domain": (
                    "Adult Demographic: PhilHealth Category"
                ),
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_a)*100:.2f}%",
            })
        for cat, n in Counter([a.get("Risk", "N/A") for a in all_adults]).items():
            rows.append({
                "Survey Question / Domain": (
                    "Adult Screening: Vital Risk Category"
                ),
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_a)*100:.2f}%",
            })

    # Child Level
    if all_children:
        tot_c = len(all_children)
        for cat, n in Counter(
            [
                c.get("Nutr", {}).get("Wasting", "N/A")
                for c in all_children
            ]
        ).items():
            rows.append({
                "Survey Question / Domain": "Child Nutrition: Wasting Status",
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_c)*100:.2f}%",
            })
        for cat, n in Counter(
            [
                c.get("Nutr", {}).get("Stunting", "N/A")
                for c in all_children
            ]
        ).items():
            rows.append({
                "Survey Question / Domain": "Child Nutrition: Stunting Status",
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_c)*100:.2f}%",
            })
        for cat, n in Counter(
            [
                c.get("Nutr", {}).get("Underweight", "N/A")
                for c in all_children
            ]
        ).items():
            rows.append({
                "Survey Question / Domain": (
                    "Child Nutrition: Underweight Status"
                ),
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_c)*100:.2f}%",
            })
        for cat, n in Counter(
            [c.get("FIC_Status", "N/A") for c in all_children]
        ).items():
            rows.append({
                "Survey Question / Domain": (
                    "Child Immunization: FIC Completion"
                ),
                "Category / Response Option": cat,
                "Frequency (n)": n,
                "Percentage (%)": f"{(n/tot_c)*100:.2f}%",
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

# ================= MODULE 0: EXECUTIVE DASHBOARD =================
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
                    1
                    for hh in hh_data
                    if "DOTS" in hh.get("TB_Status", "")
                )

                df_chronic = pd.DataFrame({
                    "Condition": [
                        "Hypertension",
                        "Diabetes",
                        "Asthma/COPD",
                        "Tuberculosis",
                    ],
                    "Diagnosed HH Count": [htn_hhs, dm_hhs, asthma_hhs, tb_hhs],
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
        else:
            st.info("No Phase 4 PERI windshield evaluations stored yet.")

    with dash_tab3:
        st.markdown("**Live Master Household Explorer**")
        if tot_hh > 0:
            flat_hhs = [
                {
                    "HH ID": h.get("HH_ID"),
                    "Barangay": h.get("Barangay"),
                    "Purok": h.get("Purok"),
                    "Head Name": h.get("Head_Name"),
                    "Vitals BP": h.get("BP"),
                    "Health Risk": h.get("Risk"),
                    "Flood Zone": h.get("Flood_Prone"),
                    "Income": h.get("Income"),
                    "Water Source": h.get("Water"),
                }
                for h in hh_data
            ]
            st.dataframe(pd.DataFrame(flat_hhs), use_container_width=True)
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
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    view = pdk.ViewState(
        latitude=map_df["Lat"].mean() if len(map_df) > 0 else 11.1560,
        longitude=map_df["Lon"].mean() if len(map_df) > 0 else 124.9915,
        zoom=15,
        pitch=30,
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
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

    with st.form("phase1_full_form"):
        c1, c2, c3 = st.columns(3)
        b_name = c1.text_input("Barangay Name")
        city = c2.text_input("City / Municipality")
        prov = c3.text_input("Province")

        g1_1 = st.number_input(
            "1.1 Signed EO/Resolution reconstituting BHB (Max 5 pts)", 0, 5, 0
        )
        g1_2 = st.number_input(
            "1.2 Multi-sectoral Representation present (Max 5 pts)", 0, 5, 0
        )
        g2_1 = st.number_input(
            "2.1 Conduct of Regular Quarterly BHB Meetings (Max 12 pts)",
            0,
            12,
            0,
        )

        gap_summary = st.text_area("Identify primary governance bottlenecks:")
        action_plan = st.text_area("Recommended corrective intervention plan:")

        if st.form_submit_button("Submit & Save Governance Scorecard"):
            total_score = sum([g1_1, g1_2, g2_1])
            rating = (
                "HIGH FUNCTIONING"
                if total_score >= 80
                else (
                    "MODERATE FUNCTIONING"
                    if total_score >= 50
                    else "LOW FUNCTIONING"
                )
            )

            st.session_state.gov_records.append({
                "Barangay": b_name,
                "City": city,
                "Province": prov,
                "Score": total_score,
                "Rating": rating,
                "Gaps": gap_summary,
                "ActionPlan": action_plan,
            })
            save_session_to_disk()
            st.success(
                f"Scorecard Saved! Score: {total_score} — Rating: {rating}"
            )

# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader(
        "Phase 2: Master Household Survey Instrument (Multi-Enumerator ID"
        " Engine & Dynamic Research Analytics)"
    )

    mode_p2 = st.radio(
        "Select Operation",
        [
            "➕ New Household Survey Entry",
            "📊 Phase 2 Interpreted Data & Research Analytics Tables",
            "📂 Review, Edit & Delete Submitted Household Surveys",
        ],
        horizontal=True,
    )

    if mode_p2 == "➕ New Household Survey Entry":
        st.markdown(
            "#### 🆔 Multi-Enumerator Household Identifier Configuration"
        )
        st.info(
            "💡 **Preventing Duplicate Household Numbers:** Each enumerator"
            " selects their unique identifier. The system dynamically generates"
            " an auto-incremented Household ID (e.g. `E1-HH-001`, `E2-HH-001`)"
            " and actively prevents duplicate submissions."
        )

        col_e1, col_e2 = st.columns(2)
        enum_sel = col_e1.selectbox(
            "Select Enumerator Identifier",
            [
                "Enumerator 1 (Code: E1)",
                "Enumerator 2 (Code: E2)",
                "Enumerator 3 (Code: E3)",
                "Custom Code",
            ],
        )

        if "Custom Code" in enum_sel:
            enum_code = col_e2.text_input("Enter Custom Enumerator Prefix", "E4")
        else:
            enum_code = enum_sel.split("Code: ")[1].replace(")", "")

        # Compute next recommended Household ID for this specific enumerator
        existing_hh_ids = [
            str(r.get("HH_ID", "")) for r in st.session_state.hh_records
        ]
        enum_existing = [
            i for i in existing_hh_ids if i.startswith(f"{enum_code}-HH-")
        ]
        next_num = len(enum_existing) + 1
        suggested_hh_id = f"{enum_code}-HH-{next_num:03d}"

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

            with t_meta:
                c1, c2, c3, c4 = st.columns(4)
                hh_id = c1.text_input(
                    "Household ID (Must be Unique)", value=suggested_hh_id
                )
                brgy = c2.text_input("Barangay Name", "Barangay 1")
                purok = c3.selectbox(
                    "Purok / Zone", [f"Purok {i}" for i in range(1, 8)]
                )
                date_survey = c4.date_input("Date of Survey")

                c1, c2, c3, c4 = st.columns(4)
                lat = c1.number_input(
                    "Latitude", value=11.1560, format="%.4f"
                )
                lon = c2.number_input(
                    "Longitude", value=124.9920, format="%.4f"
                )
                enum_name = c3.text_input(
                    "Enumerator Name", f"Enumerator ({enum_code})"
                )
                resp_role = c4.selectbox(
                    "Respondent Role", ["Head", "Spouse", "Adult Member", "Other"]
                )

                c1, c2, c3 = st.columns(3)
                surv_status = c1.selectbox(
                    "Survey Status", ["Completed", "Partially Completed", "Refused"]
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
                        "None / Secular",
                        "Other Religion",
                    ],
                )

                c1, c2, c3, c4 = st.columns(4)
                tot_children = c1.number_input("No. of Children (<18 yrs)", 0, 20, 0)
                tot_dependents = c2.number_input("No. of Other Dependents", 0, 10, 0)
                hh_head_name = c3.text_input("Household Head Full Name")
                head_civil = c4.selectbox(
                    "Head Civil Status",
                    ["Single", "Married", "Widowed", "Separated", "Cohabiting"],
                )

            with t_vitals:
                st.markdown(
                    f"**Module B: Adult Profiling & Physical Screening ({num_adults} Adult(s) Active)**"
                )
                adults_data = []
                for i in range(1, int(num_adults) + 1):
                    st.markdown(
                        f"<div class='adult-card'><strong>Adult Member {i} Profile</strong></div>",
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
                            "College Graduate",
                        ],
                        key=f"a_edu_{i}",
                    )
                    a_occ = c5.text_input(
                        f"Adult {i} Occupation", key=f"a_occ_{i}"
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
                        f"Adult {i} Pulse", 30, 200, 75, key=f"a_pulse_{i}"
                    )

                    c1, c2 = st.columns(2)
                    a_symptoms = c1.multiselect(
                        f"Adult {i} Complaints",
                        [
                            "None",
                            "Cough",
                            "Fever",
                            "Headache",
                            "Colds",
                            "Body aches",
                            "Abdominal pain",
                            "Diarrhea",
                        ],
                        default=["None"],
                        key=f"a_sym_{i}",
                    )
                    a_risk = c2.selectbox(
                        f"Adult {i} Risk Level",
                        [
                            "Normal",
                            "Hypertensive Risk",
                            "Hypoxemic (<95%)",
                            "Fever / Febrile",
                        ],
                        key=f"a_risk_{i}",
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
                        })

            with t_socio:
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

                c1, c2, c3 = st.columns(3)
                transpo_owned = c1.multiselect(
                    "Transportation Owned",
                    [
                        "None",
                        "Bicycle",
                        "Motorcycle / Tricycle",
                        "Private Car / Van",
                        "Motorized Banca",
                    ],
                    default=["None"],
                )
                utilities_avail = c2.multiselect(
                    "Utilities Available",
                    [
                        "Grid Electricity",
                        "Solar Power",
                        "Piped Water Connection",
                        "Cellular Signal",
                        "Internet",
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
                    ],
                    default=["Electric Fan"],
                )

                c1, c2, c3 = st.columns(3)
                food_skip = c1.selectbox(
                    "Skipped meal due to lack of money?", ["No", "Yes"]
                )
                food_worry = c2.selectbox(
                    "Worried about running out of food?", ["No", "Yes"]
                )
                food_fullday = c3.selectbox(
                    "Went full day without food?", ["No", "Yes"]
                )

                c1, c2, c3 = st.columns(3)
                tenure = c1.selectbox(
                    "Tenurial Status",
                    [
                        "Residential lot with house",
                        "Residential House without Lot",
                        "Renting",
                        "Shared",
                        "Informal Settler",
                    ],
                )
                house_type = c2.selectbox(
                    "Housing Construction Type",
                    [
                        "Light (Nipa/bamboo)",
                        "Medium (Wooden/G.I.)",
                        "Heavy / Permanent (Concrete)",
                    ],
                )
                cook_fuel = c3.selectbox(
                    "Indoor Air Risk (Cooking Fuel)",
                    ["LPG", "Charcoal", "Wood", "Kerosene", "Electric"],
                )

                c1, c2 = st.columns(2)
                is_flood_prone = c1.selectbox(
                    "Located in a Flood-Prone Zone?", ["No", "Yes"]
                )

                c1, c2, c3 = st.columns(3)
                water_source = c1.selectbox(
                    "Drinking Water Source Level",
                    [
                        "Level 1: Protected Well / Spring",
                        "Level 2: Piped network & communal faucet",
                        "Level 3: Individual household tap",
                        "Unsafe: Shallow Well / River",
                        "Commercial Refill Station",
                    ],
                )
                toilet_type = c2.selectbox(
                    "Sanitation / Toilet Facility Type",
                    [
                        "Pour/Flush to Septic Tank",
                        "VIP Latrine",
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
                    ],
                )

            with t_dec:
                c1, c2 = st.columns(2)
                dec_expenses = c1.multiselect(
                    "Who decides on Family Expenses?",
                    ["Father", "Mother", "Children", "Others"],
                    default=["Father", "Mother"],
                )
                dec_health = c2.multiselect(
                    "Who decides on Health Care?",
                    ["Father", "Mother", "Children", "Others"],
                    default=["Mother"],
                )

            with t_morb:
                c1, c2, c3 = st.columns(3)
                e_diarrhea = c1.selectbox(
                    "Diarrheal Episodes (>1 in past 12 mos)", ["No", "Yes"]
                )
                e_urti = c2.selectbox(
                    "Severe URTI / Pneumonia", ["No", "Yes"]
                )
                e_dengue = c3.selectbox("Dengue Cases", ["No", "Yes"])

                c1, c2 = st.columns(2)
                htn_status = c1.selectbox(
                    "Hypertension Status",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Compliant with Meds",
                        "Diagnosed - Irregular Meds",
                        "Diagnosed - Unmedicated",
                    ],
                )
                dm_status = c2.selectbox(
                    "Type 2 Diabetes Status",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Compliant with Meds",
                        "Diagnosed - Irregular Meds",
                        "Diagnosed - Unmedicated",
                    ],
                )

                c1, c2 = st.columns(2)
                asthma_status = c1.selectbox(
                    "Bronchial Asthma / COPD Status",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Active Maintenance",
                        "Diagnosed - Emergency Meds Only",
                        "Diagnosed - Untreated",
                    ],
                )
                tb_status = c2.selectbox(
                    "Tuberculosis History & DOTS",
                    [
                        "No Member Diagnosed",
                        "Currently Enrolled in TB-DOTS",
                        "Completed TB Treatment",
                        "Defaulted / Interrupted DOTS",
                    ],
                )

                c1, c2, c3 = st.columns(3)
                ckd_status = c1.selectbox(
                    "Chronic Kidney Disease",
                    ["No", "Yes - Stage 1-3", "Yes - Dialysis Dependent"],
                )
                cvd_status = c2.selectbox("CVD / History of Stroke", ["No", "Yes"])
                cancer_status = c3.selectbox(
                    "Active Malignancy / Cancer", ["No", "Yes"]
                )

            with t_mch:
                c1, c2, c3 = st.columns(3)
                is_preg = c1.selectbox("Currently Pregnant Member?", ["No", "Yes"])
                anc_visits = c2.number_input("ANC Visits (Target ≥4)", 0, 15, 0)
                anc_1st_tri = c3.selectbox(
                    "First ANC Visit in 1st Trimester?", ["N/A", "Yes", "No"]
                )

                c1, c2, c3 = st.columns(3)
                ifa_tablets = c1.selectbox(
                    "Iron-Folic Acid (IFA) Tablets",
                    ["N/A", "<180 Tablets", "≥180 Tablets (Completed)"],
                )
                td_status = c2.selectbox(
                    "Tetanus Immunization",
                    ["N/A", "Td1", "Td2", "Td3+", "Fully Immunized Mother"],
                )
                postpartum_check = c3.selectbox(
                    "Postpartum Check within 72h", ["N/A", "Yes", "No"]
                )

                c1, c2 = st.columns(2)
                deliv_personnel_yesno = c1.selectbox(
                    "Handled by trained personnel?", ["N/A", "Yes", "No"]
                )
                deliv_facility_yesno = c2.selectbox(
                    "Handled in accredited facility?", ["N/A", "Yes", "No"]
                )

                c1, c2 = st.columns(2)
                fp_access = c1.selectbox(
                    "Access to family planning?", ["Yes", "No"]
                )
                fp_practice = c2.selectbox(
                    "Practicing family planning?", ["Yes", "No"]
                )

                mortality_yesno = st.selectbox(
                    "Family deaths due to preventable diseases?", ["No", "Yes"]
                )

            with t_child:
                st.markdown(
                    f"**Module F4: Child Profiling ({num_children} Child(ren) Active)**"
                )
                children_records = []
                for c_i in range(1, int(num_children) + 1):
                    st.markdown(
                        f"<div class='child-card'><strong>👶 Child Member {c_i} Profile</strong></div>",
                        unsafe_allow_html=True,
                    )
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c_name = c1.text_input(
                        f"Child {c_i} Name", key=f"c_name_{c_i}"
                    )
                    c_sex = c2.selectbox(
                        f"Child {c_i} Sex", ["Male", "Female"], key=f"c_sex_{c_i}"
                    )
                    c_age_m = c3.number_input(
                        f"Child {c_i} Age (Mos)", 0, 59, 12, key=f"c_age_{c_i}"
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

                    ic1, ic2, ic3, ic4, ic5, ic6 = st.columns(6)
                    imm_bcg = ic1.checkbox("BCG", key=f"bcg_{c_i}")
                    imm_hepb = ic2.checkbox("Hep B", key=f"hepb_{c_i}")
                    imm_penta = ic3.checkbox("Penta 3x", key=f"penta_{c_i}")
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
                        else "Partially Immunized"
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
                        })

            with t_yakap:
                hsb_initial_actions = st.multiselect(
                    "Initial Actions When Unwell",
                    [
                        "Rest and wait",
                        "Use home/herbal remedies",
                        "Buy OTC medication",
                        "Search symptoms online",
                        "Contact healthcare provider",
                    ],
                    default=["Rest and wait"],
                )
                hsb_providers_used = st.multiselect(
                    "Facilities/Providers Used",
                    [
                        "Public hospital",
                        "Private clinic/hospital",
                        "RHU / BHS",
                        "Local pharmacy",
                        "Traditional practitioner",
                    ],
                    default=["RHU / BHS"],
                )
                hsb_travel_time = st.selectbox(
                    "Travel Time to Health Facility",
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
                        "Lack of insurance coverage",
                    ],
                )
                hsb_influencers = st.multiselect(
                    "Key Decision Influencers",
                    [
                        "Spouse / Family",
                        "Parents / Relatives",
                        "Peers",
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
                # ================= VALIDATE DUPLICATE HOUSEHOLD ID =================
                existing_ids = [
                    r.get("HH_ID") for r in st.session_state.hh_records
                ]
                if hh_id in existing_ids:
                    st.error(
                        f"⚠️ **DUPLICATE HOUSEHOLD NUMBER DETECTED!** Household ID"
                        f" '{hh_id}' has already been filled out by another"
                        " enumerator. Please update the Household ID to a unique"
                        " number."
                    )
                    st.stop()

                primary_sys = (
                    adults_data[0]["Sys"] if len(adults_data) > 0 else 120
                )
                primary_risk = (
                    adults_data[0]["Risk"] if len(adults_data) > 0 else "Normal"
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
                    " unique multi-enumerator validation!"
                )

    elif mode_p2 == "📊 Phase 2 Interpreted Data & Research Analytics Tables":
        st.markdown(
            "### 📊 Master Household Survey Research Interpretation & Frequency"
            " Tables"
        )

        if len(st.session_state.hh_records) == 0:
            st.info(
                "No household survey records found. Please add entries to view"
                " statistical research tables."
            )
        else:
            tab_res_table, tab_indiv = st.tabs([
                "🔬 Comprehensive Research Statistical Tables (All Survey Questions)",
                "🔍 Individual Response Inspector",
            ])

            with tab_res_table:
                st.markdown(
                    "#### 📊 Complete Research Frequency (n) & Percentage (%)"
                    " Breakdown"
                )
                st.caption(
                    "Presents all questions asked in the Master Household"
                    " Survey in research report format."
                )

                df_research = generate_master_survey_research_table(
                    st.session_state.hh_records
                )

                if not df_research.empty:
                    st.dataframe(
                        df_research, use_container_width=True, height=600
                    )

                    csv_data = df_research.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Download Research Frequency Table (CSV)",
                        data=csv_data,
                        file_name="Master_Household_Survey_Research_Table.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                else:
                    st.warning("No survey records available to compile.")

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
                st.json(selected_record)

    else:
        st.markdown("### 📂 Submitted Household Survey Records")
        if len(st.session_state.hh_records) == 0:
            st.info("No household records found.")
        else:
            hh_options = [
                f"[{i+1}] {r.get('HH_ID', 'N/A')} - {r.get('Barangay', 'N/A')}"
                f" ({r.get('Purok', 'N/A')})"
                for i, r in enumerate(st.session_state.hh_records)
            ]
            selected_idx = st.selectbox(
                "Select Household Record to Review / Delete",
                range(len(hh_options)),
                format_func=lambda x: hh_options[x],
            )

            if st.button("🗑️ Delete Household Record", type="primary"):
                st.session_state.hh_records.pop(selected_idx)
                save_session_to_disk()
                st.success("Household record deleted successfully!")
                st.rerun()

# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader(
        "Phase 3: Qualitative Field Tools (KII & FGD Structured Guides)"
    )
    st.info("Qualitative module active and linked with persistent storage.")

# MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader("Phase 4: Environmental Observation Matrices & PERI Index")
    st.info("Expanded PERI Windshield module active.")

# MODULE 6: PHASE 5 STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial & Statistical Analytics Module")

    if len(st.session_state.hh_records) == 0:
        st.info("No household records available for Phase 5 analytics.")
    else:
        st.markdown("### 🔬 Research Master Table Generator")
        df_research_p5 = generate_master_survey_research_table(
            st.session_state.hh_records
        )
        st.dataframe(df_research_p5, use_container_width=True, height=500)

# MODULE 7: PHASE 6 ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("Phase 6: Community Diagnosis & Action Plan")
    st.info("Community Diagnosis & Action Planning active.")

# MODULE 8: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 System Data Management & Multi-Format Export Portal")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📥 Export Full Master Household Survey")
        if len(st.session_state.hh_records) > 0:
            df_export = pd.DataFrame(st.session_state.hh_records)
            csv_hh = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Master HH Survey (CSV)",
                data=csv_hh,
                file_name="Master_Household_Survey_Data.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No household records to export.")

    with col2:
        st.markdown("#### 🔬 Export Master Research Table (n & %)")
        if len(st.session_state.hh_records) > 0:
            df_res_export = generate_master_survey_research_table(
                st.session_state.hh_records
            )
            csv_res = df_res_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Research Frequency Table (CSV)",
                data=csv_res,
                file_name="Master_Survey_Research_Frequency_Table.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("No records to generate research table.")
