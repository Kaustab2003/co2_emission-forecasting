import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

st.title("🏆 Emissions Benchmarking")

if "logged_in_user" not in st.session_state or st.session_state["logged_in_user"] is None:
    st.warning("Please log in to access this page.")
    st.stop()

company_info = st.session_state.get("company_info")
emission_sources = st.session_state.get("emission_sources", [])

if not company_info or not isinstance(company_info, dict):
    st.warning("Please fill out your company profile on the 'Company Profile' page before benchmarking.")
    st.stop()
if not emission_sources or not isinstance(emission_sources, list) or not all(isinstance(x, dict) for x in emission_sources):
    st.warning("Please add valid emission sources on the 'Company Profile' page before benchmarking.")
    st.stop()

sector = company_info["sector"]
benchmarks = get_sector_benchmarks(sector)

total_emissions = sum([src["emission"] for src in emission_sources])

st.write(f"**Your sector:** {sector}")
st.write(f"**Your total annual emissions:** {total_emissions:.1f} tons CO₂e")
st.write(f"**Industry average:** {benchmarks['average']} tons CO₂e/year")
st.write(f"**Best-in-class:** {benchmarks['best']} tons CO₂e/year")

# --- Visual Comparison ---
fig, ax = plt.subplots()
labels = ["Your Company", "Industry Avg", "Best-in-Class"]
values = [total_emissions, benchmarks["average"], benchmarks["best"]]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
ax.bar(labels, values, color=colors)
ax.set_ylabel("Annual Emissions (tons CO₂e)")
ax.set_title(f"Emissions Benchmarking: {sector}")
st.dataframe(pd.DataFrame([["Your Company", total_emissions], ["Industry Avg", benchmarks["average"]], ["Best-in-Class", benchmarks["best"]]], columns=["Label", "Emissions"]), use_container_width=True)
st.pyplot(fig, use_container_width=True)

# --- Recommendations ---
if total_emissions > benchmarks["average"]:
    st.warning("Your emissions are above the industry average. Consider implementing more aggressive reduction strategies.")
elif total_emissions > benchmarks["best"]:
    st.info("Your emissions are below average, but not yet best-in-class. Keep improving!")
else:
    st.success("Congratulations! Your emissions are best-in-class for your sector.") 