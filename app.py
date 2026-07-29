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
st.set_page_config(page_title="HMS Mobile", layout="centered")

# Mobile responsive ultimate custom CSS overwrite protection engine
st.markdown("""
<style>
/* Main Background Light Gray */
.stApp {
    background-color: #F8FAFC;
    color: #0F172A;
}

/* Tabs Layout Styling for Touch Fingers */
button[data-baseweb="tab"] {
    font-size: 15px !important;
    font-weight: bold !important;
    color: #475569 !important;
    padding: 12px 10px !important;
    flex-grow: 1 !important;
    text-align: center !important;
}

/* Active Tab Highlight (Blue) */
button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background-color: #2563EB !important;
    border-radius: 6px;
}

/* Inner Card Containers (Pure White) */
.card-container {
    background-color: #FFFFFF;
    padding: 16px;
    border-radius: 12px;
    border: 2px solid #E2E8F0 !important;
    margin-top: 10px;
    margin-bottom: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Top Headers Inside Card (Dark Blue) */
.form-header {
    background-color: #1E3A8A;
    color: white;
    text-align: center;
    padding: 12px;
    font-weight: bold;
    font-size: 18px;
    border-radius: 8px;
    margin-bottom: 20px;
}

/* Input Labels */
label, .stWidgetLabel p {
    font-size: 15px !important;
    font-weight: bold !important;
    color: #1E293B !important;
    margin-bottom: 4px !important;
}

/* --- THE ULTIMATE SOLID BOX BORDER & MOBILE LIGHT OVERWRITE FIX --- */
.stTextInput > div > div, 
.stDateInput > div > div, 
.stSelectbox > div > div, 
.stNumberInput > div > div {
    border: 2px solid #64748B !important;
    border-radius: 8px !important;
    background-color: #FFFFFF !important;
    height: 46px !important;
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
    -webkit-text-fill-color: #0F172A !important;
}

/* --- UNIVERSAL FOOLPROOF TOUCH BUTTON FIX --- */
div.stButton > button, 
div.stDownloadButton > button {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: bold !important;
    width: 100% !important;
    padding: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    margin-bottom: 10px !important;
}

div.stButton > button:hover, 
div.stDownloadButton > button:hover {
    background-color: #1D4ED8 !important;
    color: #FFFFFF !important;
}

/* Metric Counter Blocks Mobile Optimized layout */
.metric-box {
    background-color: #FFFFFF;
    border-top: 4px solid #2563EB;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    text-align: center;
    margin-bottom: 10px;
}

/* Custom Mobile-first Record Card */
.mobile-patient-card {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 12px;
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
tab1, tab2, tab3 = st.tabs(["🔒 Add Patient", "📋 View Logs", "⏳ Claims System"])

# ==========================================
# --- TAB 1: ADD PATIENT RECORD FORM ---
# ==========================================
with tab1:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">📲 Patient Entry Module</div>', unsafe_allow_html=True)
    
    next_id = get_next_id()
    
    with st.form(key="patient_entry_form", clear_on_submit=False):
        st.text_input("Computer ID:", value=str(next_id), disabled=True)
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
                st.error("Please fill all fields properly!")
            else:
                try:
                    df = pd.read_csv(CSV_FILE)
                    new_row = [int(next_id), h_id, p_date.strftime('%d/%m/%Y'), p_name, room_no, doc_name, float(amount), "Pending"]
                    df.loc[len(df)] = new_row
                    df.to_csv(CSV_FILE, index=False)
                    
                    st.success(f"Saved Successfully! ID: {next_id}")
                    st.session_state["last_saved_record"] = {
                        "comp_id": next_id, "h_id": h_id, "date": p_date.strftime('%d/%m/%Y'),
                        "name": p_name, "room": room_no, "doc": doc_name, "amount": amount
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    if "last_saved_record" in st.session_state:
        rec = st.session_state["last_saved_record"]
        st.markdown('<hr style="border:1px solid #CBD5E1;">', unsafe_allow_html=True)
        
        pdf_styles = getSampleStyleSheet()
        pdf_buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        
        pdf_elements = [
            Paragraph("<b>HEALTHCARD MANAGEMENT SYSTEM</b>", pdf_styles['Heading1']),
            Spacer(1, 15)
        ]
        
        table_data = [
            ["Computer ID", str(rec['comp_id'])], ["Patient Name", rec['name']], ["Total Amount", f"PKR {rec['amount']}"]
        ]
        receipt_table = Table(table_data)
        receipt_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#1E3A8A")),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1"))
        ]))
        pdf_elements.append(receipt_table)
        pdf_doc.build(pdf_elements)
        
        st.download_button(
            label="🖨️ Download Print Slip",
            data=pdf_buffer.getvalue(),
            file_name=f"Slip_{rec['comp_id']}.pdf",
            mime="application/pdf",
            key="action_download_pdf"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# --- TAB 2: VIEW ALL RECORDS & MOBILE DASHBOARD ---
# ==========================================
with tab2:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">📈 Business Live Overview</div>', unsafe_allow_html=True)
    
    df_all = pd.read_csv(CSV_FILE)
    
    if df_all.empty:
        st.info("No records inside datastore.")
    else:
        # Metrics indicators
        total_pkr = pd.to_numeric(df_all["Total Amount"], errors="coerce").sum()
        approved_count = len(df_all[df_all["Status"] == "Approved"])
        pending_count = len(df_all[df_all["Status"] == "Pending"])
        
        # FIXED: Pure Python clean string variables used to completely avoid any template literal or HTML span crashes
        txt_business = f"PKR {total_pkr:,.0f}"
        txt_approved = f"{approved_count} Passed"
        txt_pending = f"{pending_count} Active"
        
        st.markdown(f'<div class="metric-box" style="border-top-color: #2563EB;"><b>💰 Total Business</b><br><span style="font-size:18px; font-weight:bold; color:#1E3A8A;">{txt_business}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box" style="border-top-color: #16A34A;"><b>✅ Approved Logs</b><br><span style="font-size:18px; font-weight:bold; color:#16A34A;">{txt_approved}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box" style="border-top-color: #DC2626;"><b>⏳ Pending Claims</b><br><span style="font-size:18px; font-weight:bold; color:#DC2626;">{txt_pending}</span></div>', unsafe_allow_html=True)
        
        st.markdown('<br>', unsafe_allow_html=True)
        
        # Mobile search vertical alignment
        search_query = st.text_input("🔍 Quick Search (Name / ID):", key="search_query_all")
        status_filter = st.selectbox("🚦 Filter Status:", ["All", "Pending", "Approved"], key="status_filter_all")
            
        filtered_df = df_all.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df['Patient Name'].astype(str).str.contains(search_query, case=False, na=False) |
                filtered_df['Healthcard ID'].astype(str).str.contains(search_query, case=False, na=False) |
                filtered_df['Computer ID'].astype(str).str.contains(search_query, case=False, na=False)
            ]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            
        # Responsive Native Grid Data Matrix Output
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Export Report to Excel/CSV",
            data=csv_buffer.getvalue(),
            file_name=f"Report_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
            key="excel_report_download_btn"
        )
        
        # --- TOUCH CONTROL MANAGEMENT EDITOR ---
        st.markdown('<hr style="border:1px solid #CBD5E1; margin-top:20px;">', unsafe_allow_html=True)
        st.markdown('<p style="font-size:16px; font-weight:bold; color:#1E3A8A;">🛠️ Modify Selected Entry</p>', unsafe_allow_html=True)
        
        all_ids = df_all["Computer ID"].tolist()
        target_id = st.selectbox("Choose Target ID to edit:", all_ids, key="modify_target_id")
        
        # Safely identify selected data row
        selected_row = df_all[df_all["Computer ID"] == int(target_id)]
        
        if not selected_row.empty:
            current_name = str(selected_row.iloc[0]["Patient Name"])
            current_amount = int(float(selected_row.iloc[0]["Total Amount"]))
            
            new_patient_name = st.text_input("Change Patient Name:", value=current_name, key="edit_pname")
            new_patient_amount = st.number_input("Change Amount:", value=current_amount, key="edit_pamount")
            
            edit_btn = st.button("✏️ Push Modifications", key="fire_edit_action")
            delete_btn = st.button("❌ Remove Entry Permanently", key="fire_delete_action")
            
            if edit_btn:
                df_all.loc[df_all["Computer ID"] == int(target_id), "Patient Name"] = new_patient_name
                df_all.loc[df_all["Computer ID"] == int(target_id), "Total Amount"] = new_patient_amount
                df_all.to_csv(CSV_FILE, index=False)
                st.success("Modifications updated!")
                st.rerun()
                
            if delete_btn:
                df_all = df_all[df_all["Computer ID"] != int(target_id)]
                df_all.to_csv(CSV_FILE, index=False)
                st.warning("Entry wiped.")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# --- TAB 3: MANAGE CLAIMS (MOBILE LIST) ---
# ==========================================
with tab3:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">⏳ Claims Quick Clearance</div>', unsafe_allow_html=True)
    
    df_claims = pd.read_csv(CSV_FILE)
    pending_records = df_claims[df_claims["Status"] == "Pending"]
    
    if pending_records.empty:
        st.success("All clear! Zero pending logs outstanding.")
    else:
        # Mobile optimized block rendering for pending status clearances
        for idx, row in pending_records.iterrows():
            st.markdown(f"""
            <div class="mobile-patient-card">
                <b>🆔 ID:</b> {row['Computer ID']} | <b>🚪 Room:</b> {row['Room No']}<br>
                <b>👤 Patient:</b> {row['Patient Name']}<br>
                <b>🩺 Doc:</b> {row['Doctor Name']}<br>
                <b>💰 Amount:</b> <span style="color:#1E3A8A; font-weight:bold;">PKR {row['Total Amount']}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<hr style="border:1px solid #CBD5E1;">', unsafe_allow_html=True)
        
        pending_ids = pending_records["Computer ID"].tolist()
        selected_id = st.selectbox("Select Target ID to Clear:", pending_ids, key="claim_select_id")
        
        if st.button("✅ Execute Immediate Approval", key="action_approve_claim"):
            df_claims.loc[df_claims["Computer ID"] == int(selected_id), "Status"] = "Approved"
            df_claims.to_csv(CSV_FILE, index=False)
            st.success(f"ID {selected_id} approved smoothly!")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
