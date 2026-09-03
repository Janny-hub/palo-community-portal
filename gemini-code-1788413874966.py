import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Page Configuration
st.set_page_config(
    page_title="UP Manila - Community Clerks Portal",
    page_icon="🩺",
    layout="wide"
)

# Custom UP Maroon, Green & Gold Styling with Sticky Progress Bar CSS
CSS_STYLE = """<style>
/* Sticky Phase Completion Tracker in Sidebar */
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
    padding: 18px 24px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 24px;
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
.up-navbar-dev {
    color: #93C5FD !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    margin-top: 6px !important;
    letter-spacing: 0.3px;
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

# UP Header Banner
HEADER_HTML = """<div class="up-navbar">
<div class="up-navbar-title">UNIVERSITY OF THE PHILIPPINES MANILA</div>
<div class="up-navbar-sub">School of Health Sciences — Comprehensive Community Health Field Portal</div>
<div class="up-navbar-detail">Integrated System: Spatial Mapping, Geocoding, Analytics & Action Planning (Phases 1–6)</div>
<div class="up-navbar-dev">👨‍💻 Field Enumerators: Aubrey Maye Arrieta | Leila Projimo, PTRP | Jan Art Serna, RMT</div>
</div>"""

st.markdown(HEADER_HTML, unsafe_allow_html=True)

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

# Sidebar - Sticky Progress Tracker
st.sidebar.markdown(f"""
<div class="sticky-progress-container">
    <div style="font-weight: 700; color: #1E293B; font-size: 15px; margin-bottom: 6px;">📊 Phase Completion Tracker</div>
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
                "Barangay": b_name, "Score": total_score, "Rating": rating, "Gaps": gap_summary
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
            enum_name = c3.selectbox("Enumerator Name", ["Aubrey Maye Arrieta", "Leila Projimo, PTRP", "Jan Art Serna, RMT"])
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
                    mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
                    m_cause = mc1.text_input(f"Cause of Disease #{m_i}", key=f"m_cause_{m_i}")
                    m_reason = mc2.text_input(f"Reason of Death #{m_i}", key=f"m_reason_{m_i}")
                    m_age = mc3.number_input(f"Age #{m_i}", 0, 120, 0, key=f"m_age_{m_i}")
                    m_sex = mc4.selectbox(f"Sex #{m_i}", ["Male", "Female"], key=f"m_sex_{m_i}")
                    m_attended = mc5.selectbox(f"Health Worker Attended? #{m_i}", ["Physician", "Nurse", "Midwife", "None / Unattended"], key=f"m_att_{m_i}")
                    m_treatment = mc6.text_input(f"Treatment Used #{m_i}", key=f"m_tx_{m_i}")
                    
                    mortality_records.append({
                        "Cause": m_cause, "Reason_of_Death": m_reason, "Age": m_age, "Sex": m_sex, "Attended": m_attended, "Treatment": m_treatment
                    })

            st.markdown("---")
            st.markdown("**Module F5: Infant & Young Child Profiling & Nutrition Calculator (Profiles for 4 Children)**")
            
            children_profiles = []
            for c_i in range(1, 5):
                st.markdown(f"<div class='adult-card'><strong>Child Member {c_i} Profile & Nutritional Screening (0–59 Months)</strong></div>", unsafe_allow_html=True)
                cc1, cc2, cc3, cc4, cc5 = st.columns(5)
                c_name = cc1.text_input(f"Child {c_i} Name / ID", f"Child {c_i}", key=f"c_name_{c_i}")
                c_sex = cc2.selectbox(f"Child {c_i} Sex", ["Male", "Female"], key=f"c_sex_{c_i}")
                c_age = cc3.number_input(f"Age (Months 0–59) #{c_i}", 0, 59, 12 * c_i if c_i <= 4 else 24, key=f"c_age_{c_i}")
                c_weight = cc4.number_input(f"Weight (kg) #{c_i}", 0.0, 50.0, 3.5 + (c_age * 0.35), step=0.1, key=f"c_wt_{c_i}")
                c_height = cc5.number_input(f"Height (cm) #{c_i}", 0.0, 150.0, 50.0 + (c_age * 1.1), step=0.5, key=f"c_ht_{c_i}")

                child_diag = compute_child_nutrition(c_age, c_weight, c_height)
                st.caption(f"💡 **Child {c_i} Diagnosis:** BMI: `{child_diag['BMI']}` | **Wasting:** `{child_diag['Wasting']}` | **Stunting:** `{child_diag['Stunting']}` | **Underweight:** `{child_diag['Underweight']}`")
                
                children_profiles.append({
                    "Name": c_name, "Sex": c_sex, "Age_Months": c_age, "Weight": c_weight, "Height": c_height, "Diagnosis": child_diag
                })

        with t_yakap:
            st.markdown("**Module H & I: Healthcare Access, PhilHealth YAKAP & Barriers**")
            
            c1, c2 = st.columns(2)
            first_fac = c1.selectbox("Where does the household usually go first when someone becomes sick?", [
                "BHS", "RHU", "Government Hospital", "Private Clinic/Hospital", "Self-medication", "Traditional Healer"
            ])
            travel_time = c2.selectbox("Average one-way travel time to the nearest RHU/health center?", [
                "Less than 15 mins", "15–30 mins", "30–60 mins", "More than 1 hour"
            ])

            c1, c2 = st.columns(2)
            transpo_cost = c1.number_input("Approximate one-way transportation cost to the RHU (₱)", min_value=0.0, value=20.0, step=5.0)
            yakap_reg = c2.selectbox("PhilHealth YAKAP Registration Status", ["Yes, All Members", "Yes, Some Members", "No One Registered", "Unaware of YAKAP"])

            st.markdown("---")
            st.markdown("**Barriers to Healthcare Seeking**")
            health_barriers = st.multiselect("What are the household’s main barriers to seeking medical care?", [
                "Transportation cost",
                "Distance/travel time",
                "Long waiting time",
                "Cost of medicines/laboratory tests",
                "Loss of daily wage/work disruption",
                "Unfriendly staff/lack of trust",
                "Belief that illness will resolve on its own"
            ], default=["Cost of medicines/laboratory tests"])

        submit_master = st.form_submit_button("Save Complete Master Household Record")

        if submit_master:
            primary_bp = adults_data[0]["BP"]
            has_htn = any(a["Sys"] >= 140 or a["Risk"] == "Hypertensive Risk" for a in adults_data)
            
            if has_htn and is_flood_prone == "Yes":
                color_code = [192, 38, 211, 230]
            elif has_htn:
                color_code = [123, 17, 19, 220]
            elif is_flood_prone == "Yes":
                color_code = [37, 99, 235, 220]
            else:
                color_code = [34, 197, 94, 200]

            st.session_state.hh_records.append({
                "HH_ID": hh_id, "Barangay": brgy, "Purok": purok, "Lat": lat, "Lon": lon,
                "Enumerator": enum_name,
                "BP": primary_bp, "Risk": "Hypertensive Risk" if has_htn else "Normal",
                "Flood_Prone": is_flood_prone,
                "Income_Tier": income_cat,
                "Food_Insecurity_Skip": food_skip,
                "Cooking_Fuel": cook_fuel,
                "First_Facility": first_fac,
                "Travel_Time_RHU": travel_time,
                "Transpo_Cost_RHU": transpo_cost,
                "Health_Barriers": ", ".join(health_barriers),
                "Delivery_Personnel": deliv_personnel_type,
                "Delivery_Facility": deliv_facility_type,
                "FP_Practicing": fp_practice,
                "FP_Method": fp_method,
                "Preventable_Mortality": mortality_yesno,
                "Mortality_Details": mortality_records,
                "Children_Profiles": children_profiles,
                "WASH_Level": water_source,
                "House_Type": house_type,
                "Child_Nutritional_Status": children_profiles[0]["Diagnosis"]["Wasting"] if children_profiles else "N/A", 
                "Color": color_code
            })
            st.success(f"Master Household Survey Record {hh_id} stored successfully by {enum_name}!")

# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader("Phase 3: Qualitative Assessment Instruments (Tools 3.1, 3.2, & 3.3 Complete)")
    
    q_tool = st.selectbox("Select Qualitative Assessment Protocol", [
        "Tool 3.1: Key Informant Interview (KII) — Governance & Community Leaders",
        "Tool 3.2: Key Informant Interview (KII) — Frontline Health Personnel",
        "Tool 3.3: Focus Group Discussion (FGD) — Community Members & Beneficiaries"
    ])

    with st.form("phase3_full_form"):
        c1, c2 = st.columns(2)
        resp_info = c1.text_input("Respondent Name / Designation / FGD Participant Group")
        brgy_loc = c2.text_input("Barangay Location")

        st.markdown("---")
        
        if "Tool 3.1" in q_tool:
            st.markdown("**Tool 3.1: Complete Governance & Leadership KII Guide**")
            q31_1 = st.text_area("1. How is health prioritized in the Barangay Annual Investment Plan (AIP) and budget allocation process?")
            q31_2 = st.text_area("2. What structural, legislative, or political bottlenecks hinder the implementation of local health ordinances?")
            q31_3 = st.text_area("3. How effectively is the PhilHealth YAKAP / Konsulta program being integrated into your primary care network?")

        elif "Tool 3.2" in q_tool:
            st.markdown("**Tool 3.2: Complete Frontline Health Personnel KII Guide**")
            q32_1 = st.text_area("1. What are the most persistent operational bottlenecks in daily BHS/RHU operations (e.g., drug supply chain, staffing)?")
            q32_2 = st.text_area("2. How are client referral workflows managed for patients requiring secondary or tertiary hospital care?")

        else:
            st.markdown("**Tool 3.3: Complete Community Focus Group Discussion (FGD) Guide**")
            q33_1 = st.text_area("1. What are the most urgent health concerns, disease threats, or environmental hazards (e.g. flooding) facing families?")
            q33_2 = st.text_area("2. What out-of-pocket costs or financial burdens do residents experience when seeking emergency care?")

        if st.form_submit_button("Save Qualitative Field Record"):
            st.session_state.qual_records.append({
                "Tool": q_tool, "Respondent": resp_info, "Barangay": brgy_loc
            })
            st.success("Qualitative Assessment Protocol Recorded Successfully!")

# MODULE 5: PHASE 4 COMPLETE WINDSHIELD & PERI INSTRUMENT
elif menu == "🔍 Phase 4: Full PERI Windshield Tool":
    st.subheader("Phase 4: Windshield & PERI Environmental Assessment (12 Complete Parameters)")
    
    with st.form("phase4_full_form"):
        c1, c2, c3 = st.columns(3)
        w_brgy = c1.text_input("Barangay Name Evaluated")
        w_purok = c2.selectbox("Zone / Purok Evaluated", [f"Purok {i}" for i in range(1, 8)])
        w_evaluator = c3.selectbox("Lead Assessor / Enumerator", ["Aubrey Maye Arrieta", "Leila Projimo, PTRP", "Jan Art Serna, RMT"])

        st.caption("Rating Scale: `1 = Low Risk / Safe Standard`, `2 = Moderate Hazard`, `3 = Critical Concern / Severe Threat`")
        
        st.markdown("---")
        st.markdown("**Domain 1: Built Environment & Housing Quality**")
        c1, c2, c3 = st.columns(3)
        p1 = c1.slider("1.1 Predominance of light / makeshift housing structures", 1, 3, 1)
        p2 = c2.slider("1.2 Degree of residential overcrowding & poor spacing", 1, 3, 1)
        p3 = c3.slider("1.3 Structural vulnerability to extreme weather & flood hazards", 1, 3, 1)

        st.markdown("**Domain 2: Environmental Sanitation & Flood/Vector Risks**")
        c1, c2 = st.columns(2)
        p4 = c1.slider("2.1 Extent of uncollected garbage & open burning", 1, 3, 1)
        p5 = c2.slider("2.2 Open, unmaintained drainage channels with stagnant water pooling", 1, 3, 1)
        p6 = c1.slider("2.3 Exposure to flood vulnerability & stagnant vector breeding sites", 1, 3, 1)
        p7 = c2.slider("2.4 Presence of unrestrained stray domestic animals", 1, 3, 1)

        st.markdown("**Domain 3: Infrastructure & Geohazards**")
        c1, c2, c3 = st.columns(3)
        p8 = c1.slider("3.1 Unpaved or regularly flooded road conditions", 1, 3, 1)
        p9 = c2.slider("3.2 Absence of functional street lighting", 1, 3, 1)
        p10 = c3.slider("3.3 Distance barrier to potable water supply", 1, 3, 1)

        if st.form_submit_button("Compute Complete PERI Hazard Score"):
            peri_index = sum([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]) / 10.0
            
            if peri_index < 1.50:
                tier = "Category A: Low Vulnerability Tier"
            elif peri_index < 2.30:
                tier = "Category B: Moderate Environmental / Flood Risk"
            else:
                tier = "Category C: Critical Hazard / Severe Flood & Environmental Risk"

            st.session_state.windshield_records.append({
                "Barangay": w_brgy, "Purok": w_purok, "PERI": round(peri_index, 2), "Tier": tier, "Assessor": w_evaluator
            })
            st.warning(f"PERI Composite Index: **{peri_index:.2f} / 3.00** — Action Status: **{tier}**")

# MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial Mapping, Geocoding, & Advanced Statistical Analytics Framework")
    st.caption("Transforming raw community assessment data into high-impact public health intelligence through spatial visualization (GIS) and advanced statistical modeling.")

    t_geo, t_gis, t_stat, t_ref = st.tabs([
        "📍 6.1 Geocoding Protocol",
        "🗺️ 6.2 Multi-Layer GIS Engine",
        "📊 6.3 Advanced Statistical Modeling",
        "📋 Analytics Framework Summary Table"
    ])

    with t_geo:
        st.markdown("**6.1 Spot Mapping & Mobile Address Geocoding Protocol**")
        st.markdown("""
        * **Step 1: Participatory BHW Spot Mapping:** Mobilize Barangay Health Workers (BHWs) to draw baseline community spot maps capturing every residential structure, water source, and health facility.
        * **Step 2: GPS Mobile Geocoding:** Utilizing handheld GPS devices or mobile survey software (KoboToolbox), capture exact latitude and longitude coordinates $(x, y)$ for every surveyed household.
        * **Step 3: GIS Layering:** Upload geocoded survey points into QGIS or ArcGIS to convert static addresses into spatial shapefiles.
        """)

        st.markdown("---")
        st.markdown("**⚡ Interactive Field Tool: Mobile Geocoding Coordinate Validator**")
        c1, c2, c3 = st.columns(3)
        input_lat = c1.number_input("Test Latitude (Y Coordinate)", value=11.1562, format="%.6f")
        input_lon = c2.number_input("Test Longitude (X Coordinate)", value=124.9912, format="%.6f")
        input_acc = c3.number_input("GPS Accuracy Radius (Meters)", value=3.2, step=0.1)

        if input_acc <= 5.0:
            st.success(f"✅ **GPS Lock Validated:** High accuracy ({input_acc}m radius). Ready for household shapefile export into QGIS/ArcGIS.")
        else:
            st.warning(f"⚠️ **Weak GPS Signal:** Accuracy is {input_acc}m. Re-calibrate GPS on KoboToolbox before committing geocode.")

    with t_gis:
        st.markdown("**6.2 Multi-Layer GIS Visualization Framework**")
        
        layer_option = st.radio(
            "Select Active GIS Analytic Layer Framework",
            [
                "Layer 1: Disease Hotspot Mapping (Kernel Density Estimation / Heatmap)",
                "Layer 2: Environmental SDOH Overlay (Unsafe Water, Flood & Waste Hazards)",
                "Layer 3: Food Desert Identification (500m Buffer vs Malnutrition)",
                "Layer 4: Catchment Isochrone Modeling (15 & 30 Min RHU Access / GIDA Areas)"
            ]
        )

        gis_data = pd.DataFrame([
            {"HH_ID": "HH-001", "Lat": 11.1562, "Lon": 124.9912, "Disease": "Hypertension", "WASH": "Unsafe (Level I/Unprotected)", "Flood": "Yes", "Weight": 0.9, "Color": [220, 38, 38, 200]},
            {"HH_ID": "HH-002", "Lat": 11.1568, "Lon": 124.9918, "Disease": "None", "WASH": "Level III Tap", "Flood": "No", "Weight": 0.1, "Color": [34, 197, 94, 200]},
            {"HH_ID": "HH-003", "Lat": 11.1555, "Lon": 124.9905, "Disease": "Type 2 Diabetes", "WASH": "Unsafe (Shallow Well)", "Flood": "Yes", "Weight": 0.8, "Color": [234, 88, 12, 200]},
            {"HH_ID": "HH-004", "Lat": 11.1570, "Lon": 124.9930, "Disease": "Active TB", "WASH": "Level I Well", "Flood": "No", "Weight": 0.95, "Color": [147, 51, 234, 200]},
            {"HH_ID": "HH-005", "Lat": 11.1548, "Lon": 124.9895, "Disease": "Hypertension", "WASH": "Unsafe River/Surface", "Flood": "Yes", "Weight": 0.85, "Color": [220, 38, 38, 200]}
        ])

        view_state = pdk.ViewState(latitude=11.1560, longitude=124.9915, zoom=15, pitch=25)

        if "Layer 1" in layer_option:
            st.caption("🔥 **Layer 1: Disease Hotspot Mapping:** Apply Kernel Density Estimation (KDE) to plot heatmaps of chronic hypertension, diabetes, and active TB clusters across Puroks.")
            kde_layer = pdk.Layer(
                "HeatmapLayer",
                data=gis_data,
                get_position=["Lon", "Lat"],
                get_weight="Weight",
                radiusPixels=60
            )
            st.pydeck_chart(pdk.Deck(layers=[kde_layer], initial_view_state=view_state))

        elif "Layer 2" in layer_option:
            st.caption("🌊 **Layer 2: Environmental SDOH Overlay:** Superimpose disease hotspots over layers of unsafe water sources, flood risk zones, and open waste dumping areas.")
            sdoh_layer = pdk.Layer(
                "ScatterplotLayer",
                data=gis_data,
                get_position=["Lon", "Lat"],
                get_color="Color",
                get_radius=22,
                pickable=True
            )
            st.pydeck_chart(pdk.Deck(layers=[sdoh_layer], initial_view_state=view_state, tooltip={"text": "HH ID: {HH_ID}\nDiagnosed Disease: {Disease}\nWASH Source: {WASH}\nFlood Zone: {Flood}"}))

        elif "Layer 3" in layer_option:
            st.caption("🥗 **Layer 3: Food Desert Identification:** Perform buffer analysis (500-meter walking radius) around fresh food markets versus sari-sari store density.")
            market_point = pd.DataFrame([{"Lat": 11.1560, "Lon": 124.9915, "Name": "Barangay Public Market (Fresh Produce)"}])
            
            market_layer = pdk.Layer(
                "ScatterplotLayer",
                data=market_point,
                get_position=["Lon", "Lat"],
                get_color=[16, 185, 129, 250],
                get_radius=500,
                stroked=True,
                filled=False,
                get_line_color=[16, 185, 129, 250],
                get_line_width=3
            )
            hh_layer = pdk.Layer("ScatterplotLayer", data=gis_data, get_position=["Lon", "Lat"], get_color=[239, 68, 68, 200], get_radius=12)
            st.pydeck_chart(pdk.Deck(layers=[market_layer, hh_layer], initial_view_state=view_state, tooltip={"text": "Fresh Market 500m Buffer Zone (Walking Radius)"}))

        else:
            st.caption("🚑 **Layer 4: Catchment Isochrone Modeling:** Generate 15-minute and 30-minute travel time contours around the BHS/RHU to identify GIDAs.")
            bhs_center = pd.DataFrame([{"Lat": 11.1560, "Lon": 124.9915}])
            
            iso_15 = pdk.Layer("ScatterplotLayer", data=bhs_center, get_position=["Lon", "Lat"], get_color=[59, 130, 246, 100], get_radius=400)
            iso_30 = pdk.Layer("ScatterplotLayer", data=bhs_center, get_position=["Lon", "Lat"], get_color=[245, 158, 11, 60], get_radius=900)
            st.pydeck_chart(pdk.Deck(layers=[iso_30, iso_15], initial_view_state=view_state))
            st.markdown("🔵 **Inner Ring:** 15-Min Travel Isochrone | 🟡 **Outer Ring:** 30-Min Travel Isochrone | 🔴 **Beyond Outer Ring:** GIDA Classification Risk")

    with t_stat:
        st.markdown("**6.3 Statistical Analysis & Advanced Analytical Modeling Plan**")
        
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("<div class='stat-card'><strong>A. Descriptive Analysis (Measuring the Social Gradient)</strong>", unsafe_allow_html=True)
            st.write("Cross-tabulate clinical health outcomes across income quintiles, educational attainment levels, and geographic zones.")
            
            low_inc_htn = st.number_input("Low Income Tier (Q1) - Disease Positive", value=28, key="stat_q1_pos")
            low_inc_norm = st.number_input("Low Income Tier (Q1) - Disease Negative", value=12, key="stat_q1_neg")
            high_inc_htn = st.number_input("High Income Tier (Q5) - Disease Positive", value=8, key="stat_q5_pos")
            high_inc_norm = st.number_input("High Income Tier (Q5) - Disease Negative", value=32, key="stat_q5_neg")

            if (low_inc_norm * high_inc_htn) > 0:
                or_val = (low_inc_htn * high_inc_norm) / (low_inc_norm * high_inc_htn)
                rr_val = (low_inc_htn / (low_inc_htn + low_inc_norm)) / (high_inc_htn / (high_inc_htn + high_inc_norm))
                
                st.metric("Calculated Odds Ratio (OR)", f"{or_val:.2f}")
                st.metric("Calculated Relative Risk (RR)", f"{rr_val:.2f}")
                st.write(f"💡 **Public Health Finding:** Q1 households have **{or_val:.2f} times higher odds** of developing chronic outcomes relative to Q5.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("<div class='stat-card'><strong>B. Advanced Multivariate Modeling</strong>", unsafe_allow_html=True)
            st.write("Social determinants rarely occur in isolation; compounding social risks produce exponential health detriments.")
            
            st.markdown("**1. Principal Component & Factor Analysis (PCA):**")
            w1 = st.slider("PCA Factor Weight: Structural Housing Quality", 0.0, 1.0, 0.35)
            w2 = st.slider("PCA Factor Weight: WASH Infrastructure Level", 0.0, 1.0, 0.40)
            w3 = st.slider("PCA Factor Weight: Monthly Household Income", 0.0, 1.0, 0.25)
            
            pca_index = (w1 * 2.8) + (w2 * 2.5) + (w3 * 2.1)
            st.metric("Composite Household Deprivation Index Score", f"{pca_index:.2f} / 3.00")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='stat-card'><strong>2. Latent Class Analysis (LCA): Discrete Risk Cluster Engine</strong>", unsafe_allow_html=True)
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            st.markdown("🟢 **Class 1: High Income / High Access**\n* Estimated Prevalence: **45%**\n* Piped Water + Concrete Housing\n* Disease Probability: **8.2%**")
        with lc2:
            st.markdown("🟡 **Class 2: Moderate SDOH Risk**\n* Estimated Prevalence: **35%**\n* Level II Faucet + Medium Housing\n* Disease Probability: **22.5%**")
        with lc3:
            st.markdown("🔴 **Class 3: Severe Multi-Risk Cluster**\n* Estimated Prevalence: **20%**\n* Severe Food Insecurity + Housing Instability + No Piped Water\n* Disease Probability: **61.4%**")
        st.markdown("</div>", unsafe_allow_html=True)

    with t_ref:
        st.markdown("**Core Statistical Methodologies & Target Public Health Intelligence Outputs**")
        
        stat_summary_df = pd.DataFrame([
            {
                "Statistical Method": "Descriptive Cross-Tabulation & Odds Ratios (OR / RR)",
                "Input Variables (Survey / GIS)": "Income Quintiles × Hypertension / Diabetes Prevalence",
                "Target Public Health Output": "Quantifies the slope of the social gradient in health across income tiers."
            },
            {
                "Statistical Method": "Factor Analysis (PCA)",
                "Input Variables (Survey / GIS)": "Housing materials, WASH level, Income, Cooking fuel",
                "Target Public Health Output": "Generates a composite 'Barangay Socio-Economic Vulnerability Index'."
            },
            {
                "Statistical Method": "Latent Class Analysis (LCA)",
                "Input Variables (Survey / GIS)": "Co-occurring food insecurity, housing instability, distance barrier",
                "Target Public Health Output": "Identifies multi-risk household clusters requiring integrated LGU social protection."
            }
        ])

        st.table(stat_summary_df)

# MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS MATRIX & ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("Phase 6: Community Diagnosis Matrix & Action Planning Framework")
    st.caption("Converts analytical findings into a structured Community Health Action Plan linking identified health problems directly to underlying SDOH drivers, responsible agencies, and target indicators.")

    t_auto, t_manual, t_matrix = st.tabs([
        "⚡ Automated Community Diagnosis Generator",
        "✍️ Custom Action Plan Builder",
        "📊 Complete Active Action Plan Matrix"
    ])

    default_diag_data = [
        {
            "Identified Health Problem": "High Uncontrolled Hypertension Burden",
            "Root SDOH Driver": "Out-of-pocket medicine costs; lack of BHS supply; high-sodium diet",
            "Target Indicator / Metric": "30% reduction in uncontrolled BP cases in 12 months",
            "Intervention Strategy": "Establish BHS Mobile Medicine Distribution & Salinity Awareness Campaign",
            "Responsible Agency & Budget": "RHU / Barangay Health Board (AIP Line Item 2026)"
        },
        {
            "Identified Health Problem": "Childhood Malnutrition Clustering in Purok 4",
            "Root SDOH Driver": "Food Desert; reliance on sari-sari processed foods; low household income",
            "Target Indicator / Metric": "Zero severe acute malnutrition cases in Purok 4",
            "Intervention Strategy": "Establish Barangay Communal Garden & Supplementary Feeding Program",
            "Responsible Agency & Budget": "Barangay Agriculture & Health Committee / LGU DSWD"
        },
        {
            "Identified Health Problem": "Recurring Diarrheal Outbreaks",
            "Root SDOH Driver": "Level I unprotected water wells; open dumping in drainage canals",
            "Target Indicator / Metric": "100% household transition to Level II/III water access",
            "Intervention Strategy": "Construct Level II Communal Water Tap Station & Enact WASH Ordinance",
            "Responsible Agency & Budget": "Municipal Engineering / LGU WASH Task Force"
        }
    ]

    with t_auto:
        st.markdown("**Automated Community Diagnosis Matrix Engine**")
        st.table(pd.DataFrame(default_diag_data))

        if st.button("Commit Baseline Diagnosis Matrix into Portal Database"):
            st.session_state.diag_records.extend(default_diag_data)
            st.success("Baseline Community Diagnosis Matrix successfully appended to active system records!")

    with t_manual:
        st.markdown("**Custom Action Plan Entry Form**")
        with st.form("phase6_custom_form"):
            p_prob = st.text_input("Identified Health Problem", "e.g., Rising Dengue Incidence in Lowland Puroks")
            p_sdoh = st.text_area("Root SDOH Driver", "e.g., Uncollected solid waste; open drainage channels with stagnant water pooling")
            p_target = st.text_input("Target Indicator / Metric", "e.g., 50% reduction in larval density index within 6 months")
            p_interv = st.text_area("Intervention Strategy", "e.g., Weekly Clean-up Drives (Oplan Taob), Drain De-clogging & Larvicide Application")
            p_agency = st.text_input("Responsible Agency & Budget", "e.g., Barangay Environment & Sanitation Committee (AIP Line Item 2026)")

            if st.form_submit_button("Save Action Plan Entry"):
                st.session_state.diag_records.append({
                    "Identified Health Problem": p_prob,
                    "Root SDOH Driver": p_sdoh,
                    "Target Indicator / Metric": p_target,
                    "Intervention Strategy": p_interv,
                    "Responsible Agency & Budget": p_agency
                })
                st.success("Custom Action Plan Item saved!")

    with t_matrix:
        st.markdown("**Active Community Diagnosis & Health Action Plan Matrix**")
        if len(st.session_state.diag_records) > 0:
            diag_df = pd.DataFrame(st.session_state.diag_records)
            st.table(diag_df)
        else:
            st.info("No action plan matrix entries stored yet. Use the automated generator or custom entry builder above.")

# MODULE 8: AUTOMATED COMMUNITY DIAGNOSIS
elif menu == "🩺 Diagnostic Summary & Analytics":
    st.subheader("Automated Community Health Diagnosis & Environmental Risk Analytics")
    tot = len(st.session_state.hh_records)
    
    if tot == 0:
        st.info("No household survey data recorded yet. Enter data in Phase 2 to view automated diagnostic findings.")
    else:
        htn_cases = sum(1 for r in st.session_state.hh_records if r.get("Risk") == "Hypertensive Risk")
        flood_cases = sum(1 for r in st.session_state.hh_records if r.get("Flood_Prone") == "Yes")
        htn_rate = (htn_cases / tot) * 100
        flood_rate = (flood_cases / tot) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Surveyed Households", tot)
        c2.metric("Hypertension Risk Rate", f"{htn_rate:.1f}%")
        c3.metric("Flood-Prone Households Detected", f"{flood_rate:.1f}%")

        st.markdown("---")
        st.markdown("**Automated Health & Environmental Diagnostic Findings:**")
        if htn_rate >= 15.0:
            st.error(f"🔴 **Cardiovascular Health Risk:** High prevalence of hypertensive risk ({htn_rate:.1f}%) identified across surveyed households.")
        if flood_rate >= 20.0:
            st.warning(f"🌊 **Environmental Hazard Risk:** Significant proportion ({flood_rate:.1f}%) of households detected in flood-prone zones. Prioritize vector control (dengue/leptospirosis) and disaster preparedness planning.")

# MODULE 9: EXPORT MASTER DATA
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Export Full Assessment Datasets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(st.session_state.hh_records) > 0:
            df_out = pd.DataFrame(st.session_state.hh_records)
            st.download_button("Download Phase 2 Master Survey Data (CSV)", df_out.to_csv(index=False).encode('utf-8'), "UPM_SHS_Phase2_Master.csv", "text/csv")
        else:
            st.caption("No household records available to export yet.")
            
    with col2:
        if len(st.session_state.diag_records) > 0:
            df_diag_out = pd.DataFrame(st.session_state.diag_records)
            st.download_button("Download Phase 6 Action Plan Matrix (CSV)", df_diag_out.to_csv(index=False).encode('utf-8'), "UPM_SHS_Phase6_Action_Plan.csv", "text/csv")
        else:
            st.caption("No action plan records available to export yet.")
