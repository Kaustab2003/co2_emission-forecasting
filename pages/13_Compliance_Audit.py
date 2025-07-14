import streamlit as st
import json
import os
from fpdf import FPDF
import pandas as pd

st.title("📑 Regulatory Compliance & Audit Tools")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])

if not company_info or not emission_sources:
    st.warning("Please fill out your company profile and add emission sources on the 'Company Profile' page.")
    st.stop()

df = pd.DataFrame(emission_sources)

# --- Generate Compliance Report ---
st.header("Generate Compliance Report")
report_type = st.selectbox("Select standard", ["GHG Protocol", "ISO 14064"])
if st.button("Download Compliance Report (PDF)"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, f"{report_type} Compliance Report: {company_info['name']}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Sector: {company_info['sector']} | Size: {company_info['size']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Emission Sources:", ln=True)
    pdf.set_font("Arial", size=10)
    for idx, row in df.iterrows():
        pdf.cell(0, 8, f"- {row['type']}: {row['emission']} tons CO₂e", ln=True)
    pdf.ln(5)
    pdf.output("compliance_report.pdf")
    with open("compliance_report.pdf", "rb") as f:
        st.download_button("Download PDF", data=f, file_name="compliance_report.pdf", mime="application/pdf")
    os.remove("compliance_report.pdf")
if st.button("Download Compliance Report (CSV)"):
    st.download_button("Download CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="compliance_report.csv", mime="text/csv")

# --- Audit Document Upload/View ---
st.header("Audit Document Upload & View")
audit_dir = "audit_docs"
os.makedirs(audit_dir, exist_ok=True)
uploaded = st.file_uploader("Upload audit document (PDF, DOCX, XLSX, CSV)", type=["pdf", "docx", "xlsx", "csv"])
if uploaded:
    path = os.path.join(audit_dir, uploaded.name)
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success(f"Uploaded {uploaded.name}")
    # Log the upload
    log_file = "audit_log.json"
    log_entry = {"user": st.session_state["logged_in_user"], "company": company_info["name"], "file": uploaded.name, "timestamp": str(pd.Timestamp.now())}
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

# --- List Audit Actions ---
st.header("Audit Log")
log_file = "audit_log.json"
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        logs = json.load(f)
    logs = [l for l in logs if l["company"] == company_info["name"]]
    st.write(f"{len(logs)} audit actions for {company_info['name']}:")
    for l in logs:
        st.write(f"{l['timestamp']}: {l['user']} uploaded {l['file']}")
else:
    st.info("No audit actions found.") 