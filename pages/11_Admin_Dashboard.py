import streamlit as st
import json
import secrets
import os

st.title("🔑 Admin Dashboard")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

user = st.session_state["logged_in_user"]
users = st.session_state.get("users", {})
user_role = users.get(user, {}).get("role", "user")

if user_role != "admin":
    st.error("You must be an admin to access this page.")
    st.stop()

API_USERS_FILE = "api_users.json"

st.header("All Users")
usernames = list(users.keys())
for uname in usernames:
    uinfo = users[uname]
    st.write(f"**{uname}** | Role: {uinfo.get('role', 'user')} | API Key: {uinfo.get('api_key', '-')}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Reset API Key for {uname}"):
            new_key = secrets.token_hex(16)
            users[uname]["api_key"] = new_key
            # Update api_users.json
            try:
                if os.path.exists(API_USERS_FILE):
                    with open(API_USERS_FILE, "r") as f:
                        api_users = json.load(f)
                else:
                    api_users = {}
                api_users[uname] = new_key
                with open(API_USERS_FILE, "w") as f:
                    json.dump(api_users, f, indent=2)
            except Exception as e:
                st.warning(f"Could not update API key file: {e}")
            st.success(f"API key for {uname} reset.")
            st.session_state["users"] = users
            st.experimental_rerun()
    with col2:
        if uname != user and st.button(f"Deactivate {uname}"):
            users[uname]["active"] = False
            st.success(f"User {uname} deactivated.")
            st.session_state["users"] = users
            st.experimental_rerun()
    st.markdown("---")

# Show only active users in the rest of the app (optional)

st.header("Deactivated Users")
deactivated = [uname for uname, uinfo in users.items() if not uinfo.get("active", True)]
if deactivated:
    for uname in deactivated:
        if st.button(f"Reactivate {uname}"):
            users[uname]["active"] = True
            st.success(f"User {uname} reactivated.")
            st.session_state["users"] = users
            st.experimental_rerun()
else:
    st.info("No deactivated users.")

st.header("API Update Log")
API_LOG_FILE = "api_log.json"
log_data = []
if os.path.exists(API_LOG_FILE):
    with open(API_LOG_FILE, "r") as f:
        log_data = json.load(f)
    usernames = [u for u in users.keys()]
    companies = list({entry['company'] for entry in log_data})
    selected_user = st.selectbox("Filter by user", ["All"] + usernames)
    selected_company = st.selectbox("Filter by company", ["All"] + companies)
    filtered = log_data
    if selected_user != "All":
        filtered = [entry for entry in filtered if entry['username'] == selected_user]
    if selected_company != "All":
        filtered = [entry for entry in filtered if entry['company'] == selected_company]
    st.write(f"Showing {len(filtered)} log entries:")
    for entry in filtered:
        st.json(entry)
else:
    st.info("No API log data found.") 