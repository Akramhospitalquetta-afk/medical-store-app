import streamlit as st
import pandas as pd
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# --- 1. PAGE CONFIGURATION & LIGHT THEME STYLING ---
st.set_page_config(page_title="Healthcard Management System", layout="wide")

# Foolproof CSS for solid borders and zero spacing conflicts
st.markdown("""
<style>
/* Main Background Light Gray */
.stApp {
    background-color: #F1F5F9;
    color: #0F172A;
}

/* Tabs Layout Styling */
button[data-baseweb="tab"] {
    font-size: 18px !important;
    font-weight: bold !important;
    color: #475569 !important;
    padding: 10px 20px !important;
}

/* Active Tab Highlight (Blue) */
button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background-color: #2563EB !important;
    border-radius: 4px 4px 0px 0px;
}

/* Inner Card Containers (Pure White) */
.card-container {
    background-color: #FFFFFF;
    padding: 25px;
    border-radius: 8px;
    border: 2px solid #CBD5E1 !important; /* Thick main box container border */
    margin-top: 15px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

/* Top Headers Inside Card (Dark Blue) */
.form-header {
    background-color: #1E3A8A;
    color: white;
    text-align: center;
    padding: 12px;
    font-weight: bold;
    font-size: 22px;
    border-radius: 4px;
    margin-bottom: 25px;
}

/* Input Labels */
label, .stWidgetLabel p {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #1E293B !important;
}

/* --- THE ULTIMATE SOLID BOX BORDER & MOBILE LIGHT OVERWRITE FIX --- */
.stTextInput > div > div, 
.stDateInput > div > div, 
.stSelectbox > div > div, 
.stNumberInput > div > div {
    border: 2px solid #475569 !important;
    border-radius: 6px !important;
    background-color: #FFFFFF !important;
}

/* Text field inner wrapper styling for inputs */
div[data-baseweb="input"], div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
}

/* Mobile browser dark mode override text protection */
.stTextInput input, 
.stDateInput input, 
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] span {
    color: #0F172A !important;
    font-size: 16px !important;
    font-weight: bold !important;
    background-color: transparent !important;
    -webkit-text-fill-color: #0F172A !important; /* Force text color on iPhone/Safari */
}

/* --- UNIVERSAL FOOLPROOF BUTTON FIX --- */
div.stButton > button, 
div.stDownloadButton > button {
    background-color: #2563EB !important; /* Solid Royal Blue */
    color: #FFFFFF !important; /* Pure White Text */
    font-size: 16px !important;
    font-weight: bold !important;
    width: 100% !important;
    padding: 12px !important;
    border: none !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
}

div.stButton > button:hover, 
div.stDownloadButton > button:hover {
    background-color: #1D4ED8 !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. CORE DATABASE SETTINGS & AUTO-REPAIR ENGINE ---
CSV_FILE = "healthcard_data.csv"
COLUMNS = ["Computer ID", "Healthcard ID", "Date", "Patient Name", "Room No", "Doctor Name", "Total Amount", "Status"]

if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)
else:
    try:
        check_df = pd.read_csv(CSV_FILE)
        if check_df.empty or "Status" not in check_df.columns:
            pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)
    except:
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

def get_next_id():
    try:
        df = pd.read_csv(CSV_FILE)
        if not df.empty and "Computer ID" in df.columns:
            return int(df["Computer ID"].max()) + 1
    except:
        pass
    return 101

DOCTORS_LIST = [
    "Dr. Hidayatullah Sb", "Dr. Tahir Aslam Sb", "Dr. Naseer Ahmad Sb", 
    "Dr. Mohammad Bakhsh Shawani Sb", "Dr. Ahmad Nawaz Sb", "Dr. Shehzada Dawood Sb", 
    "Dr. Masha Khan Sb", "Dr. Fazal Mohammad Sb", "Pro. Dr Jameel Ahmad Sb", 
    "Pro Dr Saleem Barrech Sb", "Dr. Abdul Ghaffar Sb", "Dr. Muhammad Arif Sb", 
    "Dr. Ghulam Rasool Sb", "Dr. Bano Durrani", "Dr. Hameedullah Kakar Sb", 
    "Medical Store", "Akram Hospital Medical Store OT", "Medical Store 3rd Floor", 
    "Canteen (1)", "Canteen (2)", "Canteen (3)", "Dr. Janzaib Kakar Sb", 
    "Lab (Routine)", "Lab (Special)", "Dr. Atif Gulzar Sb", "Dr. Masood Sb", 
    "Dr. Saeed Ahmed Khan Sb", "Dr. Bashir Agha Sb", "Dr. Uzma Sohail", 
    "Dr. Iqbal Sb", "Dr. Fareed Agha Sb", "Dr. Fareed Kakar Sb", 
    "Dr. Kishwer Rehman Sb", "Dr. Naseeb Ullah Shah Sb", "Dr. Noor Baloch Sb", 
    "Uzma Rasheed", "Dr. Izahr Ud Din Sb"
]

# Tabs Definition
tab1, tab2, tab3 = st.tabs(["🔒 Add Patient Record", "📋 View All Records", "⏳ Manage Claims (Pending)"])

# ==========================================
# --- TAB 1: ADD PATIENT RECORD FORM ---
# ==========================================
with tab1:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">Patient Information Entry Form</div>', unsafe_allow_html=True)
    
    next_id = get_next_id()
    
    with st.form(key="patient_entry_form", clear_on_submit=False):
        comp_id = st.text_input("Computer ID:", value=str(next_id), disabled=True)
        h_id = st.text_input("Healthcard ID:", key="input_hid")
        p_date = st.date_input("Date:", datetime.now(), key="input_date")
        p_name = st.text_input("Patient Name:", key="input_name")
        room_no = st.text_input("Room No:", key="input_room")
        doc_name = st.selectbox("Doctor Name:", ["Select Doctor"] + DOCTORS_LIST, key="input_doc")
        amount = st.number_input("Total Amount (PKR):", min_value=0, step=100, key="input_amount")
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        submit_button = st.form_submit_button("💾 Save Patient Data")
        
        if submit_button:
            if not h_id or not p_name or doc_name == "Select Doctor" or amount <= 0:
                st.error("Please fill all fields properly and ensure amount is greater than 0!")
            else:
                try:
                    df = pd.read_csv(CSV_FILE)
                    new_row = [int(next_id), h_id, p_date.strftime('%d/%m/%Y'), p_name, room_no, doc_name, float(amount), "Pending"]
                    df.loc[len(df)] = new_row
                    df.to_csv(CSV_FILE, index=False)
                    
                    st.success(f"Record Saved Successfully under ID: {next_id}!")
                    
                    st.session_state["last_saved_record"] = {
                        "comp_id": next_id, "h_id": h_id, "date": p_date.strftime('%d/%m/%Y'),
                        "name": p_name, "room": room_no, "doc": doc_name, "amount": amount
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving to CSV file: {e}")

    if "last_saved_record" in st.session_state:
        rec = st.session_state["last_saved_record"]
        st.markdown('<hr style="border:1px solid #CBD5E1;">', unsafe_allow_html=True)
        st.info(f"✨ Last Saved Record Summary (ID: {rec['comp_id']}) is ready for download.")
        
        pdf_styles = getSampleStyleSheet()
        pdf_buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        
        pdf_elements = [
            Paragraph("<b>HEALTHCARD MANAGEMENT SYSTEM</b>", pdf_styles['Heading1']),
            Paragraph("Patient Slip Receipt Summary", pdf_styles['Normal']),
            Spacer(1, 15)
        ]
        
        table_data = [
            ["Computer ID", str(rec['comp_id'])], ["Healthcard ID", rec['h_id']], ["Date", rec['date']],
            ["Patient Name", rec['name']], ["Room No", rec['room']], ["Doctor Name", rec['doc']], ["Total Amount", f"PKR {rec['amount']}"]
        ]
        receipt_table = Table(table_data)
        receipt_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#1E3A8A")),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1"))
        ]))
        pdf_elements.append(receipt_table)
        pdf_doc.build(pdf_elements)
        
        st.download_button(
            label="🖨️ Download Print Slip for Saved Record",
            data=pdf_buffer.getvalue(),
            file_name=f"Slip_{rec['comp_id']}.pdf",
            mime="application/pdf",
            key="action_download_pdf"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# --- TAB 2: VIEW ALL RECORDS ---
# ==========================================
with tab2:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">Master Database Directory</div>', unsafe_allow_html=True)
    
    df_all = pd.read_csv(CSV_FILE)
    
    if df_all.empty:
        st.info("No logs or records found inside the datastore.")
    else:
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            search_query = st.text_input("🔍 Quick Search (Name or ID):", key="search_query_all")
        with search_col2:
            status_filter = st.selectbox("🚦 Filter By Status:", ["All", "Pending", "Approved"], key="status_filter_all")
            
        filtered_df = df_all.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df['Patient Name'].astype(str).str.contains(search_query, case=False, na=False) |
                filtered_df['Healthcard ID'].astype(str).str.contains(search_query, case=False, na=False) |
                filtered_df['Computer ID'].astype(str).str.contains(search_query, case=False, na=False)
            ]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# --- TAB 3: MANAGE CLAIMS (PENDING) ---
# ==========================================
with tab3:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">Claims Settlement Module</div>', unsafe_allow_html=True)
    
    df_claims = pd.read_csv(CSV_FILE)
    pending_records = df_claims[df_claims["Status"] == "Pending"]
    
    if pending_records.empty:
        st.success("All clear! There are no outstanding pending claims found.")
    else:
        st.dataframe(pending_records, use_container_width=True, hide_index=True)
        st.markdown('<hr style="border:1px solid #CBD5E1;">', unsafe_allow_html=True)
        
        claim_col1, claim_col2 = st.columns(2)
        
        with claim_col1:
            pending_ids = pending_records["Computer ID"].tolist()
            selected_id = st.selectbox("Select Computer ID to process clearance:", pending_ids, key="claim_select_id")
            
        with claim_col2:
            st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
            if st.button("✅ Approve Select Claim", key="action_approve_claim"):
                df_claims.loc[df_claims["Computer ID"] == int(selected_id), "Status"] = "Approved"
                df_claims.to_csv(CSV_FILE, index=False)
                st.success(f"Claim associated with ID {selected_id} approved!")
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)
