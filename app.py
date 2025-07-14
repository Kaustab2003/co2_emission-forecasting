import streamlit as st

# --- Branding/Welcome (no logo, but note for future) ---
st.markdown("""
<div style='text-align: center;'>
    <h1 style='color: #2c3e50;'>CO₂ Emissions Forecasting & Management Platform</h1>
    <h3 style='color: #16a085;'>Empowering Sustainable Decisions</h3>
    <p style='color: #888; font-size: 0.9em;'>Want your company logo here? Just upload <b>logo.png</b> to the project root.</p>
</div>
""", unsafe_allow_html=True)

# --- Progress Indicator ---
profile_complete = (
    "company_info" in st.session_state and
    st.session_state["company_info"] and
    isinstance(st.session_state["company_info"], dict)
)
emissions_added = (
    profile_complete and
    "emission_sources" in st.session_state and
    isinstance(st.session_state["emission_sources"], list) and
    len(st.session_state["emission_sources"]) > 0
)
forecast_run = "forecast_df" in st.session_state and st.session_state["forecast_df"] is not None

progress = int(profile_complete) + int(emissions_added) + int(forecast_run)
steps = ["Profile", "Emission Sources", "Forecast"]

st.markdown("### Onboarding Progress")
st.progress(progress / 3, text=f"{progress}/3 steps completed")
st.markdown("<ul>" + "".join([
    f'<li style=\"color: {"green" if i < progress else "#888"}\">{step}</li>'
    for i, step in enumerate(steps, 1)
]) + "</ul>", unsafe_allow_html=True)

# --- Main Usage Guide (Landing Page) ---
st.title("📖 How to Use the CO₂ Emissions Forecasting & Management Platform")
st.markdown("""
Welcome to the all-in-one CO₂ Emissions Forecasting and Management Platform! This enterprise-ready Streamlit app empowers organizations to forecast, analyze, and manage their carbon emissions with advanced analytics, scenario planning, benchmarking, and team collaboration tools.

---

## 🚀 Key Features
- **Company Profile & Emission Sources:** Manage company details and input all emission sources.
- **Forecast:** Predict future CO₂ emissions using machine learning models based on your data.
- **Dashboard:** Visualize trends, correlations, and reduction scenarios with interactive charts.
- **Manual Prediction:** Enter custom values for instant emission predictions.
- **Batch Upload:** Upload CSVs for bulk predictions.
- **Data Exploration:** Advanced EDA, clustering, regression, and time-series analysis.
- **Scenario Simulation:** Simulate emission reduction scenarios and compare outcomes.
- **Action Planning:** Plan year-by-year emission reduction actions and see their impact.
- **Scenario Library:** Save, load, and compare multiple emission scenarios.
- **Benchmarking:** Compare your emissions to industry averages and best-in-class.
- **Team Collaboration:** Assign tasks, manage team members, and communicate in-app.
- **Compliance & Audit:** Tools for regulatory compliance and audit readiness.
- **Admin Dashboard:** Manage users, companies, and app settings (admin only).
- **Interactive Dashboard:** Explore emissions data with advanced visualizations.
- **Multi-language Support:** Use the app in English or Hindi.
- **Mobile Friendly:** Optimized for desktop and mobile (landscape mode recommended).

---

## 🧭 Navigation & Workflow
1. **Login/Register:** Start by logging in or registering a new user. Admins can invite/manage users.
2. **Company Profile:** Create/select your company and fill out the profile, including sector and emission sources.
3. **Forecast:** Use the Forecast page to generate a baseline emissions forecast for your company.
4. **Dashboard:** Explore trends, correlations, and try out reduction scenarios interactively.
5. **Scenario Simulation:** Adjust emission sources and simulate different reduction strategies.
6. **Action Planning:** Plan and visualize year-by-year emission reduction actions.
7. **Scenario Library:** Save, load, and compare different scenarios for strategic planning.
8. **Benchmarking:** See how your emissions compare to industry standards.
9. **Team Collaboration:** Assign tasks, message team members, and manage roles.
10. **Compliance & Audit:** Access compliance tools and audit logs (if enabled).
11. **Admin Dashboard:** (Admins only) Manage users, companies, and app-wide settings.
12. **Data Exploration:** Dive deep into your data with advanced analytics and visualizations.
13. **Batch Upload/Manual Prediction:** For bulk or ad-hoc predictions.

---

## 📂 File & Data Management
- **All data is managed in session state and local files.**
- **CSV uploads:** Use the provided templates for batch upload, scenario, and action plan data.
- **Export:** Download results and forecasts as CSV for reporting.

---

## ⚙️ Tech Stack
- **Streamlit** (UI & app framework)
- **Scikit-learn** (ML models)
- **Pandas, Numpy** (data wrangling)
- **Matplotlib, Seaborn, Plotly** (visualizations)
- **Sweetviz, YData Profiling** (EDA)

---

## 📝 Tips & Best Practices
- Always start by updating your company profile and emission sources.
- Run a forecast before using scenario simulation or action planning.
- Use the sidebar to navigate between features.
- For best results, use the app in a modern browser (Chrome, Edge, Firefox).
- For mobile, use landscape mode for optimal experience.

---

## ❓ Need Help?
- Each page contains tooltips and instructions.
- For troubleshooting, check warnings and info messages on each page.
- For advanced support, contact your app administrator.

---

Enjoy using the CO₂ Emissions Forecasting & Management Platform to drive your sustainability journey!
""")
