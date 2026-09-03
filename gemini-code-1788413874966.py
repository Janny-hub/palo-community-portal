import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Page Configuration & Branding
st.set_page_config(
    page_title="UPM-SHS Palo Community Clerks Portal",
    page_icon="🩺",
    layout="wide"
)

# App Title & Header
st.title("University of the Philippines Manila")
st.subheader("School of Health Sciences Palo — Community Clerks Portal")
st.caption("Developed by **Jan Art A. Serna, RMT** | Integrated Health Assessment & GIS Spot Mapping System")
st.divider()

# Session State Initialization
if "hh_data" not in st.session_state:
    st.session_state.hh_data = pd.DataFrame([
        {"HH_ID": "HH-001", "Purok": "Purok 1", "Lat": 11.1562, "Lon": 124.9912, "BP": "145/92", "Risk_Category": "Hypertensive Risk", "Color": [255, 0, 0, 200]},
        {"HH_ID": "HH-002", "Purok": "Purok 1", "Lat": 11.1568, "Lon": 124.9918, "BP": "118/78", "Risk_Category": "Normal", "Color": [0, 200, 80, 200]},
        {"HH_ID": "HH-003", "Purok": "Purok 2", "Lat": 11.1550, "Lon": 124.9930, "BP": "120/80", "Risk_Category": "Severely Stunted Child", "Color": [255, 140, 0, 200]},
        {"HH_ID": "HH-004", "Purok": "Purok 3", "Lat": 11.1542, "Lon": 124.9905, "BP": "160/100", "Risk_Category": "PERI Category C Hazard", "Color": [139, 0, 0, 220]}
    ])

if "gov_score" not in st.session_state:
    st.session_state.gov_score = 75

if "peri_score" not in st.session_state:
    st.session_state.peri_score = 2.45

# Sidebar Navigation
menu = st.sidebar.radio(
    "Select Portal Module",
    [
        "🗺️ Interactive Spot Map", 
        "📋 Phase 1: BHB Governance Scorecard", 
        "🏠 Phase 2: Household & Vitals Survey", 
        "🗣️ Phase 3: Qualitative Interviews", 
        "🔍 Phase 4: Windshield & PERI Assessment", 
        "🩺 Automated Community Diagnosis Engine"
    ]
)

# MODULE 1: INTERACTIVE SPOT MAP
if menu == "🗺️ Interactive Spot Map":
    st.header("📍 Interactive Barangay Health & Risk Spot Map")
    col_map, col_filter = st.columns([3, 1])
    
    with col_filter:
        st.subheader("Filter Layers")
        puroks = list(st.session_state.hh_data["Purok"].unique())
        selected_purok = st.multiselect("Select Purok", options=puroks, default=puroks)
        show_risk_only = st.checkbox("High-Risk Cases Only")
        
        st.markdown("---")
        st.markdown("**Spot Map Legend:**")
        st.markdown("🔴 **Red:** Hypertensive Risk")
        st.markdown("🟠 **Orange:** Child Malnutrition")
        st.markdown("🟤 **Dark Red:** Environmental PERI Hazard")
        st.markdown("🟢 **Green:** Normal Vitals")

    df_filtered = st.session_state.hh_data[st.session_state.hh_data["Purok"].isin(selected_purok)]
    if show_risk_only:
        df_filtered = df_filtered[df_filtered["Risk_Category"] != "Normal"]

    with col_map:
        view_state = pdk.ViewState(latitude=11.1555, longitude=124.9915, zoom=15, pitch=30)
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_filtered,
            get_position=["Lon", "Lat"],
            get_color="Color",
            get_radius=12,
            pickable=True,
            auto_highlight=True
        )
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Household: {HH_ID}\nPurok: {Purok}\nBP: {BP}\nStatus: {Risk_Category}"}
        )
        st.pydeck_chart(r)

# MODULE 2: PHASE 1 GOVERNANCE SCORECARD
elif menu == "📋 Phase 1: BHB Governance Scorecard":
    st.header("Phase 1: Barangay Health Board (BHB) Governance Scorecard")
    with st.form("gov_form"):
        d1 = st.number_input("1. Legal Reconstitution (Max 10)", 0, 10, 8)
        d2 = st.number_input("2. Meeting Regularity (Max 20)", 0, 20, 15)
        d3 = st.number_input("3. Legislative Output (Max 20)", 0, 20, 12)
        d4 = st.number_input("4. AIP Budget Allocation (Max 20)", 0, 20, 16)
        d5 = st.number_input("5. Accomplishment Reports (Max 15)", 0, 15, 10)
        d6 = st.number_input("6. Committee Functionality (Max 15)", 0, 15, 14)
        
        if st.form_submit_button("Calculate Governance Score"):
            total = d1 + d2 + d3 + d4 + d5 + d6
            st.session_state.gov_score = total
            status = "HIGH FUNCTIONING" if total >= 80 else ("MODERATE FUNCTIONING" if total >= 50 else "LOW FUNCTIONING")
            st.success(f"Total Score: {total}/100 — Category: {status}")

# MODULE 3: PHASE 2 HOUSEHOLD SURVEY & VITALS
elif menu == "🏠 Phase 2: Household & Vitals Survey":
    st.header("Phase 2: Master Household Survey & Vitals Profiling")
    with st.form("hh_form"):
        col1, col2 = st.columns(2)
        hh_id = col1.text_input("Household ID", "HH-005")
        purok = col2.selectbox("Purok", ["Purok 1", "Purok 2", "Purok 3", "Purok 4"])
        lat = col1.number_input("Latitude (Lat)", value=11.1560, format="%.4f")
        lon = col2.number_input("Longitude (Lon)", value=124.9920, format="%.4f")
        bp = col1.text_input("Blood Pressure (mmHg)", "140/90")
        risk = col2.selectbox("Risk Category", ["Normal", "Hypertensive Risk", "Hypoxemic Risk", "Severely Stunted Child", "PERI Category C Hazard"])
        
        if st.form_submit_button("Save Household Data & Update Map"):
            color_map = {
                "Normal": [0, 200, 80, 200],
                "Hypertensive Risk": [255, 0, 0, 200],
                "Hypoxemic Risk": [139, 0, 0, 220],
                "Severely Stunted Child": [255, 140, 0, 200],
                "PERI Category C Hazard": [139, 0, 0, 220]
            }
            new_row = pd.DataFrame([{"HH_ID": hh_id, "Purok": purok, "Lat": lat, "Lon": lon, "BP": bp, "Risk_Category": risk, "Color": color_map[risk]}])
            st.session_state.hh_data = pd.concat([st.session_state.hh_data, new_row], ignore_index=True)
            st.success(f"Household {hh_id} recorded and mapped successfully!")

# MODULE 4: PHASE 3 QUALITATIVE INTERVIEWS
elif menu == "🗣️ Phase 3: Qualitative Interviews":
    st.header("Phase 3: Qualitative Assessment Instruments")
    st.text_area("Key Informant Interview (KII) — Governance & Leadership Notes")
    st.text_area("Frontline Personnel Interview — Midwife / BHW Notes")
    st.text_area("Focus Group Discussion (FGD) — Community Member Themes")
    if st.button("Save Qualitative Record"):
        st.success("Qualitative data saved successfully.")

# MODULE 5: PHASE 4 WINDSHEILD ASSESSMENT & PERI
elif menu == "🔍 Phase 4: Windshield & PERI Assessment":
    st.header("Phase 4: Multi-Domain Windshield & Environmental Assessment")
    with st.form("peri_form"):
        ds1 = st.slider("Domain 1: Sanitation & Waste Management Score", 1.0, 3.0, 2.2)
        ds2 = st.slider("Domain 2: Food Environment & Nutrition Score", 1.0, 3.0, 1.8)
        ds3 = st.slider("Domain 3: Built Environment & Housing Score", 1.0, 3.0, 2.0)
        ds4 = st.slider("Domain 4: Health Infrastructure Access Score", 1.0, 3.0, 2.5)
        ds5 = st.slider("Domain 5: Disaster Safety & Geohazards Score", 1.0, 3.0, 2.1)
        ds6 = st.slider("Domain 6: Vector Control & Exposure Score", 1.0, 3.0, 2.4)
        
        if st.form_submit_button("Calculate PERI Score"):
            peri = (ds1 + ds2 + ds3 + ds4 + ds5 + ds6) / 6.0
            st.session_state.peri_score = peri
            tier = "Category A: Low Risk" if peri < 1.50 else ("Category B: Moderate Concern" if peri < 2.30 else "Category C: Critical Hazard")
            st.warning(f"Calculated PERI Composite Index: {peri:.2f} — {tier}")

# MODULE 6: AUTOMATED COMMUNITY DIAGNOSIS
elif menu == "🩺 Automated Community Diagnosis Engine":
    st.header("Automated Community Health Diagnosis")
    
    total_hh = len(st.session_state.hh_data)
    htn_count = len(st.session_state.hh_data[st.session_state.hh_data["Risk_Category"] == "Hypertensive Risk"])
    htn_rate = (htn_count / total_hh) * 100 if total_hh > 0 else 0
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Governance Functionality", f"{st.session_state.gov_score}/100")
    col_m2.metric("PERI Composite Index", f"{st.session_state.peri_score:.2f}")
    col_m3.metric("Hypertension Rate", f"{htn_rate:.1f}%")
    
    st.subheader("Generated Diagnostic Statements")
    
    if st.session_state.peri_score >= 2.30:
        st.error(f"**Critical Environmental Risk:** High vulnerability to vector/waterborne outbreaks secondary to severe environmental hazards (PERI Index: {st.session_state.peri_score:.2f})[cite: 3].")
    if htn_rate >= 20.0:
        st.error(f"**Cardiovascular Health Risk:** High prevalence of hypertensive risk ({htn_rate:.1f}%) detected across surveyed household vitals[cite: 2].")
    if st.session_state.gov_score < 80:
        st.warning(f"**Governance Gap:** Moderate/Low local governance functionality ({st.session_state.gov_score}/100) requiring municipal technical assistance and budget alignment[cite: 1].")