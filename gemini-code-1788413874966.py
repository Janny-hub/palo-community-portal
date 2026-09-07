import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="TEKI Portal",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Maroon & Yellow Theme + Form Width Control
st.markdown("""
    <style>
    /* Dark Maroon Background */
    .stApp {
        background-color: #120608;
        color: #E6E6E6;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1A090C;
        border-right: 1px solid #4A1118;
    }
    
    /* Yellow/Gold Accents for Headers and Radio Buttons */
    h1, h2, h3, .stRadio label {
        color: #FFD700 !important;
    }
    
    /* Header Box Container */
    .header-banner {
        background: linear-gradient(135deg, #3B0A11 0%, #200407 100%);
        border: 1.5px solid #7B1113;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        padding: 24px;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    
    /* Restrict Login Container to ~4 inches (approx 384px) */
    .login-container {
        max-width: 384px;
        background-color: #1A090C;
        padding: 24px;
        border-radius: 10px;
        border: 1px solid #7B1113;
        margin-top: 15px;
    }
    
    /* Input Fields Styling */
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background-color: #2B0E13 !important;
        color: #FFFFFF !important;
        border: 1px solid #7B1113 !important;
        border-radius: 6px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 5px rgba(255, 215, 0, 0.5) !important;
    }
    
    /* Primary Buttons (Yellow Accent) */
    .stButton > button {
        background-color: #7B1113 !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #FFD700 !important;
        color: #7B1113 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONTENT -----------------
with st.sidebar:
    st.markdown("### 🎓 Capstone Project Proposed by:")
    st.markdown("""
    * **Lesterel C. Kidit, RM, RN, MD**
    * **Nova Nizza B. Dacayanan, RM, RN, MD**
    * **James O. Peconcillo, RM, RN, MD**
    
    *University of the Philippines Manila-SHS*
    """)
    
    st.divider()
    
    st.markdown("### Navigation Menu")
    st.caption("Select Program Module:")
    
    selected_module = st.radio(
        label="Select Program Module",
        options=[
            "Executive Dashboard",
            "PhilPEN Assessment Form",
            "PhilPEN Database and Analytics",
            "Nutritional Status (0-59 mos)",
            "Expanded Program on Immunization",
            "Maternal Care",
            "Schistosomiasis",
            "NTP",
            "Mental Health Program"
        ],
        label_visibility="collapsed"
    )

# ----------------- MAIN HEADER BANNER -----------------
st.markdown("""
    <div class="header-banner">
        <h1 style="margin:0; font-size: 26px; font-weight: 700; color: #FFFFFF !important;">
            TEKI: Technology-Enabled Knowledge and Information System
        </h1>
        <p style="margin: 6px 0 12px 0; font-style: italic; color: #FFD700; font-size: 15px;">
            An Integrated Digital Platform for Barangay Health Program Recording and Reporting
        </p>
        <p style="margin: 0; font-size: 14px; color: #E0E0E0;">
            👨‍💻 <strong>Lead Developer:</strong> <span style="color: #FFD700; font-weight: 600;">Jan Art A. Serna, RMT</span>
        </p>
    </div>
""", unsafe_allow_html=True)

# ----------------- MAIN CONTENT AREA -----------------

# Session state simulation for login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("TEKI Portal Login")
    
    # Render Login Form inside a 4-inch capped container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    username = st.selectbox(
        "Select Account / Barangay (Username)",
        options=["paloadmin", "barangay_1", "barangay_2"]
    )
    password = st.text_input("Access Password", type="password")
    
    if st.button("Login"):
        if password:  # Placeholder logic
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Please enter a password.")
            
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Selected Form Module View (e.g., PhilPEN Form)
    st.subheader(f"{selected_module} — Municipality of Palo (All Barangays Overview)")
    
    st.markdown("#### 1. General & Assessor Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Pangalan ng BHW / Assessor*")
    with col2:
        st.date_input("Date of Assessment*")
        
    col3, col4, col5 = st.columns(3)
    with col3:
        st.text_input("Apilido (Last Name)*")
    with col4:
        st.text_input("Pangalan (Given Name)*")
    with col5:
        st.text_input("Gitnang Pangalan (Middle Name)")
