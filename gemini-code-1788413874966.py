import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="UP Manila - Community Clerks Portal (Dev: Jan Art Serna, RMT)",
    page_icon="🩺",
    layout="wide"
)

# Initialize Authentication State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Login Form Block
def show_login_screen():
    st.markdown("""
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
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🩺 UP Manila Clerks Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Comprehensive Community Health Field Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="dev-badge-login">⭐ Lead System Developer: Jan Art Serna, RMT</div>', unsafe_allow_html=True)
    
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
    st.markdown('</div>', unsafe_allow_html=True)

# Stop execution if user is not authenticated
if not st.session_state["authenticated"]:
    show_login_screen()
    st.stop()

# ================= MAIN APPLICATION LOGIC =================

# Custom UP Maroon, Green & Gold Styling with Sticky Progress Bar CSS
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
.stat-card {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
}
</style>"""

st.markdown(CSS_STYLE, unsafe_allow_html=True)

# Top Bar Header with Developer Honor & Logout Button
col_header, col_logout = st.columns([8, 2])

with col_header:
    HEADER_HTML = """<div class="up-navbar">
    <div class="up-navbar-title">UNIVERSITY OF THE PHILIPPINES MANILA</div>
    <div class="up-navbar-sub">School of Health Sciences — Comprehensive Community Health Field Portal</div>
    <div class="up-navbar-detail">Integrated System: Spatial Mapping, Geocoding, Analytics & Action Planning (Phases 1–6)</div>
    <div class="dev-honor-banner">⭐ Lead System Developer & Architect: Jan Art Serna, RMT | Field Enumerators: Aubrey Maye Arrieta | Leila Projimo, PTRP</div>
    </div>"""
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

with col_logout:
    st.write("")
    st.write("")
    if st.button("🚪 Log Out System", use_container_width=True, type="secondary"):
        st.session_state["authenticated"] = False
        st.rerun()

# Child Nutritional Status Calculation Engine
def compute_child_nutrition(age_months, weight_kg, height_cm):
    if height_cm <= 0 or weight_kg <= 0:
        return {"BMI": "N/A", "Wasting": "Invalid Input", "Stunting": "Invalid Input", "Underweight": "Invalid Input"}
    
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    
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
        "Underweight": underweight
    }

# Session State Initialization
if "hh_records" not in st.session_state:
    st.session_state.hh_records = []
if "gov_records" not in st.session_state:
    st.session_state.gov_records = []
if "qual_records" not in st.session_state:
    st.session_state.qual_records = []
if "windshield_records" not in st.session_state:
    st.session_state.windshield_records = []
if "diag_records" not in st.session_state:
    st.session_state.diag_records = []

# Dynamic Progress Tracker Calculations
p1_status = len(st.session_state.gov_records) > 0
p2_status = len(st.session_state.hh_records) > 0
p3_status = len(st.session_state.qual_records) > 0
p4_status = len(st.session_state.windshield_records) > 0
p5_status = p2_status
p6_status = len(st.session_state.diag_records) > 0

completed_phases = sum([p1_status, p2_status, p3_status, p4_status, p5_status, p6_status])
overall_progress_pct = int((completed_phases / 6) * 100)

# Sidebar - Sticky Progress Tracker & Developer Recognition
st.sidebar.markdown(f"""
<div class="sticky-progress-container">
    <div style="font-weight: 700; color: #1E293B; font-size: 14px; margin-bottom: 4px;">📊 Phase Completion Tracker</div>
    <div style="font-weight: 800; color: #7B1113; font-size: 18px; margin-bottom: 4px;">{overall_progress_pct}% Completed</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.progress(overall_progress_pct / 100)

with st.sidebar.expander("🔍 View Detailed Phase Status", expanded=False):
    st.write(f"{'✅' if p1_status else '🔴'} **Phase 1 (Governance):** {'100%' if p1_status else '0%'}")
    st.write(f"{'✅' if p2_status else '🔴'} **Phase 2 (Master Survey):** {'100%' if p2_status else '0%'}")
    st.write(f"{'✅' if p3_status else '🔴'} **Phase 3 (Qualitative):** {'100%' if p3_status else '0%'}")
    st.write(f"{'✅' if p4_status else '🔴'} **Phase 4 (Windshield):** {'100%' if p4_status else '0%'}")
    st.write(f"{'✅' if p5_status else '🔴'} **Phase 5 (Analytics):** {'100%' if p5_status else '0%'}")
    st.write(f"{'✅' if p6_status else '🔴'} **Phase 6 (Action Plan):** {'100%' if p6_status else '0%'}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Portal Navigation")
menu = st.sidebar.radio(
    "Select Field Module",
    [
        "🗺️ Interactive Spot Map", 
        "📋 Phase 1: Full Governance Scorecard", 
        "🏠 Phase 2: Master Household Survey", 
        "🗣️ Phase 3: Qualitative Field Tools", 
        "🔍 Phase 4: Full PERI Windshield Tool", 
        "📈 Phase 5: Spatial & Statistical Analytics",
        "📋 Phase 6: Community Diagnosis & Action Plan",
        "🩺 Diagnostic Summary & Analytics",
        "💾 Data Management & Export"
    ]
)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout Account", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.caption("👨‍💻 **Lead Developer:** Jan Art Serna, RMT")

# MODULE 1: INTERACTIVE SPOT MAP
if menu == "🗺️ Interactive Spot Map":
    st.subheader("📍 Interactive Barangay Health & Environmental Hazard Spot Map")
    
    if len(st.session_state.hh_records) == 0:
        st.info("No household survey records stored yet. Showing baseline map with simulated hazard markers.")
        map_df = pd.DataFrame([
            {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk": "Hypertensive Risk", "Flood_Prone": "Yes", "Color": [192, 38, 211, 230]},
            {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk": "Normal", "Flood_Prone": "No", "Color": [34, 197, 94, 200]},
            {"HH_ID": "HH-003", "Purok": "Purok 2", "Lat": 11.1555, "Lon": 124.9905, "BP": "120/80", "Risk": "Normal", "Flood_Prone": "Yes", "Color": [37, 99, 235, 220]},
            {"HH_ID": "HH-004", "Purok": "Purok 3", "Lat": 11.1570, "Lon": 124.9930, "BP": "150/98", "Risk": "Hypertensive Risk", "Flood_Prone": "No", "Color": [123, 17, 19, 220]}
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
            zoom=15, pitch=30
        )
        layer = pdk.Layer(
            "ScatterplotLayer", 
            data=filt_df, 
            get_position=["Lon", "Lat"], 
            get_color="Color", 
            get_radius=16, 
            pickable=True
        )
        st.pydeck_chart(pdk.Deck(
            layers=[layer], 
            initial_view_state=view, 
            tooltip={"text": "HH: {HH_ID}\nPurok: {Purok}\nBP: {BP}\nHealth Risk: {Risk}\nFlood Prone: {Flood_Prone}"}
        ))

# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD
elif menu == "📋 Phase 1: Full Governance Scorecard":
    st.subheader("Phase 1: Barangay Health Board (BHB) Governance Scorecard (100-Point Instrument)")
    
    with st.form("phase1_full_form"):
        t1, t2, t3, t4 = st.tabs([
            "📌 Metadata & Leadership", 
            "🏛️ Structure, Meetings & Ordinances", 
            "💰 AIP Budgeting & Reporting", 
            "🎯 Gaps & Action Planning"
        ])

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

        if st.form_submit_button("Save Phase 1 Full Governance Scorecard"):
            total_score = sum([g1_1, g1_2, g2_1, g2_2, g2_3, g3_1, g3_2, g3_3, g4_1, g4_2, g4_3, g5_1, g5_2, g5_3, g6_1, g6_2, g6_3])
            
            if total_score >= 80:
                rating = "HIGH FUNCTIONING"
            elif total_score >= 50:
                rating = "MODERATE FUNCTIONING"
            else:
                rating = "LOW FUNCTIONING / CRITICAL INTERVENTION REQUIRED"

            st.session_state.gov_records.append({
                "Barangay": b_name, "Score": total_score, "Rating": rating, "Gaps": gap_summary, "ActionPlan": action_plan
            })
            st.success(f"Scorecard Saved! Total Score: {total_score}/100 — Status: {rating}")

# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader("Phase 2: Master Household Survey Instrument (Tool 2.1 Complete)")
    
    with st.form("phase2_complete_form"):
        t_meta, t_vitals, t_socio, t_dec, t_morb, t_mch, t_yakap = st.tabs([
            "📋 Metadata & Roster",
            "🩺 Adult Profiling & Vitals (Adults 1–5)",
            "🌾 Socio-Econ, Food Insecurity, Housing & WASH",
            "🤝 Decision-Making Patterns",
            "🤒 Complete Morbidity & Chronic Care",
            "👶 Complete Maternal, Delivery, FP, Mortality & Child Profiling",
            "🏥 Healthcare Access & PhilHealth YAKAP"
        ])

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
            dialect = c2.text_input("Primary Dialect Spoken at Home")
            religion = c3.text_input("Religion")

            st.markdown("---")
            st.markdown("**Module A: Household Demographic Roster**")
            c1, c2, c3, c4 = st.columns(4)
            tot_children = c1.number_input("No. of Children (<18 yrs)", 0, 20, 0)
            tot_dependents = c2.number_input("No. of Other Dependents", 0, 10, 0)
            hh_head_name = c3.text_input("Household Head Full Name")
            head_civil = c4.selectbox("Head Civil Status", ["Single", "Married", "Widowed", "Separated", "Cohabiting"])

        with t_vitals:
            st.markdown("**Module B: Adult Profiling & Physical Screening (Adults 1 to 5)**")
            adults_data = []
            
            for i in range(1, 6):
                st.markdown(f"<div class='adult-card'><strong>Adult Member {i} Profiling & Physical Vitals</strong></div>", unsafe_allow_html=True)
                
                c1, c2, c3, c4, c5 = st.columns(5)
                a_name = c1.text_input(f"Adult {i} Name / Initials", key=f"a_name_{i}")
                a_age = c2.number_input(f"Adult {i} Age", 18, 120, 30, key=f"a_age_{i}")
                a_edu = c3.selectbox(f"Adult {i} Educational Level", [
                    "No Formal Education", "Elementary Unfinished", "Elementary Graduate", 
                    "High School Unfinished", "High School Graduate", 
                    "Vocational / College Unfinished", "College Graduate", "Post-Graduate"
                ], key=f"a_edu_{i}")
                a_occ = c4.text_input(f"Adult {i} Primary Occupation", key=f"a_occ_{i}")
                a_ph_cat = c5.selectbox(f"Adult {i} PhilHealth Category", [
                    "Indigent", "Formal", "Informal", "Dependent", "Unenrolled"
                ], key=f"a_ph_{i}")

                c1, c2, c3, c4, c5 = st.columns(5)
                a_sys = c1.number_input(f"Adult {i} Systolic BP", 50, 250, 120, key=f"a_sys_{i}")
                a_dia = c2.number_input(f"Adult {i} Diastolic BP", 30, 150, 80, key=f"a_dia_{i}")
                a_spo2 = c3.number_input(f"Adult {i} SpO2 (%)", 50, 100, 98, key=f"a_spo2_{i}")
                a_pulse = c4.number_input(f"Adult {i} Pulse Rate (bpm)", 30, 200, 75, key=f"a_pulse_{i}")
                a_temp = c5.number_input(f"Adult {i} Temp (°C)", 30.0, 42.0, 36.5, key=f"a_temp_{i}")

                c1, c2 = st.columns(2)
                a_symptoms = c1.multiselect(f"Adult {i} Current Complaints", ["None", "Headache", "Cough", "Chest Pain", "Shortness of Breath"], default=["None"], key=f"a_sym_{i}")
                a_risk = c2.selectbox(f"Adult {i} Risk Assessment", ["Normal", "Hypertensive Risk", "Hypoxemic (<95%)"], key=f"a_risk_{i}")

                adults_data.append({
                    "ID": f"Adult {i}", "Name": a_name, "Age": a_age, "Edu": a_edu, "Occupation": a_occ,
                    "PhilHealth_Cat": a_ph_cat, "BP": f"{a_sys}/{a_dia}", "Sys": a_sys, "SpO2": a_spo2, 
                    "Pulse": a_pulse, "Temp": a_temp, "Risk": a_risk
                })

        with t_socio:
            st.markdown("**C1. Livelihood, Economic Stability & Domestic Assets**")
            c1, c2, c3 = st.columns(3)
            income_cat = c1.selectbox("Average Family Income / Month", ["≤ ₱10,000 (Q1)", "₱10,001–₱20,000 (Q2)", "₱20,001–₱35,000 (Q3)", "₱35,001–₱50,000 (Q4)", "> ₱50,000 (Q5)"])
            livelihood = c2.selectbox("Primary Livelihood Source", ["Farming (Owned)", "Farming (Tenanted)", "Laborer", "Carpentry", "Fishing", "Peddling", "Gov't Employee", "Small Industry/Sari-Sari", "Other"])
            food_prod = c3.selectbox("Engaged in Food Production?", ["Yes", "No"])

            c1, c2 = st.columns(2)
            emergency_5k = c1.selectbox("Emergency Cushion: Raise ₱5,000 in 24 hrs?", ["Yes", "No"])
            p4ps_status = c2.selectbox("Active 4Ps Beneficiary?", ["Yes", "No"])

            st.markdown("**Domestic Assets, Utilities & Transportation Owned**")
            c1, c2, c3 = st.columns(3)
            transpo_owned = c1.multiselect("Type of Transportation Owned", ["None", "Bicycle", "Motorcycle / Tricycle", "Private Car / Van", "Motorized Banca / Boat"], default=["None"])
            utilities_avail = c2.multiselect("Utilities / Services Available", ["Grid Electricity", "Solar Power", "Piped Water Connection", "Cellular Signal", "Internet / Broadband", "Garbage Collection Service"], default=["Grid Electricity"])
            appliances_owned = c3.multiselect("Appliances Owned", ["Refrigerator", "Television", "Washing Machine", "Electric Fan", "Gas / Electric Stove", "Air Conditioner"], default=["Electric Fan"])

            st.markdown("---")
            st.markdown("**C2. Household Food Insecurity Assessment (Past 30 Days)**")
            c1, c2, c3 = st.columns(3)
            food_skip = c1.selectbox("In the past 30 days, did any adult member skip a meal or reduce portion size due to lack of money?", ["No", "Yes"])
            food_worry = c2.selectbox("In the past 30 days, did your household worry about running out of food before having money to buy more?", ["No", "Yes"])
            food_fullday = c3.selectbox("In the past 30 days, did any household member go a full day without eating due to lack of food/money?", ["No", "Yes"])

            st.markdown("---")
            st.markdown("**C3. Housing, Built Environment & Indoor Air Risk**")
            c1, c2, c3 = st.columns(3)
            tenure = c1.selectbox("Tenurial / Property Status", ["Residential lot with house", "Residential House without Lot", "Renting", "Shared", "Farm Land", "Informal Settler / Caretaker"])
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

        with t_dec:
            st.markdown("**Module D: Decision-Making Pattern & Community Participation**")
            c1, c2 = st.columns(2)
            dec_expenses = c1.multiselect("Who decides on Family Expenses?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Father", "Mother"])
            dec_health = c2.multiselect("Who decides on Health & Medical Care?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Mother"])

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
            st.markdown("**Module F2: Delivery by Health Personnel & Accredited Health Facility**")
            
            c1, c2 = st.columns(2)
            deliv_personnel_yesno = c1.selectbox("6.1 Delivery handled by trained health personnel?", ["N/A", "Yes", "No"])
            
            if deliv_personnel_yesno == "Yes":
                deliv_personnel_type = c2.selectbox("If yes, specify personnel:", ["RHM (Rural Health Midwife)", "Nurse", "Physician"])
            elif deliv_personnel_yesno == "No":
                deliv_personnel_type = c2.text_input("If no, who handled the delivery (Specify):", "Traditional Birth Attendant / Hilot")
            else:
                deliv_personnel_type = "N/A"

            c1, c2 = st.columns(2)
            deliv_facility_yesno = c1.selectbox("6.2 Delivery handled in an accredited Health Facility?", ["N/A", "Yes", "No"])
            
            if deliv_facility_yesno == "Yes":
                deliv_facility_type = c2.selectbox("If yes, specify accredited facility:", ["Government Hospital", "Private Hospital", "RHU Birthing Center", "Private Lying-in"])
            else:
                deliv_facility_type = "N/A / Home Delivery"

            st.markdown("---")
            st.markdown("**Module F3: Family Planning Assessment (To be answered by Women of Reproductive Age - WRAs)**")
            
            c1, c2 = st.columns(2)
            fp_access = c1.selectbox("1. Couples with access to family planning services?", ["Yes", "No"])
            fp_practice = c2.selectbox("2. Couples practicing family planning?", ["Yes", "No"])

            c1, c2 = st.columns(2)
            if fp_practice == "Yes":
                fp_method = c1.selectbox("If yes, specify method:", ["Pills", "Injectables (DMPA)", "IUD", "Condom", "Subdermal Implant", "BTL (Tubal Ligation)", "NSV (Vasectomy)", "Natural Family Planning (NFP)"])
                fp_reason_no = "N/A"
            else:
                fp_method = "None"
                fp_reason_no = c2.text_input("If no, state reason:", "Desire for pregnancy / Religious belief / Fear of side effects")

            st.markdown("---")
            st.markdown("**Module F4: Mortality Assessment (Jan – Dec)**")
            
            mortality_yesno = st.selectbox("1. With deaths in the family due to preventable diseases (Jan-Dec)?", ["No", "Yes"])
            mortality_records = []

            if mortality_yesno == "Yes":
                st.markdown("*Record details of preventable deaths in the household below (Includes Reason of Death):*")
                for m_i in range(1, 4):
                    st.caption(f"**Mortality Entry #{m_i}**")
                    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
                    m_cause = mc1.text_input(f"Cause of Disease #{m_i}", key=f"m_cause_{m_i}")
                    m_reason = mc2.text_input(f"Reason of Death #{m_i}", key=f"m_reason_{m_i}")
                    m_age = mc3.number_input(f"Age at Death #{m_i}", 0, 120, 0, key=f"m_age_{m_i}")
                    m_sex = mc4.selectbox(f"Sex #{m_i}", ["N/A", "Male", "Female"], key=f"m_sex_{m_i}")
                    m_year = mc5.number_input(f"Year #{m_i}", 2020, 2026, 2025, key=f"m_year_{m_i}")
                    if m_cause:
                        mortality_records.append({"Cause": m_cause, "Reason": m_reason, "Age": m_age, "Sex": m_sex, "Year": m_year})

            st.markdown("---")
            st.markdown("**Module F5: Child Anthropometric & Immunization Profiling (<5 Years)**")
            
            c1, c2, c3 = st.columns(3)
            child_age_m = c1.number_input("Child Age in Months", 0, 60, 12)
            child_wt_kg = c2.number_input("Child Weight (kg)", 0.0, 40.0, 8.5)
            child_ht_cm = c3.number_input("Child Height / Length (cm)", 0.0, 120.0, 72.0)
            
            child_nutr = compute_child_nutrition(child_age_m, child_wt_kg, child_ht_cm)
            st.info(f"📊 **Calculated Nutritional Metrics:** BMI: {child_nutr['BMI']} | Wasting: **{child_nutr['Wasting']}** | Stunting: **{child_nutr['Stunting']}** | Underweight: **{child_nutr['Underweight']}**")

        with t_yakap:
            st.markdown("**Module G: Healthcare Seeking Behavior & PhilHealth YAKAP Access**")
            c1, c2 = st.columns(2)
            primary_facility = c1.selectbox("Primary Facility Consulted First When Ill", ["Barangay Health Station (BHS)", "Rural Health Unit (RHU)", "District / Provincial Hospital", "Private Clinic / Hospital", "Traditional Healer / Faith Healer"])
            delay_reason = c2.selectbox("Main Reason for Delaying Care", ["None / Immediate Care", "Financial Constraints", "Distance / Transport Cost", "Long Waiting Times", "Fear of Diagnosis"])

            c1, c2 = st.columns(2)
            yakap_registered = c1.selectbox("Registered under PhilHealth YAKAP (Konsulta)?", ["Yes", "No", "Uncertain"])
            yakap_availed = c2.selectbox("Has availed FREE First Patient Encounter (FPE) & Meds?", ["Yes", "No", "N/A"])

        if st.form_submit_button("Submit & Save Complete Household Record"):
            # Check primary adult vitals for mapping risk colors
            primary_sys = adults_data[0]["Sys"] if adults_data else 120
            primary_risk = adults_data[0]["Risk"] if adults_data else "Normal"
            
            # Marker color logic: Blue (Flood), Red (HTN), Purple (Dual), Green (Normal)
            if is_flood_prone == "Yes" and primary_sys >= 140:
                marker_color = [192, 38, 211, 230] # Purple Dual
            elif primary_sys >= 140:
                marker_color = [123, 17, 19, 220] # Maroon HTN
            elif is_flood_prone == "Yes":
                marker_color = [37, 99, 235, 220] # Blue Flood
            else:
                marker_color = [34, 197, 94, 200] # Green Normal

            st.session_state.hh_records.append({
                "HH_ID": hh_id, "Barangay": brgy, "Purok": purok, "Date": str(date_survey),
                "Lat": lat, "Lon": lon, "BP": f"{primary_sys}/80", "Risk": primary_risk,
                "Flood_Prone": is_flood_prone, "Color": marker_color,
                "Income": income_cat, "Water": water_source, "Sanitation": toilet_type,
                "Food_Skip": food_skip, "Child_Nutr": child_nutr["Wasting"],
                "Yakap": yakap_registered
            })
            st.success(f"Household record '{hh_id}' saved successfully with complete geotagging and health vitals!")

# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader("Phase 3: Community Qualitative Data Collection (KII & FGD Tools)")
    
    with st.form("phase3_qual_form"):
        st.markdown("**Key Informant Interview (KII) & Focus Group Discussion (FGD) Recorder**")
        c1, c2, c3 = st.columns(3)
        tool_type = c1.selectbox("Tool Type", ["Key Informant Interview (KII)", "Focus Group Discussion (FGD)"])
        informant_type = c2.selectbox("Informant / Group Category", ["Barangay Official", "BHW / BNS", "Barangay Midwife", "Senior Citizens", "4Ps Mothers", "Farmers/Fisherfolk Association"])
        purok_loc = c3.selectbox("Purok / Zone Conducted", [f"Purok {i}" for i in range(1, 8)])

        st.markdown("**Core Qualitative Themes**")
        health_perceptions = st.text_area("1. Perceived Top Health Bottlenecks & Environmental Risks:")
        barriers_care = st.text_area("2. Barriers to Accessing Local RHU/BHS Services:")
        indigenous_practices = st.text_area("3. Local Health Seeking Practices & Beliefs:")

        if st.form_submit_button("Save Qualitative Record"):
            st.session_state.qual_records.append({
                "Type": tool_type, "Informant": informant_type, "Purok": purok_loc,
                "Perceptions": health_perceptions, "Barriers": barriers_care, "Beliefs": indigenous_practices
            })
            st.success("Qualitative field notes saved successfully!")

# MODULE 5: PHASE 4 FULL PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Full PERI Windshield Tool":
    st.subheader("Phase 4: Community PERI Windshield Survey Instrument")
    
    with st.form("phase4_windshield_form"):
        st.markdown("**Windshield Assessment Domains**")
        c1, c2 = st.columns(2)
        purok_obs = c1.selectbox("Purok / Zone Observed", [f"Purok {i}" for i in range(1, 8)])
        obs_date = c2.date_input("Observation Date")

        st.markdown("**Environmental & Infrastructure Observations**")
        c1, c2, c3 = st.columns(3)
        housing_cond = c1.selectbox("Prevailing Housing Condition", ["Dilapidated / Informal", "Mixed Materials", "Sturdy / Concrete"])
        sanitation_obs = c2.selectbox("Visible Environmental Sanitation", ["Uncollected Garbage / Open Dumps", "Clogged Drainage", "Clean / Well Maintained"])
        hazard_obs = c3.selectbox("Dominant Environmental Hazards", ["Flood-Prone / Riverbank", "Stagnant Water / Vector Breeding", "High Traffic / Industrial Dust", "None Observed"])

        notes = st.text_area("Detailed Observational Notes on Community Dynamics & Built Environment:")

        if st.form_submit_button("Save PERI Windshield Record"):
            st.session_state.windshield_records.append({
                "Purok": purok_obs, "Date": str(obs_date), "Housing": housing_cond,
                "Sanitation": sanitation_obs, "Hazards": hazard_obs, "Notes": notes
            })
            st.success("PERI Windshield observation log saved!")

# MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial & Statistical Cross-Tabulation Analytics")
    
    if len(st.session_state.hh_records) == 0:
        st.warning("No survey data stored yet. Please record data under Phase 2 to view spatial analytics.")
    else:
        df_analytics = pd.DataFrame(st.session_state.hh_records)
        
        st.markdown("### 📊 Community Health Analytics Breakdown")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("**Purok Distribution of Surveyed Households**")
            purok_counts = df_analytics["Purok"].value_counts()
            st.bar_chart(purok_counts)

        with c2:
            st.markdown("**Environmental Flood Risk Distribution**")
            flood_counts = df_analytics["Flood_Prone"].value_counts()
            st.bar_chart(flood_counts)

        st.markdown("---")
        st.markdown("### 🧬 Cross-Tabulation: Income Level vs. Food Insecurity")
        crosstab_df = pd.crosstab(df_analytics["Income"], df_analytics["Food_Skip"])
        st.dataframe(crosstab_df, use_container_width=True)

# MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS & ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("Phase 6: Community Health Diagnosis & Prioritized Action Plan")
    
    with st.form("phase6_diag_form"):
        st.markdown("**Health Issue Prioritization (Hanlon Method / Standard Matrix)**")
        c1, c2, c3 = st.columns(3)
        problem_title = c1.text_input("Identified Health Problem / Hazard")
        magnitude = c2.slider("Magnitude of Problem (1–10)", 1, 10, 5)
        severity = c3.slider("Severity / Urgency (1–10)", 1, 10, 5)

        st.markdown("**Comprehensive Action Plan Formulation**")
        c1, c2 = st.columns(2)
        objectives = c1.text_area("Specific, Measurable Objectives (SMART):")
        interventions = c2.text_area("Recommended Community Health Interventions:")

        c1, c2, c3 = st.columns(3)
        responsible_party = c1.text_input("Responsible Lead / Sector")
        timeline = c2.text_input("Target Implementation Timeline")
        budget_req = c3.text_input("Estimated Budget Allocation")

        if st.form_submit_button("Save Action Plan & Diagnosis"):
            st.session_state.diag_records.append({
                "Problem": problem_title, "Magnitude": magnitude, "Severity": severity,
                "Score": magnitude * severity, "Objectives": objectives,
                "Interventions": interventions, "Lead": responsible_party, "Timeline": timeline, "Budget": budget_req
            })
            st.success("Community Diagnosis & Action Plan saved successfully!")

# MODULE 8: DIAGNOSTIC SUMMARY & ANALYTICS
elif menu == "🩺 Diagnostic Summary & Analytics":
    st.subheader("🩺 Diagnostic Summary Dashboard & Field Metrics")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Surveyed HHs", len(st.session_state.hh_records))
    c2.metric("BHB Scorecard", "Recorded" if p1_status else "Pending")
    c3.metric("Qualitative Logs", len(st.session_state.qual_records))
    c4.metric("Action Plans", len(st.session_state.diag_records))

    st.markdown("---")
    st.markdown("### 📌 Active Action Plans Overview")
    if len(st.session_state.diag_records) > 0:
        st.dataframe(pd.DataFrame(st.session_state.diag_records), use_container_width=True)
    else:
        st.info("No action plans created yet. Navigate to Phase 6 to generate community diagnoses.")

# MODULE 9: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Field Data Management, Backup & CSV Export")
    
    st.markdown("Export accumulated field survey records into standardized CSV format for statistical analysis.")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("**Master Household Surveys**")
        if len(st.session_state.hh_records) > 0:
            df_hh = pd.DataFrame(st.session_state.hh_records)
            csv_hh = df_hh.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Household Data (CSV)", csv_hh, "household_records.csv", "text/csv")
        else:
            st.caption("No household records available to export.")

    with c2:
        st.markdown("**BHB Governance Scorecards**")
        if len(st.session_state.gov_records) > 0:
            df_gov = pd.DataFrame(st.session_state.gov_records)
            csv_gov = df_gov.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Governance Data (CSV)", csv_gov, "governance_records.csv", "text/csv")
        else:
            st.caption("No governance records available to export.")

    with c3:
        st.markdown("**Community Action Plans**")
        if len(st.session_state.diag_records) > 0:
            df_diag = pd.DataFrame(st.session_state.diag_records)
            csv_diag = df_diag.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Action Plans (CSV)", csv_diag, "action_plans.csv", "text/csv")
        else:
            st.caption("No action plans available to export.")
