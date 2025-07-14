import os
import json
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# --- Config ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'your_email@gmail.com'  # Replace with your email
EMAIL_PASS = 'your_app_password'      # Use an app password, not your main password

# --- Load user emails and company data (mock/demo) ---
USERS_FILE = 'user_emails.json'  # {"username": {"email": ..., "company": ...}}
COMPANIES_FILE = 'api_emission_data.json'  # {"company": [emission_sources]}

with open(USERS_FILE, 'r') as f:
    users = json.load(f)
with open(COMPANIES_FILE, 'r') as f:
    companies = json.load(f)

def generate_pdf_report(company, emission_sources):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, f"CO₂ Emission Report: {company}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Emission Sources:", ln=True)
    pdf.set_font("Arial", size=10)
    for src in emission_sources:
        pdf.cell(0, 8, f"- {src['type']}: {src['emission']} tons CO₂e", ln=True)
    pdf.ln(5)
    return pdf

def send_email(to_email, subject, body, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(body)
    with open(attachment_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(attachment_path))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

# --- Main: Generate and send reports ---
for username, info in users.items():
    email = info['email']
    company = info['company']
    emission_sources = companies.get(company, [])
    if not emission_sources:
        continue
    pdf = generate_pdf_report(company, emission_sources)
    pdf_path = f"report_{company}.pdf"
    pdf.output(pdf_path)
    send_email(email, f"CO₂ Emission Report for {company}", f"Attached is your latest CO₂ emission report for {company}.", pdf_path)
    print(f"Sent report to {email} for {company}")
    os.remove(pdf_path) 