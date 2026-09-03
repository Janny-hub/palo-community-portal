import json
import os
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="UP Manila - Community Clerks Portal (Dev: Jan Art Serna, RMT)",
    page_icon="🩺",
    layout="wide",
)

# ================= SHARED MULTI-ENUMERATOR DATA PERSISTENCE =================
DATA_FILE = "shared_survey_data.json"


def load_shared_data():
    """Reads shared survey records from disk for multi-enumerator sync."""
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
    """Saves shared survey records to disk."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error persisting shared data: {e}")


def sync_session_from_disk():
    """Syncs local Streamlit session state with the shared data file."""
    shared = load_shared_data()
    st.session_state.hh_records = shared.get("hh_records", [])
    st.session_state.gov_records = shared.get("gov_records", [])
    st.session_state.qual_records = shared.get("qual_records", [])
    st.session_state.windshield_records = shared.get("windshield_records", [])
    st.session_state.diag_records = shared.get("diag_records", [])


def save_session_to_disk():
    """Writes session state records into the shared data file."""
    shared = {
        "hh_records": st.session_state.get("hh_records", []),
        "gov_records": st.session_state.get("gov_records", []),
        "qual_records": st.session_state.get("qual_records", []),
        "windshield_records": st.session_state.get("windshield_records", []),
        "diag_records": st.session_state.get("diag_records", []),
    }
    save_shared_data(shared)


# Sync latest data on rerun so enumerators see updates in real-time
sync_session_from_disk()

# Initialize Authentication & Navigation State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

NAV_OPTIONS = [
    "🗺️ Interactive Spot Map",
    "📋 Phase 1: Full Governance Scorecard",
    "🏠 Phase 2: Master Household Survey",
    "🗣️ Phase 3: Qualitative Field Tools",
    "🔍 Phase 4: Expanded PERI Windshield Tool",
    "📈 Phase 5: Spatial & Statistical Analytics",
    "📋 Phase 6: Community Diagnosis & Action Plan",
    "🩺 Diagnostic Summary & Analytics",
    "💾 Data Management & Export",
]

if "menu_selection" not in st.session_state:
    st.session_state["menu_selection"] = NAV_OPTIONS[0]

# Modal State Management
if "show_success_modal" not in st.session_state:
    st.session_state["show_success_modal"] = False
if "modal_title" not in st.session_state:
    st.session_state["modal_title"] = ""
if "modal_details" not in st.session_state:
    st.session_state["modal_details"] = ""
if "modal_next_page" not in st.session_state:
    st.session_state["modal_next_page"] = None


# Helper function to trigger success modal popup
def trigger_success_modal(title, details, next_page=None):
    st.session_state["modal_title"] = title
    st.session_state["modal_details"] = details
    st.session_state["modal_next_page"] = next_page
    st.session_state["show_success_modal"] = True


# Login Form Block
def show_login_screen():
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown(
        '<div class="login-title">🩺 UP Manila Clerks Portal</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="login-sub">Comprehensive Community Health Field Portal</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="dev-badge-login">⭐ Lead developer Jan Art A. Serna, RMT</div>',
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


# Stop execution if user is not authenticated
if not st.session_state["authenticated"]:
    show_login_screen()
    st.stop()

# ================= CLIENT-SIDE JS & AUTOSAVE INJECTION =================
# Injecting the requested 30-Second Autosave Interval, Submit Handler & Modal JS
JS_AUTOSAVE_AND_MODAL = """
<script>
// --------------------------------------------------
// 1. Save Function (Shared by Manual Save & Autosave)
// --------------------------------------------------
function autoSaveFormData() {
  console.log("Autosaving field form data to local storage & syncing...");
  const formData = {};
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach((input, idx) => {
    if (input.name || input.id) {
      formData[input.id || input.name || idx] = input.value;
    }
  });
  localStorage.setItem('upm_clerks_autosave', JSON.stringify(formData));
}

// --------------------------------------------------
// 2. 30-Second Autosave Interval (Does NOT submit)
// --------------------------------------------------
const AUTOSAVE_INTERVAL_MS = 30000; // 30 seconds

if (!window.autosaveIntervalActive) {
  setInterval(() => {
    autoSaveFormData();
  }, AUTOSAVE_INTERVAL_MS);
  window.autosaveIntervalActive = true;
}

// --------------------------------------------------
// 3. Form Submit & Success Pop-up Handler
// --------------------------------------------------
document.addEventListener('DOMContentLoaded', (event) => {
  const form = document.querySelector('form');
  const successModal = document.getElementById('successModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalOkBtn = document.getElementById('modalOkBtn');

  if (form) {
    form.addEventListener('submit', function (e) {
      autoSaveFormData();
      showSuccessModal();
    });
  }

  function showSuccessModal() {
    if (successModal) successModal.style.display = 'flex';
  }

  function hideSuccessModal() {
    if (successModal) successModal.style.display = 'none';
  }

  closeModalBtn?.addEventListener('click', hideSuccessModal);
  modalOkBtn?.addEventListener('click', hideSuccessModal);

  window.addEventListener('click', function (e) {
    if (e.target === successModal) {
      hideSuccessModal();
    }
  });

  // --------------------------------------------------
  // 4. Next Page Navigation Logic
  // --------------------------------------------------
  document.getElementById('nextPageBtn')?.addEventListener('click', function () {
    autoSaveFormData();
  });
});
</script>
"""
components.html(JS_AUTOSAVE_AND_MODAL, height=0)

# Native Streamlit 30-Second Periodic Autosave Fragment
if hasattr(st, "fragment"):
    @st.fragment(run_every="30s")
    def periodic_autosave_sync():
        save_session_to_disk()
    periodic_autosave_sync()

# ================= CUSTOM CSS STYLING =================
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
.child-card {
    background-color: #F0FDF4;
    border: 1px solid #DCFCE7;
    border-left: 4px solid #16A34A;
    padding: 12px 15px;
    border-radius: 6px;
    margin-bottom: 12px;
}
.peri-domain-header {
    background-color: #7B1113;
    color: #FFFFFF;
    padding: 8px 14px;
    border-radius: 6px;
    font-weight: 700;
    margin-bottom: 12px;
}
.autosave-indicator {
    font-size: 11px;
    color: #059669;
    font-weight: 600;
    background: #ECFDF5;
    padding: 4px 8px;
    border-radius: 4px;
    border: 1px solid #A7F3D0;
    display: inline-block;
    margin-bottom: 10px;
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
    <div class="dev-honor-banner">Lead developer Jan Art A. Serna, RMT</div>
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


# Dynamic Progress Tracker Calculations
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

# Sidebar - Sticky Progress Tracker & Multi-Enumerator Sync
st.sidebar.markdown(
    f"""
<div class="sticky-progress-container">
    <div style="font-weight: 700; color: #1E293B; font-size: 14px; margin-bottom: 4px;">📊 Phase Completion Tracker</div>
    <div style="font-weight: 800; color: #7B1113; font-size: 18px; margin-bottom: 4px;">{overall_progress_pct}% Completed</div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.progress(overall_progress_pct / 100)

st.sidebar.markdown(
    '<div class="autosave-indicator">⏱️ 30s Background Autosave Active</div>',
    unsafe_allow_html=True,
)

if st.sidebar.button(
    "🔄 Sync / Refresh Shared Data",
    use_container_width=True,
    help="Fetch live submissions from all active enumerators",
):
    sync_session_from_disk()
    st.sidebar.success("Data synced with shared storage!")
    st.rerun()

with st.sidebar.expander("🔍 View Detailed Phase Status", expanded=False):
    st.write(
        f"{'✅' if p1_status else '🔴'} **Phase 1 (Governance):**"
        f" {'100%' if p1_status else '0%'}"
    )
    st.write(
        f"{'✅' if p2_status else '🔴'} **Phase 2 (Master Survey):**"
        f" {'100%' if p2_status else '0%'}"
    )
    st.write(
        f"{'✅' if p3_status else '🔴'} **Phase 3 (Qualitative):**"
        f" {'100%' if p3_status else '0%'}"
    )
    st.write(
        f"{'✅' if p4_status else '🔴'} **Phase 4 (Expanded PERI):**"
        f" {'100%' if p4_status else '0%'}"
    )
    st.write(
        f"{'✅' if p5_status else '🔴'} **Phase 5 (Analytics):**"
        f" {'100%' if p5_status else '0%'}"
    )
    st.write(
        f"{'✅' if p6_status else '🔴'} **Phase 6 (Action Plan):**"
        f" {'100%' if p6_status else '0%'}"
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Portal Navigation")

# Sidebar Radio linked to session_state menu_selection
selected_idx = (
    NAV_OPTIONS.index(st.session_state["menu_selection"])
    if st.session_state["menu_selection"] in NAV_OPTIONS
    else 0
)

menu = st.sidebar.radio(
    "Select Field Module", NAV_OPTIONS, index=selected_idx, key="menu_radio"
)
st.session_state["menu_selection"] = menu

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout Account", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.caption("👨‍💻 **Lead Developer:** Jan Art Serna, RMT")

# ================= SUCCESS MODAL POPUP DIALOG =================
if st.session_state["show_success_modal"]:
    if hasattr(st, "dialog"):

        @st.dialog("🎉 Submission Successful")
        def render_success_dialog():
            st.balloons()
            st.success(f"**{st.session_state['modal_title']}**")
            st.info(st.session_state["modal_details"])

            col_close, col_next = st.columns(2)
            with col_close:
                if st.button(
                    "👍 OK / Close", id="modalOkBtn", use_container_width=True
                ):
                    st.session_state["show_success_modal"] = False
                    st.rerun()

            with col_next:
                next_pg = st.session_state.get("modal_next_page")
                if next_pg:
                    if st.button(
                        f"➡️ Next: {next_pg.split(':')[0]}",
                        id="nextPageBtn",
                        type="primary",
                        use_container_width=True,
                    ):
                        st.session_state["menu_selection"] = next_pg
                        st.session_state["show_success_modal"] = False
                        st.rerun()

        render_success_dialog()
    else:
        # Fallback UI card for Streamlit versions without native @st.dialog
        st.success(f"🎉 **{st.session_state['modal_title']}**")
        st.info(st.session_state["modal_details"])
        c1, c2 = st.columns(2)
        if c1.button("👍 OK / Close", use_container_width=True):
            st.session_state["show_success_modal"] = False
            st.rerun()
        if st.session_state.get("modal_next_page") and c2.button(
            f"➡️ Next Module", type="primary", use_container_width=True
        ):
            st.session_state["menu_selection"] = st.session_state[
                "modal_next_page"
            ]
            st.session_state["show_success_modal"] = False
            st.rerun()


# MODULE 1: INTERACTIVE SPOT MAP
if menu == "🗺️ Interactive Spot Map":
    st.subheader(
        "📍 Interactive Barangay Health & Environmental Hazard Spot Map"
    )

    if len(st.session_state.hh_records) == 0:
        st.info(
            "No household survey records stored yet. Showing baseline map with"
            " simulated hazard markers."
        )
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
            {
                "HH_ID": "HH-003",
                "Purok": "Purok 2",
                "Lat": 11.1555,
                "Lon": 124.9905,
                "BP": "120/80",
                "Risk": "Normal",
                "Flood_Prone": "Yes",
                "Color": [37, 99, 235, 220],
            },
            {
                "HH_ID": "HH-004",
                "Purok": "Purok 3",
                "Lat": 11.1570,
                "Lon": 124.9930,
                "BP": "150/98",
                "Risk": "Hypertensive Risk",
                "Flood_Prone": "No",
                "Color": [123, 17, 19, 220],
            },
        ])
    else:
        map_df = pd.DataFrame(st.session_state.hh_records)

    col_m, col_f = st.columns([3, 1])

    with col_f:
        st.markdown("**Map Controls & Filters**")
        puroks = list(map_df["Purok"].unique())
        sel_puroks = st.multiselect(
            "Filter Puroks", options=puroks, default=puroks
        )
        flood_filter = st.selectbox(
            "Flood Risk Filter",
            [
                "Show All Households",
                "Flood-Prone Zones Only",
                "Non-Flood Zones Only",
            ],
        )

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
    flood_detected = sum(
        1 for _, r in filt_df.iterrows() if r.get("Flood_Prone") == "Yes"
    )

    st.markdown(
        f"📊 **Detected Summary:** Showing **{total_map_hh}** households | ⚠️"
        f" **{flood_detected}** located in detected **Flood-Prone Zones**."
    )

    with col_m:
        view = pdk.ViewState(
            latitude=filt_df["Lat"].mean() if len(filt_df) > 0 else 11.1560,
            longitude=filt_df["Lon"].mean() if len(filt_df) > 0 else 124.9915,
            zoom=15,
            pitch=30,
        )
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=filt_df,
            get_position=["Lon", "Lat"],
            get_color="Color",
            get_radius=16,
            pickable=True,
        )
        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                tooltip={
                    "text": (
                        "HH: {HH_ID}\nPurok: {Purok}\nBP: {BP}\nHealth Risk:"
                        " {Risk}\nFlood Prone: {Flood_Prone}"
                    )
                },
            )
        )

    # Next Phase Quick Navigation Button
    st.markdown("---")
    if st.button(
        "➡️ Proceed to Phase 1: Full Governance Scorecard",
        type="primary",
        use_container_width=True,
    ):
        st.session_state["menu_selection"] = (
            "📋 Phase 1: Full Governance Scorecard"
        )
        st.rerun()

# MODULE 2: PHASE 1 BHB GOVERNANCE SCORECARD
elif menu == "📋 Phase 1: Full Governance Scorecard":
    st.subheader(
        "Phase 1: Barangay Health Board (BHB) Governance Scorecard (100-Point"
        " Instrument)"
    )

    mode_p1 = st.radio(
        "Select Operation",
        [
            "➕ New Scorecard Entry",
            "📂 Review, Edit & Delete Submitted Scorecards",
        ],
        horizontal=True,
    )

    if mode_p1 == "➕ New Scorecard Entry":
        with st.form("phase1_full_form"):
            t1, t2, t3, t4 = st.tabs([
                "📌 Metadata & Leadership",
                "🏛️ Structure, Meetings & Ordinances",
                "💰 AIP Budgeting & Reporting",
                "🎯 Gaps & Action Planning",
            ])

            with t1:
                c1, c2, c3 = st.columns(3)
                b_name = c1.text_input("Barangay Name")
                city = c2.text_input("City / Municipality")
                prov = c3.text_input("Province")

                c1, c2, c3 = st.columns(3)
                eval_date = c1.date_input("Date of Evaluation")
                pb_head = c2.text_input("Punong Barangay (BHB Chair)")
                health_lead = c3.text_input(
                    "Committee Lead on Health / BHW Lead"
                )

            with t2:
                st.markdown(
                    "**Domain 1: Legal Structure & Reconstitution (Max 10"
                    " Points)**"
                )
                c1, c2 = st.columns(2)
                g1_1 = c1.number_input(
                    "1.1 Updated Executive Order reconstituting BHB with mandate"
                    " terms (0–5 pts)",
                    0,
                    5,
                    0,
                )
                g1_2 = c2.number_input(
                    "1.2 Mandatory multi-sectoral reps active (0–5 pts)", 0, 5, 0
                )

                st.markdown(
                    "**Domain 2: Meeting Regularity & Quorum Compliance (Max 20"
                    " Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g2_1 = c1.number_input(
                    "2.1 Quarterly meetings in past 12 mos (0–12 pts)", 0, 12, 0
                )
                g2_2 = c2.number_input(
                    "2.2 Official quorum met during every meeting (0–4 pts)",
                    0,
                    4,
                    0,
                )
                g2_3 = c3.number_input(
                    "2.3 Signed minutes and attendance records filed (0–4 pts)",
                    0,
                    4,
                    0,
                )

                st.markdown(
                    "**Domain 3: Health Policies & Ordinance Enactment (Max 20"
                    " Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g3_1 = c1.number_input(
                    "3.1 Local health/sanitation ordinances enacted (0–10 pts)",
                    0,
                    10,
                    0,
                )
                g3_2 = c2.number_input(
                    "3.2 Active task force enforcing local health laws (0–5"
                    " pts)",
                    0,
                    5,
                    0,
                )
                g3_3 = c3.number_input(
                    "3.3 Local policies aligned with DOH UHC mandates (0–5"
                    " pts)",
                    0,
                    5,
                    0,
                )

            with t3:
                st.markdown(
                    "**Domain 4: AIP Budget Allocation & Financial Execution"
                    " (Max 20 Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g4_1 = c1.number_input(
                    "4.1 Dedicated health line-items in AIP (0–8 pts)", 0, 8, 0
                )
                g4_2 = c2.number_input(
                    "4.2 Budget for BHW honoraria, emergency response (0–6"
                    " pts)",
                    0,
                    6,
                    0,
                )
                g4_3 = c3.number_input(
                    "4.3 Health budget execution rate >75% last fiscal year"
                    " (0–6 pts)",
                    0,
                    6,
                    0,
                )

                st.markdown(
                    "**Domain 5: Health Reporting & Transparency (Max 15"
                    " Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g5_1 = c1.number_input(
                    "5.1 Quarterly health reports submitted to MHO/RHU (0–8"
                    " pts)",
                    0,
                    8,
                    0,
                )
                g5_2 = c2.number_input(
                    "5.2 Health status presented during Barangay Assemblies"
                    " (0–4 pts)",
                    0,
                    4,
                    0,
                )
                g5_3 = c3.number_input(
                    "5.3 Barangay Health Spot Map maintained at BHS (0–3 pts)",
                    0,
                    3,
                    0,
                )

                st.markdown(
                    "**Domain 6: Working Committees & Mobilization (Max 15"
                    " Points)**"
                )
                c1, c2, c3 = st.columns(3)
                g6_1 = c1.number_input(
                    "6.1 Active technical working committees (0–6 pts)", 0, 6, 0
                )
                g6_2 = c2.number_input(
                    "6.2 Monthly committee reports to BHB (0–6 pts)", 0, 6, 0
                )
                g6_3 = c3.number_input(
                    "6.3 Community health mobilization events completed (0–3"
                    " pts)",
                    0,
                    3,
                    0,
                )

            with t4:
                gap_summary = st.text_area(
                    "Identify primary governance bottlenecks & legislative"
                    " gaps:"
                )
                action_plan = st.text_area(
                    "Recommended technical assistance & corrective intervention"
                    " plan:"
                )

            if st.form_submit_button("Save Phase 1 Full Governance Scorecard"):
                total_score = sum([
                    g1_1,
                    g1_2,
                    g2_1,
                    g2_2,
                    g2_3,
                    g3_1,
                    g3_2,
                    g3_3,
                    g4_1,
                    g4_2,
                    g4_3,
                    g5_1,
                    g5_2,
                    g5_3,
                    g6_1,
                    g6_2,
                    g6_3,
                ])

                if total_score >= 80:
                    rating = "HIGH FUNCTIONING"
                elif total_score >= 50:
                    rating = "MODERATE FUNCTIONING"
                else:
                    rating = "LOW FUNCTIONING / CRITICAL INTERVENTION REQUIRED"

                st.session_state.gov_records.append({
                    "Barangay": b_name,
                    "Score": total_score,
                    "Rating": rating,
                    "Gaps": gap_summary,
                    "ActionPlan": action_plan,
                })
                save_session_to_disk()

                # Trigger Submission Success Modal
                trigger_success_modal(
                    title=f"Governance Scorecard Saved for Barangay {b_name}!",
                    details=(
                        f"Total Score: {total_score}/100 | Governance Status:"
                        f" {rating}"
                    ),
                    next_page="🏠 Phase 2: Master Household Survey",
                )
                st.rerun()

    else:
        st.markdown("### 📂 Submitted Governance Scorecards")
        if len(st.session_state.gov_records) == 0:
            st.info("No governance scorecard records found.")
        else:
            gov_options = [
                f"[{i+1}] {r.get('Barangay', 'Unnamed')} (Score:"
                f" {r.get('Score', 0)})"
                for i, r in enumerate(st.session_state.gov_records)
            ]
            selected_idx = st.selectbox(
                "Select Record to Review / Edit",
                range(len(gov_options)),
                format_func=lambda x: gov_options[x],
            )
            rec = st.session_state.gov_records[selected_idx]

            with st.form("edit_gov_form"):
                st.markdown(f"**Editing Record #{selected_idx+1}**")
                e_brgy = st.text_input(
                    "Barangay Name", value=rec.get("Barangay", "")
                )
                e_score = st.number_input(
                    "Total Score (0–100)", 0, 100, int(rec.get("Score", 0))
                )

                if e_score >= 80:
                    e_rating = "HIGH FUNCTIONING"
                elif e_score >= 50:
                    e_rating = "MODERATE FUNCTIONING"
                else:
                    e_rating = (
                        "LOW FUNCTIONING / CRITICAL INTERVENTION REQUIRED"
                    )

                st.info(f"Calculated Rating: **{e_rating}**")
                e_gaps = st.text_area(
                    "Governance Bottlenecks & Legislative Gaps",
                    value=rec.get("Gaps", ""),
                )
                e_action = st.text_area(
                    "Action & Corrective Plan", value=rec.get("ActionPlan", "")
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Changes"):
                        st.session_state.gov_records[selected_idx] = {
                            "Barangay": e_brgy,
                            "Score": e_score,
                            "Rating": e_rating,
                            "Gaps": e_gaps,
                            "ActionPlan": e_action,
                        }
                        save_session_to_disk()
                        st.success("Record updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Record"):
                        st.session_state.gov_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("Record deleted successfully!")
                        st.rerun()

# MODULE 3: PHASE 2 MASTER HOUSEHOLD SURVEY
elif menu == "🏠 Phase 2: Master Household Survey":
    st.subheader(
        "Phase 2: Master Household Survey Instrument (Tool 2.1 Complete)"
    )

    mode_p2 = st.radio(
        "Select Operation",
        [
            "➕ New Household Survey Entry",
            "📂 Review, Edit & Delete Submitted Household Surveys",
        ],
        horizontal=True,
    )

    if mode_p2 == "➕ New Household Survey Entry":
        with st.form("phase2_complete_form"):
            t_meta, t_vitals, t_socio, t_dec, t_morb, t_mch, t_child, t_yakap = (
                st.tabs([
                    "📋 Metadata & Roster",
                    "🩺 Adult Profiling & Vitals (Adults 1–5)",
                    "🌾 Socio-Econ, Food Insecurity, Housing & WASH",
                    "🤝 Decision-Making Patterns",
                    "🤒 Morbidity & Chronic Care",
                    "👩 Maternal, FP & Mortality",
                    (
                        "👶 Expanded Child Profiling & Immunizations (Children"
                        " 1–4)"
                    ),
                    "🏥 Health-Seeking Behavior & PhilHealth YAKAP",
                ])
            )

            with t_meta:
                st.markdown("**Survey Metadata Control Block**")
                c1, c2, c3, c4 = st.columns(4)
                hh_id = c1.text_input("Household ID", "HH-001")
                brgy = c2.text_input("Barangay Name")
                purok = c3.selectbox(
                    "Purok / Zone", [f"Purok {i}" for i in range(1, 8)]
                )
                date_survey = c4.date_input("Date of Survey")

                c1, c2, c3, c4 = st.columns(4)
                lat = c1.number_input("Latitude", value=11.1560, format="%.4f")
                lon = c2.number_input(
                    "Longitude", value=124.9920, format="%.4f"
                )
                enum_name = c3.selectbox(
                    "Enumerator Name",
                    [
                        "Jan Art Serna, RMT",
                        "Aubrey Maye Arrieta",
                        "Leila Projimo, PTRP",
                    ],
                )
                resp_role = c4.selectbox(
                    "Respondent Role",
                    ["Head", "Spouse", "Adult Member", "Other"],
                )

                c1, c2, c3 = st.columns(3)
                surv_status = c1.selectbox(
                    "Survey Status",
                    ["Completed", "Partially Completed", "Refused"],
                )
                dialect = c2.selectbox(
                    "Primary Dialect Spoken at Home",
                    [
                        "Waray",
                        "Tagalog",
                        "English",
                        "Mixed",
                        "Cebuano / Bisaya",
                        "Ilocano",
                        "Bicolano",
                        "Hiligaynon / Ilonggo",
                        "Pangasinan",
                        "Other Language",
                    ],
                )
                religion = c3.selectbox(
                    "Religion",
                    [
                        "Roman Catholic",
                        "Islam",
                        "Iglesia ni Cristo (INC)",
                        "Evangelical / Protestant",
                        "Seventh-day Adventist",
                        "Aglipayan (IFI)",
                        "Jehovah's Witnesses",
                        "Church of Jesus Christ of Latter-day Saints",
                        "Born Again Christian",
                        "None / Secular",
                        "Other Religion",
                    ],
                )

                st.markdown("---")
                st.markdown("**Module A: Household Demographic Roster**")
                c1, c2, c3, c4 = st.columns(4)
                tot_children = c1.number_input(
                    "No. of Children (<18 yrs)", 0, 20, 0
                )
                tot_dependents = c2.number_input(
                    "No. of Other Dependents", 0, 10, 0
                )
                hh_head_name = c3.text_input("Household Head Full Name")
                head_civil = c4.selectbox(
                    "Head Civil Status",
                    ["Single", "Married", "Widowed", "Separated", "Cohabiting"],
                )

            with t_vitals:
                st.markdown(
                    "**Module B: Adult Profiling & Physical Screening (Adults 1"
                    " to 5)**"
                )
                adults_data = []

                for i in range(1, 6):
                    st.markdown(
                        f"<div class='adult-card'><strong>Adult Member {i}"
                        " Profiling & Physical Vitals</strong></div>",
                        unsafe_allow_html=True,
                    )

                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_name = c1.text_input(
                        f"Adult {i} Name / Initials", key=f"a_name_{i}"
                    )
                    a_age = c2.number_input(
                        f"Adult {i} Age", 18, 120, 30, key=f"a_age_{i}"
                    )
                    a_edu = c3.selectbox(
                        f"Adult {i} Educational Level",
                        [
                            "No Formal Education",
                            "Elementary Unfinished",
                            "Elementary Graduate",
                            "High School Unfinished",
                            "High School Graduate",
                            "Vocational / College Unfinished",
                            "College Graduate",
                            "Post-Graduate",
                        ],
                        key=f"a_edu_{i}",
                    )
                    a_occ = c4.text_input(
                        f"Adult {i} Primary Occupation", key=f"a_occ_{i}"
                    )
                    a_ph_cat = c5.selectbox(
                        f"Adult {i} PhilHealth Category",
                        [
                            "Indigent",
                            "Formal",
                            "Informal",
                            "Dependent",
                            "Unenrolled",
                        ],
                        key=f"a_ph_{i}",
                    )

                    c1, c2, c3, c4, c5 = st.columns(5)
                    a_sys = c1.number_input(
                        f"Adult {i} Systolic BP", 50, 250, 120, key=f"a_sys_{i}"
                    )
                    a_dia = c2.number_input(
                        f"Adult {i} Diastolic BP", 30, 150, 80, key=f"a_dia_{i}"
                    )
                    a_spo2 = c3.number_input(
                        f"Adult {i} SpO2 (%)", 50, 100, 98, key=f"a_spo2_{i}"
                    )
                    a_pulse = c4.number_input(
                        f"Adult {i} Pulse Rate (bpm)",
                        30,
                        200,
                        75,
                        key=f"a_pulse_{i}",
                    )
                    a_temp = c5.number_input(
                        f"Adult {i} Temp (°C)",
                        30.0,
                        42.0,
                        36.5,
                        key=f"a_temp_{i}",
                    )

                    c1, c2 = st.columns(2)
                    a_symptoms = c1.multiselect(
                        f"Adult {i} Current Complaints / Symptoms",
                        [
                            "None",
                            "Cough",
                            "Fever / feeling feverish",
                            "Headache",
                            "Colds / runny or stuffy nose",
                            "Body aches / muscle pain",
                            "Abdominal pain / stomachache",
                            "Diarrhea / loose stools",
                            "Back pain",
                            "Dizziness / feeling lightheaded",
                            "Sore throat",
                            "Others",
                        ],
                        default=["None"],
                        key=f"a_sym_{i}",
                    )

                    a_symptoms_other = ""
                    if "Others" in a_symptoms:
                        a_symptoms_other = c1.text_input(
                            f"Adult {i} Specify Other Complaints",
                            key=f"a_sym_oth_{i}",
                        )

                    a_risk = c2.selectbox(
                        f"Adult {i} Risk Assessment",
                        [
                            "Normal",
                            "Hypertensive Risk",
                            "Hypoxemic (<95%)",
                            "Fever / Febrile",
                            "Tachycardic / Bradycardic",
                        ],
                        key=f"a_risk_{i}",
                    )

                    a_action = st.multiselect(
                        f"🩺 Adult {i} Action Taken",
                        [
                            "Referral to RHU / MHO Physician",
                            "Referral to BHS / Barangay Midwife",
                            "Health Education & Lifestyle Counseling",
                            "Medication Compliance Check & Advisal",
                            "Schedule Re-check / Follow-up Visit",
                            "Immediate Emergency Hospital Referral",
                            "None / Normal Vitals",
                        ],
                        default=["None / Normal Vitals"]
                        if a_risk == "Normal"
                        else [
                            "Referral to RHU / MHO Physician",
                            "Health Education & Lifestyle Counseling",
                        ],
                        key=f"a_action_{i}",
                    )

                    adults_data.append({
                        "ID": f"Adult {i}",
                        "Name": a_name,
                        "Age": a_age,
                        "Edu": a_edu,
                        "Occupation": a_occ,
                        "PhilHealth_Cat": a_ph_cat,
                        "BP": f"{a_sys}/{a_dia}",
                        "Sys": a_sys,
                        "SpO2": a_spo2,
                        "Pulse": a_pulse,
                        "Temp": a_temp,
                        "Complaints": a_symptoms,
                        "Complaints_Other": a_symptoms_other,
                        "Risk": a_risk,
                        "Action_Taken": a_action,
                    })

            with t_socio:
                st.markdown(
                    "**C1. Livelihood, Economic Stability & Domestic Assets**"
                )
                c1, c2, c3 = st.columns(3)
                income_cat = c1.selectbox(
                    "Average Family Income / Month",
                    [
                        "≤ ₱10,000 (Q1)",
                        "₱10,001–₱20,000 (Q2)",
                        "₱20,001–₱35,000 (Q3)",
                        "₱35,001–₱50,000 (Q4)",
                        "> ₱50,000 (Q5)",
                    ],
                )
                livelihood = c2.selectbox(
                    "Primary Livelihood Source",
                    [
                        "Farming (Owned)",
                        "Farming (Tenanted)",
                        "Laborer",
                        "Carpentry",
                        "Fishing",
                        "Peddling",
                        "Gov't Employee",
                        "Small Industry/Sari-Sari",
                        "Other",
                    ],
                )
                food_prod = c3.selectbox(
                    "Engaged in Food Production?", ["Yes", "No"]
                )

                c1, c2 = st.columns(2)
                emergency_5k = c1.selectbox(
                    "Emergency Cushion: Raise ₱5,000 in 24 hrs?", ["Yes", "No"]
                )
                p4ps_status = c2.selectbox(
                    "Active 4Ps Beneficiary?", ["Yes", "No"]
                )

                st.markdown(
                    "**Domestic Assets, Utilities & Transportation Owned**"
                )
                c1, c2, c3 = st.columns(3)
                transpo_owned = c1.multiselect(
                    "Type of Transportation Owned",
                    [
                        "None",
                        "Bicycle",
                        "Motorcycle / Tricycle",
                        "Private Car / Van",
                        "Motorized Banca / Boat",
                    ],
                    default=["None"],
                )
                utilities_avail = c2.multiselect(
                    "Utilities / Services Available",
                    [
                        "Grid Electricity",
                        "Solar Power",
                        "Piped Water Connection",
                        "Cellular Signal",
                        "Internet / Broadband",
                        "Garbage Collection Service",
                    ],
                    default=["Grid Electricity"],
                )
                appliances_owned = c3.multiselect(
                    "Appliances Owned",
                    [
                        "Refrigerator",
                        "Television",
                        "Washing Machine",
                        "Electric Fan",
                        "Gas / Electric Stove",
                        "Air Conditioner",
                    ],
                    default=["Electric Fan"],
                )

                st.markdown("---")
                st.markdown(
                    "**C2. Household Food Insecurity Assessment (Past 30"
                    " Days)**"
                )
                c1, c2, c3 = st.columns(3)
                food_skip = c1.selectbox(
                    "In the past 30 days, did any adult member skip a meal or"
                    " reduce portion size due to lack of money?",
                    ["No", "Yes"],
                )
                food_worry = c2.selectbox(
                    "In the past 30 days, did your household worry about"
                    " running out of food before having money to buy more?",
                    ["No", "Yes"],
                )
                food_fullday = c3.selectbox(
                    "In the past 30 days, did any household member go a full"
                    " day without eating due to lack of food/money?",
                    ["No", "Yes"],
                )

                st.markdown("---")
                st.markdown(
                    "**C3. Housing, Built Environment & Indoor Air Risk**"
                )
                c1, c2, c3 = st.columns(3)
                tenure = c1.selectbox(
                    "Tenurial / Property Status",
                    [
                        "Residential lot with house",
                        "Residential House without Lot",
                        "Renting",
                        "Shared",
                        "Farm Land",
                        "Informal Settler / Caretaker",
                    ],
                )
                house_type = c2.selectbox(
                    "Housing Construction Type",
                    [
                        "Light (Nipa, bamboo, cogon)",
                        "Medium (Wooden floors/walls, G.I. roof)",
                        "Heavy / Permanent (Concrete/hardwood)",
                    ],
                )
                cook_fuel = c3.selectbox(
                    "Indoor Air Risk (Cooking Fuel)",
                    ["LPG", "Charcoal", "Wood", "Kerosene", "Electric"],
                )

                c1, c2 = st.columns(2)
                is_flood_prone = c1.selectbox(
                    "🌊 Is Household Located in a Flood-Prone Zone?",
                    ["No", "Yes"],
                )

                st.markdown("---")
                st.markdown(
                    "**C4. WASH Infrastructure & Environmental Health**"
                )
                c1, c2, c3 = st.columns(3)
                water_source = c1.selectbox(
                    "Drinking Water Source Level",
                    [
                        "Level 1: Protected Well / Spring",
                        "Level 2: Piped network & communal faucet",
                        "Level 3: Individual household tap",
                        "Unsafe: Shallow Well / River / Surface",
                        "Commercial Refill Station",
                    ],
                )
                toilet_type = c2.selectbox(
                    "Sanitation / Toilet Facility Type",
                    [
                        "Pour/Flush to Septic Tank",
                        "Ventilated Improved Pit (VIP) Latrine",
                        "Open Defecation / None",
                    ],
                )
                solid_disposal = c3.selectbox(
                    "Solid Waste Disposal Method",
                    [
                        "Municipal/Barangay Collection",
                        "Composting",
                        "Burying",
                        "Burning (Siga)",
                        "Open Dumping",
                        "River Disposal",
                    ],
                )

            with t_dec:
                st.markdown(
                    "**Module D: Decision-Making Pattern & Community"
                    " Participation**"
                )
                c1, c2 = st.columns(2)
                dec_expenses = c1.multiselect(
                    "Who decides on Family Expenses?",
                    ["Father", "Mother", "Children", "Single Member", "Others"],
                    default=["Father", "Mother"],
                )
                dec_health = c2.multiselect(
                    "Who decides on Health & Medical Care?",
                    ["Father", "Mother", "Children", "Single Member", "Others"],
                    default=["Mother"],
                )

            with t_morb:
                st.markdown(
                    "**Module E1: Acute Infectious Diseases & Illnesses (Past"
                    " 12 Months)**"
                )
                c1, c2, c3 = st.columns(3)
                e_diarrhea = c1.selectbox(
                    "Diarrheal Episodes (>1 in past 12 mos in family)",
                    ["No", "Yes"],
                )
                e_urti = c2.selectbox(
                    "Severe Upper Respiratory Infections / Pneumonia",
                    ["No", "Yes"],
                )
                e_dengue = c3.selectbox(
                    "Suspected or Confirmed Dengue Cases", ["No", "Yes"]
                )

                st.markdown(
                    "**Module E2: Physician-Diagnosed Chronic Conditions &"
                    " Treatment Compliance**"
                )
                c1, c2 = st.columns(2)
                htn_status = c1.selectbox(
                    "Hypertension Status in Household",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Compliant with Meds Daily",
                        "Diagnosed - Irregular Med Compliance",
                        "Diagnosed - Unmedicated / Stopped",
                    ],
                )
                dm_status = c2.selectbox(
                    "Type 2 Diabetes Status in Household",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Compliant with Meds Daily",
                        "Diagnosed - Irregular Med Compliance",
                        "Diagnosed - Unmedicated / Stopped",
                    ],
                )

                c1, c2 = st.columns(2)
                asthma_status = c1.selectbox(
                    "Bronchial Asthma / COPD Status",
                    [
                        "No Member Diagnosed",
                        "Diagnosed - Active Maintenance Inhaler",
                        "Diagnosed - Emergency Meds Only",
                        "Diagnosed - Untreated",
                    ],
                )
                tb_status = c2.selectbox(
                    "Tuberculosis (TB) History & DOTS Status",
                    [
                        "No Member Diagnosed",
                        "Currently Enrolled in TB-DOTS",
                        "Completed TB Treatment",
                        "Defaulted / Interrupted DOTS",
                    ],
                )

                c1, c2, c3 = st.columns(3)
                ckd_status = c1.selectbox(
                    "Chronic Kidney Disease (CKD)",
                    ["No", "Yes - Stage 1-3", "Yes - Dialysis Dependent"],
                )
                cvd_status = c2.selectbox(
                    "Cardiovascular Disease / History of Stroke", ["No", "Yes"]
                )
                cancer_status = c3.selectbox(
                    "Active Malignancy / Cancer", ["No", "Yes"]
                )

            with t_mch:
                st.markdown(
                    "**Module F1: Maternal & Reproductive Health Protocols**"
                )
                c1, c2, c3 = st.columns(3)
                is_preg = c1.selectbox(
                    "Currently Pregnant Member in Household?", ["No", "Yes"]
                )
                anc_visits = c2.number_input(
                    "Antenatal Care (ANC) Visits (Target ≥4)", 0, 15, 0
                )
                anc_1st_tri = c3.selectbox(
                    "First ANC Visit in 1st Trimester?", ["N/A", "Yes", "No"]
                )

                c1, c2, c3 = st.columns(3)
                ifa_tablets = c1.selectbox(
                    "Iron-Folic Acid (IFA) Tablets Received",
                    ["N/A", "<180 Tablets", "≥180 Tablets (Completed)"],
                )
                td_status = c2.selectbox(
                    "Tetanus Diphtheria (Td) Immunization",
                    ["N/A", "Td1", "Td2", "Td3+", "Fully Immunized Mother"],
                )
                postpartum_check = c3.selectbox(
                    "Postpartum Checkup within 72 hours", ["N/A", "Yes", "No"]
                )

                st.markdown("---")
                st.markdown("**Module F2: Delivery & Family Planning**")
                c1, c2 = st.columns(2)
                deliv_personnel_yesno = c1.selectbox(
                    "Delivery handled by trained health personnel?",
                    ["N/A", "Yes", "No"],
                )
                deliv_facility_yesno = c2.selectbox(
                    "Delivery handled in an accredited Health Facility?",
                    ["N/A", "Yes", "No"],
                )

                c1, c2 = st.columns(2)
                fp_access = c1.selectbox(
                    "Couples with access to family planning services?",
                    ["Yes", "No"],
                )
                fp_practice = c2.selectbox(
                    "Couples practicing family planning?", ["Yes", "No"]
                )

                st.markdown("---")
                st.markdown("**Module F3: Mortality Assessment (Jan–Dec)**")
                mortality_yesno = st.selectbox(
                    "With deaths in the family due to preventable diseases"
                    " (Jan-Dec)?",
                    ["No", "Yes"],
                )

            with t_child:
                st.markdown(
                    "**Module F4: Expanded Child Anthropometric & Immunization"
                    " Record Profiling (Up to 4 Children)**"
                )
                children_records = []

                for c_i in range(1, 5):
                    st.markdown(
                        f"<div class='child-card'><strong>👶 Child Member {c_i}"
                        " Profile & Immunization Screening</strong></div>",
                        unsafe_allow_html=True,
                    )

                    c1, c2, c3, c4, c5 = st.columns(5)
                    c_name = c1.text_input(
                        f"Child {c_i} Name / Initials", key=f"c_name_{c_i}"
                    )
                    c_sex = c2.selectbox(
                        f"Child {c_i} Sex",
                        ["Male", "Female"],
                        key=f"c_sex_{c_i}",
                    )
                    c_age_m = c3.number_input(
                        f"Child {c_i} Age (Months)",
                        0,
                        59,
                        12,
                        key=f"c_age_{c_i}",
                    )
                    c_wt_kg = c4.number_input(
                        f"Child {c_i} Weight (kg)",
                        0.0,
                        35.0,
                        8.5,
                        key=f"c_wt_{c_i}",
                    )
                    c_ht_cm = c5.number_input(
                        f"Child {c_i} Height (cm)",
                        0.0,
                        120.0,
                        72.0,
                        key=f"c_ht_{c_i}",
                    )

                    c_nutr = compute_child_nutrition(c_age_m, c_wt_kg, c_ht_cm)
                    st.caption(
                        f"📊 **Nutritional Outcome:** BMI: {c_nutr['BMI']} |"
                        f" Wasting: **{c_nutr['Wasting']}** | Stunting:"
                        f" **{c_nutr['Stunting']}** | Underweight:"
                        f" **{c_nutr['Underweight']}**"
                    )

                    st.markdown(
                        f"**💉 Child {c_i} Immunization Card Check:**"
                    )
                    ic1, ic2, ic3, ic4, ic5, ic6 = st.columns(6)
                    imm_bcg = ic1.checkbox("BCG (Birth)", key=f"bcg_{c_i}")
                    imm_hepb = ic2.checkbox("Hep B (Birth)", key=f"hepb_{c_i}")
                    imm_penta = ic3.checkbox(
                        "Pentavalent 3x", key=f"penta_{c_i}"
                    )
                    imm_opv = ic4.checkbox("OPV/IPV 3x", key=f"opv_{c_i}")
                    imm_pcv = ic5.checkbox("PCV 3x", key=f"pcv_{c_i}")
                    imm_mmr = ic6.checkbox(
                        "MMR 2x (9m & 12m)", key=f"mmr_{c_i}"
                    )

                    is_fic = all([
                        imm_bcg,
                        imm_hepb,
                        imm_penta,
                        imm_opv,
                        imm_pcv,
                        imm_mmr,
                    ])
                    fic_status = (
                        "Fully Immunized Child (FIC)"
                        if is_fic
                        else "Partially Immunized / Incomplete"
                    )
                    st.markdown(f"**Imm. Summary:** Status = `{fic_status}`")

                    is_abnormal_nutr = (
                        "Wasted" in c_nutr["Wasting"]
                        or "Stunted" in c_nutr["Stunting"]
                        or "Underweight" in c_nutr["Underweight"]
                    )

                    c_action = st.multiselect(
                        f"👶 Child {c_i} Action Taken",
                        [
                            "Referral to RHU / Municipal Nutrition Officer",
                            "Referral to BHS / BNS for Supplementary Feeding",
                            (
                                "Health Education & Infant/Young Child Feeding"
                                " (IYCF) Counseling"
                            ),
                            "Schedule Immunization Catch-up at BHS",
                            (
                                "Micro-nutrient Powder (MNP) / Vitamin A"
                                " Supplementation Referral"
                            ),
                            "Deworming Administration / Referral",
                            "None / Normal Growth & Fully Immunized",
                        ],
                        default=["None / Normal Growth & Fully Immunized"]
                        if (not is_abnormal_nutr and is_fic)
                        else [
                            "Referral to RHU / Municipal Nutrition Officer",
                            (
                                "Health Education & Infant/Young Child Feeding"
                                " (IYCF) Counseling"
                            ),
                        ],
                        key=f"c_action_{c_i}",
                    )

                    children_records.append({
                        "Child_Num": f"Child {c_i}",
                        "Name": c_name,
                        "Sex": c_sex,
                        "Age_Months": c_age_m,
                        "Weight": c_wt_kg,
                        "Height": c_ht_cm,
                        "Nutr": c_nutr,
                        "FIC_Status": fic_status,
                        "Action_Taken": c_action,
                    })

            with t_yakap:
                st.markdown(
                    "**Module G: Health-Seeking Behavior & PhilHealth YAKAP"
                    " Access**"
                )

                hsb_initial_actions = st.multiselect(
                    "What immediate steps do you take when you first notice"
                    " symptoms?",
                    [
                        "Rest and wait to see if symptoms improve on their own",
                        (
                            "Use home remedies, herbal teas, or traditional"
                            " methods"
                        ),
                        (
                            "Buy over-the-counter (OTC) medication from a"
                            " store/pharmacy"
                        ),
                        "Search symptoms online or on social media",
                        (
                            "Ask family members, friends, or neighbors for"
                            " advice"
                        ),
                        (
                            "Contact or schedule an appointment with a"
                            " healthcare professional"
                        ),
                    ],
                    default=[
                        "Rest and wait to see if symptoms improve on their own"
                    ],
                )

                hsb_providers_used = st.multiselect(
                    "Which types of healthcare sources do you visit?",
                    [
                        "Public or government hospital",
                        "Private clinic or hospital",
                        "Community health center or rural health unit",
                        "Local pharmacy or chemist",
                        "Traditional, herbal, or faith-based practitioner",
                        "Telehealth app or online consultation service",
                    ],
                    default=["Community health center or rural health unit"],
                )

                hsb_travel_time = st.selectbox(
                    "Estimated travel time to nearest health facility?",
                    [
                        "Less than 15 minutes",
                        "15 to 30 minutes",
                        "30 minutes to 1 hour",
                        "More than 1 hour",
                    ],
                )

                hsb_barriers = st.multiselect(
                    "Barriers causing delay in seeking medical care:",
                    [
                        "High cost of consultation, tests, or medication",
                        "Long waiting times at health facilities",
                        "Distance or lack of affordable transportation",
                        (
                            "Inability to take time off work or caregiving"
                            " responsibilities"
                        ),
                        "Fear of diagnosis, medical tests, or procedures",
                        (
                            "Past negative experiences or poor communication"
                            " with health staff"
                        ),
                        "Lack of health insurance coverage",
                    ],
                )

                hsb_influencers = st.multiselect(
                    "Who influences healthcare decisions?",
                    [
                        "Spouse, partner, or immediate family members",
                        "Parents or older relatives",
                        "Friends, co-workers, or peers",
                        "Community or religious leaders",
                        "Local pharmacist or drug vendor",
                        "Online forums or patient support groups",
                        "I make all decisions independently",
                    ],
                    default=["I make all decisions independently"],
                )

                hsb_criteria = st.multiselect(
                    "Key factors determining choice of healthcare provider:",
                    [
                        "Low cost or acceptance of health insurance",
                        "Proximity to home or work",
                        "Short waiting times for appointments",
                        "Strong reputation or recommendations from loved ones",
                        "Respectful, welcoming, and confidential staff",
                        (
                            "Clean facilities and availability of"
                            " medicines/equipment"
                        ),
                    ],
                )

                st.markdown("---")
                st.markdown("**PhilHealth YAKAP (Konsulta) Coverage**")
                c1, c2 = st.columns(2)
                yakap_registered = c1.selectbox(
                    "Registered under PhilHealth YAKAP (Konsulta)?",
                    ["Yes", "No", "Uncertain"],
                )
                yakap_availed = c2.selectbox(
                    "Has availed FREE First Patient Encounter (FPE) & Meds?",
                    ["Yes", "No", "N/A"],
                )

            if st.form_submit_button("Submit & Save Complete Household Record"):
                primary_sys = adults_data[0]["Sys"] if adults_data else 120
                primary_risk = (
                    adults_data[0]["Risk"] if adults_data else "Normal"
                )

                if is_flood_prone == "Yes" and primary_sys >= 140:
                    marker_color = [192, 38, 211, 230]
                elif primary_sys >= 140:
                    marker_color = [123, 17, 19, 220]
                elif is_flood_prone == "Yes":
                    marker_color = [37, 99, 235, 220]
                else:
                    marker_color = [34, 197, 94, 200]

                st.session_state.hh_records.append({
                    "HH_ID": hh_id,
                    "Barangay": brgy,
                    "Purok": purok,
                    "Date": str(date_survey),
                    "Lat": lat,
                    "Lon": lon,
                    "BP": f"{primary_sys}/80",
                    "Risk": primary_risk,
                    "Flood_Prone": is_flood_prone,
                    "Color": marker_color,
                    "Income": income_cat,
                    "Water": water_source,
                    "Sanitation": toilet_type,
                    "Food_Skip": food_skip,
                    "Children": children_records,
                    "Adults": adults_data,
                    "Dialect": dialect,
                    "Religion": religion,
                    "HSB_Initial_Actions": hsb_initial_actions,
                    "HSB_Providers_Used": hsb_providers_used,
                    "HSB_Travel_Time": hsb_travel_time,
                    "HSB_Barriers": hsb_barriers,
                    "HSB_Influencers": hsb_influencers,
                    "HSB_Criteria": hsb_criteria,
                    "Yakap": yakap_registered,
                })
                save_session_to_disk()

                # Trigger Submission Success Modal
                trigger_success_modal(
                    title=f"Household Record '{hh_id}' Successfully Saved!",
                    details=(
                        f"Barangay: {brgy} | {purok} | Geocoded Position:"
                        f" [{lat:.4f}, {lon:.4f}]"
                    ),
                    next_page="🗣️ Phase 3: Qualitative Field Tools",
                )
                st.rerun()

    else:
        st.markdown("### 📂 Submitted Household Survey Records")
        if len(st.session_state.hh_records) == 0:
            st.info("No household records found.")
        else:
            hh_options = [
                f"[{i+1}] {r.get('HH_ID', 'N/A')} - {r.get('Barangay', 'N/A')}"
                f" ({r.get('Purok', 'N/A')})"
                for i, r in enumerate(st.session_state.hh_records)
            ]
            selected_idx = st.selectbox(
                "Select Household Record to Review / Edit",
                range(len(hh_options)),
                format_func=lambda x: hh_options[x],
            )
            rec = st.session_state.hh_records[selected_idx]

            with st.form("edit_hh_form"):
                st.markdown(
                    f"**Editing Household Record #{selected_idx+1}"
                    f" ({rec.get('HH_ID', '')})**"
                )
                c1, c2, c3 = st.columns(3)
                e_hh_id = c1.text_input(
                    "Household ID", value=rec.get("HH_ID", "")
                )
                e_brgy = c2.text_input(
                    "Barangay Name", value=rec.get("Barangay", "")
                )
                e_purok = c3.text_input("Purok", value=rec.get("Purok", ""))

                c1, c2, c3 = st.columns(3)
                e_lat = c1.number_input(
                    "Latitude",
                    value=float(rec.get("Lat", 11.1560)),
                    format="%.4f",
                )
                e_lon = c2.number_input(
                    "Longitude",
                    value=float(rec.get("Lon", 124.9920)),
                    format="%.4f",
                )
                e_flood = c3.selectbox(
                    "Flood Prone?",
                    ["No", "Yes"],
                    index=0 if rec.get("Flood_Prone") == "No" else 1,
                )

                c1, c2, c3 = st.columns(3)
                e_dialect = c1.text_input(
                    "Dialect", value=rec.get("Dialect", "Waray")
                )
                e_religion = c2.text_input(
                    "Religion", value=rec.get("Religion", "Roman Catholic")
                )
                e_yakap = c3.selectbox(
                    "PhilHealth YAKAP Registered",
                    ["Yes", "No", "Uncertain"],
                    index=["Yes", "No", "Uncertain"].index(
                        rec.get("Yakap", "Yes")
                    )
                    if rec.get("Yakap") in ["Yes", "No", "Uncertain"]
                    else 0,
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Household Edits"):
                        rec["HH_ID"] = e_hh_id
                        rec["Barangay"] = e_brgy
                        rec["Purok"] = e_purok
                        rec["Lat"] = e_lat
                        rec["Lon"] = e_lon
                        rec["Flood_Prone"] = e_flood
                        rec["Dialect"] = e_dialect
                        rec["Religion"] = e_religion
                        rec["Yakap"] = e_yakap

                        st.session_state.hh_records[selected_idx] = rec
                        save_session_to_disk()
                        st.success("Household record updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Household Record"):
                        st.session_state.hh_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("Household record deleted successfully!")
                        st.rerun()

# MODULE 4: PHASE 3 QUALITATIVE FIELD TOOLS
elif menu == "🗣️ Phase 3: Qualitative Field Tools":
    st.subheader(
        "Phase 3: Community Qualitative Data Collection (KII & FGD Tools)"
    )

    mode_p3 = st.radio(
        "Select Operation",
        [
            "➕ New Qualitative Entry",
            "📂 Review, Edit & Delete Submitted Qualitative Records",
        ],
        horizontal=True,
    )

    if mode_p3 == "➕ New Qualitative Entry":
        with st.form("phase3_qual_form"):
            st.markdown(
                "**Key Informant Interview (KII) & Focus Group Discussion"
                " (FGD) Recorder**"
            )
            c1, c2, c3 = st.columns(3)
            tool_type = c1.selectbox(
                "Tool Type",
                [
                    "Key Informant Interview (KII)",
                    "Focus Group Discussion (FGD)",
                ],
            )
            informant_type = c2.selectbox(
                "Informant / Group Category",
                [
                    "Barangay Official",
                    "BHW / BNS",
                    "Barangay Midwife",
                    "Senior Citizens",
                    "4Ps Mothers",
                    "Farmers/Fisherfolk Association",
                ],
            )
            purok_loc = c3.selectbox(
                "Purok / Zone Conducted", [f"Purok {i}" for i in range(1, 8)]
            )

            st.markdown("**Core Qualitative Themes**")
            health_perceptions = st.text_area(
                "1. Perceived Top Health Bottlenecks & Environmental Risks:"
            )
            barriers_care = st.text_area(
                "2. Barriers to Accessing Local RHU/BHS Services:"
            )
            indigenous_practices = st.text_area(
                "3. Local Health Seeking Practices & Beliefs:"
            )

            if st.form_submit_button("Save Qualitative Record"):
                st.session_state.qual_records.append({
                    "Type": tool_type,
                    "Informant": informant_type,
                    "Purok": purok_loc,
                    "Perceptions": health_perceptions,
                    "Barriers": barriers_care,
                    "Beliefs": indigenous_practices,
                })
                save_session_to_disk()

                # Trigger Submission Success Modal
                trigger_success_modal(
                    title=f"{tool_type} Record Saved!",
                    details=(
                        f"Informant: {informant_type} | Location: {purok_loc}"
                    ),
                    next_page="🔍 Phase 4: Expanded PERI Windshield Tool",
                )
                st.rerun()

    else:
        st.markdown("### 📂 Submitted Qualitative Records")
        if len(st.session_state.qual_records) == 0:
            st.info("No qualitative records found.")
        else:
            qual_options = [
                f"[{i+1}] {r.get('Type', 'N/A')} - {r.get('Informant', 'N/A')}"
                f" ({r.get('Purok', 'N/A')})"
                for i, r in enumerate(st.session_state.qual_records)
            ]
            selected_idx = st.selectbox(
                "Select Qualitative Record to Review / Edit",
                range(len(qual_options)),
                format_func=lambda x: qual_options[x],
            )
            rec = st.session_state.qual_records[selected_idx]

            with st.form("edit_qual_form"):
                st.markdown(f"**Editing Qualitative Record #{selected_idx+1}**")
                c1, c2, c3 = st.columns(3)
                e_type = c1.selectbox(
                    "Tool Type",
                    [
                        "Key Informant Interview (KII)",
                        "Focus Group Discussion (FGD)",
                    ],
                    index=0 if "KII" in rec.get("Type", "") else 1,
                )
                e_informant = c2.text_input(
                    "Informant Category", value=rec.get("Informant", "")
                )
                e_purok = c3.text_input(
                    "Purok / Zone", value=rec.get("Purok", "")
                )

                e_perceptions = st.text_area(
                    "1. Perceived Health Bottlenecks & Environmental Risks",
                    value=rec.get("Perceptions", ""),
                )
                e_barriers = st.text_area(
                    "2. Barriers to Accessing Local RHU/BHS Services",
                    value=rec.get("Barriers", ""),
                )
                e_beliefs = st.text_area(
                    "3. Local Health Seeking Practices & Beliefs",
                    value=rec.get("Beliefs", ""),
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Changes"):
                        st.session_state.qual_records[selected_idx] = {
                            "Type": e_type,
                            "Informant": e_informant,
                            "Purok": e_purok,
                            "Perceptions": e_perceptions,
                            "Barriers": e_barriers,
                            "Beliefs": e_beliefs,
                        }
                        save_session_to_disk()
                        st.success("Qualitative record updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Record"):
                        st.session_state.qual_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("Qualitative record deleted successfully!")
                        st.rerun()

# MODULE 5: PHASE 4 EXPANDED PERI WINDSHIELD TOOL
elif menu == "🔍 Phase 4: Expanded PERI Windshield Tool":
    st.subheader(
        "Phase 4: Expanded PERI Environmental Observation Matrices & Scoring"
        " System"
    )

    mode_p4 = st.radio(
        "Select Operation",
        [
            "➕ New PERI Assessment Entry",
            "📂 Review, Edit & Delete Submitted PERI Records",
        ],
        horizontal=True,
    )

    if mode_p4 == "➕ New PERI Assessment Entry":
        with st.form("phase4_expanded_form"):
            st.markdown("**Field Metadata Control**")
            mc1, mc2, mc3 = st.columns(3)
            purok_eval = mc1.selectbox(
                "Target Purok / Zone Evaluated",
                [f"Purok {i}" for i in range(1, 8)],
            )
            eval_date = mc2.date_input("Evaluation Date")
            evaluator_name = mc3.selectbox(
                "Lead Evaluator",
                [
                    "Jan Art Serna, RMT",
                    "Aubrey Maye Arrieta",
                    "Leila Projimo, PTRP",
                ],
            )

            tab_d1, tab_d2, tab_d3, tab_d4, tab_d5, tab_d6, tab_manual = (
                st.tabs([
                    "1. Sanitation & Waste",
                    "2. Food Env & Nutrition",
                    "3. Built Env & Housing",
                    "4. Health Infra Access",
                    "5. DRR & Climate Safety",
                    "6. Vector Control & Hazards",
                    "📖 Scoring Manual & Index",
                ])
            )

            # DOMAIN 1
            with tab_d1:
                st.markdown(
                    "<div class='peri-domain-header'>Domain 1: Sanitation &"
                    " Waste Management Assessment</div>",
                    unsafe_allow_html=True,
                )
                d1_scores = []
                d1_items = [
                    (
                        "1.1 Uncollected Household Solid Waste",
                        "Trash piles, scattered plastic on road shoulders/lots",
                        ["Clean (1)", "Moderate (2)", "Severe Risk (3)"],
                    ),
                    (
                        "1.2 Open Drainage & Canal Integrity",
                        (
                            "Clogged roadside canals, unpaved ditching,"
                            " stagnant greywater"
                        ),
                        ["Adequate (1)", "Substandard (2)", "Hazardous (3)"],
                    ),
                    (
                        "1.3 Stagnant Water & Pooling",
                        "Standing water in road depressions, tires >48 hrs",
                        ["Low Risk (1)", "Moderate (2)", "Severe Risk (3)"],
                    ),
                    (
                        "1.4 Stray & Unattended Animals",
                        (
                            "Free-roaming dogs, cats, or livestock scavenging"
                            " waste"
                        ),
                        ["Controlled (1)", "Moderate (2)", "Uncontrolled (3)"],
                    ),
                    (
                        "1.5 Material Recovery & Garbage Hubs",
                        "Purok MRF condition: overflowing bins, no segregation",
                        [
                            "Clean/Segregated (1)",
                            "Overflowing (2)",
                            "Dilapidated/None (3)",
                        ],
                    ),
                    (
                        "1.6 Open Waste Burning (Siga)",
                        "Visual/smell evidence of plastic or leaf burning",
                        ["Absent (1)", "Occasional (2)", "Frequent/Severe (3)"],
                    ),
                    (
                        "1.7 Odor & Airborne Emissions",
                        "Pungent odor from waste, sewage, or livestock pens",
                        [
                            "Odor-Free (1)",
                            "Moderate Odor (2)",
                            "Severe/Noxious (3)",
                        ],
                    ),
                    (
                        "1.8 Fecal Contamination Exposure",
                        "Visible animal/human feces along walkways/canals",
                        [
                            "None Visible (1)",
                            "Isolated (2)",
                            "Widespread Risk (3)",
                        ],
                    ),
                    (
                        "1.9 Commercial / Market Waste",
                        "Rotting produce, fish water around sari-sari/talipapa",
                        ["Sanitary (1)", "Substandard (2)", "Severe Risk (3)"],
                    ),
                ]

                d1_data = {}
                for code_title, desc, opts in d1_items:
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 3])
                    c1.markdown(f"**{code_title}**\n\n*{desc}*")
                    val = c2.radio(
                        "Rating", opts, key=f"d1_{code_title}", horizontal=True
                    )
                    score = 1 if "(1)" in val else (2 if "(2)" in val else 3)
                    d1_scores.append(score)
                    purok_hs = c3.text_input(
                        "Hotspot Purok", key=f"hs_d1_{code_title}"
                    )
                    lm = c4.text_input(
                        "Landmark / Notes", key=f"lm_d1_{code_title}"
                    )
                    d1_data[code_title] = {
                        "Score": score,
                        "Rating": val,
                        "Hotspot": purok_hs,
                        "Landmark": lm,
                    }
                    st.markdown("---")

            # DOMAIN 2
            with tab_d2:
                st.markdown(
                    "<div class='peri-domain-header'>Domain 2: Food Environment"
                    " & Nutritional Accessibility Assessment</div>",
                    unsafe_allow_html=True,
                )
                d2_scores = []
                d2_items = [
                    (
                        "2.1 Fresh Produce Access (Talipapa)",
                        (
                            "Fresh fruit/veg/meat markets within 300m walking"
                            " distance"
                        ),
                        [
                            "High Access (1)",
                            "Limited Access (2)",
                            "Food Desert (3)",
                        ],
                    ),
                    (
                        "2.2 Sari-Sari Store Food Profile",
                        (
                            "Dominance of salty snacks, sugary drinks, instant"
                            " noodles"
                        ),
                        [
                            "Balanced/Healthy (1)",
                            "Junk-Dominant (2)",
                            "Unhealthy Swamp (3)",
                        ],
                    ),
                    (
                        "2.3 Produce Quality & Freshness",
                        (
                            "Physical condition of produce: fresh vs."
                            " wilted/spoiled"
                        ),
                        [
                            "High Quality (1)",
                            "Mixed Quality (2)",
                            "Poor/Spoiled (3)",
                        ],
                    ),
                    (
                        "2.4 Street Food Vending Hygiene",
                        "Food covers, glass displays, clean water for utensils",
                        [
                            "Sanitary (1)",
                            "Substandard (2)",
                            "Unsanitary/High Risk (3)",
                        ],
                    ),
                    (
                        "2.5 Child-Targeted Marketing",
                        (
                            "Aggressive advertising banners targeting school"
                            " children"
                        ),
                        [
                            "Low Exposure (1)",
                            "Moderate (2)",
                            "High/Aggressive (3)",
                        ],
                    ),
                    (
                        "2.6 Tobacco & Alcohol Visibility",
                        (
                            "Prominent display/sale near youth gathering"
                            " points/schools"
                        ),
                        [
                            "Restricted/Far (1)",
                            "Moderate (2)",
                            "Highly Visible (3)",
                        ],
                    ),
                    (
                        "2.7 Safe Drinking Water Refill Outlets",
                        (
                            "Availability and sanitary state of commercial"
                            " refill stations"
                        ),
                        [
                            "Accessible & Clean (1)",
                            "Scarcely Available (2)",
                            "Unsightly/Risky (3)",
                        ],
                    ),
                ]
                d2_data = {}
                for code_title, desc, opts in d2_items:
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 3])
                    c1.markdown(f"**{code_title}**\n\n*{desc}*")
                    val = c2.radio(
                        "Rating", opts, key=f"d2_{code_title}", horizontal=True
                    )
                    score = 1 if "(1)" in val else (2 if "(2)" in val else 3)
                    d2_scores.append(score)
                    purok_hs = c3.text_input(
                        "Hotspot Purok", key=f"hs_d2_{code_title}"
                    )
                    lm = c4.text_input(
                        "Landmark / Notes", key=f"lm_d2_{code_title}"
                    )
                    d2_data[code_title] = {
                        "Score": score,
                        "Rating": val,
                        "Hotspot": purok_hs,
                        "Landmark": lm,
                    }
                    st.markdown("---")

            # DOMAIN 3
            with tab_d3:
                st.markdown(
                    "<div class='peri-domain-header'>Domain 3: Built"
                    " Environment, Housing Quality & Infrastructure</div>",
                    unsafe_allow_html=True,
                )
                d3_scores = []
                d3_items = [
                    (
                        "3.1 Housing Structural Integrity",
                        (
                            "Concrete/permanent vs. makeshift, tarpaulin, light"
                            " bamboo"
                        ),
                        [
                            "Mostly Concrete (1)",
                            "Mixed Structural (2)",
                            "Predominantly Makeshift (3)",
                        ],
                    ),
                    (
                        "3.2 Pedestrian Walkways & Sidewalks",
                        (
                            "Paved, unblocked sidewalks separated from vehicle"
                            " traffic"
                        ),
                        [
                            "Safe/Paved (1)",
                            "Partial/Blocked (2)",
                            "Absent/Dangerous (3)",
                        ],
                    ),
                    (
                        "3.3 Street Lighting & Night Illumination",
                        (
                            "Functioning streetlights along main roads and dark"
                            " alleys"
                        ),
                        [
                            "Fully Lit (1)",
                            "Dim/Partial (2)",
                            "Dark/Unlit Alleys (3)",
                        ],
                    ),
                    (
                        "3.4 Public Open Spaces & Youth Parks",
                        "Clean public plazas/courts free from glass/hazards",
                        [
                            "Safe & Accessible (1)",
                            "Dilapidated/Unkept (2)",
                            "None/Unsafe (3)",
                        ],
                    ),
                    (
                        "3.5 Universal Physical Accessibility",
                        (
                            "Ramps and unblocked curb cuts for"
                            " PWDs/Seniors/Strollers"
                        ),
                        [
                            "Barrier-Free (1)",
                            "Partially Barrier-Free (2)",
                            "Severe Barriers (3)",
                        ],
                    ),
                    (
                        "3.6 Electrical Wiring & Power Safety",
                        (
                            "Overhead wires: neatly bundled vs. entangled"
                            " octopus lines"
                        ),
                        [
                            "Orderly/Safe (1)",
                            "Cluttered/Low (2)",
                            "Hazardous 'Octopus' (3)",
                        ],
                    ),
                    (
                        "3.7 Road Surface & Speed Management",
                        "Quality of road paving and presence of speed humps",
                        [
                            "Well-Paved/Safe (1)",
                            "Unpaved/Potholes (2)",
                            "Severely Broken/Muddy (3)",
                        ],
                    ),
                ]
                d3_data = {}
                for code_title, desc, opts in d3_items:
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 3])
                    c1.markdown(f"**{code_title}**\n\n*{desc}*")
                    val = c2.radio(
                        "Rating", opts, key=f"d3_{code_title}", horizontal=True
                    )
                    score = 1 if "(1)" in val else (2 if "(2)" in val else 3)
                    d3_scores.append(score)
                    purok_hs = c3.text_input(
                        "Hotspot Zone", key=f"hs_d3_{code_title}"
                    )
                    lm = c4.text_input(
                        "Landmark / Notes", key=f"lm_d3_{code_title}"
                    )
                    d3_data[code_title] = {
                        "Score": score,
                        "Rating": val,
                        "Hotspot": purok_hs,
                        "Landmark": lm,
                    }
                    st.markdown("---")

            # DOMAIN 4
            with tab_d4:
                st.markdown(
                    "<div class='peri-domain-header'>Domain 4: Health"
                    " Infrastructure & Primary Care Accessibility</div>",
                    unsafe_allow_html=True,
                )
                d4_scores = []
                d4_items = [
                    (
                        "4.1 Barangay Health Station (BHS) State",
                        "Physical appearance: clean/painted vs. cracked/leaking",
                        [
                            "Well-Maintained (1)",
                            "Substandard/Wear (2)",
                            "Dilapidated/Blighted (3)",
                        ],
                    ),
                    (
                        "4.2 Facility Visibility & Signage",
                        (
                            "Prominent exterior signage detailing services and"
                            " hours"
                        ),
                        [
                            "Clear & Complete (1)",
                            "Faded/Incomplete (2)",
                            "Missing/No Signage (3)",
                        ],
                    ),
                    (
                        "4.3 Public Transport Proximity (<100m)",
                        (
                            "Distance from BHS entrance to nearest public"
                            " transport stop"
                        ),
                        [
                            "High Access (<50m) (1)",
                            "Moderate (50-150m) (2)",
                            "Isolated (>150m) (3)",
                        ],
                    ),
                    (
                        "4.4 Pharmacy / Essential Med Access",
                        "Proximity of BHS dispensing room or private Botika",
                        [
                            "Co-located/Nearby (1)",
                            "Limited/Distant (2)",
                            "Absent in Zone (3)",
                        ],
                    ),
                    (
                        "4.5 Emergency Vehicle Access Corridors",
                        "Width of access roads for ambulance/fire truck entry",
                        [
                            "Unobstructed Wide (1)",
                            "Narrow/Tight Turn (2)",
                            "Blocked/Inaccessible (3)",
                        ],
                    ),
                    (
                        "4.6 Health Promotion Advisory Display",
                        (
                            "Outdoor bulletin boards displaying updated health"
                            " warnings"
                        ),
                        [
                            "Updated & Visible (1)",
                            "Outdated Posters (2)",
                            "Blank/Damaged (3)",
                        ],
                    ),
                    (
                        "4.7 BHS Sanitation & Basic Utilities",
                        (
                            "Functioning sink, clean patient toilet, running"
                            " water & power"
                        ),
                        [
                            "Fully Functional (1)",
                            "Partial/Defective (2)",
                            "Non-Functional/None (3)",
                        ],
                    ),
                ]
                d4_data = {}
                for code_title, desc, opts in d4_items:
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 3])
                    c1.markdown(f"**{code_title}**\n\n*{desc}*")
                    val = c2.radio(
                        "Rating", opts, key=f"d4_{code_title}", horizontal=True
                    )
                    score = 1 if "(1)" in val else (2 if "(2)" in val else 3)
                    d4_scores.append(score)
                    purok_hs = c3.text_input(
                        "Hotspot Location", key=f"hs_d4_{code_title}"
                    )
                    lm = c4.text_input(
                        "Landmark / Notes", key=f"lm_d4_{code_title}"
                    )
                    d4_data[code_title] = {
                        "Score": score,
                        "Rating": val,
                        "Hotspot": purok_hs,
                        "Landmark": lm,
                    }
                    st.markdown("---")

            # DOMAIN 5
            with tab_d5:
                st.markdown(
                    "<div class='peri-domain-header'>Domain 5: Disaster Risk"
                    " Reduction & Climate Environmental Safety</div>",
                    unsafe_allow_html=True,
                )
                d5_scores = []
                d5_items = [
                    (
                        "5.1 High-Hazard Proximity (Geohazards)",
                        "Homes along steep slopes, active riverbanks, sea walls",
                        [
                            "Low Exposure (1)",
                            "Moderate Buffer (2)",
                            "High Hazard Zone (3)",
                        ],
                    ),
                    (
                        "5.2 Flood Vulnerability & High-Water Marks",
                        (
                            "Visible watermark lines, silt, or low-lying basin"
                            " topography"
                        ),
                        [
                            "Flood-Free/High (1)",
                            "Ankle-Deep/Slow (2)",
                            "Rapid Deep Inundation (3)",
                        ],
                    ),
                    (
                        "5.3 Evacuation Route Signage & Clarity",
                        "Reflectorized directional signs along major footpaths",
                        [
                            "Clearly Marked (1)",
                            "Faded/Sparse (2)",
                            "No Signage Found (3)",
                        ],
                    ),
                    (
                        "5.4 Evacuation Center Readiness",
                        (
                            "Structural condition/roof integrity of covered"
                            " court/school"
                        ),
                        [
                            "Ready & Accessible (1)",
                            "Minor Maintenance (2)",
                            "Unsafe/Restricted (3)",
                        ],
                    ),
                    (
                        "5.5 Major Drainage Outfalls & Waterways",
                        (
                            "River outlets/creeks: free-flowing vs. choked with"
                            " trash/silt"
                        ),
                        [
                            "Clear Outflow (1)",
                            "Moderately Clogged (2)",
                            "Severely Choked (3)",
                        ],
                    ),
                    (
                        "5.6 Urban Fire Hazard & Density",
                        (
                            "Extremely dense wooden housing clusters separated"
                            " by <1.5m alleys"
                        ),
                        [
                            "Low Fire Risk (1)",
                            "Moderate Density (2)",
                            "High Fire Trap (3)",
                        ],
                    ),
                    (
                        "5.7 Slope Protection & Retaining Walls",
                        (
                            "Concrete retaining walls/gabions along steep"
                            " roadside cuts"
                        ),
                        [
                            "Intact Protection (1)",
                            "Cracking/Eroded (2)",
                            "Unprotected Slope (3)",
                        ],
                    ),
                ]
                d5_data = {}
                for code_title, desc, opts in d5_items:
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 3])
                    c1.markdown(f"**{code_title}**\n\n*{desc}*")
                    val = c2.radio(
                        "Rating", opts, key=f"d5_{code_title}", horizontal=True
                    )
                    score = 1 if "(1)" in val else (2 if "(2)" in val else 3)
                    d5_scores.append(score)
                    purok_hs = c3.text_input(
                        "Hazard Zone Purok", key=f"hs_d5_{code_title}"
                    )
                    lm = c4.text_input(
                        "Landmark / Notes", key=f"lm_d5_{code_title}"
                    )
                    d5_data[code_title] = {
                        "Score": score,
                        "Rating": val,
                        "Hotspot": purok_hs,
                        "Landmark": lm,
                    }
                    st.markdown("---")

            # DOMAIN 6
            with tab_d6:
                st.markdown(
                    "<div class='peri-domain-header'>Domain 6: Vector Control"
                    " & Environmental Exposure Hazards</div>",
                    unsafe_allow_html=True,
                )
                d6_scores = []
                d6_items = [
                    (
                        "6.1 Dengue Vector Breeding Sites",
                        (
                            "Density of tires, uncovered rain barrels, open tin"
                            " cans"
                        ),
                        [
                            "Rare/Clean (1)",
                            "Moderate Sites (2)",
                            "Prolific Breeding (3)",
                        ],
                    ),
                    (
                        "6.2 Rodent & Fly Infestation Signs",
                        (
                            "Rat burrows along canal banks, swarms of flies"
                            " near waste"
                        ),
                        [
                            "Low/Unnoticed (1)",
                            "Moderate Signs (2)",
                            "Severe Infestation (3)",
                        ],
                    ),
                    (
                        "6.3 Commercial / Workshop Pollution",
                        (
                            "Proximity of residential homes to auto-repair/waste"
                            " oil dumping"
                        ),
                        [
                            "Buffer Compliant (1)",
                            "Moderate Nuisance (2)",
                            "Severe Toxic Exposure (3)",
                        ],
                    ),
                    (
                        "6.4 Dust, Exhaust & Air Quality",
                        (
                            "Heavy airborne dust from dirt roads or intense"
                            " diesel exhaust"
                        ),
                        [
                            "Clean Air (1)",
                            "Moderate Dust/Fumes (2)",
                            "High Particulate Dust (3)",
                        ],
                    ),
                ]
                d6_data = {}
                for code_title, desc, opts in d6_items:
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 3])
                    c1.markdown(f"**{code_title}**\n\n*{desc}*")
                    val = c2.radio(
                        "Rating", opts, key=f"d6_{code_title}", horizontal=True
                    )
                    score = 1 if "(1)" in val else (2 if "(2)" in val else 3)
                    d6_scores.append(score)
                    purok_hs = c3.text_input(
                        "Hotspot Purok", key=f"hs_d6_{code_title}"
                    )
                    lm = c4.text_input(
                        "Landmark / Notes", key=f"lm_d6_{code_title}"
                    )
                    d6_data[code_title] = {
                        "Score": score,
                        "Rating": val,
                        "Hotspot": purok_hs,
                        "Landmark": lm,
                    }
                    st.markdown("---")

            # MANUAL & INDEX TAB
            with tab_manual:
                st.markdown(
                    "### 📖 Comprehensive Result Interpretation & Field"
                    " Scoring Manual"
                )
                st.markdown("""
                **3.1 Quantitative Scoring & Index Calculation Methodology**
                - **Score 1.0 (Optimal / Low Risk):** Parameter meets sanitary and structural standards. Minimal or no hazard observed.
                - **Score 2.0 (Moderate Risk / Substandard):** Parameter displays noticeble deficiencies, wear, or moderate sanitation gaps.
                - **Score 3.0 (Severe Hazard / Critical):** Parameter presents acute, severe environmental hazards or immediate health risks.
                
                | PERI Score Range | Risk Tier Category | Operational Response Required |
                | :--- | :--- | :--- |
                | **1.00 – 1.49** | **CATEGORY A: Low Risk (Green)** | Routine quarterly monitoring; maintain existing services. |
                | **1.50 – 2.29** | **CATEGORY B: Moderate Concern (Amber)** | Targeted 30-day intervention; schedule clean-up drives & health education. |
                | **2.30 – 3.00** | **CATEGORY C: Critical Hazard (Red)** | Immediate Emergency Action (<7 days); escalate to Mayor, LGU Health Officer & DRRMO. |
                """)

            # Calculate Real-Time PERI
            ds1 = sum(d1_scores) / len(d1_scores)
            ds2 = sum(d2_scores) / len(d2_scores)
            ds3 = sum(d3_scores) / len(d3_scores)
            ds4 = sum(d4_scores) / len(d4_scores)
            ds5 = sum(d5_scores) / len(d5_scores)
            ds6 = sum(d6_scores) / len(d6_scores)

            peri_index = (ds1 + ds2 + ds3 + ds4 + ds5 + ds6) / 6.0

            if peri_index >= 2.30:
                tier_cat = "CATEGORY C: Critical Hazard (Red)"
                tier_color = "red"
            elif peri_index >= 1.50:
                tier_cat = "CATEGORY B: Moderate Concern (Amber)"
                tier_color = "orange"
            else:
                tier_cat = "CATEGORY A: Low Risk (Green)"
                tier_color = "green"

            st.markdown("---")
            st.markdown(
                "### 📊 Calculated PERI Composite Score for"
                f" {purok_eval}: **{peri_index:.2f} / 3.00**"
            )
            st.markdown(f"**Assigned Tier:** :{tier_color}[**{tier_cat}**]")

            if st.form_submit_button(
                "Save Complete Phase 4 Expanded PERI Record"
            ):
                st.session_state.windshield_records.append({
                    "Purok": purok_eval,
                    "Date": str(eval_date),
                    "Evaluator": evaluator_name,
                    "DS1_Sanitation": ds1,
                    "DS2_Food": ds2,
                    "DS3_BuiltEnv": ds3,
                    "DS4_HealthInfra": ds4,
                    "DS5_DRR": ds5,
                    "DS6_Vector": ds6,
                    "PERI_Index": peri_index,
                    "Tier_Category": tier_cat,
                })
                save_session_to_disk()

                # Trigger Submission Success Modal
                trigger_success_modal(
                    title=(
                        f"PERI Windshield Assessment for {purok_eval} Saved!"
                    ),
                    details=(
                        f"PERI Index: {peri_index:.2f}/3.00 | Assigned Tier:"
                        f" {tier_cat}"
                    ),
                    next_page="📈 Phase 5: Spatial & Statistical Analytics",
                )
                st.rerun()

    else:
        st.markdown("### 📂 Submitted PERI Windshield Assessment Records")
        if len(st.session_state.windshield_records) == 0:
            st.info("No PERI records found.")
        else:
            peri_options = [
                f"[{i+1}] {r.get('Purok', 'N/A')} - PERI:"
                f" {r.get('PERI_Index', 0.0):.2f} ({r.get('Date', 'N/A')})"
                for i, r in enumerate(st.session_state.windshield_records)
            ]
            selected_idx = st.selectbox(
                "Select PERI Record to Review / Edit",
                range(len(peri_options)),
                format_func=lambda x: peri_options[x],
            )
            rec = st.session_state.windshield_records[selected_idx]

            with st.form("edit_peri_form"):
                st.markdown(f"**Editing PERI Record #{selected_idx+1}**")
                c1, c2, c3 = st.columns(3)
                e_purok = c1.text_input(
                    "Target Purok", value=rec.get("Purok", "")
                )
                e_evaluator = c2.text_input(
                    "Lead Evaluator", value=rec.get("Evaluator", "")
                )
                e_date = c3.text_input(
                    "Evaluation Date", value=rec.get("Date", "")
                )

                c1, c2, c3 = st.columns(3)
                e_ds1 = c1.number_input(
                    "DS1 Sanitation (1.0 - 3.0)",
                    1.0,
                    3.0,
                    float(rec.get("DS1_Sanitation", 1.0)),
                )
                e_ds2 = c2.number_input(
                    "DS2 Food (1.0 - 3.0)",
                    1.0,
                    3.0,
                    float(rec.get("DS2_Food", 1.0)),
                )
                e_ds3 = c3.number_input(
                    "DS3 Built Env (1.0 - 3.0)",
                    1.0,
                    3.0,
                    float(rec.get("DS3_BuiltEnv", 1.0)),
                )

                c1, c2, c3 = st.columns(3)
                e_ds4 = c1.number_input(
                    "DS4 Health Infra (1.0 - 3.0)",
                    1.0,
                    3.0,
                    float(rec.get("DS4_HealthInfra", 1.0)),
                )
                e_ds5 = c2.number_input(
                    "DS5 DRR Safety (1.0 - 3.0)",
                    1.0,
                    3.0,
                    float(rec.get("DS5_DRR", 1.0)),
                )
                e_ds6 = c3.number_input(
                    "DS6 Vector Hazard (1.0 - 3.0)",
                    1.0,
                    3.0,
                    float(rec.get("DS6_Vector", 1.0)),
                )

                e_peri = (e_ds1 + e_ds2 + e_ds3 + e_ds4 + e_ds5 + e_ds6) / 6.0
                if e_peri >= 2.30:
                    e_tier = "CATEGORY C: Critical Hazard (Red)"
                elif e_peri >= 1.50:
                    e_tier = "CATEGORY B: Moderate Concern (Amber)"
                else:
                    e_tier = "CATEGORY A: Low Risk (Green)"

                st.info(
                    f"Recalculated PERI Index: **{e_peri:.2f}** | Tier:"
                    f" **{e_tier}**"
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Changes"):
                        st.session_state.windshield_records[selected_idx] = {
                            "Purok": e_purok,
                            "Date": e_date,
                            "Evaluator": e_evaluator,
                            "DS1_Sanitation": e_ds1,
                            "DS2_Food": e_ds2,
                            "DS3_BuiltEnv": e_ds3,
                            "DS4_HealthInfra": e_ds4,
                            "DS5_DRR": e_ds5,
                            "DS6_Vector": e_ds6,
                            "PERI_Index": e_peri,
                            "Tier_Category": e_tier,
                        }
                        save_session_to_disk()
                        st.success("PERI record updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Record"):
                        st.session_state.windshield_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("PERI record deleted successfully!")
                        st.rerun()

# MODULE 6: PHASE 5 SPATIAL & STATISTICAL ANALYTICS
elif menu == "📈 Phase 5: Spatial & Statistical Analytics":
    st.subheader("Phase 5: Spatial & Statistical Cross-Tabulation Analytics")

    if len(st.session_state.hh_records) == 0:
        st.warning(
            "No survey data stored yet. Please record data under Phase 2 to view"
            " spatial analytics."
        )
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
        crosstab_df = pd.crosstab(
            df_analytics["Income"], df_analytics["Food_Skip"]
        )
        st.dataframe(crosstab_df, use_container_width=True)

    # Next Phase Quick Navigation Button
    st.markdown("---")
    if st.button(
        "➡️ Proceed to Phase 6: Community Diagnosis & Action Plan",
        type="primary",
        use_container_width=True,
    ):
        st.session_state["menu_selection"] = (
            "📋 Phase 6: Community Diagnosis & Action Plan"
        )
        st.rerun()

# MODULE 7: PHASE 6 COMMUNITY DIAGNOSIS & ACTION PLAN
elif menu == "📋 Phase 6: Community Diagnosis & Action Plan":
    st.subheader("Phase 6: Community Health Diagnosis & Prioritized Action Plan")

    mode_p6 = st.radio(
        "Select Operation",
        [
            "➕ New Action Plan Entry",
            "📂 Review, Edit & Delete Submitted Action Plans",
        ],
        horizontal=True,
    )

    if mode_p6 == "➕ New Action Plan Entry":
        with st.form("phase6_diag_form"):
            st.markdown(
                "**Health Issue Prioritization (Hanlon Method / Standard"
                " Matrix)**"
            )
            c1, c2, c3 = st.columns(3)
            problem_title = c1.text_input("Identified Health Problem / Hazard")
            magnitude = c2.slider("Magnitude of Problem (1–10)", 1, 10, 5)
            severity = c3.slider("Severity / Urgency (1–10)", 1, 10, 5)

            st.markdown("**Comprehensive Action Plan Formulation**")
            c1, c2 = st.columns(2)
            objectives = c1.text_area("Specific, Measurable Objectives (SMART):")
            interventions = c2.text_area(
                "Recommended Community Health Interventions:"
            )

            c1, c2, c3 = st.columns(3)
            responsible_party = c1.text_input("Responsible Lead / Sector")
            timeline = c2.text_input("Target Implementation Timeline")
            budget_req = c3.text_input("Estimated Budget Allocation")

            if st.form_submit_button("Save Action Plan & Diagnosis"):
                st.session_state.diag_records.append({
                    "Problem": problem_title,
                    "Magnitude": magnitude,
                    "Severity": severity,
                    "Score": magnitude * severity,
                    "Objectives": objectives,
                    "Interventions": interventions,
                    "Lead": responsible_party,
                    "Timeline": timeline,
                    "Budget": budget_req,
                })
                save_session_to_disk()

                # Trigger Submission Success Modal
                trigger_success_modal(
                    title=(
                        f"Action Plan for '{problem_title}' Saved"
                        " Successfully!"
                    ),
                    details=(
                        f"Priority Score: {magnitude * severity}/100 | Lead:"
                        f" {responsible_party}"
                    ),
                    next_page="🩺 Diagnostic Summary & Analytics",
                )
                st.rerun()

    else:
        st.markdown("### 📂 Submitted Action Plans & Diagnoses")
        if len(st.session_state.diag_records) == 0:
            st.info("No action plans found.")
        else:
            diag_options = [
                f"[{i+1}] {r.get('Problem', 'N/A')} (Score:"
                f" {r.get('Score', 0)})"
                for i, r in enumerate(st.session_state.diag_records)
            ]
            selected_idx = st.selectbox(
                "Select Action Plan to Review / Edit",
                range(len(diag_options)),
                format_func=lambda x: diag_options[x],
            )
            rec = st.session_state.diag_records[selected_idx]

            with st.form("edit_diag_form"):
                st.markdown(f"**Editing Action Plan #{selected_idx+1}**")
                c1, c2, c3 = st.columns(3)
                e_prob = c1.text_input(
                    "Identified Health Problem", value=rec.get("Problem", "")
                )
                e_mag = c2.slider(
                    "Magnitude (1–10)", 1, 10, int(rec.get("Magnitude", 5))
                )
                e_sev = c3.slider(
                    "Severity (1–10)", 1, 10, int(rec.get("Severity", 5))
                )

                c1, c2 = st.columns(2)
                e_obj = c1.text_area(
                    "Objectives", value=rec.get("Objectives", "")
                )
                e_interv = c2.text_area(
                    "Interventions", value=rec.get("Interventions", "")
                )

                c1, c2, c3 = st.columns(3)
                e_lead = c1.text_input(
                    "Responsible Lead", value=rec.get("Lead", "")
                )
                e_time = c2.text_input(
                    "Timeline", value=rec.get("Timeline", "")
                )
                e_bud = c3.text_input(
                    "Budget Allocation", value=rec.get("Budget", "")
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("💾 Save Changes"):
                        st.session_state.diag_records[selected_idx] = {
                            "Problem": e_prob,
                            "Magnitude": e_mag,
                            "Severity": e_sev,
                            "Score": e_mag * e_sev,
                            "Objectives": e_obj,
                            "Interventions": e_interv,
                            "Lead": e_lead,
                            "Timeline": e_time,
                            "Budget": e_bud,
                        }
                        save_session_to_disk()
                        st.success("Action plan updated successfully!")
                        st.rerun()
                with col_btn2:
                    if st.form_submit_button("🗑️ Delete Record"):
                        st.session_state.diag_records.pop(selected_idx)
                        save_session_to_disk()
                        st.success("Action plan deleted successfully!")
                        st.rerun()

# MODULE 8: DIAGNOSTIC SUMMARY & ANALYTICS
elif menu == "🩺 Diagnostic Summary & Analytics":
    st.subheader("🩺 Diagnostic Summary Dashboard & Field Metrics")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Surveyed HHs", len(st.session_state.hh_records))
    c2.metric("BHB Scorecard", "Recorded" if p1_status else "Pending")
    c3.metric("Qualitative Logs", len(st.session_state.qual_records))
    c4.metric(
        "PERI Windshield Logs", len(st.session_state.windshield_records)
    )

    st.markdown("---")
    st.markdown("### 📌 Active Action Plans Overview")
    if len(st.session_state.diag_records) > 0:
        st.dataframe(
            pd.DataFrame(st.session_state.diag_records),
            use_container_width=True,
        )
    else:
        st.info(
            "No action plans created yet. Navigate to Phase 6 to generate"
            " community diagnoses."
        )

# MODULE 9: DATA MANAGEMENT & EXPORT
elif menu == "💾 Data Management & Export":
    st.subheader("💾 Field Data Management, Backup & CSV Export")

    st.markdown(
        "Export accumulated field survey records into standardized CSV format"
        " for statistical analysis."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**Master Household Data**")
        if len(st.session_state.hh_records) > 0:
            df_hh = pd.DataFrame(st.session_state.hh_records)
            csv_hh = df_hh.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Household CSV",
                csv_hh,
                "household_records.csv",
                "text/csv",
            )
        else:
            st.caption("No household records available.")

    with c2:
        st.markdown("**BHB Governance Scorecards**")
        if len(st.session_state.gov_records) > 0:
            df_gov = pd.DataFrame(st.session_state.gov_records)
            csv_gov = df_gov.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Governance CSV",
                csv_gov,
                "governance_records.csv",
                "text/csv",
            )
        else:
            st.caption("No governance records available.")

    with c3:
        st.markdown("**Expanded PERI Windshield**")
        if len(st.session_state.windshield_records) > 0:
            df_peri = pd.DataFrame(st.session_state.windshield_records)
            csv_peri = df_peri.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download PERI CSV",
                csv_peri,
                "peri_windshield_records.csv",
                "text/csv",
            )
        else:
            st.caption("No PERI records available.")

    with c4:
        st.markdown("**Action Plans**")
        if len(st.session_state.diag_records) > 0:
            df_diag = pd.DataFrame(st.session_state.diag_records)
            csv_diag = df_diag.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Action Plans CSV",
                csv_diag,
                "action_plans.csv",
                "text/csv",
            )
        else:
            st.caption("No action plans available.")
