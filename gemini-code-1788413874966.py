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

# Custom UP Maroon & Gray Styling
st.markdown("""
    <style>
    .up-navbar {
        background-color: #7B1113;
        border-bottom: 4px solid #4A5568;
        padding: 16px 24px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .up-navbar img {
        height: 75px;
        width: auto;
    }
    .up-navbar-title {
        color: #FFFFFF !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        line-height: 1.2;
    }
    .up-navbar-sub {
        color: #E2E8F0 !important;
        font-size: 14px !important;
        margin: 2px 0 0 0 !important;
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
    </style>
""", unsafe_allow_html=True)

# UP Manila Header Banner
st.markdown("""
    <div class="up-navbar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/University_of_the_Philippines_Manila_logo.svg/1200px-University_of_the_Philippines_Manila_logo.svg.png" alt="UP Manila Seal">
        <div>
            <div class="up-navbar-title">UNIVERSITY OF THE PHILIPPINES MANILA</div>
            <div class="up-navbar-sub">School of Health Sciences — Comprehensive Community Health Field Portal</div>
            <div style="font-size: 12px; color: #CBD5E1; margin-top: 3px;">Full System Framework: Complete Protocols for Phases 1, 2, 3, & 4</div>
        </div>
    </div>
""", unsafe_allow_html=True)

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

# Portal Navigation Bar
st.sidebar.markdown("### 🌐 Portal Navigation")
menu = st.sidebar.radio(
    "Select Field Module",
    [
        "🗺️ Interactive Spot Map", 
        "📋 Phase 1: Full Governance Scorecard", 
        "🏠 Phase 2: Master Household Survey", 
        "🗣️ Phase 3: Qualitative Field Tools", 
        "🔍 Phase 4: Full PERI Windshield Tool", 
        "🩺 Diagnostic Summary & Analytics",
        "💾 Data Management & Export"
    ]
)

# ------------------------------------------------------------------------------
# MODULE 1: INTERACTIVE SPOT MAP
# ------------------------------------------------------------------------------
if menu == "🗺️ Interactive Spot Map":
    st.subheader("📍 Interactive Barangay Health & Risk Spot Map")
    if len(st.session_state.hh_records) == 0:
        st.info("No household survey records stored yet. Showing default baseline map.")
        map_df = pd.DataFrame([
            {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk": "Hypertensive Risk", "Color": [123, 17, 19, 220]},
            {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk": "Normal", "Color": [34, 197, 94, 200]}
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_m, col_f = st.columns([3, 1])
    with col_f:
        st.markdown("**Map Controls**")
        puroks = list(map_df["Purok"].unique())
        sel_puroks = st.multiselect("Filter Puroks", options=puroks, default=puroks)
        st.markdown("---")
        st.markdown("**Legend:**\n🔴 Maroon: Hypertensive/Risk\n🟢 Green: Normal Vitals")

    filt_df = map_df[map_df["Purok"].isin(sel_puroks)]
    with col_m:
        view = pdk.ViewState(
            latitude=filt_df["Lat"].mean() if len(filt_df) > 0 else 11.1560,
            longitude=filt_df["Lon"].mean() if len(filt_df) > 0 else 124.9915,
            zoom=15, pitch=30
        )
        layer = pdk.Layer("ScatterplotLayer", data=filt_df, get_position=["Lon", "Lat"], get_color="Color", get_radius=14, pickable=True)
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip={"text": "HH: {HH_ID}\nPurok: {Purok}\nBP: {BP}\nRisk: {Risk}"}))

# ------------------------------------------------------------------------------
# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD (COMPLETE 100-POINT MATRIX)
# ------------------------------------------------------------------------------
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
            g1_2 = c2.number_input("1.2 Mandatory multi-sectoral reps active (NGO, BHW, Senior, Youth) (0–5 pts)", 0, 5, 0)

            st.markdown("**Domain 2: Meeting Regularity & Quorum Compliance (Max 20 Points)**")
            c1, c2, c3 = st.columns(3)
            g2_1 = c1.number_input("2.1 Quarterly meetings in past 12 mos (3 pts/meeting, Max 12 pts)", 0, 12, 0)
            g2_2 = c2.number_input("2.2 Official quorum met during every meeting (0–4 pts)", 0, 4, 0)
            g2_3 = c3.number_input("2.3 Signed minutes and attendance records filed (0–4 pts)", 0, 4, 0)

            st.markdown("**Domain 3: Health Policies & Ordinance Enactment (Max 20 Points)**")
            c1, c2, c3 = st.columns(3)
            g3_1 = c1.number_input("3.1 Local health/sanitation ordinances enacted in past 24 mos (0–10 pts)", 0, 10, 0)
            g3_2 = c2.number_input("3.2 Active task force enforcing local health laws (0–5 pts)", 0, 5, 0)
            g3_3 = c3.number_input("3.3 Local policies aligned with DOH UHC mandates (0–5 pts)", 0, 5, 0)

        with t3:
            st.markdown("**Domain 4: AIP Budget Allocation & Financial Execution (Max 20 Points)**")
            c1, c2, c3 = st.columns(3)
            g4_1 = c1.number_input("4.1 Dedicated health line-items in AIP (0–8 pts)", 0, 8, 0)
            g4_2 = c2.number_input("4.2 Budget for BHW honoraria, emergency response, medicines (0–6 pts)", 0, 6, 0)
            g4_3 = c3.number_input("4.3 Health budget execution rate >75% last fiscal year (0–6 pts)", 0, 6, 0)

            st.markdown("**Domain 5: Health Reporting & Transparency (Max 15 Points)**")
            c1, c2, c3 = st.columns(3)
            g5_1 = c1.number_input("5.1 Quarterly health reports submitted to MHO/RHU (0–8 pts)", 0, 8, 0)
            g5_2 = c2.number_input("5.2 Health status presented during Barangay Assemblies (0–4 pts)", 0, 4, 0)
            g5_3 = c3.number_input("5.3 Barangay Health Spot Map maintained at BHS (0–3 pts)", 0, 3, 0)

            st.markdown("**Domain 6: Working Committees & Mobilization (Max 15 Points)**")
            c1, c2, c3 = st.columns(3)
            g6_1 = c1.number_input("6.1 Active technical working committees (Dengue, WASH, Nutrition) (0–6 pts)", 0, 6, 0)
            g6_2 = c2.number_input("6.2 Monthly committee reports to BHB (0–6 pts)", 0, 6, 0)
            g6_3 = c3.number_input("6.3 Community health mobilization events completed in past year (0–3 pts)", 0, 3, 0)

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

# ------------------------------------------------------------------------------
# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY (FULLY COMPREHENSIVE)
# ------------------------------------------------------------------------------
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader("Phase 2: Master Household Survey Instrument (Tool 2.1 Complete)")
    
    with st.form("phase2_complete_form"):
        t_meta, t_vitals, t_socio, t_dec, t_morb, t_mch, t_yakap = st.tabs([
            "📋 Metadata & Roster",
            "🩺 Adult Vitals (Adults 1–5)",
            "🌾 Socio-Econ, Assets & WASH",
            "🤝 Decision-Making Patterns",
            "🤒 Complete Morbidity & Chronic Care",
            "👶 Complete Maternal, EPI & Nutrition",
            "🏥 PhilHealth YAKAP & Access"
        ])

        # TAB 1: METADATA
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
            enum_name = c3.text_input("Enumerator Name")
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

        # TAB 2: ADULT VITALS (5 ADULTS)
        with t_vitals:
            st.markdown("**Module B: Adult & Ill Member Physical Screening (Objective Vitals for Adults 1 to 5)**")
            adults_data = []
            
            for i in range(1, 6):
                st.markdown(f"<div class='adult-card'><strong>Adult Member {i} Profiling & Physical Vitals</strong></div>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns(5)
                a_name = c1.text_input(f"Adult {i} Name / Initials", key=f"a_name_{i}")
                a_age = c2.number_input(f"Adult {i} Age", 18, 120, 30, key=f"a_age_{i}")
                a_sys = c3.number_input(f"Adult {i} Systolic BP", 50, 250, 120, key=f"a_sys_{i}")
                a_dia = c4.number_input(f"Adult {i} Diastolic BP", 30, 150, 80, key=f"a_dia_{i}")
                a_spo2 = c5.number_input(f"Adult {i} SpO2 (%)", 50, 100, 98, key=f"a_spo2_{i}")

                c1, c2, c3, c4 = st.columns(4)
                a_pulse = c1.number_input(f"Adult {i} Pulse Rate (bpm)", 30, 200, 75, key=f"a_pulse_{i}")
                a_temp = c2.number_input(f"Adult {i} Temp (°C)", 30.0, 42.0, 36.5, key=f"a_temp_{i}")
                a_symptoms = c3.multiselect(f"Adult {i} Current Complaints", ["None", "Headache", "Cough", "Chest Pain", "Shortness of Breath"], default=["None"], key=f"a_sym_{i}")
                a_risk = c4.selectbox(f"Adult {i} Risk Assessment", ["Normal", "Hypertensive Risk", "Hypoxemic (<95%)"], key=f"a_risk_{i}")

                adults_data.append({
                    "ID": f"Adult {i}", "Name": a_name, "Age": a_age, "BP": f"{a_sys}/{a_dia}",
                    "Sys": a_sys, "SpO2": a_spo2, "Pulse": a_pulse, "Temp": a_temp, "Risk": a_risk
                })

        # TAB 3: SOCIO-ECONOMIC & WASH
        with t_socio:
            st.markdown("**C1. Livelihood & Economic Stability**")
            c1, c2, c3 = st.columns(3)
            income_cat = c1.selectbox("Average Family Income / Month", ["≤ ₱10,000", "₱10,001–₱30,000", "₱30,001–₱45,000", "> ₱50,000"])
            livelihood = c2.selectbox("Primary Livelihood Source", ["Farming (Owned)", "Farming (Tenanted)", "Laborer", "Carpentry", "Fishing", "Peddling", "Gov't Employee", "Small Industry/Sari-Sari", "Other"])
            food_prod = c3.selectbox("Engaged in Food Production?", ["Yes", "No"])

            c1, c2 = st.columns(2)
            emergency_5k = c1.selectbox("Emergency Cushion: Raise ₱5,000 in 24 hrs?", ["Yes", "No"])
            p4ps_status = c2.selectbox("Active 4Ps Beneficiary?", ["Yes", "No"])

            st.markdown("**C2. Housing & Asset Ownership**")
            c1, c2, c3 = st.columns(3)
            tenure = c1.selectbox("Tenurial / Property Status", ["Residential lot with house", "Residential House without Lot", "Renting", "Shared", "Farm Land", "Informal Settler / Caretaker"])
            house_type = c2.selectbox("Housing Construction Type", ["Light (Nipa, bamboo, cogon)", "Medium (Wooden floors/walls, G.I. roof)", "Heavy / Permanent (Concrete/hardwood)"])
            cook_fuel = c3.selectbox("Indoor Cooking Fuel", ["LPG", "Electricity", "Charcoal / Wood (Indoor)", "Kerosene"])

            st.markdown("**C3. Household Food Security (USDA 30-Day Screening)**")
            c1, c2, c3 = st.columns(3)
            meal_freq = c1.selectbox("Meal Frequency & Adequacy", ["4+ times/day (Adequate)", "3 times/day (Adequate)", "3 times/day (Inadequate)", "2 times/day", "1 time/day"])
            usda_worried = c2.selectbox("Worried about food running out?", ["Yes", "No"])
            usda_skipped = c3.selectbox("Adult skipped meal/reduced portion due to money?", ["Yes", "No"])

            st.markdown("**C4. WASH Infrastructure & Environmental Health**")
            c1, c2, c3 = st.columns(3)
            water_source = c1.selectbox("Drinking Water Source Level", ["Level 1: Protected Well / Spring", "Level 2: Piped network & communal faucet", "Level 3: Individual household tap", "Unsafe: Shallow Well / River / Surface", "Commercial Refill Station"])
            toilet_type = c2.selectbox("Sanitation / Toilet Facility Type", ["Pour/Flush to Septic Tank", "Ventilated Improved Pit (VIP) Latrine", "Open Defecation / None"])
            solid_disposal = c3.selectbox("Solid Waste Disposal Method", ["Municipal/Barangay Collection", "Composting", "Burying", "Burning (Siga)", "Open Dumping", "River Disposal"])

        # TAB 4: DECISIONS
        with t_dec:
            st.markdown("**Module D: Decision-Making Pattern & Community Participation**")
            c1, c2 = st.columns(2)
            dec_expenses = c1.multiselect("Who decides on Family Expenses?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Father", "Mother"])
            dec_health = c2.multiselect("Who decides on Health & Medical Care?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Mother"])

        # TAB 5: COMPLETE MORBIDITY & CHRONIC CARE (EXPANDED FULL MODULE E)
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

            st.markdown("**Module E3: Healthcare Utilization, Hospitalization & Disability**")
            c1, c2, c3 = st.columns(3)
            med_source = c1.selectbox("Primary Maintenance Medicine Source", ["Free from BHS / RHU", "Out-of-pocket Private Pharmacy", "Mixed (BHS + Pharmacy)", "Unable to Buy / Non-compliant"])
            hosp_count = c2.number_input("Hospital Admissions in Family (Past 12 Mos)", 0, 10, 0)
            pwd_count = c3.number_input("Persons with Disability (PWD) in Household", 0, 10, 0)

            st.markdown("**Module E4: Household Mortality (Past 12 Months)**")
            has_death = st.selectbox("Were there any deaths in the household in the past 12 months?", ["No", "Yes"])
            if has_death == "Yes":
                c1, c2, c3 = st.columns(3)
                d_age = c1.number_input("Deceased Age", 0, 120, 50)
                d_cause = c2.text_input("Cause of Death (Medical/Suspected)")
                d_attended = c3.selectbox("Attended by Health Worker / Physician?", ["Yes", "No"])

        # TAB 6: COMPLETE MATERNAL, EPI & NUTRITION (EXPANDED FULL MODULE F)
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

            c1, c2 = st.columns(2)
            deliv_place = c1.selectbox("Place of Delivery", ["N/A", "Barangay Health Station / Lying-In", "Rural Health Unit / District Hospital", "Tertiary Public Hospital", "Private Hospital / Clinic", "Home Delivery"])
            deliv_attendant = c2.selectbox("Delivery Attendant", ["N/A", "Physician", "Nurse", "Midwife", "Traditional Birth Attendant (Hilot)", "Unattended"])

            fp_method = st.selectbox("Current Family Planning / Contraceptive Method (Women 15-49)", ["None / Desires Pregnancy", "Pills (POP/COC)", "DMPA Injectable", "Subdermal Implant", "IUD", "BTL / Vasectomy", "Condom", "Natural (LAM/BBT/SDM)", "Unmet Need for FP"])

            st.markdown("---")
            st.markdown("**Module F2: Expanded Program on Immunization (EPI) & Child Preventive Health**")
            c1, c2, c3 = st.columns(3)
            epi_status = c1.selectbox("Child Immunization Status (0-12 mos)", ["N/A - No Infant", "Fully Immunized Child (FIC)", "Partially Immunized / Ongoing", "Unimmunized"])
            vit_a = c2.selectbox("Vitamin A Supplementation in Past 6 Mos (6-59 mos)", ["N/A", "Yes", "No"])
            deworming = c3.selectbox("Deworming Pill Received in Past 6 Mos (12-59 mos)", ["N/A", "Yes", "No"])

            st.markdown("---")
            st.markdown("**Module F3: Infant & Young Child Feeding (IYCF)**")
            c1, c2, c3 = st.columns(3)
            bf_1hr = c1.selectbox("Initiated Breastfeeding within 1 Hour of Birth?", ["N/A", "Yes", "No"])
            excl_bf = c2.selectbox("Exclusively Breastfed for First 6 Months?", ["N/A", "Yes", "No"])
            comp_feeding = c3.selectbox("Complementary Feeding Introduced at 6 Months?", ["N/A", "Yes", "No", "Early (<6 mos)", "Late (>6 mos)"])

            st.markdown("---")
            st.markdown("**Module F4: Objective Child Anthropometry & Nutritional Status Calculator (0–59 Months)**")
            c1, c2, c3, c4 = st.columns(4)
            c_id = c1.text_input("Child Member ID / Name", "Child 1")
            c_age = c2.number_input("Child Age (Months: 0–59)", 0, 59, 24)
            c_weight = c3.number_input("Weight (kg)", 0.0, 50.0, 11.5, step=0.1)
            c_height = c4.number_input("Height (cm)", 0.0, 150.0, 85.0, step=0.5)

            child_diag = compute_child_nutrition(c_age, c_weight, c_height)
            st.info(f"💡 **Automated Child Nutritional Diagnosis:** BMI: {child_diag['BMI']} | **Wasting:** {child_diag['Wasting']} | **Stunting:** {child_diag['Stunting']} | **Underweight:** {child_diag['Underweight']}")

        # TAB 7: PHILHEALTH YAKAP & ACCESS
        with t_yakap:
            st.markdown("**Module H & I: PhilHealth YAKAP & 3-Delay Framework**")
            c1, c2 = st.columns(2)
            yakap_reg = c1.selectbox("PhilHealth YAKAP Registration Status", ["Yes, All Members", "Yes, Some Members", "No One Registered", "Unaware of YAKAP"])
            first_fac = c2.selectbox("First Facility Visited When Sick", ["BHS", "RHU", "Gov't Hospital", "Private Clinic", "Pharmacy/Self-Care", "Traditional Healer (Albularyo)"])

            delay1 = st.multiselect("Delay 1: Delays in Deciding to Seek Care", ["Failure to recognize danger signs", "Lack of money for care/transport", "No one to care for home/children", "Belief illness will resolve on its own"])
            delay2 = st.multiselect("Delay 2: Delays in Reaching Care Facility", ["Excessive distance from home", "Lack of transport / High travel cost", "Poor road conditions"])
            delay3 = st.multiselect("Delay 3: Delays in Receiving Quality Care at Facility", ["Long waiting times", "Shortage of medicines/supplies", "Lack of skilled health staff", "Incompatible clinic hours"])

        submit_master = st.form_submit_button("Save Complete Master Household Record")

        if submit_master:
            primary_bp = adults_data[0]["BP"]
            has_htn = any(a["Sys"] >= 140 or a["Risk"] == "Hypertensive Risk" for a in adults_data)
            color_code = [123, 17, 19, 220] if has_htn else [34, 197, 94, 200]

            st.session_state.hh_records.append({
                "HH_ID": hh_id, "Barangay": brgy, "Purok": purok, "Lat": lat, "Lon": lon,
                "BP": primary_bp, "Risk": "Hypertensive Risk" if has_htn else "Normal",
                "Child_Nutritional_Status": child_diag["Wasting"], "Color": color_code
            })
            st.success(f"Master Household Survey Record {hh_id} stored successfully!")

# ------------------------------------------------------------------------------
# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS (COMPLETE INTERVIEW GUIDES)
# ------------------------------------------------------------------------------
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
            q31_4 = st.text_area("4. What formal mechanisms exist for inter-agency collaboration (RHU, DSWD, CSOs) during health outbreaks or emergencies?")
            q31_5 = st.text_area("5. What strategies are currently utilized to foster active community mobilization and participation in health programs?")

        elif "Tool 3.2" in q_tool:
            st.markdown("**Tool 3.2: Complete Frontline Health Personnel KII Guide**")
            q32_1 = st.text_area("1. What are the most persistent operational bottlenecks in daily BHS/RHU operations (e.g., drug supply chain, staffing, equipment)?")
            q32_2 = st.text_area("2. How are client referral workflows managed for patients requiring secondary or tertiary hospital care, and where do delays occur?")
            q32_3 = st.text_area("3. What specific barriers prevent complete YAKAP / Konsulta registration and health risk assessment profiling among residents?")
            q32_4 = st.text_area("4. What factors contribute most to client delays in seeking care (Delay 1), reaching facilities (Delay 2), or receiving care (Delay 3)?")
            q32_5 = st.text_area("5. What support, training, or honoraria adjustments are required to strengthen BHW and frontline health worker performance?")

        else:
            st.markdown("**Tool 3.3: Complete Community Focus Group Discussion (FGD) Guide**")
            q33_1 = st.text_area("1. What are the most urgent health concerns, disease threats, or safety hazards currently facing families in this barangay?")
            q33_2 = st.text_area("2. What out-of-pocket costs or financial burdens do residents experience when seeking medical consultation or emergency care?")
            q33_3 = st.text_area("3. How do community members evaluate the accessibility, provider attitude, and service quality at the local BHS / RHU?")
            q33_4 = st.text_area("4. What environmental, water, or sanitation risks (e.g., uncollected garbage, open drainage) pose the greatest threat to family health?")
            q33_5 = st.text_area("5. What concrete health projects or government interventions would community members prioritize for immediate implementation?")

        if st.form_submit_button("Save Qualitative Field Record"):
            st.session_state.qual_records.append({
                "Tool": q_tool, "Respondent": resp_info, "Barangay": brgy_loc
            })
            st.success("Qualitative Assessment Protocol Recorded Successfully!")

# ------------------------------------------------------------------------------
# MODULE 5: PHASE 4 COMPLETE WINDSHIELD & PERI INSTRUMENT
# ------------------------------------------------------------------------------
elif menu == "🔍 Phase 4: Full PERI Windshield Tool":
    st.subheader("Phase 4: Windshield & PERI Environmental Assessment (12 Complete Parameters)")
    
    with st.form("phase4_full_form"):
        c1, c2, c3 = st.columns(3)
        w_brgy = c1.text_input("Barangay Name Evaluated")
        w_purok = c2.selectbox("Zone / Purok Evaluated", [f"Purok {i}" for i in range(1, 8)])
        w_evaluator = c3.text_input("Lead Assessor / Community Clerk")

        st.caption("Rating Scale: `1 = Low Risk / Safe Standard`, `2 = Moderate Hazard`, `3 = Critical Concern / Severe Threat`")
        
        st.markdown("---")
        st.markdown("**Domain 1: Built Environment & Housing Quality**")
        c1, c2, c3 = st.columns(3)
        p1 = c1.slider("1.1 Predominance of light / makeshift / dilapidated housing structures", 1, 3, 1)
        p2 = c2.slider("1.2 Degree of residential overcrowding & insufficient inter-house spacing", 1, 3, 1)
        p3 = c3.slider("1.3 Structural vulnerability to extreme weather, typhoons, or fire hazard", 1, 3, 1)

        st.markdown("**Domain 2: Environmental Sanitation & Vector Risks**")
        c1, c2 = st.columns(2)
        p4 = c1.slider("2.1 Extent of uncollected household garbage & visible open burning (siga)", 1, 3, 1)
        p5 = c2.slider("2.2 Open, unmaintained drainage channels with stagnant blackwater pooling", 1, 3, 1)
        p6 = c1.slider("2.3 Density of potential vector breeding grounds (dengue, leptospirosis risks)", 1, 3, 1)
        p7 = c2.slider("2.4 Presence of unrestrained, unvaccinated stray domestic animals roaming public spaces", 1, 3, 1)

        st.markdown("**Domain 3: Physical Infrastructure & Public Access Services**")
        c1, c2, c3 = st.columns(3)
        p8 = c1.slider("3.1 Unpaved, flooded, or impassable road conditions limiting access", 1, 3, 1)
        p9 = c2.slider("3.2 Absence of functional street lighting along primary pedestrian thoroughfares", 1, 3, 1)
        p10 = c3.slider("3.3 Distance / accessibility barrier to potable water supply refill stations", 1, 3, 1)

        st.markdown("**Domain 4: Geohazards & Community Safety Hazards**")
        c1, c2 = st.columns(2)
        p11 = c1.slider("4.1 Direct settlement exposure to geohazards (riverbanks, steep slopes, flood zones)", 1, 3, 1)
        p12 = c2.slider("4.2 Hazardous electrical wiring (illegal taps, low-hanging lines, exposed cables)", 1, 3, 1)

        if st.form_submit_button("Compute Complete PERI Hazard Score"):
            peri_index = sum([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12]) / 12.0
            
            if peri_index < 1.50:
                tier = "Category A: Low Vulnerability Tier"
            elif peri_index < 2.30:
                tier = "Category B: Moderate Environmental Concern Tier"
            else:
                tier = "Category C: Critical Hazard / Urgent Mitigation Required"

            st.session_state.windshield_records.append({
                "Barangay": w_brgy, "Purok": w_purok, "PERI": round(peri_index, 2), "Tier": tier
            })
            st.warning(f"PERI Composite Index: **{peri_index:.2f} / 3.00** — Action Status: **{tier}**")

# ------------------------------------------------------------------------------
# MODULE 6: AUTOMATED COMMUNITY DIAGNOSIS
# ------------------------------------------------------------------------------
elif menu == "🩺 Diagnostic Summary & Analytics":
    st.subheader("Automated Community Health Diagnosis & Analytics")
    tot = len(st.session_state.hh_records)
    if tot == 0:
        st.info("No household survey data recorded yet. Enter data in Phase 2 to view diagnostic findings.")
    else:
        htn_cases = sum(1 for r in st.session_state.hh_records if r.get("Risk") == "Hypertensive Risk")
        htn_rate = (htn_cases / tot) * 100
        
        c1, c2 = st.columns(2)
        c1.metric("Total Surveyed Households", tot)
        c2.metric("Community Hypertension Rate", f"{htn_rate:.1f}%")

        st.markdown("---")
        st.markdown("**Automated Health System Diagnostic Statements:**")
        if htn_rate >= 15.0:
            st.error(f"🔴 **Cardiovascular Health Risk:** High prevalence of hypertensive risk ({htn_rate:.1f}%) identified across surveyed households. Initiate regular BHS monitoring and facilitate PhilHealth YAKAP enrollment.")

# ------------------------------------------------------------------------------
# MODULE 7: EXPORT MASTER DATA
# ------------------------------------------------------------------------------
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Export Full Assessment Datasets")
    if len(st.session_state.hh_records) > 0:
        df_out = pd.DataFrame(st.session_state.hh_records)
        st.download_button("Download Phase 2 Master Survey Data (CSV)", df_out.to_csv(index=False).encode('utf-8'), "UPM_SHS_Phase2_Master.csv", "text/csv")
    else:
        st.caption("No household records available to export yet.")
