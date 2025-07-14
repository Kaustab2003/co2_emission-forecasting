import streamlit as st
import json
import os

st.title("🤝 Team Collaboration & Task Assignment")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])
company_info = st.session_state.get("company_info")
if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page to use this page.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page to use this page.")
    st.stop()

company_name = company_info["name"]

# --- Team Management ---
st.header("Team Members")
TEAM_FILE = "company_teams.json"
if os.path.exists(TEAM_FILE):
    with open(TEAM_FILE, "r") as f:
        teams = json.load(f)
else:
    teams = {}
if company_name not in teams:
    teams[company_name] = {}

user = st.session_state["logged_in_user"]
users = st.session_state.get("users", {})
user_role = users.get(user, {}).get("role", "user")

st.write(f"Team for {company_name}:")
for uname, role in teams[company_name].items():
    st.write(f"- {uname} ({role})")

if user_role == "admin":
    st.subheader("Invite User to Team")
    invite_user = st.text_input("Username to invite")
    invite_role = st.selectbox("Assign role", ["manager", "analyst"])
    if st.button("Invite User") and invite_user:
        teams[company_name][invite_user] = invite_role
        with open(TEAM_FILE, "w") as f:
            json.dump(teams, f, indent=2)
        st.success(f"Invited {invite_user} as {invite_role} to {company_name}")

# --- In-App Messaging & Task Assignment ---
st.header("Team Messages & Tasks")
TASKS_FILE = "company_tasks.json"
if os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "r") as f:
        tasks = json.load(f)
else:
    tasks = {}
if company_name not in tasks:
    tasks[company_name] = []

st.subheader("Assign a Task/Message")
task_to = st.selectbox("Assign to", list(teams[company_name].keys()) or [user])
task_msg = st.text_area("Task/Message")
if st.button("Send Task/Message") and task_msg:
    task = {"from": user, "to": task_to, "msg": task_msg, "timestamp": str(st.session_state.get('now', ''))}
    tasks[company_name].append(task)
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)
    st.success(f"Task/message sent to {task_to}")

st.subheader("Team Inbox")
for t in tasks[company_name]:
    if t["to"] == user or t["from"] == user:
        st.write(f"[{t['timestamp']}] {t['from']} → {t['to']}: {t['msg']}") 