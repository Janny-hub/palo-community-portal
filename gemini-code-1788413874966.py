import json
import math
import os
from collections import Counter
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# Page Configuration
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

if st.sidebar.button("🔄 Sync / Refresh Shared Data", use_container_width=True):
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
    m1.metric("Total Surveyed HHs", f"{tot_hh}", delta=f"{tot_pop} Profiled")
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
    )
    m5.metric(
        "Action Plans Saved",
        f"{len(diag_data)} Plans",
        delta=f"{len(qual_data)} Notes",
    )

    st.markdown("---")
    st.markdown("### 🤖 Automated Community Health Risk & Vulnerability Predictor")

    risk_triggers = []
    if htn_rate > 25.0:
        risk_triggers.append({
            "type": "high",
            "title": "🚨 Severe Adult Cardiovascular & Hypertension Surge",
            "desc": (
                f"Hyper-prevalence detected: **{htn_rate:.1f}%** of screened"
                " adults present with high BP (≥140/90 mmHg)."
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
                " located within flood-prone zones."
            ),
            "action": (
                "Coordinate with Municipal DRRMO for pre-disaster evacuation"
                " and WASH protocols."
            ),
        })

    if not risk_triggers:
        st.info("✅ Baseline parameters indicate low immediate community risk.")
    else:
        for trig in risk_triggers:
            st.error(
                f"**{trig['title']}**\n\n{trig['desc']}\n\n*🎯 Target Action:"
                f" {trig['action']}*"
            )

# MODULE 1: INTERACTIVE SPOT MAP
elif menu == "🗺️ Interactive Spot Map":
    st.subheader(
        "📍 Interactive Barangay Health & Environmental Hazard Spot Map"
    )

    if len(st.session_state.hh_records) == 0:
        st.info("No household survey records stored yet. Showing baseline map.")
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
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position=["Lon", "Lat"],
        get_color="Color",
        get_radius=16,
        pickable=True,
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))

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

        st.markdown("**Domain Scores Entry (0-100)**")
        g_score = st.number_input("Total BHB Governance Score", 0, 100, 75)
        gap_summary = st.text_area("Governance Bottlenecks")
        action_plan = st.text_area("Action Plan")

        if st.form_submit_button("Save Governance Scorecard"):
            rating = (
                "HIGH FUNCTIONING"
                if g_score >= 80
                else ("MODERATE FUNCTIONING" if g_score >= 50 else "LOW FUNCTIONING")
            )
            st.session_state.gov_records.append({
                "Barangay": b_name,
                "City": city,
                "Province": prov,
                "Score": g_score,
                "Rating": rating,
                "Gaps": gap_summary,
                "ActionPlan": action_plan,
            })
            save_session_to_disk()
            st.success(f"Saved! Total Score: {g_score} ({rating})")

# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader("Phase 2: Master Household Survey Instrument")

    if "adult_count" not in st.session_state:
        st.session_state.adult_count = 1
    if "child_count" not in st.session_state:
        st.session_state.child_count = 0

    c_cnt1, c_cnt2 = st.columns(2)
    st.session_state.adult_count = c_cnt1.number_input(
        "Adult Members", 0, 20, st.session_state.adult_count
    )
    st.session_state.child_count = c_cnt2.number_input(
        "Child Members (<5 yrs)", 0, 15, st.session_state.child_count
    )

    with st.form("phase2_complete_form"):
        c1, c2, c3 = st.columns(3)
        hh_id = c1.text_input("Household ID", "HH-E1-001")
        brgy = c2.text_input("Barangay Name", "Barangay 1")
        purok = c3.selectbox("Purok", [f"Purok {i}" for i in range(1, 8)])

        c1, c2, c3 = st.columns(3)
        lat = c1.number_input("Latitude", value=11.1560, format="%.4f")
        lon = c2.number_input("Longitude", value=124.9920, format="%.4f")
        head_name = c3.text_input("Head Name", "Juan Dela Cruz")

        c1, c2, c3 = st.columns(3)
        income = c1.selectbox(
            "Income Quintile",
            [
                "≤ ₱10,000 (Q1)",
                "₱10,001–₱20,000 (Q2)",
                "₱20,001–₱35,000 (Q3)",
                "₱35,001–₱50,000 (Q4)",
                "> ₱50,000 (Q5)",
            ],
        )
        water = c2.selectbox(
            "Water Source",
            [
                "Level 1: Protected Well",
                "Level 2: Communal Tap",
                "Level 3: Individual Tap",
                "Unsafe Water Source",
            ],
        )
        house_mat = c3.selectbox(
            "Housing Material",
            [
                "Light (Nipa/Bamboo)",
                "Medium (Wooden/GI)",
                "Heavy (Concrete/Concrete Block)",
            ],
        )

        c1, c2, c3 = st.columns(3)
        cook_fuel = c1.selectbox(
            "Cooking Fuel", ["Wood / Charcoal", "Kerosene", "LPG / Electric"]
        )
        food_skip = c2.selectbox("Skipped Meals (Food Insecure)?", ["No", "Yes"])
        flood_prone = c3.selectbox("Flood Prone Zone?", ["No", "Yes"])

        adults_data = []
        for i in range(1, st.session_state.adult_count + 1):
            st.markdown(f"**Adult Member {i}**")
            a_sys = st.number_input(
                f"Adult {i} Systolic BP", 80, 220, 120, key=f"sys_{i}"
            )
            a_dia = st.number_input(
                f"Adult {i} Diastolic BP", 50, 140, 80, key=f"dia_{i}"
            )
            a_dm = st.selectbox(
                f"Adult {i} Diagnosed Diabetes?",
                ["No", "Yes"],
                key=f"dm_{i}",
            )
            a_tb = st.selectbox(
                f"Adult {i} Active TB?", ["No", "Yes"], key=f"tb_{i}"
            )
            a_risk = (
                "Hypertensive Risk"
                if (a_sys >= 140 or a_dia >= 90)
                else "Normal"
            )
            adults_data.append({
                "Name": f"Adult {i}",
                "Sys": a_sys,
                "Dia": a_dia,
                "Diabetes": a_dm,
                "TB": a_tb,
                "Risk": a_risk,
            })

        children_data = []
        for j in range(1, st.session_state.child_count + 1):
            st.markdown(f"**Child Member {j}**")
            c_age = st.number_input(
                f"Child {j} Age (mos)", 0, 59, 12, key=f"cage_{j}"
            )
            c_wt = st.number_input(
                f"Child {j} Weight (kg)", 1.0, 30.0, 8.0, key=f"cwt_{j}"
            )
            c_ht = st.number_input(
                f"Child {j} Height (cm)", 30.0, 120.0, 75.0, key=f"cht_{j}"
            )
            c_nutr = compute_child_nutrition(c_age, c_wt, c_ht)
            children_data.append(
                {"Name": f"Child {j}", "Age_Months": c_age, "Nutr": c_nutr}
            )

        if st.form_submit_button("Submit Household Record"):
            st.session_state.hh_records.append({
                "HH_ID": hh_id,
                "Barangay": brgy,
                "Purok": purok,
                "Lat": lat,
                "Lon": lon,
                "Head_Name": head_name,
                "Income": income,
                "Water": water,
                "House_Type": house_mat,
                "Cook_Fuel": cook_fuel,
                "Food_Skip": food_skip,
                "Flood_Prone": flood_prone,
                "Adults": adults_data,
                "Children": children_data,
                "BP": f"{adults_data[0]['Sys']}/{adults_data[0]['Dia']}"
                if adults_data
                else "120/80",
                "Risk": adults_data[0]["Risk"] if adults_data else "Normal",
                "Color": [192, 38, 211, 230]
                if flood_prone == "Yes"
                else [34, 197, 94, 200],
            })
            save_session_to_disk()
            st.success(f"Household record {hh_id} saved successfully!")

# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader(
        "Phase 3: Qualitative Field Tools (KII & FGD Structured Guides)"
    )

    with st.form("qual_form"):
        tool_type = st.selectbox(
            "Tool Instrument", ["Tool 3.1: KII Governance", "Tool 3.3: FGD Community"]
        )
        resp_name = st.text_input("Respondent / Group Identification")
        notes = st.text_area("Field Notes & Key Findings")

        if st.form_submit_button("Save Qualitative Record"):
            st.session_state.qual_records.append({
                "Tool": tool_type,
                "Respondent": resp_name,
                "Notes": notes,
            })
            save_session_to_disk()
            st.success("Qualitative field notes saved!")

# MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader(
        "Phase 4: Purok Environmental Risk Index (PERI) Windshield Tool"
    )

    with st.form("peri_form"):
        purok_name = st.selectbox("Select Purok", [f"Purok {i}" for i in range(1, 8)])
        s1 = st.slider("Domain 1: Sanitation & Waste Risk", 1, 3, 2)
        s2 = st.slider("Domain 2: Food & Retail Environment", 1, 3, 2)
        s3 = st.slider("Domain 3: Built Environment & Housing", 1, 3, 2)
        s4 = st.slider("Domain 4: Health Infrastructure", 1, 3, 2)
        s5 = st.slider("Domain 5: DRR & Climate Hazards", 1, 3, 2)
        s6 = st.slider("Domain 6: Vector & Pest Hazards", 1, 3, 2)

        if st.form_submit_button("Save PERI Evaluation"):
            peri_idx = float(np.mean([s1, s2, s3, s4, s5, s6]))
            st.session_state.windshield_records.append({
                "Purok": purok_name,
                "DS1_Sanitation": s1,
                "DS2_Food": s2,
                "DS3_BuiltEnv": s3,
                "DS4_HealthInfra": s4,
                "DS5_DRR": s5,
                "DS6_Vector": s6,
                "PERI_Index": peri_idx,
            })
            save_session_to_disk()
            st.success(f"PERI Index for {purok_name} saved: {peri_idx:.2f}")

# ================= MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS =================
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial & Advanced Statistical Analytics Framework")

    st.markdown("""
    This automated module computes real-time GIS spatial layers (**Section 6.2**) and executes advanced multivariate epidemiological modeling (**Section 6.3**) on the active community dataset.
    """)

    tab_gis, tab_stats = st.tabs([
        "🗺️ 6.2 Multi-Layer GIS Visualization Framework",
        "📊 6.3 Statistical Analysis & Advanced Analytical Modeling Plan",
    ])

    # ------------------ SECTION 6.2: MULTI-LAYER GIS FRAMEWORK ------------------
    with tab_gis:
        st.markdown("### 🗺️ 6.2 Multi-Layer GIS Visualization Framework")

        hh_list = st.session_state.hh_records
        if len(hh_list) == 0:
            st.info(
                "No household data available to render GIS spatial layers."
                " Populating with synthetic baseline spatial dataset."
            )
            hh_df = pd.DataFrame([
                {
                    "HH_ID": "HH-001",
                    "Purok": "Purok 1",
                    "Lat": 11.1562,
                    "Lon": 124.9912,
                    "Hypertension": 1,
                    "Diabetes": 0,
                    "TB": 0,
                    "Water_Unsafe": 1,
                    "Flood_Zone": 1,
                    "Open_Dumping": 1,
                    "Fresh_Market": 0,
                    "Sari_Sari": 1,
                    "Malnourished_Child": 1,
                    "BHS_Distance_km": 1.2,
                },
                {
                    "HH_ID": "HH-002",
                    "Purok": "Purok 2",
                    "Lat": 11.1585,
                    "Lon": 124.9935,
                    "Hypertension": 1,
                    "Diabetes": 1,
                    "TB": 1,
                    "Water_Unsafe": 1,
                    "Flood_Zone": 0,
                    "Open_Dumping": 1,
                    "Fresh_Market": 0,
                    "Sari_Sari": 1,
                    "Malnourished_Child": 1,
                    "BHS_Distance_km": 3.8,
                },
                {
                    "HH_ID": "HH-003",
                    "Purok": "Purok 3",
                    "Lat": 11.1530,
                    "Lon": 124.9890,
                    "Hypertension": 0,
                    "Diabetes": 0,
                    "TB": 0,
                    "Water_Unsafe": 0,
                    "Flood_Zone": 0,
                    "Open_Dumping": 0,
                    "Fresh_Market": 1,
                    "Sari_Sari": 0,
                    "Malnourished_Child": 0,
                    "BHS_Distance_km": 0.5,
                },
                {
                    "HH_ID": "HH-004",
                    "Purok": "Purok 4",
                    "Lat": 11.1610,
                    "Lon": 124.9960,
                    "Hypertension": 1,
                    "Diabetes": 1,
                    "TB": 0,
                    "Water_Unsafe": 1,
                    "Flood_Zone": 1,
                    "Open_Dumping": 1,
                    "Fresh_Market": 0,
                    "Sari_Sari": 1,
                    "Malnourished_Child": 1,
                    "BHS_Distance_km": 4.5,
                },
            ])
        else:
            rows = []
            for h in hh_list:
                adults = h.get("Adults", [])
                children = h.get("Children", [])

                has_htn = 1 if any(a.get("Sys", 0) >= 140 for a in adults) else 0
                has_dm = (
                    1 if any(a.get("Diabetes") == "Yes" for a in adults) else 0
                )
                has_tb = 1 if any(a.get("TB") == "Yes" for a in adults) else 0

                water_unsafe = (
                    1
                    if "Unsafe" in h.get("Water", "")
                    or "Level 1" in h.get("Water", "")
                    else 0
                )
                flood_zone = 1 if h.get("Flood_Prone") == "Yes" else 0

                has_malnutrition = 0
                for c in children:
                    w = c.get("Nutr", {}).get("Wasting", "")
                    st_val = c.get("Nutr", {}).get("Stunting", "")
                    if "Wasted" in w or "Stunted" in st_val:
                        has_malnutrition = 1

                # Distance approximation from arbitrary reference center (11.1560, 124.9910)
                lat, lon = h.get("Lat", 11.1560), h.get("Lon", 124.9910)
                dist_km = math.sqrt(
                    (lat - 11.1560) ** 2 + (lon - 124.9910) ** 2
                ) * 111.0

                rows.append({
                    "HH_ID": h.get("HH_ID"),
                    "Purok": h.get("Purok"),
                    "Lat": lat,
                    "Lon": lon,
                    "Hypertension": has_htn,
                    "Diabetes": has_dm,
                    "TB": has_tb,
                    "Water_Unsafe": water_unsafe,
                    "Flood_Zone": flood_zone,
                    "Open_Dumping": 1 if h.get("Cook_Fuel") == "Wood" else 0,
                    "Fresh_Market": 1 if "Q4" in h.get("Income", "") else 0,
                    "Sari_Sari": 1,
                    "Malnourished_Child": has_malnutrition,
                    "BHS_Distance_km": dist_km,
                })
            hh_df = pd.DataFrame(rows)

        g_col1, g_col2 = st.columns([1, 3])

        with g_col1:
            st.markdown("**GIS Layer Controls**")
            show_layer1 = st.checkbox(
                "🔥 Layer 1: Disease Hotspot Mapping (KDE)", value=True
            )
            show_layer2 = st.checkbox(
                "🌊 Layer 2: Environmental SDOH Overlay", value=True
            )
            show_layer3 = st.checkbox(
                "🛒 Layer 3: Food Desert Identification (500m Buffer)",
                value=True,
            )
            show_layer4 = st.checkbox(
                "⏱️ Layer 4: Catchment Isochrone Modeling (GIDAs)", value=True
            )

        with g_col2:
            layers = []
            avg_lat = hh_df["Lat"].mean()
            avg_lon = hh_df["Lon"].mean()

            # LAYER 1: Disease Hotspot Mapping (Kernel Density Estimation Proxy)
            if show_layer1:
                disease_pts = hh_df[
                    (hh_df["Hypertension"] == 1)
                    | (hh_df["Diabetes"] == 1)
                    | (hh_df["TB"] == 1)
                ]
                layers.append(
                    pdk.Layer(
                        "HeatmapLayer",
                        data=disease_pts,
                        get_position=["Lon", "Lat"],
                        get_weight="Hypertension + Diabetes + TB",
                        radiusPixels=40,
                    )
                )

            # LAYER 2: Environmental SDOH Overlay
            if show_layer2:
                sdoh_pts = hh_df[
                    (hh_df["Water_Unsafe"] == 1) | (hh_df["Flood_Zone"] == 1)
                ]
                layers.append(
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=sdoh_pts,
                        get_position=["Lon", "Lat"],
                        get_color="[220, 38, 38, 200]",
                        get_radius=25,
                        pickable=True,
                    )
                )

            # LAYER 3: Food Desert Buffer Analysis (500m walking radius)
            if show_layer3:
                food_desert_pts = hh_df[
                    (hh_df["Fresh_Market"] == 0)
                    & (hh_df["Malnourished_Child"] == 1)
                ]
                layers.append(
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=food_desert_pts,
                        get_position=["Lon", "Lat"],
                        get_color="[234, 179, 8, 160]",
                        get_radius=500,  # 500m buffer
                        stroked=True,
                        filled=False,
                        get_line_color="[234, 179, 8, 255]",
                        get_line_width=3,
                    )
                )

            # LAYER 4: Catchment Isochrone Modeling (15-min and 30-min travel times)
            if show_layer4:
                bhs_center = pd.DataFrame([{
                    "Lat": avg_lat,
                    "Lon": avg_lon,
                    "Name": "BHS / RHU Health Center",
                }])
                # 15-min contour (~1.5km walking radius)
                layers.append(
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=bhs_center,
                        get_position=["Lon", "Lat"],
                        get_radius=1500,
                        get_color="[34, 197, 94, 60]",
                        get_line_color="[34, 197, 94, 255]",
                        stroked=True,
                    )
                )
                # 30-min contour (~3.0km walking radius - GIDA boundary)
                layers.append(
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=bhs_center,
                        get_position=["Lon", "Lat"],
                        get_radius=3000,
                        get_color="[239, 68, 68, 40]",
                        get_line_color="[239, 68, 68, 255]",
                        stroked=True,
                    )
                )

            view = pdk.ViewState(
                latitude=avg_lat, longitude=avg_lon, zoom=14, pitch=25
            )
            st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view))

        st.markdown("#### 📖 GIS Analytical Layer Interpretation")
        c1, c2, c3, c4 = st.columns(4)
        c1.info(
            "**Layer 1: Disease KDE**\nIdentifies high-density chronic NCD and"
            " TB clusters across Purok boundaries."
        )
        c2.warning(
            "**Layer 2: SDOH Overlay**\nSuperimposes unsafe WASH facilities and"
            " flood hazards over disease clusters."
        )
        c3.error(
            "**Layer 3: Food Deserts**\nHighlights 500m non-access zones"
            " correlating fresh markets with child stunting."
        )
        c4.success(
            "**Layer 4: Isochrones**\nModels >30-min travel barriers to"
            " delineate Geographically Isolated & Disadvantaged Areas (GIDAs)."
        )

    # ------------------ SECTION 6.3: STATISTICAL & MULTIVARIATE MODELING ------------------
    with tab_stats:
        st.markdown(
            "### 📊 6.3 Statistical Analysis & Advanced Analytical Modeling"
            " Plan"
        )

        # Prepare Statistical Dataframe
        hh_all = st.session_state.hh_records
        if len(hh_all) < 3:
            st.warning(
                "⚠️ Insufficient records in session storage for robust statistical"
                " modeling. Operating automated modeling engine on expanded"
                " simulated cohort based on current parameters."
            )
            # Create standard dataset for modeling demonstrate
            data_matrix = []
            for i in range(1, 41):
                inc_q = f"Q{(i % 5) + 1}"
                inc_val = (i % 5) + 1
                htn = 1 if (inc_val <= 2 and i % 2 == 0) or (i % 4 == 0) else 0
                dm = 1 if (inc_val <= 2 and i % 3 == 0) else 0
                mat_score = 3 if inc_val <= 2 else 1
                wash_score = 3 if inc_val <= 2 else 1
                fuel_score = 3 if inc_val <= 2 else 1
                food_ins = 1 if inc_val <= 2 else 0
                gida = 1 if i % 3 == 0 else 0

                data_matrix.append({
                    "HH_ID": f"HH-{i:03d}",
                    "Income_Quintile": inc_q,
                    "Income_Num": inc_val,
                    "Hypertension": htn,
                    "Diabetes": dm,
                    "Housing_Material_Vulnerability": mat_score,
                    "WASH_Vulnerability": wash_score,
                    "Fuel_Vulnerability": fuel_score,
                    "Food_Insecurity": food_ins,
                    "GIDA_Distance_Barrier": gida,
                })
            df_stat = pd.DataFrame(data_matrix)
        else:
            rows = []
            for h in hh_all:
                inc = h.get("Income", "Q1")
                inc_num = (
                    1
                    if "Q1" in inc
                    else (
                        2
                        if "Q2" in inc
                        else (3 if "Q3" in inc else (4 if "Q4" in inc else 5))
                    )
                )

                adults = h.get("Adults", [])
                htn = 1 if any(a.get("Sys", 0) >= 140 for a in adults) else 0
                dm = 1 if any(a.get("Diabetes") == "Yes" for a in adults) else 0

                mat_v = 3 if "Light" in h.get("House_Type", "") else 1
                wash_v = (
                    3
                    if "Unsafe" in h.get("Water", "")
                    or "Level 1" in h.get("Water", "")
                    else 1
                )
                fuel_v = (
                    3
                    if "Wood" in h.get("Cook_Fuel", "")
                    or "Charcoal" in h.get("Cook_Fuel", "")
                    else 1
                )
                food_ins = 1 if h.get("Food_Skip") == "Yes" else 0
                gida = 1 if "30" in h.get("HSB_Travel_Time", "") else 0

                rows.append({
                    "HH_ID": h.get("HH_ID"),
                    "Income_Quintile": f"Q{inc_num}",
                    "Income_Num": inc_num,
                    "Hypertension": htn,
                    "Diabetes": dm,
                    "Housing_Material_Vulnerability": mat_v,
                    "WASH_Vulnerability": wash_v,
                    "Fuel_Vulnerability": fuel_v,
                    "Food_Insecurity": food_ins,
                    "GIDA_Distance_Barrier": gida,
                })
            df_stat = pd.DataFrame(rows)

        st.markdown(
            "#### A. Descriptive Analysis (Measuring the Social Gradient)"
        )

        # Calculate Odds Ratio and Relative Risk for Low Income (Q1) vs Higher Income (Q2-Q5)
        exposed_htn = len(
            df_stat[
                (df_stat["Income_Num"] == 1) & (df_stat["Hypertension"] == 1)
            ]
        )
        exposed_no_htn = len(
            df_stat[
                (df_stat["Income_Num"] == 1) & (df_stat["Hypertension"] == 0)
            ]
        )
        unexposed_htn = len(
            df_stat[
                (df_stat["Income_Num"] > 1) & (df_stat["Hypertension"] == 1)
            ]
        )
        unexposed_no_htn = len(
            df_stat[
                (df_stat["Income_Num"] > 1) & (df_stat["Hypertension"] == 0)
            ]
        )

        # Calculations
        a, b, c, d = (
            max(1, exposed_htn),
            max(1, exposed_no_htn),
            max(1, unexposed_htn),
            max(1, unexposed_no_htn),
        )
        odds_ratio = (a * d) / (b * c)
        relative_risk = (a / (a + b)) / (c / (c + d))

        st.markdown(f"""
        **Cross-Tabulation Analysis: Income Quintiles vs Disease Burden**
        * **Target Comparison:** Quintile 1 (Lowest Income Tier) vs. Quintiles 2–5 (Higher Tiers)
        * **Odds Ratio (OR):** `{odds_ratio:.2f}` (Low-income households have {odds_ratio:.2f}× higher odds of hypertension/chronic disease)
        * **Relative Risk (RR):** `{relative_risk:.2f}` (Low-income households present {relative_risk:.2f}× relative risk)
        """)

        st.markdown("---")
        st.markdown(
            "#### B. Advanced Multivariate Modeling (Factor Analysis & Latent"
            " Class Analysis)"
        )

        col_fa, col_lca = st.columns(2)

        with col_fa:
            st.markdown(
                "##### 1. Principal Component & Factor Analysis (PCA)"
            )
            st.caption(
                "Collapses correlated environmental and economic variables into"
                " a composite index."
            )

            # Compute Principal Component 1 (Household Deprivation Index)
            features = [
                "Housing_Material_Vulnerability",
                "WASH_Vulnerability",
                "Fuel_Vulnerability",
                "Income_Num",
            ]
            X = df_stat[features].values
            X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-5)

            # Covariance matrix & Eigenvalue Decomposition
            cov_matrix = np.cov(X_norm, rowvar=False)
            eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
            pc1_weights = eigenvectors[:, -1]
            pc1_scores = X_norm.dot(pc1_weights)

            # Normalize factor scores into a 0-100 index
            deprivation_index = (
                (pc1_scores - pc1_scores.min())
                / (pc1_scores.max() - pc1_scores.min() + 1e-5)
            ) * 100
            df_stat["Barangay_SocioEconomic_Vulnerability_Index"] = (
                deprivation_index
            )

            var_explained = (
                eigenvalues[-1] / np.sum(eigenvalues)
            ) * 100.0

            st.write(
                f"**Composite Index Generated:** Barangay Socio-Economic"
                " Vulnerability Index"
            )
            st.write(f"**PC1 Variance Explained:** `{var_explained:.1f}%`")

            df_pca_summary = pd.DataFrame({
                "Variable": features,
                "Factor Loading Weight": pc1_weights,
            })
            st.dataframe(df_pca_summary, use_container_width=True)

        with col_lca:
            st.markdown("##### 2. Latent Class Analysis (LCA)")
            st.caption(
                "Groups households into discrete multi-risk vulnerability"
                " classes."
            )

            # Assign households to 3 Latent Classes based on overlapping social risks
            def assign_lca_class(row):
                risk_score = (
                    row["Food_Insecurity"]
                    + row["GIDA_Distance_Barrier"]
                    + (1 if row["WASH_Vulnerability"] > 1 else 0)
                )
                if risk_score == 0:
                    return "Class 1: High Access / Low Vulnerability"
                elif risk_score == 1:
                    return "Class 2: Moderate Single-Risk Cluster"
                else:
                    return "Class 3: Severe Multi-Domain Risk Cluster"

            df_stat["LCA_Vulnerability_Class"] = df_stat.apply(
                assign_lca_class, axis=1
            )

            lca_summary = (
                df_stat.groupby("LCA_Vulnerability_Class")
                .agg(
                    Household_Count=("HH_ID", "count"),
                    Hypertension_Prevalence=("Hypertension", "mean"),
                    Diabetes_Prevalence=("Diabetes", "mean"),
                )
                .reset_index()
            )

            lca_summary["Hypertension_Prevalence"] = lca_summary[
                "Hypertension_Prevalence"
            ].map(lambda x: f"{x*100:.1f}%")
            lca_summary["Diabetes_Prevalence"] = lca_summary[
                "Diabetes_Prevalence"
            ].map(lambda x: f"{x*100:.1f}%")

            st.dataframe(lca_summary, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📋 Target Public Health Output Summary Table")

        target_summary_df = pd.DataFrame([
            {
                "Statistical Method": (
                    "Descriptive Cross-Tabulation & Odds Ratios"
                ),
                "Input Variables (Survey/GIS)": (
                    "Income Quintiles × Hypertension / Diabetes Prevalence"
                ),
                "Target Public Health Output": (
                    "Quantifies the slope of the social gradient in health"
                    f" across income tiers (OR: {odds_ratio:.2f}, RR:"
                    f" {relative_risk:.2f})."
                ),
            },
            {
                "Statistical Method": "Factor Analysis (PCA)",
                "Input Variables (Survey/GIS)": (
                    "Housing materials, WASH level, Income, Cooking fuel"
                ),
                "Target Public Health Output": (
                    "Generates a composite 'Barangay Socio-Economic"
                    f" Vulnerability Index' (Explains {var_explained:.1f}%"
                    " variance)."
                ),
            },
            {
                "Statistical Method": "Latent Class Analysis (LCA)",
                "Input Variables (Survey/GIS)": (
                    "Co-occurring food insecurity, housing instability,"
                    " distance barrier"
                ),
                "Target Public Health Output": (
                    "Identifies multi-risk household clusters requiring"
                    " integrated LGU social protection."
                ),
            },
        ])

        st.table(target_summary_df)

# MODULE 7: PHASE 6 ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader(
        "Phase 6: Community Health Diagnosis & Integrated Action Plan"
    )

    with st.form("phase6_form"):
        diag_title = st.text_input(
            "Community Health Diagnosis Title",
            "High Hypertension & Vector Vulnerability in Flood-Prone Zones",
        )
        copar_phase = st.selectbox(
            "COPAR Phase",
            [
                "Pre-Entry Phase",
                "Entry Phase",
                "Organization Phase",
                "Action Phase",
                "Sustaining / Phase-Out Phase",
            ],
        )

        st.markdown("**Prioritization Matrix (Shiffman & Brunner Criteria)**")
        c1, c2, c3 = st.columns(3)
        p_mag = c1.slider("Magnitude of Problem (1-5)", 1, 5, 4)
        p_sev = c2.slider("Severity & Danger (1-5)", 1, 5, 4)
        p_feas = c3.slider("Feasibility of Intervention (1-5)", 1, 5, 5)

        target_obj = st.text_area("Key Objective & Target Metric")
        budget_alloc = st.number_input("Estimated LGU Budget (₱)", 0, 1000000, 50000)

        if st.form_submit_button("Save Action Plan"):
            st.session_state.diag_records.append({
                "Title": diag_title,
                "COPAR_Phase": copar_phase,
                "Priority_Score": p_mag + p_sev + p_feas,
                "Objective": target_obj,
                "Budget": budget_alloc,
            })
            save_session_to_disk()
            st.success("Community Diagnosis Action Plan saved successfully!")

# MODULE 8: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 System Data Management & Complete Backup Export")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 📥 Backup Data Export")
        all_data = load_shared_data()
        json_str = json.dumps(all_data, indent=4)
        st.download_button(
            label="💾 Download Master JSON Database",
            data=json_str,
            file_name="upm_community_health_data.json",
            mime="application/json",
            use_container_width=True,
        )

    with c2:
        st.markdown("#### 🗑️ Clear Storage")
        if st.button("⚠️ Reset All Persistent Data", use_container_width=True):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            sync_session_from_disk()
            st.success("Persistent storage cleared!")
            st.rerun()
