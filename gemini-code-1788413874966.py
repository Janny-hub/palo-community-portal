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
            <div style="font-size: 12px; color: #CBD5E1; margin-top: 3px;">Tool 2.1 Master Household Survey & Windshield Assessment System</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Automated Child Nutritional Calculator Function
def compute_child_nutrition(age_months, weight_kg, height_cm):
    if height_cm <= 0 or weight_kg <= 0:
        return {"Wasting": "Invalid Input", "Stunting": "Invalid Input", "Underweight": "Invalid Input"}
    
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    
    # Weight-for-Height / Wasting (BMI Proxy)
    if bmi < 13.5:
        wasting = "Severely Wasted / SAM"
    elif bmi < 14.5:
        wasting = "Wasted / MAM"
    elif bmi > 18.0:
        wasting = "Overweight / Obese Risk"
    else:
        wasting = "Normal Weight-for-Height"

    # Height-for-Age / Stunting
    exp_height = 50.0 + (age_months * 1.15)
    if height_cm < (exp_height * 0.85):
        stunting = "Severely Stunted"
    elif height_cm < (exp_height * 0.92):
        stunting = "Stunted"
    else:
        stunting = "Normal Height-for-Age"

    # Weight-for-Age / Underweight
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

# Session State Initializations
if "hh_records" not in st.session_state:
    st.session_state.hh_records = []
if "gov_records" not in st.session_state:
    st.session_state.gov_records = []
if "qual_records" not in st.session_state:
    st.session_state.qual_records = []
if "windshield_records" not in st.session_state:
    st.session_state.windshield_records = []

# Sidebar Website Portal Navigation
st.sidebar.markdown("### 🌐 Portal Navigation")
menu = st.sidebar.radio(
    "Select Portal Module",
    [
        "🗺️ Interactive Spot Map", 
        "📋 Phase 1: BHB Governance Scorecard", 
        "🏠 Phase 2: Complete Household Survey", 
        "🗣️ Phase 3: Qualitative Field Tools", 
        "🔍 Phase 4: Full Windshield Assessment", 
        "🩺 Diagnostic Summary & Analytics",
        "💾 Data Management & Export"
    ]
)

# ------------------------------------------------------------------------------
# MODULE 1: SPOT MAP
# ------------------------------------------------------------------------------
if menu == "🗺️ Interactive Spot Map":
    st.subheader("📍 Interactive Barangay Health & Risk Spot Map")
    if len(st.session_state.hh_records) == 0:
        st.info("No household survey records currently stored. Showing default baseline preview.")
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
# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD
# ------------------------------------------------------------------------------
elif menu == "📋 Phase 1: BHB Governance Scorecard":
    st.subheader("Phase 1: Barangay Health Board (BHB) Governance Scorecard")
    with st.form("phase1_form"):
        st.markdown("**1. Governance Structure & Meetings**")
        c1, c2 = st.columns(2)
        sc1 = c1.number_input("1.1 Executive Order reconstituting BHB (Max 5)", 0, 5, 0)
        sc2 = c2.number_input("1.2 Multi-sectoral representation (Max 5)", 0, 5, 0)
        sc3 = c1.number_input("2.1 Quarterly meetings held (Max 12)", 0, 12, 0)
        sc4 = c2.number_input("2.2 Quorum reached & signed minutes (Max 8)", 0, 8, 0)
        
        st.markdown("**2. Health Policies & Budget Allocation**")
        sc5 = c1.number_input("3.1 Health/Sanitation ordinances enacted (Max 10)", 0, 10, 0)
        sc6 = c2.number_input("4.1 Dedicated health budget in AIP (Max 8)", 0, 8, 0)
        sc7 = c1.number_input("4.2 BHW honoraria & medicine allocation (Max 6)", 0, 6, 0)
        sc8 = c2.number_input("5.1 Quarterly reports submitted to RHU (Max 8)", 0, 8, 0)

        if st.form_submit_button("Save Governance Scorecard"):
            tot = sc1 + sc2 + sc3 + sc4 + sc5 + sc6 + sc7 + sc8
            st.session_state.gov_records.append({"Score": tot})
            st.success(f"Scorecard recorded! Total Score: {tot}/62")

# ------------------------------------------------------------------------------
# MODULE 3: PHASE 2 COMPLETE MASTER HOUSEHOLD SURVEY
# ------------------------------------------------------------------------------
elif menu == "🏠 Phase 2: Complete Household Survey":
    st.subheader("Phase 2: Master Household Survey Instrument (Tool 2.1 Complete)")
    
    with st.form("phase2_complete_form"):
        t_meta, t_vitals, t_socio, t_dec, t_morb, t_mch, t_yakap = st.tabs([
            "📋 Metadata & Roster",
            "🩺 Adult Vitals (Adults 1–5)",
            "🌾 Socio-Econ, Assets & WASH",
            "🤝 Decisions & Community",
            "🤒 Morbidity & Chronic Care",
            "👶 Maternal, EPI & Nutrition",
            "🏥 PhilHealth YAKAP & Access"
        ])

        # TAB 1: SURVEY METADATA & MODULE A ROSTER
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
            st.markdown("**Module A: Household Demographic & Livelihood Roster (Summary)**")
            c1, c2, c3, c4 = st.columns(4)
            tot_children = c1.number_input("No. of Children (<18 yrs)", 0, 20, 0)
            tot_dependents = c2.number_input("No. of Other Dependents", 0, 10, 0)
            hh_head_name = c3.text_input("Household Head Full Name")
            head_civil = c4.selectbox("Head Civil Status", ["Single", "Married", "Widowed", "Separated", "Cohabiting"])

        # TAB 2: MODULE B ADULT PHYSICAL SCREENING (5 ADULTS)
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
            
            action_vitals = st.multiselect("Action Taken for Abnormal Vitals", ["Referred to BHS/RHU", "Advised Medication Compliance", "Health Education Provided", "Scheduled Re-check Visit"])

        # TAB 3: MODULE C SOCIO-ECONOMIC, ASSETS & WASH
        with t_socio:
            st.markdown("**C1. Livelihood & Economic Stability**")
            c1, c2, c3 = st.columns(3)
            income_cat = c1.selectbox("Average Family Income / Month", ["≤ ₱10,000", "₱10,001–₱30,000", "₱30,001–₱45,000", "> ₱50,000"])
            livelihood = c2.selectbox("Primary Livelihood Source", ["Farming (Owned)", "Farming (Tenanted)", "Laborer", "Carpentry", "Fishing", "Peddling", "Gov't Employee", "Small Industry/Sari-Sari", "Other"])
            food_prod = c3.selectbox("Engaged in Food Production?", ["Yes", "No"])

            c1, c2, c3 = st.columns(3)
            prod_types = c1.multiselect("Food Production Activities", ["Vegetable Gardening", "Piggery / Livestock", "Poultry", "Fruit Trees"])
            emergency_5k = c2.selectbox("Emergency Cushion: Raise ₱5,000 in 24 hrs?", ["Yes", "No"])
            p4ps_status = c3.selectbox("Active 4Ps Beneficiary?", ["Yes", "No"])

            st.markdown("**C2. Housing & Asset Ownership**")
            c1, c2, c3 = st.columns(3)
            tenure = c1.selectbox("Tenurial / Property Status", ["Residential lot with house", "Residential House without Lot", "Renting", "Shared", "Farm Land", "Informal Settler / Caretaker"])
            house_type = c2.selectbox("Housing Construction Type", ["Light (Nipa, bamboo, cogon)", "Medium (Wooden floors/walls, G.I. roof)", "Heavy / Permanent (Concrete/hardwood)"])
            cook_fuel = c3.selectbox("Indoor Cooking Fuel", ["LPG", "Electricity", "Charcoal / Wood (Indoor)", "Kerosene"])

            appliances = st.multiselect("Household Appliances Owned", ["Radio/Cassette", "TV", "Electric Fan", "Refrigerator", "Gas Burner", "Computer/Laptop", "None"])
            transport = st.multiselect("Transportation Owned", ["Motorcycle", "Tricycle", "Car/Private Jeep", "Truck", "Kuliglig", "None"])
            clothing_suff = st.selectbox("Clothing Sufficiency (At least 3 sets/member)?", ["Yes", "No"])

            st.markdown("**C3. Household Food Security (USDA 30-Day Screening)**")
            c1, c2, c3 = st.columns(3)
            meal_freq = c1.selectbox("Meal Frequency & Adequacy", ["4+ times/day (Adequate)", "3 times/day (Adequate)", "3 times/day (Inadequate)", "2 times/day", "1 time/day"])
            usda_worried = c2.selectbox("Worried about food running out?", ["Yes", "No"])
            usda_skipped = c3.selectbox("Adult skipped meal/reduced portion due to money?", ["Yes", "No"])

            st.markdown("**C4. WASH Infrastructure & Environmental Health**")
            c1, c2, c3 = st.columns(3)
            water_source = c1.selectbox("Drinking Water Source Level", ["Level 1: Protected Well / Spring", "Level 2: Piped network & communal faucet", "Level 3: Individual household tap", "Unsafe: Shallow Well / River / Surface", "Commercial Refill Station"])
            water_storage = c2.selectbox("Water Storage Method", ["Covered Container", "Open Container", "Both"])
            water_treat = c3.selectbox("Drinking Water Treatment Method", ["Boiling", "Chlorination", "Water Filter", "None"])

            c1, c2, c3 = st.columns(3)
            toilet_type = c1.selectbox("Sanitation / Toilet Facility Type", ["Pour/Flush to Septic Tank", "Ventilated Improved Pit (VIP) Latrine", "Open Defecation / None"])
            toilet_owner = c2.selectbox("Toilet Facility Ownership", ["Owned (Functional)", "Owned (Non-functional)", "Shared (Functional)", "Shared (Non-functional)"])
            waste_water = c3.selectbox("Domestic Liquid Waste Disposal", ["Blind Drainage", "Open Drainage", "Direct Discharge to Yard/Street"])

            c1, c2 = st.columns(2)
            solid_disposal = c1.selectbox("Solid Waste Disposal Method", ["Municipal/Barangay Collection", "Composting", "Burying", "Burning (Siga)", "Open Dumping", "River Disposal"])
            animal_containment = c2.selectbox("Animal Containment Method", ["Tied", "Fenced / Caged", "Astray (Roaming)", "No Animals"])

        # TAB 4: MODULE D & MODULE E (DECISIONS & MORBIDITY)
        with t_dec:
            st.markdown("**Module D: Decision-Making Pattern & Community Participation**")
            c1, c2 = st.columns(2)
            dec_expenses = c1.multiselect("Who decides on Family Expenses?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Father", "Mother"])
            dec_health = c2.multiselect("Who decides on Health & Medical Care?", ["Father", "Mother", "Children", "Single Member", "Others"], default=["Mother"])

            po_active = c1.selectbox("Active in People's Organizations (POs)?", ["Yes", "No"])
            po_name = c2.text_input("Name of Organization(s) / Community Projects")

            st.markdown("---")
            st.markdown("**Module E: Morbidity & Chronic Illness Tracking**")
            child_diarrhea = st.selectbox("Did any child <6 yrs experience >1 diarrheal episode in the past 12 mos?", ["No", "Yes"])
            
            st.markdown("Physician-Diagnosed Chronic Illness Tracking")
            c1, c2, c3 = st.columns(3)
            htn_med = c1.selectbox("Hypertension Med Compliance", ["N/A - Not Diagnosed", "Daily", "Irregular", "Stopped", "None"])
            dm_med = c2.selectbox("Type 2 Diabetes Med Compliance", ["N/A - Not Diagnosed", "Daily", "Irregular", "Stopped", "None"])
            tb_status = c3.selectbox("Active TB DOTS Status", ["N/A - Not Diagnosed", "Enrolled in TB-DOTS", "Stopped Treatment"])

            st.markdown("Household Mortality (Past 12 Months)")
            has_death = st.selectbox("Were there any deaths in the family in the past 12 months?", ["No", "Yes"])
            if has_death == "Yes":
                c1, c2, c3 = st.columns(3)
                d_age = c1.number_input("Deceased Age", 0, 120, 50)
                d_cause = c2.text_input("Cause of Death")
                d_attended = c3.selectbox("Health Worker Attended?", ["Yes", "No"])

        # TAB 5: MODULE F & G MATERNAL, EPI, NUTRITION, COVID
        with t_mch:
            st.markdown("**Module F1: Maternal & Reproductive Health**")
            c1, c2, c3 = st.columns(3)
            is_preg = c1.selectbox("Currently Pregnant Members in Household?", ["No", "Yes"])
            prenatal_1st = c2.selectbox("First prenatal visit in 1st trimester?", ["N/A", "Yes", "No"])
            td_doses = c3.selectbox("Tetanus Diphtheria (Td) Vaccination Status", ["N/A", "Received 2 doses (Td1/Td2)", "Received 3+ doses (Td2+)"])

            c1, c2 = st.columns(2)
            deliv_attendant = c1.selectbox("Delivery Attendant", ["Physician", "Nurse", "Midwife", "Traditional Birth Attendant (Hilot)", "None/Other"])
            fp_method = c2.selectbox("Family Planning Method Used (Women 15-49)", ["None", "Pills", "Injectable (DMPA)", "Implant", "IUD", "BTL/Vasectomy", "Natural", "Condom"])

            st.markdown("---")
            st.markdown("**Module F2: Infant Feeding & Child Nutritional Status (0–59 Months)**")
            c1, c2 = st.columns(2)
            excl_bf = c1.selectbox("Exclusively breastfed for first 6 months?", ["N/A", "Yes", "No"])
            epi_status = c2.selectbox("Overall EPI Immunization Status (Children 0-12 mos)", ["N/A", "Fully Immunized Child (FIC)", "Ongoing / Incomplete", "None"])

            st.markdown("**Child Nutritional Assessment Calculator**")
            c1, c2, c3, c4 = st.columns(4)
            c_id = c1.text_input("Child Member ID / Name", "Child 1")
            c_age = c2.number_input("Child Age (Months: 0–59)", 0, 59, 24)
            c_weight = c3.number_input("Weight (kg)", 0.0, 50.0, 11.5, step=0.1)
            c_height = c4.number_input("Height (cm)", 0.0, 150.0, 85.0, step=0.5)

            child_diag = compute_child_nutrition(c_age, c_weight, c_height)
            st.info(f"💡 **Automated Child Nutritional Status:** BMI: {child_diag['BMI']} | **Wasting:** {child_diag['Wasting']} | **Stunting:** {child_diag['Stunting']} | **Underweight:** {child_diag['Underweight']}")

            st.markdown("---")
            st.markdown("**Module G: COVID-19 Vaccination Tracker**")
            c1, c2 = st.columns(2)
            covid_vax = c1.selectbox("Has any family member received a COVID-19 vaccine?", ["Yes", "No"])
            covid_booster = c2.selectbox("Booster Status", ["None", "1st Booster Received", "2nd Booster Received"])

        # TAB 6: MODULE H, I & J PHILHEALTH YAKAP & ACCESS
        with t_yakap:
            st.markdown("**Module H: PhilHealth YAKAP / Konsulta Program Integration**")
            c1, c2 = st.columns(2)
            yakap_reg = c1.selectbox("PhilHealth YAKAP / Konsulta Registration Status", ["Yes, All Members", "Yes, Some Members", "No One Registered", "Unaware of YAKAP/Konsulta"])
            yakap_facility = c2.selectbox("Assigned YAKAP Primary Care Facility", ["Rural Health Unit (RHU)", "Barangay Health Station (BHS)", "Government Public Hospital", "Accredited Private Medical Clinic"])

            yakap_services = st.multiselect("YAKAP Services Availed in Past 12 Months", [
                "Initial Primary Care Consultation / Annual Physical",
                "Health Risk Assessment (HRA) Profiling",
                "Free Diagnostic & Laboratory Tests",
                "Free Essential Outpatient Medicines",
                "Targeted Health Education & Lifestyle Counseling",
                "Specialist Consultation Referral",
                "None Availed Yet"
            ])

            st.markdown("---")
            st.markdown("**Module I: Healthcare Access & 3-Delay Framework Analysis**")
            c1, c2, c3 = st.columns(3)
            first_fac = c1.selectbox("First Facility Visited When Sick", ["BHS", "RHU", "Gov't Hospital", "Private Clinic", "Pharmacy/Self-Care", "Traditional Healer (Albularyo)"])
            travel_time = c2.selectbox("Travel Time to RHU", ["<15 mins", "15–30 mins", "31–60 mins", ">1 hour"])
            trans_mode = c3.selectbox("Transport Mode to Health Facility", ["Walking", "Tricycle/Habal-habal", "Jeepney", "Private Vehicle"])

            delay1 = st.multiselect("Delay 1: Delays in Deciding to Seek Care", ["Failure to recognize danger signs", "Lack of money for care/transport", "No one to care for home/children", "Belief illness will resolve on its own"])
            delay2 = st.multiselect("Delay 2: Delays in Reaching Appropriate Care Facility", ["Excessive distance from home", "Lack of transport / High travel cost", "Poor road conditions"])
            delay3 = st.multiselect("Delay 3: Delays in Receiving Quality Care at Facility", ["Long waiting times", "Shortage of medicines/supplies", "Lack of skilled health staff", "Incompatible clinic hours"])

            st.markdown("---")
            st.markdown("**Module J: Top Community Health Problems & Solutions**")
            prob1 = st.text_input("Priority 1 Community Problem")
            sol1 = st.text_input("Recommended Solution for Problem 1")

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
            st.success(f"Successfully recorded Master Survey for Household ID {hh_id}!")

# ------------------------------------------------------------------------------
# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS
# ------------------------------------------------------------------------------
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader("Phase 3: Qualitative Field Assessment Instruments")
    q_tool = st.selectbox("Select Assessment Tool", ["Tool 3.1: Governance KII", "Tool 3.2: Frontline Personnel KII", "Tool 3.3: Community FGD"])
    with st.form("qual_form"):
        resp = st.text_input("Key Informant / Group Name")
        notes = st.text_area("Field Notes & Key Qualitative Findings")
        if st.form_submit_button("Save Qualitative Entry"):
            st.session_state.qual_records.append({"Tool": q_tool, "Respondent": resp, "Notes": notes})
            st.success("Qualitative Record Saved.")

# ------------------------------------------------------------------------------
# MODULE 5: PHASE 4 COMPLETE WINDSHIELD & PERI ASSESSMENT
# ------------------------------------------------------------------------------
elif menu == "🔍 Phase 4: Full Windshield Assessment":
    st.subheader("Phase 4: Windshield & PERI Environmental Health Assessment (Complete Framework)")
    
    with st.form("windshield_full_form"):
        c1, c2, c3 = st.columns(3)
        w_brgy = c1.text_input("Barangay Name")
        w_purok = c2.selectbox("Zone / Purok Evaluated", [f"Purok {i}" for i in range(1, 8)])
        w_assessor = c3.text_input("Lead Assessor / Community Clerk")

        st.markdown("---")
        st.markdown("**1. Built Environment & Housing Quality**")
        w1 = st.slider("1.1 Predominance of light/dilapidated housing structures", 1, 3, 1, help="1=Low (<10%), 2=Moderate (10-40%), 3=High (>40%)")
        w2 = st.slider("1.2 Severe structural overcrowding & narrow physical spacing", 1, 3, 1)

        st.markdown("**2. Environmental Sanitation & Waste Vector Risks**")
        w3 = st.slider("2.1 Uncollected household garbage & visible open burning (siga)", 1, 3, 1)
        w4 = st.slider("2.2 Open, unmaintained drainage channels with stagnant wastewater pooling", 1, 3, 1)
        w5 = st.slider("2.3 Presence of dengue vectors & artificial mosquito breeding sites", 1, 3, 1)

        st.markdown("**3. Physical Infrastructure & Access Services**")
        w6 = st.slider("3.1 Unpaved, inaccessible, or severely damaged roads", 1, 3, 1)
        w7 = st.slider("3.2 Absence of functional street lighting in primary walkways", 1, 3, 1)

        st.markdown("**4. Geohazards & Community Safety Hazards**")
        w8 = st.slider("4.1 Direct exposure to flood-prone zones, riverbanks, or steep landslides", 1, 3, 1)
        w9 = st.slider("4.2 Uncontrolled roaming / stray animals in public areas", 1, 3, 1)

        if st.form_submit_button("Compute Complete PERI Hazard Index"):
            peri_score = (w1 + w2 + w3 + w4 + w5 + w6 + w7 + w8 + w9) / 9.0
            if peri_score < 1.50:
                tier = "Category A: Low Vulnerability"
            elif peri_score < 2.30:
                tier = "Category B: Moderate Hazard Tier"
            else:
                tier = "Category C: Critical Environmental Risk"

            st.session_state.windshield_records.append({"Barangay": w_brgy, "Purok": w_purok, "PERI": round(peri_score, 2), "Tier": tier})
            st.warning(f"Calculated PERI Hazard Index: **{peri_score:.2f}** | Action Classification: **{tier}**")

# ------------------------------------------------------------------------------
# MODULE 6: AUTOMATED COMMUNITY DIAGNOSIS
# ------------------------------------------------------------------------------
elif menu == "🩺 Diagnostic Summary & Analytics":
    st.subheader("Automated Community Health Diagnosis & Analytics")
    tot = len(st.session_state.hh_records)
    if tot == 0:
        st.info("No household survey data available yet. Complete survey entries in Phase 2 to view dynamic community health diagnoses.")
    else:
        htn_cases = sum(1 for r in st.session_state.hh_records if r.get("Risk") == "Hypertensive Risk")
        htn_rate = (htn_cases / tot) * 100
        
        c1, c2 = st.columns(2)
        c1.metric("Total Households Surveyed", tot)
        c2.metric("Community Hypertensive Risk Rate", f"{htn_rate:.1f}%")

        st.markdown("---")
        st.markdown("**System-Generated Health Diagnostic Findings:**")
        if htn_rate >= 15.0:
            st.error(f"🔴 **Priority Health Problem:** High prevalence of hypertensive risk ({htn_rate:.1f}%) detected across physical screenings. Recommend initiating community BHS BP monitoring and PhilHealth YAKAP NCD risk assessment profiling.")

# ------------------------------------------------------------------------------
# MODULE 7: EXPORT MASTER DATA
# ------------------------------------------------------------------------------
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Export Survey Data Records")
    if len(st.session_state.hh_records) > 0:
        df_out = pd.DataFrame(st.session_state.hh_records)
        st.download_button("Download Tool 2.1 Master Household Dataset (CSV)", df_out.to_csv(index=False).encode('utf-8'), "UPM_SHS_Tool_2_1_Master_Dataset.csv", "text/csv")
    else:
        st.caption("No household records logged for export.")
