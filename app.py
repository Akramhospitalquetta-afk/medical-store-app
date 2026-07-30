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

st.markdown("""
<style>
.stApp { background-color: #F8FAFC; color: #0F172A; }
button[data-baseweb="tab"] { font-size: 15px !important; font-weight: bold !important; color: #475569 !important; padding: 12px 10px !important; flex-grow: 1 !important; text-align: center !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #FFFFFF !important; background-color: #2563EB !important; border-radius: 6px; }
.card-container { background-color: #FFFFFF; padding: 16px; border-radius: 12px; border: 2px solid #E2E8F0 !important; margin-top: 10px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.form-header { background-color: #1E3A8A; color: white; text-align: center; padding: 12px; font-weight: bold; font-size: 18px; border-radius: 8px; margin-bottom: 20px; }
label, .stWidgetLabel p { font-size: 15px !important; font-weight: bold !important; color: #1E293B !important; margin-bottom: 4px !important; }
.stTextInput > div > div, .stDateInput > div > div, .stSelectbox > div > div, .stNumberInput > div > div { border: 2px solid #64748B !important; border-radius: 8px !important; background-color: #FFFFFF !important; height: 46px !important; }
div[data-baseweb="input"], div[data-baseweb="select"] { background-color: #FFFFFF !important; }
.stTextInput input, .stDateInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] span { color: #0F172A !important; font-size: 16px !important; font-weight: bold !important; background-color: transparent !important; -webkit-text-fill-color: #0F172A !important; }
div.stButton > button, div.stDownloadButton > button { background-color: #2563EB !important; color: #FFFFFF !important; font-size: 16px !important; font-weight: bold !important; width: 100% !important; padding: 14px !important; border: none !important; border-radius: 8px !important; box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important; margin-bottom: 10px !important; }
div.stButton > button:hover, div.stDownloadButton > button:hover { background-color: #1D4ED8 !important; color: #FFFFFF !important; }
.metric-box { background-color: #FFFFFF; border-top: 4px solid #2563EB; padding: 12px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px; font-size: 14px; color: #0F172A; }
.mobile-patient-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 2. CORE DATABASE SETTINGS ---
CSV_FILE = "healthcard_data.csv"
COLUMNS = ["Computer ID", "Healthcard ID", "Date", "Patient Name", "Room No", "Doctor Name", "Total Amount", "Status"]

if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
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
    "Dr. Kishwer Rehman Sb", "Dr. Naseeb Ullah Shah Sb", "Noor Baloch Sb", 
    "Uzma Rasheed", "Dr. Izahr Ud Din Sb"
]

tab1, tab2, tab3 = st.tabs(["🔒 Add Patient", "📋 View Logs", "⏳ Claims System"])

# --- TAB 1: ADD PATIENT ---
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
        pdf_styles = getSampleStyleSheet()
        pdf_buffer = io.BytesIO()
        pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        pdf_elements = [Paragraph("<b>HEALTHCARD MANAGEMENT SYSTEM</b>", pdf_styles['Heading1']), Spacer(1, 15)]
        table_data = [
            ["Computer ID", str(rec['comp_id'])], ["Healthcard ID", str(rec['h_id'])], ["Date", str(rec['date'])],
            ["Patient Name", str(rec['name'])], ["Room No", str(rec['room'])], ["Doctor Name", str(rec['doc'])], ["Total Amount", f"PKR {rec['amount']:,}"]
        ]
        t = Table(table_data)
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (0,-1), colors.lightgrey), ('GRID', (0,0), (-1,-1), 1, colors.grey)]))
        pdf_elements.append(t)
        pdf_doc.build(pdf_elements)
        st.download_button(label="📥 Download Receipt PDF", data=pdf_buffer.getvalue(), file_name=f"receipt_{rec['comp_id']}.pdf", mime="application/pdf")

# --- TAB 2: VIEW LOGS ---
with tab2:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">📋 Business Live Overview</div>', unsafe_allow_html=True)
    
    try:
        if os.path.exists(CSV_FILE):
            df_all = pd.read_csv(CSV_FILE)
            if df_all.empty:
                st.info("No records inside datastore.")
            else:
                total_pkr = pd.to_numeric(df_all["Total Amount"], errors="coerce").sum()
                approved_count = len(df_all[df_all["Status"] == "Approved"])
                pending_count = len(df_all[df_all["Status"] == "Pending"])
                
                col1, col2, col3 = st.columns(3)
                with col1: st.markdown(f'<div class="metric-box">💰 Total Business<br><b>PKR {total_pkr:,.0f}</b></div>', unsafe_allow_html=True)
                with col2: st.markdown(f'<div class="metric-box">✅ Approved Logs<br><b>{approved_count} Passed</b></div>', unsafe_allow_html=True)
                with col3: st.markdown(f'<div class="metric-box">⏳ Pending Claims<br><b>{pending_count} Active</b></div>', unsafe_allow_html=True)
                
                search_query = st.text_input("🔍 Quick Search (Name / ID):", key="search_query_live_final_new")
                status_options = ["All", "Pending", "Approved"]
                selected_status = st.selectbox("🚦 Filter Status:", status_options, key="status_filter_live_final_new")
                
                filtered_df = df_all.copy()
                if search_query:
                    filtered_df = filtered_df[filtered_df["Patient Name"].astype(str).str.contains(search_query, case=False) | filtered_df["Computer ID"].astype(str).str.contains(search_query, case=False)]
                if selected_status != "All":
                    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
                
                st.dataframe(filtered_df, use_container_width=True)
                
                csv_buffer = io.StringIO()
                filtered_df.to_csv(csv_buffer, index=False)
                st.download_button(label="📥 Export Report to CSV", data=csv_buffer.getvalue(), file_name=f"HMS_Report_{datetime.now().strftime('%d_%m_%Y')}.csv", mime="text/csv")
        else:
            st.info("No records inside datastore.")
    except Exception as e:
        st.error(f"Error reading datastore: {e}")

# --- TAB 3: CLAIMS SYSTEM ---
with tab3:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">⏳ Claims Status Management</div>', unsafe_allow_html=True)
    try:
        if os.path.exists(CSV_FILE):
            df_claims = pd.read_csv(CSV_FILE)
            if df_claims.empty:
                st.info("No pending claims found.")
            else:
                pending_df = df_claims[df_claims["Status"] == "Pending"]
                if pending_df.empty:
                    st.success("All claims are cleared!")
                else:
                    st.dataframe(pending_df, use_container_width=True)
        else:
            st.info("No claims database detected.")
    except Exception as e:
        st.error(f"Error loading Claims: {e}")
