import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Page Setup
st.set_page_config(
    page_title="UP Manila - Community Clerks Portal",
    page_icon="🩺",
    layout="wide"
)

# Custom Maroon & Gray UI Styling
st.markdown("""
    <style>
    /* Top Website Header Banner */
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
    
    /* Container & Card Styling */
    div[data-testid="stForm"] {
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        background-color: #FFFFFF;
        padding: 24px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }
    
    /* Navigation Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F1F5F9;
        border-right: 1px solid #E2E8F0;
    }
    
    .adult-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #7B1113;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Banner with UP Manila Logo
st.markdown("""
    <div class="up-navbar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/University_of_the_Philippines_Manila_logo.svg/1200px-University_of_the_Philippines_Manila_logo.svg.png" alt="UP Manila Seal">
        <div>
            <div class="up-navbar-title">UNIVERSITY OF THE PHILIPPINES MANILA</div>
            <div class="up-navbar-sub">School of Health Sciences Palo — Community Clerks Field Portal</div>
            <div style="font-size: 12px; color: #CBD5E1; margin-top: 3px;">Lead Developer: <strong>Jan Art A. Serna, RMT</strong> | Comprehensive Health Mapping System</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Helper Function: Compute Child Nutritional Status
def calculate_child_nutrition(age_months, weight_kg, height_cm):
    if height_cm <= 0 or weight_kg <= 0 or age_months <= 0:
        return "Incomplete Measurements"
    
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    
    # Clinical Screening Logic
    wasting_status = "Normal Weight"
    if bmi < 13.5:
        wasting_status = "Severe Acute Malnutrition (SAM) / Severely Wasted"
    elif bmi < 14.5:
        wasting_status = "Moderate Acute Malnutrition (MAM) / Wasted"
    elif bmi > 18.0:
        wasting_status = "Overweight Risk"

    expected_height = 50.0 + (age_months * 1.15)
    stunting_status = "Normal Height"
    if height_cm < (expected_height * 0.85):
        stunting_status = "Severely Stunted"
    elif height_cm < (expected_height * 0.92):
        stunting_status = "Stunted"

    return f"{wasting_status} | {stunting_status} (BMI: {bmi:.1f})"

# Session State Storage
if "hh_records" not in st.session_state:
    st.session_state.hh_records = []
if "gov_records" not in st.session_state:
    st.session_state.gov_records = []
if "qual_records" not in st.session_state:
    st.session_state.qual_records = []
if "windshield_records" not in st.session_state:
    st.session_state.windshield_records = []

# Sidebar Navigation
st.sidebar.markdown("### 🌐 Portal Web Navigation")
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
    st.subheader("📍 Interactive Barangay Health & Risk Spot Map")
    
    if len(st.session_state.hh_records) == 0:
        st.info("No household survey data recorded yet. Displaying baseline spot map preview.")
        map_df = pd.DataFrame([
            {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk": "Hypertensive Risk", "Color": [123, 17, 19, 220]},
            {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk": "Normal", "Color": [34, 197, 94, 200]},
            {"HH_ID": "HH-003", "Purok": "Purok 2", "Lat": 11.1550, "Lon": 124.9930, "BP": "120/80", "Risk": "Severely Stunted Child", "Color": [234, 88, 12, 200]}
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_map, col_filter = st.columns([3, 1])
    
    with col_filter:
        st.markdown("**Map Controls & Filters**")
        purok_list = list(map_df["Purok"].unique())
        selected_puroks = st.multiselect("Filter Purok Zone", options=purok_list, default=purok_list)
        
        st.markdown("---")
        st.markdown("**Spot Map Visual Legend:**")
        st.markdown("🔴 **Maroon/Red:** Hypertensive / Cardiac Risk")
        st.markdown("🟠 **Orange:** Child Malnutrition (SAM/Stunted)")
        st.markdown("🟢 **Green:** Normal Vitals")

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
        t1, t2, t3 = st.tabs(["📝 Metadata", "📊 Complete Governance Matrix (100 pts)", "🎯 Action Plan"])
        
        with t1:
            c1, c2, c3 = st.columns(3)
            brgy_name = c1.text_input("What is the official Barangay Name?")
            city_muni = c2.text_input("What is the City or Municipality?")
            province = c3.text_input("What is the Province?")
            assess_date = c1.date_input("Date of Governance Assessment")
            pb_chair = c2.text_input("Name of Punong Barangay (BHB Chairperson)")
            bhb_sec = c3.text_input("Name of BHB Secretary / Health Committee Lead")

        with t2:
            col_a, col_b = st.columns(2)
            with col_a:
                sc1_1 = st.number_input("1.1 Is there an Executive Order reconstituting the BHB? (Max 5)", 0, 5, 0)
                sc1_2 = st.number_input("1.2 Are mandatory multi-sectoral reps present? (Max 5)", 0, 5, 0)
                sc2_1 = st.number_input("2.1 How many quarterly meetings were held? (3 pts/qtr, Max 12)", 0, 12, 0)
                sc2_2 = st.number_input("2.2 Was official quorum reached in meetings? (Max 4)", 0, 4, 0)
                sc2_3 = st.number_input("2.3 Are signed meeting minutes available? (Max 4)", 0, 4, 0)
                sc3_1 = st.number_input("3.1 Were local health/sanitation ordinances enacted? (Max 10)", 0, 10, 0)
                sc3_2 = st.number_input("3.2 Is an active enforcement task force formed? (Max 5)", 0, 5, 0)
                sc3_3 = st.number_input("3.3 Are local policies aligned with DOH UHC mandates? (Max 5)", 0, 5, 0)
            with col_b:
                sc4_1 = st.number_input("4.1 Are dedicated health line-items in the AIP? (Max 8)", 0, 8, 0)
                sc4_2 = st.number_input("4.2 Is there a budget for BHW honoraria & drugs? (Max 6)", 0, 6, 0)
                sc4_3 = st.number_input("4.3 Is the health budget execution rate >75%? (Max 6)", 0, 6, 0)
                sc5_1 = st.number_input("5.1 Are quarterly health reports submitted to RHU? (Max 8)", 0, 8, 0)
                sc5_2 = st.number_input("5.2 Was health status presented in Barangay Assembly? (Max 4)", 0, 4, 0)
                sc5_3 = st.number_input("5.3 Is a functional Barangay Health Spot Map maintained? (Max 3)", 0, 3, 0)
                sc6_1 = st.number_input("6.1 Are technical working committees active? (Max 6)", 0, 6, 0)
                sc6_2 = st.number_input("6.2 Are monthly committee reports submitted? (Max 6)", 0, 6, 0)
                sc6_3 = st.number_input("6.3 Were community mobilization activities completed? (Max 3)", 0, 3, 0)

        with t3:
            gap = st.text_area("What primary governance gaps were identified during evaluation?")
            action = st.text_area("What technical assistance or corrective action is required?")

        submit_p1 = st.form_submit_button("Save Phase 1 Governance Scorecard")
        if submit_p1:
            total = sum([sc1_1, sc1_2, sc2_1, sc2_2, sc2_3, sc3_1, sc3_2, sc3_3, sc4_1, sc4_2, sc4_3, sc5_1, sc5_2, sc5_3, sc6_1, sc6_2, sc6_3])
            rating = "HIGH FUNCTIONING" if total >= 80 else ("MODERATE FUNCTIONING" if total >= 50 else "LOW FUNCTIONING")
            st.session_state.gov_records.append({"Barangay": brgy_name, "Score": total, "Rating": rating})
            st.success(f"Scorecard Recorded! Total Score: {total}/100 — Status: {rating}")

# ------------------------------------------------------------------------------
# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY[cite: 2]
# ------------------------------------------------------------------------------
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader("Phase 2: Master Household Survey & Multi-Adult Vitals Profiling[cite: 2]")
    
    with st.form("phase2_form"):
        t1, t2, t3, t4 = st.tabs([
            "📌 Metadata & Demographics", 
            "🩺 Adult Physical Screening (Adults 1–5)", 
            "👶 Child Growth & Nutrition Calculator", 
            "🌐 SDOH & Environmental Risks"
        ])

        with t1:
            c1, c2, c3 = st.columns(3)
            hh_id = c1.text_input("Household ID Number", "HH-001")
            brgy = c2.text_input("Barangay Name")
            purok = c3.selectbox("Purok / Zone Location", [f"Purok {i}" for i in range(1, 8)])
            lat = c1.number_input("GPS Latitude Coordinate", value=11.1560, format="%.4f")
            lon = c2.number_input("GPS Longitude Coordinate", value=124.9920, format="%.4f")
            head_name = c3.text_input("Household Head Full Name / Initials")
            
            c1, c2, c3 = st.columns(3)
            income = c1.selectbox("What is the total monthly household income?", ["< ₱10,000", "₱10,000–₱25,000", "₱25,001–₱50,000", "> ₱50,000"])
            philhealth = c2.selectbox("What is the primary PhilHealth membership status?", ["Formal Private/Govt", "Indigent/NHTS", "Senior Citizen", "PWD", "Unenrolled"])
            p4ps = c3.selectbox("Is the household a 4Ps beneficiary?", ["No", "Yes"])

        with t2:
            st.markdown("**Complete Physical Vitals Screening for Up to 5 Adults**")
            
            adult_vitals = []
            for i in range(1, 6):
                with st.expander(f"👤 Adult Member {i} Vitals Screening", expanded=(i == 1)):
                    st.markdown(f"<div class='adult-card'><strong>Adult {i} Profile & Measurements</strong></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns(4)
                    a_name = c1.text_input(f"Adult {i} Name/Initials", key=f"a{i}_name")
                    a_age = c2.number_input(f"Adult {i} Age", 18, 120, 30, key=f"a{i}_age")
                    a_sex = c3.selectbox(f"Adult {i} Sex", ["Male", "Female"], key=f"a{i}_sex")
                    a_sys = c4.number_input(f"Adult {i} Systolic BP (mmHg)", 50, 250, 120, key=f"a{i}_sys")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    a_dia = c1.number_input(f"Adult {i} Diastolic BP (mmHg)", 30, 150, 80, key=f"a{i}_dia")
                    a_spo2 = c2.number_input(f"Adult {i} SpO2 (%)", 50, 100, 98, key=f"a{i}_spo2")
                    a_hr = c3.number_input(f"Adult {i} Heart Rate (bpm)", 30, 200, 75, key=f"a{i}_hr")
                    a_symptom = c4.selectbox(f"Adult {i} Active Risk/Symptom", ["Normal", "Hypertensive Risk", "Hypoxemic Risk", "Chest Pain", "Dizziness"], key=f"a{i}_sym")
                    
                    adult_vitals.append({
                        "Adult": f"Adult {i}", "Name": a_name, "BP": f"{a_sys}/{a_dia}", 
                        "SpO2": a_spo2, "Risk": a_symptom, "Sys": a_sys
                    })

        with t3:
            st.markdown("**Automated Child Growth & Nutritional Status Assessment (0–59 Months)**")
            c1, c2, c3 = st.columns(3)
            child_name = c1.text_input("Child Name / Initials")
            child_age = c2.number_input("Child Age in Months (0–59 mos)", 0, 59, 12)
            child_sex = c3.selectbox("Child Sex", ["Male", "Female"])
            
            c1, c2 = st.columns(2)
            child_weight = c1.number_input("Child Weight in Kilograms (kg)", 0.0, 50.0, 9.0, step=0.1)
            child_height = c2.number_input("Child Height / Recumbent Length in Centimeters (cm)", 0.0, 150.0, 75.0, step=0.5)

            computed_nutritional_status = calculate_child_nutrition(child_age, child_weight, child_height)
            st.info(f"💡 **Calculated Nutritional Diagnosis:** {computed_nutritional_status}")

        with t4:
            c1, c2, c3 = st.columns(3)
            water = c1.selectbox("What is the primary drinking water source?", ["Level III (Tap)", "Level II (Communal Well)", "Level I (Point Source)", "Commercial Water Refill Station", "Unprotected Spring/Surface Water"])
            toilet = c2.selectbox("What type of toilet facility is used?", ["Pour-flush to Septic (Exclusive)", "Pour-flush to Septic (Shared)", "Pit Latrine", "Open Defecation / None"])
            waste = c3.selectbox("How is household solid waste disposed?", ["Municipal/Barangay Collection", "Open Burning (Siga)", "Dumping in Waterway/Vacant Lot", "Composting"])

        submit_p2 = st.form_submit_button("Save Household Data & Update Map Spot")

        if submit_p2:
            primary_adult_bp = adult_vitals[0]["BP"]
            has_htn = any(a["Sys"] >= 140 or a["Risk"] == "Hypertensive Risk" for a in adult_vitals if a["Name"] != "")
            color = [123, 17, 19, 220] if has_htn else [34, 197, 94, 200]
            
            st.session_state.hh_records.append({
                "HH_ID": hh_id, "Barangay": brgy, "Purok": purok, "Lat": lat, "Lon": lon,
                "BP": primary_adult_bp, "Risk": "Hypertensive Risk" if has_htn else "Normal",
                "Child_Nutritional_Status": computed_nutritional_status, "Color": color
            })
            st.success(f"Household {hh_id} with Adult Vitals & Child Nutritional Calculation recorded!")

# ------------------------------------------------------------------------------
# MODULE 4: PHASE 3 QUALITATIVE ASSESSMENT[cite: 4]
# ------------------------------------------------------------------------------
elif menu == "🗣️ Phase 3: Qualitative Assessment":
    st.subheader("Phase 3: Qualitative Field Interview Instruments[cite: 4]")
    
    qual_tool = st.selectbox("Select Assessment Tool", [
        "Tool 3.1: Governance & Leadership KII",
        "Tool 3.2: Frontline Health Personnel KII",
        "Tool 3.3: Community Focus Group Discussion (FGD)"
    ])

    with st.form("phase3_form"):
        c1, c2 = st.columns(2)
        resp = c1.text_input("Name/Position of Respondent or FGD Group")
        loc = c2.text_input("Barangay Location")

        q1 = st.text_area("What are the primary health system bottlenecks identified by the respondent?")
        q2 = st.text_area("What community-level solutions or recommendations were proposed?")

        if st.form_submit_button("Save Qualitative Interview Record"):
            st.session_state.qual_records.append({"Tool": qual_tool, "Respondent": resp, "Notes": q1[:100] + "..."})
            st.success("Qualitative Record Saved!")

# ------------------------------------------------------------------------------
# MODULE 5: PHASE 4 WINDSHEILD ASSESSMENT[cite: 3]
# ------------------------------------------------------------------------------
elif menu == "🔍 Phase 4: Windshield Assessment":
    st.subheader("Phase 4: Windshield & PERI Environmental Assessment[cite: 3]")
    
    with st.form("phase4_form"):
        c1, c2 = st.columns(2)
        brgy_w = c1.text_input("Barangay Evaluated")
        evaluator = c2.text_input("Lead Assessor Name")

        st.caption("Rating Scale: `1 = Low Risk / Safe`, `2 = Moderate Hazard`, `3 = Critical Concern`")

        w1 = st.slider("1. Uncollected Household Solid Waste & Open Burning Exposure", 1, 3, 1)
        w2 = st.slider("2. Open Drainage Channels & Stagnant Wastewater Pooling", 1, 3, 1)
        w3 = st.slider("3. Presence of Dengue Vectors & Mosquito Breeding Sites", 1, 3, 1)
        w4 = st.slider("4. Proximity to Geohazard/Flood Prone Zones", 1, 3, 1)

        if st.form_submit_button("Compute PERI Hazard Score"):
            peri_val = (w1 + w2 + w3 + w4) / 4.0
            tier = "Category A: Low Risk" if peri_val < 1.50 else ("Category B: Moderate Concern" if peri_val < 2.30 else "Category C: Critical Hazard")
            st.session_state.windshield_records.append({"Barangay": brgy_w, "PERI": round(peri_val, 2), "Tier": tier})
            st.warning(f"PERI Composite Index: {peri_val:.2f} — Action Tier: {tier}")

# ------------------------------------------------------------------------------
# MODULE 6: AUTOMATED COMMUNITY DIAGNOSIS
# ------------------------------------------------------------------------------
elif menu == "🩺 Automated Community Diagnosis":
    st.subheader("Automated Community Health Diagnosis Engine")
    
    total_hh = len(st.session_state.hh_records)
    if total_hh == 0:
        st.info("No survey records found. Enter survey data in Phase 2 & Phase 4 to generate live diagnostic statements.")
    else:
        htn_count = sum(1 for r in st.session_state.hh_records if r.get("Risk") == "Hypertensive Risk")
        htn_rate = (htn_count / total_hh) * 100

        c1, c2 = st.columns(2)
        c1.metric("Total Surveyed Households", total_hh)
        c2.metric("Community Hypertension Prevalence", f"{htn_rate:.1f}%")

        st.markdown("---")
        st.markdown("**Automated Diagnostic Statements:**")

        if htn_rate >= 15.0:
            st.error(f"**Cardiovascular Disease Risk:** High prevalence of hypertensive risk ({htn_rate:.1f}%) detected during physical screening across household adult profiles[cite: 2].")

# ------------------------------------------------------------------------------
# MODULE 7: EXPORT MASTER DATA
# ------------------------------------------------------------------------------
elif menu == "💾 Export Master Data":
    st.subheader("💾 Export Survey Data Files")
    if len(st.session_state.hh_records) > 0:
        df_export = pd.DataFrame(st.session_state.hh_records)
        st.download_button("Download Phase 2 Master CSV File", df_export.to_csv(index=False).encode('utf-8'), "UPM_SHS_Phase2_Master.csv", "text/csv")
    else:
        st.caption("No records available to export yet.")
