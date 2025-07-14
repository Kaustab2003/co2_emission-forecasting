import streamlit as st
import pandas as pd
import datetime
import json
import os
import secrets
from utils.utils import fetch_external_emission_data

API_USERS_FILE = "api_users.json"

def get_sector_benchmarks(sector):
    # Example hardcoded benchmarks (tons CO2e/year)
    benchmarks = {
        "Manufacturing": {"average": 5000, "best": 2000},
        "Energy": {"average": 20000, "best": 8000},
        "Transport": {"average": 8000, "best": 3000},
        "IT": {"average": 1000, "best": 400},
        "Other": {"average": 3000, "best": 1000},
    }
    return benchmarks.get(sector, {"average": 3000, "best": 1000})

# --- Multi-language Support ---
LANGUAGES = {"en": "English", "hi": "हिन्दी"}
TRANSLATIONS = {
    "en": {
        "title": "Company Profile & Emission Sources",
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "register": "Register",
        "logout": "Logout",
        "select_company": "Select or Create Company",
        "new_company": "New company",
        "new_company_name": "New Company Name",
        "sector": "Sector",
        "size": "Company Size",
        "create_company": "Create Company",
        "add_emission_sources": "Add Emission Sources",
        "source_type": "Source Type",
        "annual_emissions": "Annual Emissions (tons CO2e)",
        "add_source": "Add Source",
        "current_emission_sources": "Current Emission Sources",
        "upload_csv": "Upload Emission Data (CSV)",
        "choose_csv": "Choose a CSV file",
        "sync_api": "Sync with API",
        "import_external": "Import from External Source",
        "logout": "Logout"
    },
    "hi": {
        "title": "कंपनी प्रोफ़ाइल और उत्सर्जन स्रोत",
        "login": "लॉगिन",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "register": "रजिस्टर करें",
        "logout": "लॉगआउट",
        "select_company": "कंपनी चुनें या बनाएं",
        "new_company": "नई कंपनी",
        "new_company_name": "नई कंपनी का नाम",
        "sector": "क्षेत्र",
        "size": "कंपनी का आकार",
        "create_company": "कंपनी बनाएं",
        "add_emission_sources": "उत्सर्जन स्रोत जोड़ें",
        "source_type": "स्रोत प्रकार",
        "annual_emissions": "वार्षिक उत्सर्जन (टन CO2e)",
        "add_source": "स्रोत जोड़ें",
        "current_emission_sources": "वर्तमान उत्सर्जन स्रोत",
        "upload_csv": "उत्सर्जन डेटा (CSV) अपलोड करें",
        "choose_csv": "CSV फ़ाइल चुनें",
        "sync_api": "API से सिंक करें",
        "import_external": "बाहरी स्रोत से आयात करें",
        "logout": "लॉगआउट"
    }
}
if "language" not in st.session_state:
    st.session_state["language"] = "en"
language = st.selectbox("🌐 Language / भाषा", list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="language_select")
st.session_state["language"] = language
T = TRANSLATIONS[language]

st.title(T["title"])

# --- Simple User Authentication with Registration and Roles ---
if "users" not in st.session_state:
    st.session_state["users"] = {"admin": {"password": "admin123", "role": "admin"}}
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False

if st.session_state["logged_in_user"] is None:
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")
    if login:
        if username in st.session_state["users"] and st.session_state["users"][username]["password"] == password:
            st.session_state["logged_in_user"] = username
            st.success(f"Logged in as {username}")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    if st.button("Register"):
        st.session_state["show_register"] = True
        st.rerun()
    if st.session_state["show_register"]:
        st.header("Register New User")
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            register = st.form_submit_button("Register")
        if register:
            if new_username in st.session_state["users"]:
                st.error("Username already exists.")
            elif not new_username or not new_password:
                st.error("Username and password required.")
            else:
                api_key = secrets.token_hex(16)
                st.session_state["users"][new_username] = {"password": new_password, "role": role, "api_key": api_key}
                # Save API key to shared file
                try:
                    if os.path.exists(API_USERS_FILE):
                        with open(API_USERS_FILE, "r") as f:
                            api_users = json.load(f)
                    else:
                        api_users = {}
                    api_users[new_username] = api_key
                    with open(API_USERS_FILE, "w") as f:
                        json.dump(api_users, f, indent=2)
                except Exception as e:
                    st.warning(f"Could not save API key to file: {e}")
                st.success(f"User {new_username} registered as {role}. Please log in.")
                st.session_state["show_register"] = False
                st.rerun()
    st.stop()
else:
    user_role = st.session_state["users"][st.session_state["logged_in_user"]]["role"]
    st.write(f"Logged in as: {st.session_state['logged_in_user']} ({user_role})")
    user_api_key = st.session_state["users"][st.session_state["logged_in_user"]].get("api_key")
    if user_api_key:
        st.info(f"Your API key: {user_api_key}")
    if st.button("Logout"):
        st.session_state["logged_in_user"] = None
        st.rerun()

# --- Multi-Company Support ---
st.header("Select or Create Company")
if "companies" not in st.session_state:
    st.session_state["companies"] = {}
if "selected_company" not in st.session_state:
    st.session_state["selected_company"] = None

company_names = list(st.session_state["companies"].keys())
selected = st.selectbox("Select a company", ["(New company)"] + company_names)

if selected == "(New company)":
    with st.form("new_company_form"):
        new_company_name = st.text_input("New Company Name")
        sector = st.selectbox("Sector", ["Manufacturing", "Energy", "Transport", "IT", "Other"])
        size = st.selectbox("Company Size", ["Small", "Medium", "Large"])
        create_company = st.form_submit_button("Create Company")
    if create_company and new_company_name:
        st.session_state["companies"][new_company_name] = {
            "info": {"name": new_company_name, "sector": sector, "size": size},
            "emission_sources": []
        }
        st.session_state["selected_company"] = new_company_name
        st.success(f"Created and selected company: {new_company_name}")
else:
    st.session_state["selected_company"] = selected

selected_company = st.session_state["selected_company"]

if selected_company:
    company_data = st.session_state["companies"][selected_company]
    st.header(f"Company Information: {selected_company}")
    st.write(company_data["info"])

    # --- Emission Sources Form ---
    st.header("Add Emission Sources")
    if "emission_sources" not in company_data:
        company_data["emission_sources"] = []

    with st.form("emission_source_form"):
        source_type = st.selectbox("Source Type", ["Electricity", "Transport", "Supply Chain", "Other"])
        annual_emission = st.number_input("Annual Emissions (tons CO2e)", min_value=0.0, step=0.01)
        add_source = st.form_submit_button("Add Source")

    if add_source:
        company_data["emission_sources"].append({
            "type": source_type,
            "emission": annual_emission
        })
        st.success(f"Added {source_type} source with {annual_emission} tons CO2e")
        st.session_state["last_update"] = datetime.datetime.now().date()
        # Show updated table immediately after adding
        st.write("### Current Emission Sources")
        st.dataframe(pd.DataFrame(company_data["emission_sources"]))

    # --- Display Current Data ---
    st.header("Current Emission Sources")
    if company_data["emission_sources"]:
        df = pd.DataFrame(company_data["emission_sources"])
        if "emission" not in df.columns:
            st.warning("No 'emission' column found in emission sources. Please check your data input.")
            total_emissions = 0
        else:
            total_emissions = df["emission"].sum()
        # Fix: get benchmarks for the current sector
        sector = company_data["info"].get("sector", "Other")
        benchmarks = get_sector_benchmarks(sector)
        issues = []
        for idx, row in df.iterrows():
            if row["emission"] < 0:
                issues.append(f"Negative value for {row['type']}.")
            if row["emission"] > 2 * benchmarks["average"]:
                issues.append(f"Unusually high value for {row['type']} (> {2*benchmarks['average']} tons CO₂e).")
        if total_emissions > 2 * benchmarks["average"]:
            issues.append(f"Total emissions are much higher than sector average ({benchmarks['average']} tons CO₂e).")
        if issues:
            st.warning("Data validation issues detected:")
            for issue in issues:
                st.write(f"- {issue}")
    else:
        st.info("No emission sources added yet.")

    # --- Optionally, allow CSV upload for batch input ---
    st.header("Upload Emission Data (CSV)")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file:
        df_upload = pd.read_csv(uploaded_file)
        company_data["emission_sources"] = df_upload.to_dict("records")
        st.success("Emission sources updated from uploaded file.")
        st.dataframe(df_upload)
        st.session_state["last_update"] = datetime.datetime.now().date()

    # --- Sync with API ---
    st.header("Sync with API")
    if st.button("Sync with API"):
        api_file = "api_emission_data.json"
        if os.path.exists(api_file):
            with open(api_file, "r") as f:
                api_data = json.load(f)
            if selected_company in api_data:
                company_data["emission_sources"] = api_data[selected_company]
                st.success(f"Emission sources updated from API for {selected_company}.")
                st.session_state["last_update"] = datetime.datetime.now().date()
            else:
                st.info(f"No API data found for {selected_company}.")
        else:
            st.info("API data file not found.")

    # --- Import from External Source ---
    st.header("Import from External Source")
    if st.button("Import from External Source"):
        try:
            external_data = fetch_external_emission_data(selected_company)
            if external_data:
                company_data["emission_sources"] = external_data
                st.success(f"Emission sources imported from external source for {selected_company}.")
                st.session_state["last_update"] = datetime.datetime.now().date()
            else:
                st.info("No data returned from external source.")
        except Exception as e:
            st.error(f"Failed to import from external source: {e}")

    # Save back to session state
    st.session_state["companies"][selected_company] = company_data
    st.session_state["company_info"] = company_data["info"]
    st.session_state["emission_sources"] = company_data["emission_sources"] 