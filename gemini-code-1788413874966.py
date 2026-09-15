import streamlit as st
import pandas as pd
import numpy as np
import json
import os

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Palo Community Health Assessment & Analytics",
    page_icon="🩺",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 26px; font-weight: bold; color: #1E3A8A; }
    .peri-domain-header { font-size: 16px; font-weight: bold; color: #0D9488; margin-top: 15px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# Constants
PALO_BARANGAYS = [
    "Anibong", "Arado", "Bagon", "Baras", "Barayong", "Bawi", "Cabarasan Daku",
    "Cabarasan Guti", "Campetic", "Candahug", "Cangumbang", "Canhiptoc",
    "Concepcion", "Cogon", "Guti", "Guindapunan", "Lawi", "Lira", "Lutao",
    "Malirong", "Naga-naga", "San Antonio", "San Fernando", "San Isidro",
    "San Jose", "San Roque", "Santa Cruz", "Santee", "Sevilla", "Sua",
    "Takuranga", "Tugbao", "Victoria"
]

DATA_FILE = "copar_session_data.json"

# Persistence Helper Functions
def save_session_to_disk():
    data = {
        "hh_records": st.session_state.get("hh_records", []),
        "gov_records": st.session_state.get("gov_records", []),
        "qual_records": st.session_state.get("qual_records", []),
        "windshield_records": st.session_state.get("windshield_records", []),
        "diag_records": st.session_state.get("diag_records", [])
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_session_from_disk():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "hh_records": [],
        "gov_records": [],
        "qual_records": [],
        "windshield_records": [],
        "diag_records": []
    }

# Initialize Session State
saved_data = load_session_from_disk()
if "hh_records" not in st.session_state:
    st.session_state.hh_records = saved_data.get("hh_records", [])
if "gov_records" not in st.session_state:
    st.session_state.gov_records = saved_data.get("gov_records", [])
if "qual_records" not in st.session_state:
    st.session_state.qual_records = saved_data.get("qual_records", [])
if "windshield_records" not in st.session_state:
    st.session_state.windshield_records = saved_data.get("windshield_records", [])
if "diag_records" not in st.session_state:
    st.session_state.diag_records = saved_data.get("diag_records", [])

# Navigation Sidebar
st.sidebar.title("🩺 COPAR Health Suite")
menu = st.sidebar.radio(
    "Select Module / Assessment Phase",
    [
        "📋 Phase 1 & 2: Household Quantitative Survey",
        "🏛️ Tool 3.1: KII — LGU & Health Governance",
        "🗣️ Phase 3: Qualitative KII & FGD Tools",
        "🔍 Phase 4: Expanded PERI Windshield Tool",
        "📈 Phase 5: Spatial & Statistical Analytics",
        "📊 Social Determinants of Health Presentation & Interpretation",
        "📋 Phase 6: Community Diagnosis & Action Plan",
        "💾 Data Management & Export"
    ]
)

# ================= MODULE 1: HOUSEHOLD SURVEY =================
if menu == "📋 Phase 1 & 2: Household Quantitative Survey":
    st.subheader("📋 Phase 1 & 2: Household Quantitative Survey")
    
    with st.form("hh_survey_form"):
        c1, c2, c3 = st.columns(3)
        brgy = c1.selectbox("Barangay", PALO_BARANGAYS)
        purok = c2.text_input("Purok / Zone", "Purok 1")
        hh_num = c3.text_input("Household Number", "HH-001")
        
        c1, c2, c3 = st.columns(3)
        respondent = c1.text_input("Respondent Name")
        income = c2.selectbox("Monthly Family Income", ["< ₱5,000", "₱5,000 - ₱10,000", "₱10,001 - ₱20,000", "> ₱20,000"])
        four_ps = c3.selectbox("4Ps Beneficiary", ["Yes", "No"])
        
        st.markdown("**Environmental & Health Indicators**")
        c1, c2, c3 = st.columns(3)
        water = c1.selectbox("Primary Water Source", ["Level I (Point Source)", "Level II (Communal Faucet)", "Level III (Individual Connection)", "Unimproved/Well"])
        sanitation = c2.selectbox("Sanitation Facility", ["Sanitary Toilet (Poured/Flush)", "Unsanitary Toilet", "No Toilet / Open Defecation"])
        flood_prone = c3.selectbox("Flood Risk Area", ["High", "Moderate", "Low / None"])
        
        st.markdown("**Health Status & Morbidity**")
        c1, c2, c3 = st.columns(3)
        htn = c1.selectbox("Hypertension Cases in HH", ["None", "Diagnosed & Controlled", "Diagnosed & Uncontrolled", "Undiagnosed / Suspected"])
        dm = c2.selectbox("Diabetes Cases in HH", ["None", "Diagnosed & Controlled", "Diagnosed & Uncontrolled", "Undiagnosed / Suspected"])
        food_skip = c3.selectbox("Skipped Meals Due to Cost (Past Month)", ["Never", "Sometimes", "Often"])
        
        risk = st.select_slider("Assessed Overall Household Risk Level", options=["Low", "Moderate", "High", "Critical"])
        
        if st.form_submit_button("💾 Save Household Record"):
            st.session_state.hh_records.append({
                "Barangay": brgy,
                "Purok": purok,
                "HH_Num": hh_num,
                "Respondent": respondent,
                "Income": income,
                "Four_Ps": four_ps,
                "Water": water,
                "Sanitation": sanitation,
                "Flood_Prone": flood_prone,
                "Hypertension_Status": htn,
                "Diabetes_Status": dm,
                "Food_Skip": food_skip,
                "Risk": risk
            })
            save_session_to_disk()
            st.success("Household Record Saved Successfully!")

# ================= MODULE 2: GOVERNANCE KII =================
elif menu == "🏛️ Tool 3.1: KII — LGU & Health Governance":
    st.subheader("🏛️ Tool 3.1: Key Informant Interview — Governance & LGU Leadership")
    
    with st.form("gov_kii_form"):
        c1, c2 = st.columns(2)
        resp_name = c1.text_input("Respondent Name & Office")
        brgy_covered = c2.selectbox("Barangay / Jurisdiction", PALO_BARANGAYS)
        
        st.markdown("**Governance & Budgeting Assessment**")
        budget_alloc = st.text_area("1. Local Health Board / Barangay Health Budget Allocation & Spending Priorities:")
        infra_dev = st.text_area("2. Health Infrastructure & BHS Maintenance/Equipage:")
        disaster_res = st.text_area("3. Disaster Preparedness & Health Resilience Mechanisms:")
        
        if st.form_submit_button("💾 Save Governance Record"):
            st.session_state.gov_records.append({
                "Respondent": resp_name,
                "Barangay": brgy_covered,
                "BudgetAllocation": budget_alloc,
                "InfraDev": infra_dev,
                "DisasterResilience": disaster_res
            })
            save_session_to_disk()
            st.success("Governance KII Saved Successfully!")

# ================= MODULE 3: PHASE 3 QUALITATIVE TOOLS =================
elif menu == "🗣️ Phase 3: Qualitative KII & FGD Tools":
    st.subheader("🗣️ Phase 3: Qualitative Data Collection Tools")
    
    tool_choice = st.selectbox("Select Tool", [
        "TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE PERSONNEL",
        "TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS"
    ])
    
    if tool_choice == "TOOL 3.2: KEY INFORMANT INTERVIEW (KII) GUIDE — FRONTLINE PERSONNEL":
        st.markdown("### 📋 TOOL 3.2: KII GUIDE — FRONTLINE HEALTH WORKERS (BHW, BHM, RHU STAFF)")
        with st.form("kii_frontline_form"):
            c1, c2, c3 = st.columns(3)
            resp_name = c1.text_input("Respondent Name (Optional)")
            role = c2.selectbox("Designation / Role", ["BHW (Barangay Health Worker)", "BHM (Midwife)", "PHN (Public Health Nurse)", "RHM", "Sanitary Inspector", "Other"])
            bhs_name = c3.selectbox("Assigned Barangay / BHS", PALO_BARANGAYS)

            c1, c2, c3, c4 = st.columns(4)
            date_time = c1.text_input("Date & Time", "2026-09-15 10:00")
            interviewer = c2.text_input("Interviewer Name")
            years_service = c3.number_input("Years of Service in Palo", 0, 50, 5)
            consent = c4.selectbox("Informed Consent Obtained?", ["Yes", "No"])

            audio_rec = st.radio("Audio Recording Permission:", ["Granted", "Declined (Notes Only)"], horizontal=True)
            st.markdown("---")

            st.markdown("**1. Workload, Resource Constraints & Supply Chains**")
            st.info("What are the primary resource shortages (medications, equipment, PPE) that affect your daily duties?")
            st.caption("• How frequently do essential NCD (hypertension, diabetes) or maternal supplies run out?\n• How does workload impact your home-visiting coverage per purok?")
            q1_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 1)", key="kii_f_q1")

            st.markdown("**2. Referral Logistics & Transport Emergency Networks**")
            st.info("Walk me through the referral process when a patient needs urgent secondary or tertiary care.")
            st.caption("• What are the bottleneck challenges between BHS, RHU, and target receiving hospitals?\n• How are high-risk pregnant women or trauma cases handled when transport is delayed?")
            q2_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 2)", key="kii_f_q2")

            st.markdown("**3. Treatment Compliance & Community Adherence**")
            st.info("What are the primary reasons patients stop taking their hypertension, diabetes, or TB medications?")
            st.caption("• Are financial constraints, side-effects, or cultural beliefs the main barriers?\n• How do BHWs monitor daily compliance in remote puroks?")
            q3_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 3)", key="kii_f_q3")

            st.markdown("**4. Maternal & Child Health Support**")
            st.info("What challenges do you face in ensuring 100% facility-based deliveries and complete child immunizations?")
            q4_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 4)", key="kii_f_q4")

            st.markdown("**5. Frontline Support & Compensation**")
            st.info("What support or incentive changes would most boost frontline worker morale and effectiveness?")
            q5_notes = st.text_area("Qualitative Notes / Key Quotations (Domain 5)", key="kii_f_q5")

            if st.form_submit_button("💾 Save TOOL 3.2 Interview Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.2: KII — Frontline Personnel",
                    "Respondent": resp_name,
                    "Designation": role,
                    "Barangay": bhs_name,
                    "Date_Time": date_time,
                    "Interviewer": interviewer,
                    "Years_Service": years_service,
                    "Consent": consent,
                    "Audio": audio_rec,
                    "D1_Workload": q1_notes,
                    "D2_Referral": q2_notes,
                    "D3_Adherence": q3_notes,
                    "D4_MCH": q4_notes,
                    "D5_FrontlineSupport": q5_notes,
                })
                save_session_to_disk()
                st.success("TOOL 3.2 KII Frontline Record Saved Successfully!")

    elif tool_choice == "TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS":
        st.markdown("### 👥 TOOL 3.3: FOCUS GROUP DISCUSSION (FGD) GUIDE — COMMUNITY MEMBERS")
        with st.form("fgd_form"):
            c1, c2, c3 = st.columns(3)
            group_desc = c1.text_input("Group Profile (e.g., Mothers, Seniors, Farmers)")
            brgy_name = c2.selectbox("Barangay / Location", PALO_BARANGAYS)
            num_participants = c3.number_input("Number of Participants", 3, 20, 8)

            c1, c2 = st.columns(2)
            facilitator = c1.text_input("Facilitator Name")
            note_taker = c2.text_input("Note-Taker Name")

            st.markdown("---")
            fgd_q1 = st.text_area("1. Perceptions of Local Health Services & Facilities:")
            fgd_q2 = st.text_area("2. Environmental & Water/Sanitation Concerns:")
            fgd_q3 = st.text_area("3. Barriers to Seeking Emergency & Preventive Care:")
            fgd_q4 = st.text_area("4. Community-Suggested Priorities & Solutions:")

            if st.form_submit_button("💾 Save TOOL 3.3 FGD Record"):
                st.session_state.qual_records.append({
                    "Tool": "TOOL 3.3: FGD — Community Members",
                    "Group Profile": group_desc,
                    "Barangay": brgy_name,
                    "Participants": num_participants,
                    "Facilitator": facilitator,
                    "Note_Taker": note_taker,
                    "Q1_HealthServices": fgd_q1,
                    "Q2_WASH": fgd_q2,
                    "Q3_Barriers": fgd_q3,
                    "Q4_Solutions": fgd_q4,
                })
                save_session_to_disk()
                st.success("TOOL 3.3 FGD Record Saved Successfully!")

# ================= MODULE 4: PHASE 4 EXPANDED PERI WINDSHIELD TOOL =================
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader("🔍 Phase 4: Expanded Purok Environmental Risk Index (PERI) Windshield Tool")

    with st.form("peri_windshield_form"):
        c1, c2, c3 = st.columns(3)
        purok_name = c1.selectbox("Purok", [f"Purok {i}" for i in range(1, 8)])
        eval_brgy = c2.selectbox("Barangay", PALO_BARANGAYS)
        evaluator = c3.text_input("Evaluator Full Name")

        st.markdown("<div class='peri-domain-header'>Domain 1: Water & Sanitation Vulnerability (0-3)</div>", unsafe_allow_html=True)
        ds1 = st.slider("Score (0 = Low Risk/Clean, 3 = Severe Hazard)", 0.0, 3.0, 1.0, 0.5, key="ds1")

        st.markdown("<div class='peri-domain-header'>Domain 2: Food Safety & Market Hygiene (0-3)</div>", unsafe_allow_html=True)
        ds2 = st.slider("Score (0 = Low Risk, 3 = Severe Hazard)", 0.0, 3.0, 1.0, 0.5, key="ds2")

        st.markdown("<div class='peri-domain-header'>Domain 3: Built Environment & Housing Resilience (0-3)</div>", unsafe_allow_html=True)
        ds3 = st.slider("Score (0 = Sound Structure, 3 = Dilapidated/High Risk)", 0.0, 3.0, 1.0, 0.5, key="ds3")

        st.markdown("<div class='peri-domain-header'>Domain 4: Health Infrastructure Accessibility (0-3)</div>", unsafe_allow_html=True)
        ds4 = st.slider("Score (0 = Highly Accessible, 3 = Isolated/No Access)", 0.0, 3.0, 1.0, 0.5, key="ds4")

        st.markdown("<div class='peri-domain-header'>Domain 5: Disaster Risk & Climate Vulnerability (0-3)</div>", unsafe_allow_html=True)
        ds5 = st.slider("Score (0 = Safe Zone, 3 = Severe Flood/Landslide Risk)", 0.0, 3.0, 1.0, 0.5, key="ds5")

        st.markdown("<div class='peri-domain-header'>Domain 6: Vector & Environmental Waste Hazard (0-3)</div>", unsafe_allow_html=True)
        ds6 = st.slider("Score (0 = Clean, 3 = Heavy Breeding/Dumping Sites)", 0.0, 3.0, 1.0, 0.5, key="ds6")

        peri_notes = st.text_area("Field Assessment Notes & Observations:")

        if st.form_submit_button("💾 Save PERI Windshield Record"):
            peri_index = np.mean([ds1, ds2, ds3, ds4, ds5, ds6])
            st.session_state.windshield_records.append({
                "Purok": purok_name,
                "Barangay": eval_brgy,
                "Evaluator": evaluator,
                "DS1_Sanitation": ds1,
                "DS2_Food": ds2,
                "DS3_BuiltEnv": ds3,
                "DS4_HealthInfra": ds4,
                "DS5_DRR": ds5,
                "DS6_Vector": ds6,
                "PERI_Index": float(round(peri_index, 2)),
                "Notes": peri_notes,
            })
            save_session_to_disk()
            st.success(f"PERI Windshield Assessment Saved! Overall Index: {peri_index:.2f}")

# ================= MODULE 5: PHASE 5 STATISTICAL ANALYTICS =================
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("📈 Phase 5: Statistical Analytics & Cross-Tabulations")

    if len(st.session_state.hh_records) == 0:
        st.info("No household records found for cross-tabulation. Please complete Household Surveys first.")
    else:
        df_hh = pd.DataFrame(st.session_state.hh_records)
        col_x, col_y = st.columns(2)
        var_x = col_x.selectbox("Select Variable X (Row)", ["Income", "Water", "Sanitation", "Flood_Prone", "Four_Ps"])
        var_y = col_y.selectbox("Select Variable Y (Column)", ["Risk", "Hypertension_Status", "Diabetes_Status", "Food_Skip"])

        ct = pd.crosstab(df_hh[var_x], df_hh[var_y], margins=True)
        st.markdown(f"**Cross-Tabulation: {var_x} vs. {var_y}**")
        st.dataframe(ct, use_container_width=True)

# ================= MODULE 6: SDOH PRESENTATION =================
elif menu == "📊 Social Determinants of Health Presentation & Interpretation":
    st.subheader("📊 Social Determinants of Health (SDOH) Strategic Framework")
    st.markdown("""
    **Key Structural Domains:**
    * **Economic Stability:** Income quintiles, 4Ps coverage, ₱5k emergency cushion resilience.
    * **Education Access:** Literacy levels, school dropouts, health literacy barriers.
    * **Healthcare Access & Quality:** PhilHealth YAKAP enrollment, travel times, medicine stock-outs.
    * **Neighborhood & Built Environment:** Flood hazard mapping, Level 1-3 water security, toilet availability.
    * **Social & Community Context:** Family decision-making structures, local leadership support.
    """)

# ================= MODULE 7: PHASE 6 ACTION PLAN =================
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("📋 Phase 6: Prioritized Community Diagnosis & Strategic Action Plan")

    with st.form("diag_form"):
        diag_title = st.text_input("Community Health Diagnosis / Problem Statement")
        priority_lvl = st.selectbox("Priority Ranking", ["High Priority", "Medium Priority", "Low Priority"])
        target_pop = st.text_input("Target Population / Purok")
        objectives = st.text_area("Specific, Measurable Objectives (SMART)")
        interventions = st.text_area("Proposed Public Health Interventions")
        responsible_parties = st.text_input("Responsible Lead Agencies / Stakeholders")
        timeline = st.text_input("Implementation Timeline (e.g., Q1-Q2 2026)")

        if st.form_submit_button("💾 Save Action Plan Entry"):
            st.session_state.diag_records.append({
                "Diagnosis": diag_title,
                "Priority": priority_lvl,
                "Target": target_pop,
                "Objectives": objectives,
                "Interventions": interventions,
                "Responsible": responsible_parties,
                "Timeline": timeline,
            })
            save_session_to_disk()
            st.success("Action Plan saved successfully!")

    if len(st.session_state.diag_records) > 0:
        st.markdown("### 📑 Stored Community Action Plans")
        st.dataframe(pd.DataFrame(st.session_state.diag_records), use_container_width=True)

# ================= MODULE 8: DATA MANAGEMENT & EXPORT =================
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Data Management, Cloud Backup & JSON/CSV Export")

    st.markdown("**Export Permanent Session Data**")
    c1, c2, c3 = st.columns(3)

    if len(st.session_state.hh_records) > 0:
        hh_json = json.dumps(st.session_state.hh_records, indent=2)
        c1.download_button("📥 Download HH Survey Data (JSON)", hh_json, "hh_records.json", "application/json")

    if len(st.session_state.gov_records) > 0:
        gov_json = json.dumps(st.session_state.gov_records, indent=2)
        c2.download_button("📥 Download Governance Data (JSON)", gov_json, "gov_records.json", "application/json")

    if len(st.session_state.windshield_records) > 0:
        peri_json = json.dumps(st.session_state.windshield_records, indent=2)
        c3.download_button("📥 Download PERI Data (JSON)", peri_json, "peri_records.json", "application/json")

    st.markdown("---")
    st.markdown("**⚠️ Administrative Controls**")
    if st.button("🚨 Clear All Local Session Storage"):
        st.session_state.hh_records = []
        st.session_state.gov_records = []
        st.session_state.qual_records = []
        st.session_state.windshield_records = []
        st.session_state.diag_records = []
        save_session_to_disk()
        st.warning("All records cleared from persistent cloud storage.")
        st.rerun()
