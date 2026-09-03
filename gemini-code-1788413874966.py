import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Page Configuration
st.set_page_config(
    page_title="UPM-SHS Palo Community Clerks Portal",
    page_icon="🩺",
    layout="wide"
)

# Custom CSS Injection for UI Enhancement
st.markdown("""
    <style>
    /* Top Header Banner */
    .portal-header {
        background: linear-gradient(135deg, #7B1113 0%, #500B0D 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .portal-header h1 {
        color: #F4C430 !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        margin: 0 0 6px 0 !important;
    }
    .portal-header p {
        color: #E5E7EB !important;
        font-size: 14px !important;
        margin: 0 !important;
    }
    
    /* Card Container Styling */
    div[data-testid="stForm"] {
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 24px;
        background-color: #FFFFFF;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    
    /* Metric Card Customization */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# Custom Branded Header
st.markdown("""
    <div class="portal-header">
        <h1>University of the Philippines Manila</h1>
        <p><strong>School of Health Sciences Palo — Community Clerks Portal</strong></p>
        <p style="font-size: 12px; color: #D1D5DB; margin-top: 4px;">Lead Developer: Jan Art A. Serna, RMT | Integrated Health Assessment & GIS System</p>
    </div>
""", unsafe_allow_html=True)

# Session State Initialization
if "hh_records" not in st.session_state:
    st.session_state.hh_records = []
if "gov_records" not in st.session_state:
    st.session_state.gov_records = []
if "qual_records" not in st.session_state:
    st.session_state.qual_records = []
if "windshield_records" not in st.session_state:
    st.session_state.windshield_records = []

# Navigation Sidebar
st.sidebar.title("📌 Portal Navigation")
menu = st.sidebar.radio(
    "Select Module",
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
    st.subheader("📍 Barangay Interactive Health & Risk Spot Map")
    
    if len(st.session_state.hh_records) == 0:
        st.info("No household survey data recorded yet. Showing baseline community map.")
        map_df = pd.DataFrame([
            {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk": "Hypertensive Risk", "Color": [255, 0, 0, 200]},
            {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk": "Normal", "Color": [0, 200, 80, 200]},
            {"HH_ID": "HH-003", "Purok": "Purok 2", "Lat": 11.1550, "Lon": 124.9930, "BP": "120/80", "Risk": "Severely Stunted Child", "Color": [255, 140, 0, 200]},
            {"HH_ID": "HH-004", "Purok": "Purok 3", "Lat": 11.1542, "Lon": 124.9905, "BP": "160/100", "Risk": "PERI Category C Hazard", "Color": [139, 0, 0, 220]}
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_map, col_filter = st.columns([3, 1])
    
    with col_filter:
        st.markdown("**Map Controls & Layer Filters**")
        purok_list = list(map_df["Purok"].unique())
        selected_puroks = st.multiselect("Filter Purok", options=purok_list, default=purok_list)
        
        st.markdown("---")
        st.markdown("**Map Legend:**")
        st.markdown("🔴 **Red:** Hypertensive / Cardiac Risk")
        st.markdown("🟠 **Orange:** Child Malnutrition Risk")
        st.markdown("🟤 **Dark Red:** PERI Category C Hazard")
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
# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD[cite: 1]
# ------------------------------------------------------------------------------
elif menu == "📋 Phase 1: BHB Governance Scorecard":
    st.subheader("Phase 1: Barangay Health Board (BHB) Governance Functionality Scorecard[cite: 1]")
    
    with st.form("phase1_form"):
        tab1, tab2, tab3 = st.tabs(["📝 Metadata", "📊 Scorecard Matrix", "🎯 Governance Action Plan"])
        
        with tab1:
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

        with tab2:
            st.markdown("**Domain Evaluation Scores (Max 100 Points Total)**")
            col_a, col_b = st.columns(2)
            with col_a:
                sc1_1 = st.number_input("1.1 Legal Reconstitution EO Signed (Max 5)", 0, 5, 0)
                sc1_2 = st.number_input("1.2 Mandatory Multi-sectoral Representation (Max 5)", 0, 5, 0)
                sc2_1 = st.number_input("2.1 Regular Quarterly Meetings Conducted (Max 12)", 0, 12, 0)
                sc2_2 = st.number_input("2.2 Quorum Documented (Max 4)", 0, 4, 0)
                sc2_3 = st.number_input("2.3 Action-Oriented Minutes Maintained (Max 4)", 0, 4, 0)
                sc3_1 = st.number_input("3.1 Health/WASH Ordinances Enacted (Max 10)", 0, 10, 0)
                sc3_2 = st.number_input("3.2 Enforcement Task Force Functional (Max 5)", 0, 5, 0)
                sc3_3 = st.number_input("3.3 DOH UHC Priority Alignment (Max 5)", 0, 5, 0)
            with col_b:
                sc4_1 = st.number_input("4.1 AIP Budget Line-Items Allocated (Max 8)", 0, 8, 0)
                sc4_2 = st.number_input("4.2 Medicine & BHW Honoraria Budget (Max 6)", 0, 6, 0)
                sc4_3 = st.number_input("4.3 Budget Execution Rate >75% (Max 6)", 0, 6, 0)
                sc5_1 = st.number_input("5.1 Quarterly Health Status Reports (Max 8)", 0, 8, 0)
                sc5_2 = st.number_input("5.2 Barangay Assembly Health Briefing (Max 4)", 0, 4, 0)
                sc5_3 = st.number_input("5.3 Health Info Map Maintained (Max 3)", 0, 3, 0)
                sc6_1 = st.number_input("6.1 Active Working Committees (Max 6)", 0, 6, 0)
                sc6_2 = st.number_input("6.2 Monthly Activity Execution (Max 6)", 0, 6, 0)
                sc6_3 = st.number_input("6.3 Community Campaigns (Max 3)", 0, 3, 0)

        with tab3:
            gap_desc = st.text_input("Identified Governance Gap")
            corrective_action = st.text_input("Recommended Technical Assistance / Action")
            c_a, c_b = st.columns(2)
            target_date = c_a.text_input("Target Implementation Date")
            resp_person = c_b.text_input("Responsible Lead Person")

        submit_p1 = st.form_submit_button("Save Governance Scorecard")
        
        if submit_p1:
            total_score = sum([sc1_1, sc1_2, sc2_1, sc2_2, sc2_3, sc3_1, sc3_2, sc3_3, sc4_1, sc4_2, sc4_3, sc5_1, sc5_2, sc5_3, sc6_1, sc6_2, sc6_3])
            rating = "HIGH FUNCTIONING" if total_score >= 80 else ("MODERATE FUNCTIONING" if total_score >= 50 else "LOW FUNCTIONING")
            st.session_state.gov_records.append({"Barangay": brgy_name, "Total_Score": total_score, "Rating": rating, "Gap": gap_desc})
            st.success(f"Scorecard Recorded! Score: {total_score}/100 — Rating: {rating}")

# ------------------------------------------------------------------------------
# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY[cite: 2]
# ------------------------------------------------------------------------------
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader("Phase 2: Master Household & Vitals Survey Instrument[cite: 2]")
    
    with st.form("phase2_form"):
        t1, t2, t3, t4, t5 = st.tabs(["📌 Identification", "👥 Demographics", "🩺 Objective Vitals", "🌐 Environment & SDOH", "🏥 Maternal & Care Access"])

        with t1:
            c1, c2, c3 = st.columns(3)
            hh_id = c1.text_input("Household ID", "HH-001")
            brgy = c2.text_input("Barangay Name")
            purok = c3.selectbox("Purok / Zone", [f"Purok {i}" for i in range(1, 8)])
            lat = c1.number_input("GPS Latitude", value=11.1560, format="%.4f")
            lon = c2.number_input("GPS Longitude", value=124.9920, format="%.4f")
            enumerator = c3.text_input("Enumerator Name")

        with t2:
            c1, c2, c3 = st.columns(3)
            head_name = c1.text_input("Household Head Initials")
            head_age = c2.number_input("Head Age", 0, 120, 40)
            head_sex = c3.selectbox("Head Sex", ["Male", "Female"])
            civil_stat = c1.selectbox("Civil Status", ["Single", "Married", "Widowed", "Separated"])
            edu_level = c2.selectbox("Education Level", ["None", "Elementary", "High School", "College", "Post-Grad"])
            philhealth = c3.selectbox("PhilHealth Status", ["Formal", "Indigent/NHTS", "Senior Citizen", "PWD", "Unenrolled"])

        with t3:
            c1, c2, c3 = st.columns(3)
            sys_bp = c1.number_input("Systolic BP (mmHg)", 50, 250, 120)
            dia_bp = c2.number_input("Diastolic BP (mmHg)", 30, 150, 80)
            spo2 = c3.number_input("SpO2 (%)", 50, 100, 98)
            temp = c1.number_input("Temperature (°C)", 30.0, 45.0, 36.5)
            symptoms = c2.multiselect("Active Symptoms", ["None", "Headache", "Cough", "Chest Pain", "Shortness of Breath"])
            vitals_outcome = c3.selectbox("Vitals Risk Profile", ["Normal", "Hypertensive Risk", "Hypoxemic Risk (<95%)"])

        with t4:
            c1, c2, c3 = st.columns(3)
            income = c1.selectbox("Monthly Income", ["< ₱10,000", "₱10,000–₱25,000", "₱25,001–₱50,000", "> ₱50,000"])
            water_src = c2.selectbox("Drinking Water Source", ["Level III (Tap)", "Level II (Communal)", "Level I (Well)", "Commercial Refill", "Surface/Unsafe"])
            sanitation = c3.selectbox("Toilet Facility", ["Exclusive Septic", "Shared Septic", "Pit Latrine", "Open Defecation"])
            
            with st.expander("Household Food Security (USDA Adapt)"):
                usda1 = st.selectbox("Worry about running out of food?", ["No", "Yes"])
                usda2 = st.selectbox("Adult skip meal or reduce portion?", ["No", "Yes"])

        with t5:
            c1, c2, c3 = st.columns(3)
            malnutrition = c1.selectbox("Child Malnutrition Status", ["Normal", "Underweight", "Stunted", "Wasted", "SAM"])
            fic_status = c2.selectbox("Child FIC Status", ["N/A", "Yes (FIC Verified)", "Incomplete"])
            barriers = c3.multiselect("Access Barriers", ["Transport Cost", "Distance", "Medicine Cost", "Waiting Time"])

        submit_p2 = st.form_submit_button("Save Household Survey & Pin to Spot Map")

        if submit_p2:
            bp_str = f"{sys_bp}/{dia_bp}"
            color = [255, 0, 0, 200] if (sys_bp >= 140 or vitals_outcome == "Hypertensive Risk") else ([255, 140, 0, 200] if malnutrition != "Normal" else [0, 200, 80, 200])
            st.session_state.hh_records.append({
                "HH_ID": hh_id, "Barangay": brgy, "Purok": purok, "Lat": lat, "Lon": lon,
                "BP": bp_str, "SpO2": spo2, "Risk": vitals_outcome if vitals_outcome != "Normal" else malnutrition,
                "Water_Source": water_src, "Sanitation": sanitation, "Color": color
            })
            st.success(f"Household {hh_id} Saved and Spot Map Updated!")

# ------------------------------------------------------------------------------
# MODULE 4: PHASE 3 QUALITATIVE ASSESSMENT[cite: 4]
# ------------------------------------------------------------------------------
elif menu == "🗣️ Phase 3: Qualitative Assessment":
    st.subheader("Phase 3: Qualitative Instruments & Field Notes[cite: 4]")
    
    qual_type = st.selectbox("Select Instrument Tool", [
        "Tool 3.1: Governance & Leadership KII",
        "Tool 3.2: Frontline Personnel KII",
        "Tool 3.3: Community Focus Group Discussion (FGD)"
    ])

    with st.form("phase3_form"):
        c1, c2 = st.columns(2)
        resp_title = c1.text_input("Respondent / Group Title")
        brgy_q = c2.text_input("Barangay Location")

        q1 = st.text_area("Key Interview Notes / Theme Observations")
        q2 = st.text_area("Identified Health Bottlenecks & Community Priorities")

        submit_p3 = st.form_submit_button("Save Qualitative Interview Entry")
        if submit_p3:
            st.session_state.qual_records.append({"Type": qual_type, "Title": resp_title, "Notes": q1[:100] + "..."})
            st.success("Qualitative Record Saved!")

# ------------------------------------------------------------------------------
# MODULE 5: PHASE 4 WINDSHEILD ASSESSMENT[cite: 3]
# ------------------------------------------------------------------------------
elif menu == "🔍 Phase 4: Windshield Assessment":
    st.subheader("Phase 4: Windshield & PERI Assessment Matrix[cite: 3]")
    
    with st.form("phase4_form"):
        c1, c2, c3 = st.columns(3)
        brgy_w = c1.text_input("Barangay Name")
        assessor = c2.text_input("Lead Assessor Name")
        weather = c3.selectbox("Weather Condition", ["Clear", "Rain", "Post-Storm"])

        st.caption("Rating Scale: `1 = Optimal / Safe`, `2 = Moderate Risk`, `3 = Severe Hazard`")

        d_tabs = st.tabs(["1. Sanitation", "2. Food Env", "3. Built Env", "4. Health Access", "5. Disaster", "6. Vector Risk"])
        
        with d_tabs[0]:
            d1_1 = st.slider("1.1 Uncollected Waste", 1, 3, 1)
            d1_2 = st.slider("1.2 Open Canal Drainage Risk", 1, 3, 1)
        with d_tabs[1]:
            d2_1 = st.slider("2.1 Fresh Food Access", 1, 3, 1)
            d2_2 = st.slider("2.2 Junk Food Dominance", 1, 3, 1)
        with d_tabs[2]:
            d3_1 = st.slider("3.1 Housing Structural Risk", 1, 3, 1)
            d3_2 = st.slider("3.2 Night Illumination & Safety", 1, 3, 1)
        with d_tabs[3]:
            d4_1 = st.slider("4.1 BHS Physical Readiness", 1, 3, 1)
            d4_2 = st.slider("4.2 Emergency Vehicle Access", 1, 3, 1)
        with d_tabs[4]:
            d5_1 = st.slider("5.1 Geohazard Proximity", 1, 3, 1)
            d5_2 = st.slider("5.2 Flood Vulnerability", 1, 3, 1)
        with d_tabs[5]:
            d6_1 = st.slider("6.1 Mosquito/Dengue Breeding", 1, 3, 1)
            d6_2 = st.slider("6.2 Rodent Vectors Present", 1, 3, 1)

        submit_p4 = st.form_submit_button("Calculate PERI Score")

        if submit_p4:
            peri = sum([d1_1, d1_2, d2_1, d2_2, d3_1, d3_2, d4_1, d4_2, d5_1, d5_2, d6_1, d6_2]) / 12.0
            tier = "Category A: Low Risk" if peri < 1.50 else ("Category B: Moderate Concern" if peri < 2.30 else "Category C: Critical Hazard")
            st.session_state.windshield_records.append({"Barangay": brgy_w, "PERI_Score": round(peri, 2), "Tier": tier})
            st.warning(f"PERI Composite Score: {peri:.2f} — Action Tier: {tier}")

# ------------------------------------------------------------------------------
# MODULE 6: AUTOMATED COMMUNITY DIAGNOSIS
# ------------------------------------------------------------------------------
elif menu == "🩺 Automated Community Diagnosis":
    st.subheader("Automated Community Health Diagnosis Engine")
    
    total_hh = len(st.session_state.hh_records)
    
    if total_hh == 0:
        st.info("No survey records found. Enter data in Module 2 & Module 4 to generate live diagnostic statements.")
    else:
        htn_cases = sum(1 for r in st.session_state.hh_records if r.get("Risk") == "Hypertensive Risk")
        htn_rate = (htn_cases / total_hh) * 100
        last_peri = st.session_state.windshield_records[-1]["PERI_Score"] if len(st.session_state.windshield_records) > 0 else 2.10

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Households", total_hh)
        c2.metric("Hypertension Rate", f"{htn_rate:.1f}%")
        c3.metric("PERI Index", f"{last_peri:.2f}")

        st.markdown("---")
        st.markdown("**Generated Diagnostic Statements:**")

        if htn_rate >= 15.0:
            st.error(f"**Cardiovascular Health Risk:** High prevalence of hypertensive risk ({htn_rate:.1f}%) detected across household vitals screening[cite: 2].")
        if last_peri >= 2.30:
            st.error(f"**Environmental Vector Risk:** Critical environmental degradation (PERI Score: {last_peri:.2f}) elevated vector outbreak hazard[cite: 3].")

# ------------------------------------------------------------------------------
# MODULE 7: EXPORT MASTER DATA
# ------------------------------------------------------------------------------
elif menu == "💾 Export Master Data":
    st.subheader("💾 Export Survey Data Files")
    col1, col2 = st.columns(2)

    with col1:
        if len(st.session_state.hh_records) > 0:
            df1 = pd.DataFrame(st.session_state.hh_records)
            st.download_button("Download Phase 2 Households CSV", df1.to_csv(index=False).encode('utf-8'), "Phase2_Households.csv", "text/csv")
        else:
            st.caption("No household records available for download.")

    with col2:
        if len(st.session_state.windshield_records) > 0:
            df2 = pd.DataFrame(st.session_state.windshield_records)
            st.download_button("Download Phase 4 Windshield CSV", df2.to_csv(index=False).encode('utf-8'), "Phase4_Windshield.csv", "text/csv")
        else:
            st.caption("No windshield assessment records available for download.")
