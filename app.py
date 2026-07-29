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

# --- 2. CORE DATABASE SETTINGS ---
# --- 2. CORE DATABASE SETTINGS & AUTO-REPAIR ENGINE ---
CSV_FILE = "healthcard_data.csv"
COLUMNS = ["Computer ID", "Healthcard ID", "Date", "Patient Name", "Room No", "Doctor Name", "Total Amount", "Status"]

# Yeh logic khali file banna bilkul block kar dega
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
    
    comp_id = st.text_input("Computer ID:", value=str(next_id), disabled=True)
    h_id = st.text_input("Healthcard ID:", key="input_hid")
    p_date = st.date_input("Date:", datetime.now(), key="input_date")
    p_name = st.text_input("Patient Name:", key="input_name")
    room_no = st.text_input("Room No:", key="input_room")
    doc_name = st.selectbox("Doctor Name:", ["Select Doctor"] + DOCTORS_LIST, key="input_doc")
    amount = st.text_input("Total Amount:", key="input_amount")
    
    st.markdown('<br>', unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns(3)
    
    with b_col1:
        if st.button("💾 Save Patient Data", key="action_save"):
            if not h_id or not p_name or doc_name == "Select Doctor" or not amount:
                st.error("Please fill all fields properly before saving!")
            else:
                df = pd.read_csv(CSV_FILE)
                new_row = [next_id, h_id, p_date.strftime('%d/%m/%Y'), p_name, room_no, doc_name, amount, "Pending"]
                df.loc[len(df)] = new_row
                df.to_csv(CSV_FILE, index=False)
                st.success("Record Saved Successfully!")
                st.rerun()
                
    with b_col2:
        if st.button("🧹 Clear Form Fields", key="action_clear"):
            st.rerun()
            
    with b_col3:
        pdf_styles = getSampleStyleSheet()
        pdf_buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        
        pdf_elements = [
            Paragraph("<b>HEALTHCARD MANAGEMENT SYSTEM</b>", pdf_styles['Heading1']),
            Paragraph("Patient Slip Receipt Summary", pdf_styles['Normal']),
            Spacer(1, 15)
        ]
        
        table_data = [
            ["Computer ID", comp_id], ["Healthcard ID", h_id], ["Date", p_date.strftime('%d/%m/%Y')],
            ["Patient Name", p_name], ["Room No", room_no], ["Doctor Name", doc_name], ["Total Amount", f"PKR {amount}"]
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
            label="🖨️ Download Print Slip",
            data=pdf_buffer.getvalue(),
            file_name=f"Slip_{next_id}.pdf",
            mime="application/pdf",
            key="action_print"
        )
        
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# --- TAB 2: VIEW ALL RECORDS SHEET ---
# ==========================================
with tab2:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 2, 1.5])
    f_col5, f_col6, f_col7, f_col8 = st.columns([1.5, 1.5, 1, 1])
    
    df_all = pd.read_csv(CSV_FILE)
if not df_all.empty and "Status" in df_all.columns:
    status_filter_options = ["All"] + list(df_all["Status"].dropna().unique())
else:
    status_filter_options = ["All", "Pending", "Paid"]

    
    with f_col1: search_q = st.text_input("🔍 Search Patient:", placeholder="Name or ID...", key="v_search")
    with f_col2: sel_status = st.selectbox("📋 Status Filter:", status_filter_options, key="v_status")
    with f_col3: sel_doc = st.selectbox("👨‍⚕️ Doctor Filter:", ["All"] + DOCTORS_LIST, key="v_doc")
    with f_col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🖨️ PDF Print Report", key="v_pdf_btn"):
            st.info("Full layout report print processing triggered.")
            
    with f_col5: d_from = st.date_input("📅 Date From:", datetime.now(), key="v_from")
    with f_col6: d_to = st.date_input("📅 Date To:", datetime.now(), key="v_to")
    with f_col7:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", key="v_refresh"): st.rerun()
    with f_col8:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("📊 Export Excel", data=df_all.to_csv(index=False).encode('utf-8'), file_name="Healthcard_All_Records.csv", mime="text/csv", key="v_excel")

    st.markdown("<hr style='border-color: #CBD5E1; margin-top: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    if not df_all.empty:
        df_filtered = df_all.copy()
        
        # 1. Date formatting block create karein (Iske bagair error aata hai)
        df_filtered['Date_Parsed'] = pd.to_datetime(df_filtered['Date'], format='%d/%m/%Y', errors='coerce')
        if df_filtered['Date_Parsed'].isna().all():
            df_filtered['Date_Parsed'] = pd.to_datetime(df_filtered['Date'], format='%Y-%m-%d', errors='coerce')

        # 2. Filtering Core Engine Operations
        if search_q:
            df_filtered = df_filtered[df_filtered['Patient Name'].astype(str).str.contains(search_q, case=False, na=False) | df_filtered['Computer ID'].astype(str).str.contains(search_q, case=False, na=False)]
        if sel_status != "All": 
            df_filtered = df_filtered[df_filtered['Status'] == sel_status]
        if sel_doc != "All": 
            df_filtered = df_filtered[df_filtered['Doctor Name'] == sel_doc]
            
        # 3. Safe Date Range Filter check
        if 'Date_Parsed' in df_filtered.columns:
            df_filtered = df_filtered[(df_filtered['Date_Parsed'].dt.date >= d_from) & (df_filtered['Date_Parsed'].dt.date <= d_to)]
        
        display_final_df = df_filtered.drop(columns=['Date_Parsed'], errors='ignore')
        st.dataframe(display_final_df, use_container_width=True, hide_index=True)
        total_filtered_sum = pd.to_numeric(df_filtered['Total Amount'], errors='coerce').sum()
        st.markdown(f'<div style="background-color: #059669; padding: 12px; border-radius: 4px; font-weight: bold; font-size: 18px; color: white;">Grand Total (Filtered Data): PKR {total_filtered_sum:,.2f}</div>', unsafe_allow_html=True)
    else:
        st.info("System database sheet currently clean or empty.")
        
    st.markdown('</div>', unsafe_allow_html=True)

    


# ==========================================
# --- TAB 3: CLAIMS OPERATIONS LOGIC ---
# ==========================================
with tab3:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    df_master_claims = pd.read_csv(CSV_FILE)
    df_pending_only = df_master_claims[df_master_claims["Status"] == "Pending"].copy()
    
    c_row1, c_row2 = st.columns(2)
    with c_row1: 
        search_pending_val = st.text_input("🔍 Filter Search Pending:", placeholder="Type name or code reference...", key="p_search")
    
    if search_pending_val and not df_pending_only.empty:
        df_pending_active = df_pending_only[df_pending_only['Patient Name'].astype(str).str.contains(search_pending_val, case=False, na=False) | df_pending_only['Computer ID'].astype(str).str.contains(search_pending_val, case=False, na=False)]
    else: 
        df_pending_active = df_pending_only.copy()
        
    calc_pending_sum = pd.to_numeric(df_pending_active['Total Amount'], errors='coerce').sum()
    with c_row2:
        st.markdown(f'<div style="background-color: #D97706; padding: 12px; border-radius: 4px; font-weight: bold; font-size: 18px; text-align: center; color: white; margin-top: 18px;">Total Pending Amount: PKR {calc_pending_sum:,.2f}</div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not df_pending_active.empty:
        df_pending_active.insert(0, "Select", False)
        interactive_editor = st.data_editor(df_pending_active, hide_index=True, use_container_width=True, key="p_editor_grid")
        
        extracted_selected_ids = interactive_editor[interactive_editor["Select"] == True]["Computer ID"].tolist()
        
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            if st.button("☑️ Mark Selected Patient as PAID (Money Received)", key="p_paid_act"):
                if extracted_selected_ids:
                    df_upd = pd.read_csv(CSV_FILE)
                    df_upd.loc[df_upd["Computer ID"].isin(extracted_selected_ids), "Status"] = "Paid"
                    df_upd.to_csv(CSV_FILE, index=False)
                    st.success("Selected records marked as Paid successfully!")
                    st.rerun()
                else:
                    st.warning("Please tick mark at least one patient record checkbox.")
                    
        with act_col2:
            if st.button("🗑️ Delete Selected Record", key="p_del_act"):
                if extracted_selected_ids:
                    df_upd = pd.read_csv(CSV_FILE)
                    df_upd = df_upd[~df_upd["Computer ID"].isin(extracted_selected_ids)]
                    df_upd.to_csv(CSV_FILE, index=False)
                    st.error("Selected patient records dropped entirely.")
                    st.rerun()
                else:
                    st.warning("Please tick mark at least one patient record checkbox.")
    else:
        st.info("Great! No outstanding pending transaction records found.")
        
    st.markdown('</div>', unsafe_allow_html=True)
