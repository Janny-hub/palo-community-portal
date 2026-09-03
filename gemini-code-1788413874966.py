import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import json

# Page Configuration & Portal Branding
st.set_page_config(
    page_title="UPM-SHS Palo Community Clerks Portal",
    page_icon="🩺",
    layout="wide"
)

st.title("University of the Philippines Manila")
st.subheader("School of Health Sciences Palo — Community Clerks Portal")
st.caption("Developed by **Jan Art A. Serna, RMT** | Comprehensive Community Diagnosis & GIS Spot Mapping System")
st.divider()

# Session State Storage Initialization
if "hh_records" not in st.session_state:
    st.session_state.hh_records = []
if "gov_records" not in st.session_state:
    st.session_state.gov_records = []
if "qual_records" not in st.session_state:
    st.session_state.qual_records = []
if "windshield_records" not in st.session_state:
    st.session_state.windshield_records = []

# Sidebar Navigation
menu = st.sidebar.radio(
    "Select Portal Module",
    [
        "🗺️ Interactive Spot Map", 
        "📋 Phase 1: BHB Governance Scorecard", 
        "🏠 Phase 2: Master Household Survey", 
        "🗣️ Phase 3: Qualitative Assessment", 
        "🔍 Phase 4: Windshield Assessment", 
        "🩺 Automated Community Diagnosis",
        "💾 Export Master Data"
    ]
)

# ------------------------------------------------------------------------------
# MODULE 1: INTERACTIVE SPOT MAP
# ------------------------------------------------------------------------------
if menu == "🗺️ Interactive Spot Map":
    st.header("📍 Barangay Interactive Health & Risk Spot Map")
    
    if len(st.session_state.hh_records) == 0:
        st.info("No household survey data recorded yet. Showing default community spot map preview.")
        map_df = pd.DataFrame([
            {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk": "Hypertensive Risk", "Color": [255, 0, 0, 200]},
            {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk": "Normal", "Color": [0, 200, 80, 200]},
            {"HH_ID": "HH-003", "Purok": "Purok 2", "Lat": 11.1550, "Lon": 124.9930, "BP": "120/80", "Risk": "Severely Stunted Child", "Color": [255, 140, 0, 200]},
            {"HH_ID": "HH-004", "Purok": "Purok 3", "Lat": 11.1542, "Lon": 124.9905, "BP": "160/100", "Risk": "Severe Hazard Zone", "Color": [139, 0, 0, 220]}
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_map, col_filter = st.columns([3, 1])
    
    with col_filter:
        st.subheader("Map Controls")
        purok_list = list(map_df["Purok"].unique())
        selected_puroks = st.multiselect("Filter by Purok", options=purok_list, default=purok_list)
        
        st.markdown("---")
        st.markdown("**Spot Map Visual Legend:**")
        st.markdown("🔴 **Red:** Hypertensive / Cardiac Risk")
        st.markdown("🟠 **Orange:** Child Malnutrition (SAM/Stunted)")
        st.markdown("🟤 **Dark Red:** Critical Hazard / PERI Tier C")
        st.markdown("🟢 **Green:** Normal Household Vitals")

    filtered_df = map_df[map_df["Purok"].isin(selected_puroks)]

    with col_map:
        view_state = pdk.ViewState(
            latitude=filtered_df["Lat"].mean() if len(filtered_df) > 0 else 11.1555,
            longitude=filtered_df["Lon"].mean() if len(filtered_df) > 0 else 124.9915,
            zoom=15, pitch=30
        )
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df,
            get_position=["Lon", "Lat"],
            get_color="Color",
            get_radius=14,
            pickable=True,
            auto_highlight=True
        )
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Household: {HH_ID}\nPurok: {Purok}\nBP: {BP}\nStatus: {Risk}"}
        )
        st.pydeck_chart(r)

# ------------------------------------------------------------------------------
# MODULE 2: PHASE 1 GOVERNANCE SCORECARD
# ------------------------------------------------------------------------------
elif menu == "📋 Phase 1: BHB Governance Scorecard":
    st.header("Phase 1: Barangay Health Board (BHB) Governance Functionality Scorecard")
    
    with st.form("phase1_form"):
        st.subheader("I. Assessment Metadata & Administrative Control")
        c1, c2, c3 = st.columns(3)
        brgy_name = c1.text_input("Barangay Name")
        city_muni = c2.text_input("City / Municipality")
        province = c3.text_input("Province")
        assess_date = c1.date_input("Assessment Date")
        pb_chair = c2.text_input("Punong Barangay (BHB Chair)")
        bhb_sec = c3.text_input("BHB Secretary Name")
        assess_period = c1.text_input("Assessment Period", "CY 2025 / 2026")
        eval_name = c2.text_input("Evaluator Name(s)")
        eval_desig = c3.selectbox("Evaluator Designation", ["MHO Representative", "DOH-DTTB/PHN", "NGO Evaluator"])
        verif_status = c1.selectbox("Verification Status", ["Initial Assessment", "Re-evaluation / Validation"])

        st.subheader("II. Governance Functionality Evaluation Matrix")
        st.markdown("**Domain 1: Legal Reconstitution (Max: 10 pts)**")
        sc1_1 = st.number_input("1.1 Signed EO/Resolution reconstituting BHB (Max 5)", 0, 5, 0)
        sc1_2 = st.number_input("1.2 Mandatory Multi-sectoral Representation present (Max 5)", 0, 5, 0)
        
        st.markdown("**Domain 2: Meeting Regularity (Max: 20 pts)**")
        sc2_1 = st.number_input("2.1 Conduct of Regular Quarterly BHB Meetings (3 pts/qtr, Max 12)", 0, 12, 0)
        sc2_2 = st.number_input("2.2 Official Quorum (>50% attendance) documented (Max 4)", 0, 4, 0)
        sc2_3 = st.number_input("2.3 Approved Action-Oriented Minutes with action tracking (Max 4)", 0, 4, 0)

        st.markdown("**Domain 3: Legislative Output (Max: 20 pts)**")
        sc3_1 = st.number_input("3.1 Enactment of local ordinances (Sanitation, Dengue, WASH, Tobacco) (Max 10)", 0, 10, 0)
        sc3_2 = st.number_input("3.2 Active enforcement mechanism/Task Force created (Max 5)", 0, 5, 0)
        sc3_3 = st.number_input("3.3 Policy alignment with DOH UHC & Municipal priorities (Max 5)", 0, 5, 0)

        st.markdown("**Domain 4: AIP Budget Allocation (Max: 20 pts)**")
        sc4_1 = st.number_input("4.1 Dedicated Health & Sanitation budget line-items in AIP (Max 8)", 0, 8, 0)
        sc4_2 = st.number_input("4.2 Budget for essential drugs, BHW honoraria, emergency response (Max 6)", 0, 6, 0)
        sc4_3 = st.number_input("4.3 Budget execution & liquidation status >75% (Max 6)", 0, 6, 0)

        st.markdown("**Domain 5: Accomplishment Reports (Max: 15 pts)**")
        sc5_1 = st.number_input("5.1 Quarterly health tracking & epidemiological reports to RHU (Max 8)", 0, 8, 0)
        sc5_2 = st.number_input("5.2 Barangay Health Status presented in Barangay Assembly (Max 4)", 0, 4, 0)
        sc5_3 = st.number_input("5.3 Functional Barangay Health Information Board/Map maintained (Max 3)", 0, 3, 0)

        st.markdown("**Domain 6: Committee Functionality (Max: 15 pts)**")
        sc6_1 = st.number_input("6.1 Functional Technical Working Committees created (Max 6)", 0, 6, 0)
        sc6_2 = st.number_input("6.2 Monthly operational meetings & activity reports (Max 6)", 0, 6, 0)
        sc6_3 = st.number_input("6.3 Execution of community mobilization campaigns (Max 3)", 0, 3, 0)

        st.subheader("IV. Governance Improvement Action Plan")
        gap_desc = st.text_input("Identified Governance Gap")
        corrective_action = st.text_input("Recommended Corrective Action / TA Needed")
        target_date = st.text_input("Target Date")
        resp_person = st.text_input("Responsible Person")

        submit_p1 = st.form_submit_button("Save Governance Scorecard")
        
        if submit_p1:
            total_score = sc1_1 + sc1_2 + sc2_1 + sc2_2 + sc2_3 + sc3_1 + sc3_2 + sc3_3 + sc4_1 + sc4_2 + sc4_3 + sc5_1 + sc5_2 + sc5_3 + sc6_1 + sc6_2 + sc6_3
            rating = "HIGH FUNCTIONING" if total_score >= 80 else ("MODERATE FUNCTIONING" if total_score >= 50 else "LOW FUNCTIONING")
            
            p1_entry = {
                "Barangay": brgy_name, "City": city_muni, "Province": province, "Date": str(assess_date),
                "Total_Score": total_score, "Rating": rating, "Gap": gap_desc, "Action": corrective_action
            }
            st.session_state.gov_records.append(p1_entry)
            st.success(f"Scorecard Saved! Total Score: {total_score}/100 — Status: {rating}")

# ------------------------------------------------------------------------------
# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY
# ------------------------------------------------------------------------------
elif menu == "🏠 Phase 2: Master Household Survey":
    st.header("Phase 2: Master Household Survey Instrument")
    
    with st.form("phase2_form"):
        st.subheader("Survey Metadata Control Block")
        c1, c2, c3 = st.columns(3)
        hh_id = c1.text_input("Household ID", "HH-001")
        brgy = c2.text_input("Barangay Name")
        purok = c3.selectbox("Purok / Zone", ["Purok 1", "Purok 2", "Purok 3", "Purok 4", "Purok 5", "Purok 6", "Purok 7"])
        lat = c1.number_input("GPS Latitude (Lat)", value=11.1560, format="%.4f")
        lon = c2.number_input("GPS Longitude (Lon)", value=124.9920, format="%.4f")
        enumerator = c3.text_input("Enumerator Name")
        respondent_role = c1.selectbox("Respondent Role", ["Head", "Spouse", "Adult Member", "Other"])
        survey_status = c2.selectbox("Survey Status", ["Completed", "Partially Completed", "Refused"])

        st.subheader("Module A: Demographic & PhilHealth Roster")
        head_name = c1.text_input("Household Head Name/Initials")
        head_age = c2.number_input("Head Age", 0, 120, 40)
        head_sex = c3.selectbox("Head Sex", ["Male", "Female"])
        civil_stat = c1.selectbox("Civil Status", ["Single", "Married", "Widowed", "Separated"])
        edu_level = c2.selectbox("Education Level", ["None", "Elementary", "High School", "College", "Post-Graduate"])
        occupation = c3.text_input("Primary Occupation")
        philhealth = c1.selectbox("PhilHealth Category", ["Formal Private", "Formal Gov't", "Indigent/NHTS-PR", "Senior Citizen", "PWD", "Self-Earning/Informal", "Unenrolled"])

        st.subheader("Module B: Adult & Ill Member Physical Screening (Objective Vitals)")
        sys_bp = c1.number_input("Systolic BP (mmHg)", 50, 250, 120)
        dia_bp = c2.number_input("Diastolic BP (mmHg)", 30, 150, 80)
        spo2 = c3.number_input("SpO2 (%)", 50, 100, 98)
        pulse = c1.number_input("Pulse Rate (bpm)", 30, 200, 75)
        temp = c2.number_input("Temperature (°C)", 30.0, 45.0, 36.5)
        symptoms = c3.multiselect("Current Symptoms", ["None", "Headache", "Cough", "Chest Pain", "Shortness of Breath"])
        vitals_outcome = c1.selectbox("Assessment Outcome & Risk", ["Normal", "Hypertensive Risk", "Hypoxemic Risk (<95%)"])
        action_taken = c2.multiselect("Action Taken for Abnormal Vitals", ["Referred to BHS/RHU", "Advised Medication Compliance", "Health Education Provided", "Scheduled Re-check Visit"])

        st.subheader("Module C: Social Determinants & Environmental Risk Factors")
        income = c1.selectbox("Monthly Income Bracket", ["< ₱10,000", "₱10,000–₱25,000", "₱25,001–₱50,000", "> ₱50,000"])
        emergency_cushion = c2.selectbox("Can raise ₱5,000 in 24h?", ["Yes", "No"])
        p4ps = c3.selectbox("4Ps Beneficiary Status", ["Yes", "No"])
        tenure = c1.selectbox("Tenurial Status", ["Owned", "Renting", "Informal Settler / Temporary Structure", "Caretaker"])
        walls = c2.selectbox("Outer Wall Materials", ["Concrete / Brick", "Wood / Bamboo", "Salvaged / Makeshift Materials"])
        cooking_fuel = c3.selectbox("Indoor Air Risk (Cooking Fuel)", ["LPG", "Electricity", "Charcoal / Wood (Indoor)", "Kerosene"])
        water_src = c1.selectbox("Drinking Water Source", ["Level III (Tap)", "Level II (Communal)", "Level I (Well)", "Commercial Station", "Surface/River (Unsafe)"])
        sanitation = c2.selectbox("Sanitation Facility", ["Pour-flush to Septic (Exclusive)", "Pour-flush (Shared)", "Pit Latrine", "Open Defecation / None"])
        waste_disp = c3.selectbox("Solid Waste Disposal", ["Barangay Collection", "Open Burning", "Dumping in River / Vacant Lot", "Composting"])
        
        st.markdown("**Household Food Security (USDA 3-Item Adapt)**")
        usda1 = c1.selectbox("Worry about running out of food?", ["Yes", "No"])
        usda2 = c2.selectbox("Adult skip meal or reduce portion?", ["Yes", "No"])
        usda3 = c3.selectbox("Go full day without eating?", ["Yes", "No"])

        st.subheader("Module D: Family Disease History & Morbidity Profiling")
        lead_illness1 = c1.text_input("Rank 1 Leading Sickness", "URTI / Flu")
        lead_illness2 = c2.text_input("Rank 2 Leading Sickness", "Hypertension Flares")
        chronic_cond = c3.multiselect("Diagnosed Chronic Conditions", ["None", "Hypertension", "Type 2 Diabetes", "Active TB", "Asthma", "Mental Health", "Cardiovascular Disease"])
        med_status = c1.selectbox("Medication Adherence Status", ["Yes, Daily", "Irregular", "Stopped", "None"])
        med_source = c2.selectbox("Source of Medicines", ["BHS / RHU (Free)", "Out-of-pocket (Private)"])

        st.subheader("Module E: Hospitalization History & Acute Care")
        hospitalized = c1.selectbox("Inpatient Hospitalization in Past 12 Months?", ["No", "Yes"])
        coping_mech = c2.multiselect("Financial Coping Mechanism", ["Savings", "Borrowed Money / High-Interest Loan", "Sold Property/Assets", "Government Assistance (MAIFIP/PCSO/DSWD)", "Family Contribution"])

        st.subheader("Module F: Maternal, Child & Reproductive Health")
        pregnant = c1.selectbox("Pregnant Members present?", ["No", "Yes"])
        prenatal_visits = c2.selectbox("Prenatal Visits Completed", ["N/A", "< 4 visits", "≥ 4 visits (Standard)"])
        fic_status = c3.selectbox("Fully Immunized Child (FIC) Status (0-23 mos)", ["N/A", "Yes (FIC Verified)", "Incomplete", "Card Lost"])
        malnutrition = c1.selectbox("Child Malnutrition Status (0-59 mos)", ["Normal", "Underweight", "Severely Underweight", "Stunted", "Severely Stunted", "Wasted", "SAM"])

        st.subheader("Module G: Healthcare Access & Service Utilization")
        first_facility = c1.selectbox("Primary Facility First Visited", ["Barangay Health Station (BHS)", "Rural Health Unit (RHU)", "Government Public Hospital", "Private Clinic / Hospital", "Pharmacy / OTC", "Traditional Healer"])
        travel_time = c2.selectbox("Travel Time to RHU", ["< 15 mins", "15–30 mins", "31–60 mins", "> 1 hour"])
        barriers = c3.multiselect("Major Barriers to Medical Care", ["Transportation cost", "Distance/Travel time", "Long waiting times", "High out-of-pocket costs", "Loss of daily wage", "Unfriendly staff", "Incompatible clinic hours", "Belief illness will self-resolve"])

        submit_p2 = st.form_submit_button("Save Household Survey & Pin to Spot Map")

        if submit_p2:
            bp_str = f"{sys_bp}/{dia_bp}"
            color = [255, 0, 0, 200] if (sys_bp >= 140 or vitals_outcome == "Hypertensive Risk") else ([255, 140, 0, 200] if malnutrition != "Normal" else [0, 200, 80, 200])
            
            p2_entry = {
                "HH_ID": hh_id, "Barangay": brgy, "Purok": purok, "Lat": lat, "Lon": lon,
                "Enumerator": enumerator, "Head_Name": head_name, "BP": bp_str, "SpO2": spo2,
                "Risk": vitals_outcome if vitals_outcome != "Normal" else malnutrition,
                "Water_Source": water_src, "Sanitation": sanitation, "Income": income,
                "Barriers": ", ".join(barriers), "Color": color
            }
            st.session_state.hh_records.append(p2_entry)
            st.success(f"Household {hh_id} successfully recorded and pinned to Spot Map!")

# ------------------------------------------------------------------------------
# MODULE 4: PHASE 3 QUALITATIVE ASSESSMENT
# ------------------------------------------------------------------------------
elif menu == "🗣️ Phase 3: Qualitative Assessment":
    st.header("Phase 3: Qualitative Assessment Instruments")
    
    qual_type = st.selectbox("Select Qualitative Assessment Instrument", [
        "Tool 3.1: Governance & Leadership KII",
        "Tool 3.2: Frontline Personnel KII",
        "Tool 3.3: Community Focus Group Discussion (FGD)"
    ])

    with st.form("phase3_form"):
        if qual_type == "Tool 3.1: Governance & Leadership KII":
            st.subheader("Tool 3.1: Governance & Leadership Key Informant Interview")
            c1, c2 = st.columns(2)
            resp_name = c1.text_input("Respondent Name")
            resp_pos = c2.selectbox("Position", ["Punong Barangay", "Health Committee Chair", "Municipal Health Officer (MHO)"])
            
            q1 = st.text_area("1. Resource Allocation & AIP Prioritization Notes")
            q2 = st.text_area("2. Policy Infrastructure & Ordinance Enforcement Notes")
            q3 = st.text_area("3. Supply Chain Integrity & Emergency Procurement Notes")
            q4 = st.text_area("4. Health Inequity & Disadvantaged Populations Notes")
            q5 = st.text_area("5. Strategic Governance Synthesis & Vision Notes")

        elif qual_type == "Tool 3.2: Frontline Personnel KII":
            st.subheader("Tool 3.2: Frontline Personnel Key Informant Interview")
            c1, c2 = st.columns(2)
            resp_name = c1.text_input("Respondent Name")
            resp_pos = c2.selectbox("Frontline Role", ["Rural Health Midwife", "BHW President", "Barangay Nutrition Scholar (BNS)"])
            
            q1 = st.text_area("1. Clinical Workload & Essential Supply Deficits Notes")
            q2 = st.text_area("2. Emergency Referral Pathway & Pipeline Breakdown Notes")
            q3 = st.text_area("3. Non-Medical Treatment Adherence Barriers Notes")
            q4 = st.text_area("4. Systemic Worker Bottlenecks & Capacity Needs Notes")

        else:
            st.subheader("Tool 3.3: Focus Group Discussion (FGD) — Community Members")
            c1, c2 = st.columns(2)
            brgy_fgd = c1.text_input("Barangay / Location")
            group_comp = c2.selectbox("Group Composition", ["Mothers", "Senior Citizens", "PWDs", "Mixed Community Group"])
            
            q1 = st.text_area("1. Health Seeking Decision Dynamics Notes")
            q2 = st.text_area("2. Catastrophic Healthcare Expenses & Coping Notes")
            q3 = st.text_area("3. Provider-Patient Interaction & Quality Perception Notes")
            q4 = st.text_area("4. Community Priorities & Grassroots Solutions Notes")
            q5 = st.text_area("Group Dynamics, Non-Verbal Cues & Consensus Summary")

        submit_p3 = st.form_submit_button("Save Qualitative Interview Entry")
        if submit_p3:
            st.session_state.qual_records.append({"Type": qual_type, "Respondent": resp_name if 'resp_name' in locals() else "FGD Group", "Notes_Summary": q1[:100] + "..."})
            st.success("Qualitative Interview Transcript Saved Successfully!")

# ------------------------------------------------------------------------------
# MODULE 5: PHASE 4 WINDSHEILD & PERI ASSESSMENT
# ------------------------------------------------------------------------------
elif menu == "🔍 Phase 4: Windshield Assessment":
    st.header("Phase 4: Multi-Domain Windshield & Direct Field Observation Matrix")
    
    with st.form("phase4_form"):
        st.subheader("Field Administration Control")
        c1, c2, c3 = st.columns(3)
        brgy_w = c1.text_input("Barangay Name")
        muni_w = c2.text_input("Municipality / City")
        assessor = c3.text_input("Lead Assessor Name")
        purok_w = c1.text_input("Target Puroks / Zones", "Purok 1 to 7")
        weather = c2.selectbox("Weather Conditions", ["Clear", "Rain", "Post-Storm"])

        st.markdown("---")
        st.markdown("**Domain Rating Scale:** `1 = Optimal / Clean`, `2 = Moderate Risk`, `3 = Severe Hazard / Critical`")

        st.subheader("Domain 1: Sanitation & Waste Management Assessment")
        d1_1 = st.slider("1.1 Uncollected Household Solid Waste", 1, 3, 1)
        d1_2 = st.slider("1.2 Open Drainage & Canal Integrity", 1, 3, 1)
        d1_3 = st.slider("1.3 Stagnant Water & Pooling", 1, 3, 1)
        d1_4 = st.slider("1.4 Stray & Unattended Animals", 1, 3, 1)
        d1_5 = st.slider("1.5 Material Recovery & Garbage Hubs", 1, 3, 1)
        d1_6 = st.slider("1.6 Open Waste Burning (Siga)", 1, 3, 1)
        d1_7 = st.slider("1.7 Odor & Airborne Emissions", 1, 3, 1)
        d1_8 = st.slider("1.8 Fecal Contamination Exposure", 1, 3, 1)
        d1_9 = st.slider("1.9 Commercial / Market Waste", 1, 3, 1)

        st.subheader("Domain 2: Food Environment & Nutritional Accessibility")
        d2_1 = st.slider("2.1 Fresh Produce Access (Talipapa/Markets)", 1, 3, 1)
        d2_2 = st.slider("2.2 Sari-Sari Store Food Profile (Junk Dominance)", 1, 3, 1)
        d2_3 = st.slider("2.3 Produce Quality & Freshness", 1, 3, 1)
        d2_4 = st.slider("2.4 Street Food Vending Hygiene", 1, 3, 1)
        d2_5 = st.slider("2.5 Child-Targeted Marketing", 1, 3, 1)
        d2_6 = st.slider("2.6 Tobacco & Alcohol Visibility", 1, 3, 1)
        d2_7 = st.slider("2.7 Safe Drinking Water Refilling Outlets", 1, 3, 1)

        st.subheader("Domain 3: Built Environment & Housing Quality")
        d3_1 = st.slider("3.1 Housing Structural Integrity", 1, 3, 1)
        d3_2 = st.slider("3.2 Pedestrian Walkways & Sidewalks", 1, 3, 1)
        d3_3 = st.slider("3.3 Street Lighting & Night Illumination", 1, 3, 1)
        d3_4 = st.slider("3.4 Public Open Spaces & Youth Parks", 1, 3, 1)
        d3_5 = st.slider("3.5 Universal Physical Accessibility (PWD)", 1, 3, 1)
        d3_6 = st.slider("3.6 Electrical Wiring & Power Line Safety", 1, 3, 1)
        d3_7 = st.slider("3.7 Road Surface & Speed Management", 1, 3, 1)

        st.subheader("Domain 4: Health Infrastructure & Primary Care Access")
        d4_1 = st.slider("4.1 Barangay Health Station (BHS) State", 1, 3, 1)
        d4_2 = st.slider("4.2 Facility Visibility & Operational Signage", 1, 3, 1)
        d4_3 = st.slider("4.3 Public Transport Proximity (<100m)", 1, 3, 1)
        d4_4 = st.slider("4.4 Pharmacy / Essential Medicine Access", 1, 3, 1)
        d4_5 = st.slider("4.5 Emergency Vehicle Access Corridors", 1, 3, 1)
        d4_6 = st.slider("4.6 Health Promotion Advisory Display", 1, 3, 1)
        d4_7 = st.slider("4.7 BHS Sanitation & Basic Utilities", 1, 3, 1)

        st.subheader("Domain 5: Disaster Risk Reduction & Climate Safety")
        d5_1 = st.slider("5.1 High-Hazard Proximity (Geohazards)", 1, 3, 1)
        d5_2 = st.slider("5.2 Flood Vulnerability & Water Marks", 1, 3, 1)
        d5_3 = st.slider("5.3 Evacuation Route Signage & Clarity", 1, 3, 1)
        d5_4 = st.slider("5.4 Evacuation Center Readiness", 1, 3, 1)
        d5_5 = st.slider("5.5 Major Drainage Outfalls & Waterways", 1, 3, 1)
        d5_6 = st.slider("5.6 Urban Fire Hazard & Density", 1, 3, 1)
        d5_7 = st.slider("5.7 Slope Protection & Retaining Walls", 1, 3, 1)

        st.subheader("Domain 6: Vector Control & Environmental Hazards")
        d6_1 = st.slider("6.1 Dengue Vector Breeding Sites", 1, 3, 1)
        d6_2 = st.slider("6.2 Rodent & Fly Infestation Signs", 1, 3, 1)
        d6_3 = st.slider("6.3 Commercial / Workshop Pollution", 1, 3, 1)
        d6_4 = st.slider("6.4 Dust, Exhaust & Air Quality", 1, 3, 1)

        submit_p4 = st.form_submit_button("Calculate PERI Score & Save Windshield Data")

        if submit_p4:
            ds1 = sum([d1_1, d1_2, d1_3, d1_4, d1_5, d1_6, d1_7, d1_8, d1_9]) / 9.0
            ds2 = sum([d2_1, d2_2, d2_3, d2_4, d2_5, d2_6, d2_7]) / 7.0
            ds3 = sum([d3_1, d3_2, d3_3, d3_4, d3_5, d3_6, d3_7]) / 7.0
            ds4 = sum([d4_1, d4_2, d4_3, d4_4, d4_5, d4_6, d4_7]) / 7.0
            ds5 = sum([d5_1, d5_2, d5_3, d5_4, d5_5, d5_6, d5_7]) / 7.0
            ds6 = sum([d6_1, d6_2, d6_3, d6_4]) / 4.0

            peri = (ds1 + ds2 + ds3 + ds4 + ds5 + ds6) / 6.0
            tier = "CATEGORY A: Low Risk" if peri < 1.50 else ("CATEGORY B: Moderate Concern" if peri < 2.30 else "CATEGORY C: Critical Hazard")

            st.session_state.windshield_records.append({
                "Barangay": brgy_w, "PERI_Score": round(peri, 2), "Action_Tier": tier,
                "DS1_Sanitation": round(ds1, 2), "DS2_Food": round(ds2, 2), "DS3_Built": round(ds3, 2),
                "DS4_Health": round(ds4, 2), "DS5_Disaster": round(ds5, 2), "DS6_Vector": round(ds6, 2)
            })
            st.warning(f"Calculated Composite PERI Score: {peri:.2f} — Action Tier: {tier}")

# ------------------------------------------------------------------------------
# MODULE 6: AUTOMATED COMMUNITY DIAGNOSIS ENGINE
# ------------------------------------------------------------------------------
elif menu == "🩺 Automated Community Diagnosis":
    st.header("Automated Community Health Diagnosis Engine")
    
    total_hh = len(st.session_state.hh_records)
    
    if total_hh == 0:
        st.info("Please enter Phase 1–4 data across modules to generate real-time diagnostic statements.")
    else:
        htn_cases = sum(1 for r in st.session_state.hh_records if r.get("Risk") == "Hypertensive Risk")
        htn_rate = (htn_cases / total_hh) * 100
        
        last_peri = st.session_state.windshield_records[-1]["PERI_Score"] if len(st.session_state.windshield_records) > 0 else 2.10
        last_gov = st.session_state.gov_records[-1]["Total_Score"] if len(st.session_state.gov_records) > 0 else 75

        st.subheader("Aggregated Community Health Indicators")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Surveyed Households", total_hh)
        m2.metric("Hypertension Risk Rate", f"{htn_rate:.1f}%")
        m3.metric("PERI Composite Risk Score", f"{last_peri:.2f}")

        st.subheader("Synthesized Automated Diagnoses")

        if htn_rate >= 15.0:
            st.error(f"**Cardiovascular Disease Risk:** Elevated community prevalence of Hypertensive Risk ({htn_rate:.1f}%) identified during objective physical screening, requiring primary care screening and drug supply expansion.")

        if last_peri >= 2.30:
            st.error(f"**High Environmental Vector & Outbreak Hazard:** Critical environmental degradation detected (PERI Composite Score: {last_peri:.2f} — Tier C), driven by uncollected solid waste and open drainage channels[cite: 3].")

        if last_gov < 80:
            st.warning(f"**Impaired Local Health Governance:** Moderate/Low Barangay Health Board functionality score ({last_gov}/100), indicating bottlenecks in ordinance enforcement and AIP health budget execution[cite: 1, 4].")

# ------------------------------------------------------------------------------
# MODULE 7: EXPORT MASTER DATA
# ------------------------------------------------------------------------------
elif menu == "💾 Export Master Data":
    st.header("💾 Download Gathered Community Assessment Data")
    st.markdown("Download all data recorded during field clerk sessions directly to your device as CSV files.")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Phase 2 Household Master File")
        if len(st.session_state.hh_records) > 0:
            df_hh_exp = pd.DataFrame(st.session_state.hh_records)
            st.download_button("Download Household CSV", df_hh_exp.to_csv(index=False).encode('utf-8'), "UPM_SHS_Phase2_Households.csv", "text/csv")
        else:
            st.caption("No Phase 2 records available to download.")

    with c2:
        st.subheader("Phase 4 Windshield Assessment File")
        if len(st.session_state.windshield_records) > 0:
            df_w_exp = pd.DataFrame(st.session_state.windshield_records)
            st.download_button("Download PERI Assessment CSV", df_w_exp.to_csv(index=False).encode('utf-8'), "UPM_SHS_Phase4_Windshield.csv", "text/csv")
        else:
            st.caption("No Phase 4 records available to download.")
