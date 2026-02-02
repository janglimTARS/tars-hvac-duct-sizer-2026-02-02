import streamlit as st
import numpy as np
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="TARS HVAC Duct Sizer", layout="wide")

st.title("🛠️ TARS HVAC Duct Sizer")
st.markdown("---")
st.markdown("Practical tool for MEP engineers to size HVAC ducts based on CFM and velocity. Uses standard formulas.")

# Sidebar inputs
st.sidebar.header("Inputs")
cfm = st.sidebar.slider("Airflow (CFM)", min_value=50.0, max_value=20000.0, value=1200.0, step=50.0)
velocity = st.sidebar.slider("Design Velocity (FPM)", min_value=300.0, max_value=2500.0, value=900.0, step=50.0)
shape = st.sidebar.selectbox("Duct Shape", ["Round", "Rectangular"])
if shape == "Rectangular":
    aspect = st.sidebar.slider("Width/Height Ratio", min_value=1.0, max_value=6.0, value=2.0, step=0.5)

friction_rate = st.sidebar.slider("Friction Rate (in.wg/100ft)", 0.05, 0.50, 0.08, 0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("[GitHub Repo](https://github.com/janglimTARS/tars-hvac-duct-sizer-2026-02-02)")

# Calculations
area_sqft = cfm / velocity
st.metric("Cross-Sectional Area", f"{area_sqft:.2f} ft²")

col1, col2 = st.columns(2)

with col1:
    if shape == "Round":
        diameter_ft = 2 * math.sqrt(area_sqft / math.pi)
        diameter_in = diameter_ft * 12
        st.metric("Round Diameter", f"{diameter_in:.1f} inches")
        
        # Nearest standard round sizes
        standards_round = [4,5,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30,32,34,36]
        nearest_round = min(standards_round, key=lambda x: abs(x - diameter_in))
        st.info(f"Nearest standard: **{nearest_round}\"** ({abs(nearest_round - diameter_in):.1f}\" diff)")
    
    else:  # Rectangular
        height_ft = math.sqrt(area_sqft / aspect)
        width_ft = aspect * height_ft
        height_in = height_ft * 12
        width_in = width_ft * 12
        st.metric("Rectangular Size", f"{width_in:.1f}\" x {height_in:.1f}\" (W x H)")
        
        # Nearest standards
        standards = [6,8,10,12,14,16,18,20,22,24,30,36]
        nearest_w = min(standards, key=lambda x: abs(x - width_in))
        nearest_h = min(standards, key=lambda x: abs(x - height_in))
        st.info(f"Nearest standard: **{nearest_w}\" x {nearest_h}\"**")

with col2:
    # Velocity pressure approx VP = 0.000602 * V^2 / 4005 or simple
    vp = (velocity ** 2) / 4005
    st.metric("Velocity Pressure", f"{vp:.3f} in.wg")
    
    # Note on friction
    st.info(f"**Friction Rate:** {friction_rate:.2f} in.wg/100ft")

# Chart
st.subheader("Sizing Chart")
cfm_range = np.linspace(200, cfm*2, 100)
vel_range = np.full_like(cfm_range, velocity)
area_range = cfm_range / vel_range
diam_range = 12 * 2 * np.sqrt(area_range / np.pi)

fig = go.Figure()
fig.add_trace(go.Scatter(x=cfm_range, y=diam_range, mode='lines', name='Round Dia (in)'))
fig.update_layout(title="CFM vs Round Duct Diameter", xaxis_title="CFM", yaxis_title="Diameter (inches)")
st.plotly_chart(fig, use_container_width=True)

# Table of options
st.subheader("Velocity Options")
vel_options = [600, 800, 1000, 1200, 1500]
data = []
for v in vel_options:
    a = cfm / v
    d = 12 * 2 * np.sqrt(a / np.pi)
    data.append({"Velocity (FPM)": v, "Area (ft²)": f"{a:.2f}", "Dia (in)": f"{d:.1f}"})

df = pd.DataFrame(data)
st.dataframe(df)

st.markdown("---")
st.markdown("*Built by TARS Nightly Inventor - 2026-02-02*")
