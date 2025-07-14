import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
import datetime
import plotly.graph_objs as go
from utils.utils import load_model, forecast_emissions, ai_anomaly_detection

st.title("📊 Emission Dashboard")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

# Check for company info and emission sources
company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])
if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page to view the dashboard.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page to view the dashboard.")
    st.stop()

try:
    company_name = company_info.get('name', 'Unknown') if company_info else 'Unknown'
    company_sector = company_info.get('sector', 'Unknown') if company_info else 'Unknown'
    company_size = company_info.get('size', 'Unknown') if company_info else 'Unknown'
    st.write(f"Dashboard for **{company_name}** ({company_sector}, {company_size})")
except Exception as e:
    st.warning(f"Error reading company info: {e}")
    st.stop()

# --- Notification/Reminder System ---
if "last_update" not in st.session_state:
    st.session_state["last_update"] = datetime.datetime.now().date()

# Check if emission sources were updated recently
last_update = st.session_state["last_update"]
today = datetime.datetime.now().date()
days_since_update = (today - last_update).days
if days_since_update > 30:
    st.info(f"It's been over {days_since_update} days since you last updated your emission sources. Please review and update your data.")

# --- Notification System ---
if "notifications" not in st.session_state:
    st.session_state["notifications"] = []

def add_notification(msg, level="info"):
    st.session_state["notifications"].append({"msg": msg, "level": level})

# Display notifications
if st.session_state["notifications"]:
    for note in st.session_state["notifications"]:
        if note["level"] == "success":
            st.success(note["msg"])
        elif note["level"] == "warning":
            st.warning(note["msg"])
        elif note["level"] == "error":
            st.error(note["msg"])
        else:
            st.info(note["msg"])
    if st.button("Clear Notifications"):
        st.session_state["notifications"] = []

st.info("This dashboard is optimized for mobile and desktop. For best experience on mobile, use landscape mode.")

try:
    df = pd.DataFrame(emission_sources)
    has_emission_type = "emission" in df.columns and "type" in df.columns
except Exception as e:
    st.error(f"Error processing emission sources: {e}")
    has_emission_type = False
    df = pd.DataFrame()

if not has_emission_type:
    st.warning("No 'emission' or 'type' column found in emission sources. Please check your data input.")
# --- Current Emissions by Source ---
if has_emission_type:
    try:
        fig1, ax1 = plt.subplots()
        ax1.pie(df["emission"], labels=df["type"], autopct="%1.1f%%", startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1, use_container_width=True)

        fig2, ax2 = plt.subplots()
        ax2.bar(df["type"], df["emission"])
        ax2.set_xlabel("Source Type")
        ax2.set_ylabel("Annual Emissions (tons CO₂e)")
        ax2.set_title("Emissions by Source")
        st.pyplot(fig2, use_container_width=True)

        # --- Plotly Interactive Pie Chart ---
        plotly_pie = go.Figure(data=[go.Pie(labels=df["type"], values=df["emission"], hole=0.3)])
        plotly_pie.update_layout(title="Interactive Emission Breakdown by Source")
        st.plotly_chart(plotly_pie, use_container_width=True)
        # --- Plotly Interactive Bar Chart ---
        plotly_bar = go.Figure(data=[go.Bar(x=df["type"], y=df["emission"])] )
        plotly_bar.update_layout(title="Interactive Emission Bar Chart", xaxis_title="Source Type", yaxis_title="Annual Emissions (tons CO₂e)")
        st.plotly_chart(plotly_bar, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying emission source charts: {e}")

    # --- Recommendations Section ---
    st.write("### Recommendations & Best Practices")
    recommendations = []
    try:
        for idx, row in df.sort_values("emission", ascending=False).iterrows():
            source = row.get("type")
            emission_val = row.get("emission")
            if source is None:
                continue
            if emission_val is None or emission_val <= 0:
                rec = f"No emissions recorded for {source}. Add emission data to see savings estimates."
                recommendations.append(rec)
                continue
            if source == "Electricity":
                rec = f"Consider switching a portion of your electricity use to renewables. Reducing electricity emissions by 20% could save {emission_val*0.2:.1f} tons CO₂e per year. [Learn more](https://www.epa.gov/greenpower/green-power-partnership-basics)"
            elif source == "Transport":
                rec = f"Transitioning company vehicles to electric or hybrid could reduce transport emissions. Cutting transport emissions by 10% saves {emission_val*0.1:.1f} tons CO₂e. [Best practices](https://www.epa.gov/greenvehicles)"
            elif source == "Supply Chain":
                rec = f"Work with suppliers who prioritize sustainability. A 5% reduction in supply chain emissions saves {emission_val*0.05:.1f} tons CO₂e. [Supply chain tips](https://www.cdp.net/en/supply-chain)"
            else:
                rec = f"Review and optimize this source. Even a small reduction (5%) saves {emission_val*0.05:.1f} tons CO₂e."
            recommendations.append(rec)
        for rec in recommendations:
            st.markdown(f"- {rec}")
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
else:
    recommendations = []

# --- Forecasted Emissions (if available) ---
forecast_df = st.session_state.get("forecast_df")
if forecast_df is not None and hasattr(forecast_df, 'head'):
    try:
        if "Year" in forecast_df.columns and "Emission" in forecast_df.columns:
            st.write("### Forecasted Emissions")
            st.dataframe(forecast_df, use_container_width=True)
            fig3, ax3 = plt.subplots()
            ax3.plot(forecast_df['Year'], forecast_df['Emission'], marker='o')
            ax3.set_xlabel("Year")
            ax3.set_ylabel("CO₂ Emissions (tons)")
            ax3.set_title(f"Emission Forecast for {company_name}")
            st.pyplot(fig3, use_container_width=True)
            # --- Plotly Interactive Chart ---
            plotly_fig = go.Figure()
            plotly_fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Emission'], mode='lines+markers', name='Forecast'))
            plotly_fig.update_layout(title=f"Interactive Emission Forecast for {company_name}", xaxis_title="Year", yaxis_title="CO₂ Emissions (tons)")
            st.plotly_chart(plotly_fig, use_container_width=True)
        else:
            st.info("No 'Year' or 'Emission' column found in forecast data. Please ensure your forecast data is correctly formatted.")
    except Exception as e:
        st.error(f"Error displaying forecast data: {e}")
else:
    st.info("No forecast data available. Please generate a forecast on the 'Forecast' page.")

# --- Analytics & Insights ---
st.header("Analytics & Insights")
if forecast_df is not None and hasattr(forecast_df, 'head') and len(forecast_df) > 1:
    try:
        emissions = forecast_df["Emission"].values
        years = forecast_df["Year"].values
        diffs = emissions[1:] - emissions[:-1]
        avg_change = diffs.mean()
        trend = "decreasing" if avg_change < 0 else "increasing"
        st.write(f"Average annual change: {avg_change:.2f} tons CO₂e/year ({trend})")
        # Detect spikes/drops
        spikes = []
        for i, d in enumerate(diffs):
            if abs(d) > 2 * abs(avg_change) and abs(avg_change) > 0:
                spikes.append((years[i+1], d))
                add_notification(f"Year {int(years[i+1])}: {'Increase' if d > 0 else 'Decrease'} of {d:.2f} tons CO₂e detected.", level="warning")
        if spikes:
            st.warning("Unusual spikes/drops detected:")
            for year, d in spikes:
                st.write(f"Year {int(year)}: {'Increase' if d > 0 else 'Decrease'} of {d:.2f} tons CO₂e")
        else:
            st.success("No unusual spikes or drops detected in forecast.")
    except Exception as e:
        st.error(f"Error analyzing forecast data: {e}")
else:
    st.info("Not enough forecast data for analytics.")

# --- Export Section ---
st.write("### Export Data")
import io
if has_emission_type and st.button("Export Emission Sources as CSV"):
    try:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Emission Sources CSV", data=csv, file_name="emission_sources.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error exporting emission sources: {e}")

if forecast_df is not None:
    try:
        csv_forecast = forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Forecast CSV", data=csv_forecast, file_name="forecast.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error exporting forecast data: {e}")

# --- PDF Export Section ---
def generate_pdf_report(company_info, df, forecast_df, recommendations, fig_path=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, f"CO₂ Emission Report: {company_info['name']}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Sector: {company_info['sector']} | Size: {company_info['size']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Emission Sources:", ln=True)
    pdf.set_font("Arial", size=10)
    if has_emission_type:
        for idx, row in df.iterrows():
            pdf.cell(0, 8, f"- {row['type']}: {row['emission']} tons CO₂e", ln=True)
    pdf.ln(5)
    if forecast_df is not None:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Forecast (first 5 years):", ln=True)
        pdf.set_font("Arial", size=10)
        for i, row in forecast_df.head(5).iterrows():
            pdf.cell(0, 8, f"Year {int(row['Year'])}: {row['Emission']:.2f} tons CO₂e", ln=True)
        pdf.ln(5)
    if fig_path:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Forecast Chart:", ln=True)
        pdf.image(fig_path, w=170)
        pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Recommendations:", ln=True)
    pdf.set_font("Arial", size=10)
    for rec in recommendations:
        pdf.multi_cell(0, 8, f"- {rec}")
    return pdf.output(dest='S').encode('latin1')

st.write("### Download PDF Report")
if has_emission_type and st.button("Download PDF Report"):
    # Save forecast chart as image
    fig_path = None
    if forecast_df is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            fig3, ax3 = plt.subplots()
            ax3.plot(forecast_df['Year'], forecast_df['Emission'], marker='o')
            ax3.set_xlabel("Year")
            ax3.set_ylabel("CO₂ Emissions (tons)")
            ax3.set_title(f"Emission Forecast for {company_name}")
            fig3.savefig(tmpfile.name)
            fig_path = tmpfile.name
    pdf_bytes = generate_pdf_report(company_info, df, forecast_df, recommendations, fig_path)
    st.download_button("Download PDF Report", data=pdf_bytes, file_name="emission_report.pdf", mime="application/pdf")
    if fig_path:
        os.remove(fig_path)

def get_sector_benchmarks(sector):
    benchmarks = {
        "Manufacturing": {"average": 5000, "best": 2000},
        "Energy": {"average": 20000, "best": 8000},
        "Transport": {"average": 8000, "best": 3000},
        "IT": {"average": 1000, "best": 400},
        "Other": {"average": 3000, "best": 1000},
    }
    return benchmarks.get(sector, {"average": 3000, "best": 1000})

# Data validation and anomaly detection
sector = company_info["sector"]
benchmarks = get_sector_benchmarks(sector)
if has_emission_type:
    total_emissions = df["emission"].sum()
    issues = []
    for idx, row in df.iterrows():
        if "emission" not in row or "type" not in row:
            continue
        if row["emission"] < 0:
            issues.append(f"Negative value for {row['type']}.")
        if row["emission"] > 2 * benchmarks["average"]:
            issues.append(f"Unusually high value for {row['type']} (>{2*benchmarks['average']} tons CO₂e).")
    if total_emissions > 2 * benchmarks["average"]:
        issues.append(f"Total emissions are much higher than sector average ({benchmarks['average']} tons CO₂e).")
    if issues:
        st.warning("Data validation issues detected:")
        for issue in issues:
            st.write(f"- {issue}")

# --- AI-powered Data Validation ---
st.header("AI-powered Data Validation & Anomaly Detection")
if has_emission_type:
    anomalies = ai_anomaly_detection(df)
    if anomalies:
        st.warning(f"ML model flagged {len(anomalies)} emission source(s) as anomalies:")
        for idx in anomalies:
            row = df.loc[idx]
            st.write(f"- {row['type']}: {row['emission']} tons CO₂e")
    else:
        st.success("No anomalies detected by ML model.")

# --- Predictive Target Achievement ---
st.header("Predictive Target Achievement")
target = st.number_input("Set your target annual emissions (tons CO₂e)", min_value=0.0, value=1000.0, step=100.0)
target_year = None
if forecast_df is not None:
    below_target = forecast_df[forecast_df["Emission"] <= target]
    if not below_target.empty:
        target_year = int(below_target.iloc[0]["Year"])
        st.success(f"At current pace, you will reach your target in {target_year}.")
        add_notification(f"Target of {target} tons CO₂e will be reached in {target_year}.", level="success")
    else:
        st.info("Your target is not reached within the forecast period.")
else:
    st.info("No forecast data available.")

# --- Downloadable Analytics Report ---
st.header("Download Analytics Report")
import io
if forecast_df is not None and len(forecast_df) > 1:
    # Prepare analytics data
    analytics = []
    emissions = forecast_df["Emission"].values
    years = forecast_df["Year"].values
    diffs = emissions[1:] - emissions[:-1]
    avg_change = diffs.mean()
    trend = "decreasing" if avg_change < 0 else "increasing"
    analytics.append({"Metric": "Average annual change", "Value": f"{avg_change:.2f} ({trend})"})
    # Spikes
    for i, d in enumerate(diffs):
        if abs(d) > 2 * abs(avg_change) and abs(avg_change) > 0:
            analytics.append({"Metric": f"Spike in {int(years[i+1])}", "Value": f"{'Increase' if d > 0 else 'Decrease'} of {d:.2f}"})
    # Target achievement
    if target_year:
        analytics.append({"Metric": "Target Achievement Year", "Value": str(target_year)})
    else:
        analytics.append({"Metric": "Target Achievement Year", "Value": "Not reached in forecast"})
    analytics_df = pd.DataFrame(analytics)
    csv = analytics_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Analytics Report (CSV)", data=csv, file_name="analytics_report.csv", mime="text/csv")
else:
    st.info("Not enough forecast data for analytics report.")

# --- Interactive ML Recommendations ---
st.header("Interactive Emission Reduction Planner")
model = load_model()
# Custom cost per ton inputs
if "custom_costs" not in st.session_state:
    st.session_state["custom_costs"] = {}
COST_PER_TON = {}
for idx, row in df.iterrows():
    source = row.get("type")
    emission_val = row.get("emission")
    if source is None or emission_val is None:
        continue
    default_cost = {"Electricity": 50, "Transport": 100, "Supply Chain": 75, "Other": 60}.get(source, 60)
    st.session_state["custom_costs"][f"{source}_{idx}"] = st.number_input(
        f"Cost per ton for {source} ($)",
        min_value=1,
        value=st.session_state["custom_costs"].get(f"{source}_{idx}", default_cost),
        step=1,
        key=f"cost_{source}_{idx}"
    )
    COST_PER_TON[source] = st.session_state["custom_costs"][f"{source}_{idx}"]

# --- Min/Max Reduction Constraints ---
st.subheader("Set Min/Max Reduction Constraints")
if "reduction_constraints" not in st.session_state:
    st.session_state["reduction_constraints"] = {}
constraints = {}
for idx, row in df.iterrows():
    source = row.get("type")
    emission_val = row.get("emission")
    if source is None or emission_val is None:
        continue
    min_val = st.number_input(f"Min reduction for {source} (%)", min_value=0, max_value=100, value=0, step=1, key=f"min_{source}_{idx}")
    max_val = st.number_input(f"Max reduction for {source} (%)", min_value=min_val, max_value=100, value=100, step=1, key=f"max_{source}_{idx}")
    constraints[source] = (min_val, max_val)

reduction_options = {}
costs = {}
for idx, row in df.iterrows():
    source = row.get("type")
    emission_val = row.get("emission")
    if source is None or emission_val is None:
        continue
    current = emission_val
    min_val, max_val = constraints[source]
    reduction_options[source] = st.slider(
        f"Reduce {source} emissions by (%)",
        min_value=min_val,
        max_value=max_val,
        value=min_val,
        step=1,
        key=f"slider_{source}_{idx}"
    )
    tons_reduced = current * reduction_options[source] / 100
    cost = tons_reduced * COST_PER_TON.get(source, 60)
    costs[source] = cost
    st.caption(f"Estimated cost: ${cost:,.0f} for {tons_reduced:.1f} tons CO₂e reduced")

# --- Cost vs. Reduction Curve Visualization ---
st.subheader("Cost vs. CO₂e Reduction Curve")
import numpy as np
import plotly.graph_objs as go
curve_points = []
for pct in range(0, 101, 5):
    total_cost = 0
    total_reduced = 0
    for idx, row in df.iterrows():
        source = row.get("type")
        emission_val = row.get("emission")
        if source is None or emission_val is None:
            continue
        cost = COST_PER_TON.get(source, 60)
        min_val, max_val = constraints[source]
        # Use pct only if within constraints
        use_pct = min(max(pct, min_val), max_val)
        tons_reduced = emission_val * use_pct / 100
        total_cost += tons_reduced * cost
        total_reduced += tons_reduced
    curve_points.append((total_cost, total_reduced))
curve_points = np.array(curve_points)
curve_fig = go.Figure()
curve_fig.add_trace(go.Scatter(x=curve_points[:,0], y=curve_points[:,1], mode='lines+markers', name='Cost vs. CO₂e Reduced'))
curve_fig.update_layout(title="Cost vs. CO₂e Reduction Curve", xaxis_title="Total Cost ($)", yaxis_title="Total CO₂e Reduced (tons)")
st.plotly_chart(curve_fig, use_container_width=True)

# --- Save/Load Reduction Plans ---
if "reduction_plans" not in st.session_state:
    st.session_state["reduction_plans"] = {}

st.subheader("Save or Load Reduction Plans")
plan_name = st.text_input("Plan Name")
if st.button("Save Current Plan") and plan_name:
    st.session_state["reduction_plans"][plan_name] = reduction_options.copy()
    st.success(f"Plan '{plan_name}' saved.")

if st.session_state["reduction_plans"]:
    selected_plan = st.selectbox("Load a saved plan", ["(Select)"] + list(st.session_state["reduction_plans"].keys()))
    if selected_plan != "(Select)":
        if st.button("Apply Selected Plan"):
            for src in reduction_options:
                reduction_options[src] = st.session_state["reduction_plans"][selected_plan][src]
            st.success(f"Plan '{selected_plan}' applied. Adjust sliders if needed and re-apply reductions.")

total_cost = sum(costs.values())
st.markdown(f"**Total estimated cost for this plan: ${total_cost:,.0f}**")

if "emission" not in df.columns:
    st.warning("No 'emission' column found in emission sources. Please check your data input.")
else:
    new_emissions = df["emission"].copy()
    for idx, row in df.iterrows():
        pct = reduction_options.get(row.get("type"), 0)
        emission_val = row.get("emission")
        if emission_val is None:
            continue
        new_emissions[idx] = emission_val * (1 - pct/100)
    total_new = new_emissions.sum()
    forecast_new = forecast_emissions(model, total_new, len(forecast_df) if forecast_df is not None else 10)
    st.subheader("Combined Impact of Selected Reductions")
    import plotly.graph_objs as go
    plotly_fig = go.Figure()
    if forecast_df is not None:
        plotly_fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Emission'], mode='lines+markers', name='Current Forecast'))
    plotly_fig.add_trace(go.Scatter(x=forecast_new['Year'], y=forecast_new['Emission'], mode='lines+markers', name='With Selected Reductions'))
    plotly_fig.update_layout(title="Forecast Impact of Selected Reductions", xaxis_title="Year", yaxis_title="CO₂ Emissions (tons)")
    st.plotly_chart(plotly_fig, use_container_width=True)

# --- ML Budget Optimization ---
st.header("ML: Cost-Effective Reduction Plan for Your Budget")
if "emission" not in df.columns:
    st.warning("No 'emission' column found in emission sources. Please check your data input.")
else:
    budget = st.number_input("Enter your budget ($)", min_value=0, value=1000, step=100)
    if st.button("Suggest Optimal Plan for Budget"):
        # Sort sources by cost per ton (ascending)
        sources_sorted = sorted([(row.get("type"), row.get("emission"), COST_PER_TON.get(row.get("type"), 60)) for idx, row in df.iterrows()], key=lambda x: x[2])
        remaining_budget = budget
        optimal_reduction = {src: 0 for src, _, _ in sources_sorted}
        total_tons_reduced = 0
        for src, tons, cost_per_ton in sources_sorted:
            if src is None or tons is None or cost_per_ton is None:
                continue
            max_tons = tons * constraints[src][1] / 100 if src in constraints else tons
            if max_tons is None or not isinstance(max_tons, (int, float)) or not isinstance(cost_per_ton, (int, float)) or cost_per_ton is None or cost_per_ton <= 0:
                continue
            affordable_tons = min(max_tons, remaining_budget / cost_per_ton)
            pct = int((affordable_tons / tons) * 100) if tons > 0 else 0
            optimal_reduction[src] = pct
            spent = affordable_tons * cost_per_ton
            total_tons_reduced += affordable_tons
            remaining_budget -= spent
            if remaining_budget <= 0:
                break
        st.write("**Recommended Reductions (%):**")
        for src in optimal_reduction:
            st.write(f"{src}: {optimal_reduction[src]}%")
        st.write(f"**Total tons CO₂e reduced:** {total_tons_reduced:.1f}")
        # Show forecast impact
        new_emissions = df["emission"].copy()
        for idx, row in df.iterrows():
            pct = optimal_reduction.get(row.get("type"), 0)
            emission_val = row.get("emission")
            if emission_val is None:
                continue
            new_emissions[idx] = emission_val * (1 - pct/100)
        total_new = new_emissions.sum()
        forecast_new = forecast_emissions(model, total_new, len(forecast_df) if forecast_df is not None else 10)
        st.subheader("Forecast Impact of Optimal Plan")
        import plotly.graph_objs as go
        plotly_fig = go.Figure()
        if forecast_df is not None:
            plotly_fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Emission'], mode='lines+markers', name='Current Forecast'))
        plotly_fig.add_trace(go.Scatter(x=forecast_new['Year'], y=forecast_new['Emission'], mode='lines+markers', name='Optimal Plan'))
        plotly_fig.update_layout(title="Forecast Impact of Cost-Effective Plan", xaxis_title="Year", yaxis_title="CO₂ Emissions (tons)")
        st.plotly_chart(plotly_fig, use_container_width=True)

# --- Carbon Offset Marketplace Integration (Prototype) ---
st.header("Purchase Carbon Offsets (Prototype)")
if "emission" not in df.columns:
    st.warning("No 'emission' column found in emission sources. Please check your data input.")
else:
    current_emissions = df["emission"].sum()
    st.write(f"Your current annual emissions: **{current_emissions:,.1f} tons CO₂e**")
    offset_price = 10  # $10 per ton (mock price)
    tons_to_offset = st.number_input("Tons to offset", min_value=0.0, max_value=float(current_emissions), value=0.0, step=1.0)
    total_offset_cost = tons_to_offset * offset_price
    st.write(f"Estimated cost: **${total_offset_cost:,.2f}** at ${offset_price}/ton")
    if st.button("Purchase Offsets") and tons_to_offset > 0:
        import json
        import datetime
        purchase = {
            "user": st.session_state["logged_in_user"],
            "company": company_info["name"],
            "tons": tons_to_offset,
            "cost": total_offset_cost,
            "timestamp": str(datetime.datetime.now())
        }
        file = "offset_purchases.json"
        try:
            if os.path.exists(file):
                with open(file, "r") as f:
                    purchases = json.load(f)
            else:
                purchases = []
            purchases.append(purchase)
            with open(file, "w") as f:
                json.dump(purchases, f, indent=2)
            st.success(f"Purchased {tons_to_offset} tons of carbon offsets for ${total_offset_cost:,.2f} (mock transaction recorded).")
        except Exception as e:
            st.error(f"Failed to record purchase: {e}")
