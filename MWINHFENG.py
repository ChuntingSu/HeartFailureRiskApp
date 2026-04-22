import streamlit as st

# --- Core Calculation Function ---

def calculate_muscle_call_risk(age, nyha, egfr, bmi, hb):
    """Calculate total score based on statistical weights"""
    score = 0
    # 1. NYHA Class IV
    if nyha == 'IV': score += 28140
    # 2. Age > 75.5
    if age > 75.5: score += 938
    # 3. eGFR < 56.45
    if egfr < 56.45: score += 134
    # 4. BMI <= 22.5
    if bmi <= 22.5: score += 67
    # 5. Hb < 11.5
    if hb < 11.5: score += 5
    # 6. NYHA Class II
    if nyha == 'II': score += 1
    return score

# --- Streamlit Interface & Logic ---

st.set_page_config(page_title="Muscle Call Risk Prediction System", layout="centered")
st.title("Muscle Call in Heart Failure Risk Prediction System")
st.markdown("This system utilizes clinical indicators to assess the risk of muscle weakness in patients with heart failure.")
st.markdown("---")

# --- 1. Data Input Section ---
st.header("📋 Clinical Data Input")

col1, col2 = st.columns(2)

with col1:
    # 1. Age
    st.markdown("### 1. Age")
    age_input = st.number_input("Enter patient's age (years)", min_value=1.0, max_value=120.0, value=65.0, step=0.1)

    # 2. Hemoglobin (Hb)
    st.markdown("### 2. Hemoglobin (Hb)")
    hgb_input = st.number_input("Enter Hb level (g/dL)", min_value=1.0, max_value=25.0, value=13.0, step=0.1)

    # 3. Body Mass Index (BMI)
    st.markdown("### 3. Body Mass Index (BMI)")
    bmi_input = st.number_input("Enter BMI (kg/m²)", min_value=5.0, max_value=60.0, value=24.0, step=0.1)

with col2:
    # 4. estimated Glomerular Filtration Rate (eGFR)
    st.markdown("### 4. eGFR")
    egfr_input = st.number_input("Enter eGFR (mL/min/1.73m²)", min_value=1.0, max_value=200.0, value=70.0, step=0.1)

    # 5. NYHA Functional Class
    st.markdown("### 5. NYHA Functional Class")
    nyha_input = st.radio("Select NYHA Class", ['I', 'II', 'III', 'IV'], index=0, horizontal=True)

# --- 2. Calculation Logic ---
total_score = calculate_muscle_call_risk(age_input, nyha_input, egfr_input, bmi_input, hgb_input)

# --- 3. Results Section ---
st.markdown("---")
st.header("✨ Assessment Results")

# Risk definition based on ROC Cut-offs (5.0 and 206.0)
if total_score < 5.0:
    risk_level = "Low Risk"
    color = "#28a745"  # Green
    bg_color = "#e8f5e9"
    advice = "The patient's clinical indicators are stable. Current physical activity and nutritional follow-up are recommended."
    risk_idx = 0
elif 5.0 <= total_score <= 206.0:
    risk_level = "Intermediate Risk"
    color = "#fd7e14"  # Orange
    bg_color = "#fff3e0"
    advice = "Potential risk factors detected (e.g., advanced age or biochemical deviations). Nutritional support and supervised resistance training are suggested."
    risk_idx = 1
else:
    risk_level = "High Risk"
    color = "#dc3545"  # Red
    bg_color = "#fdecea"
    advice = "CRITICAL ALERT: The risk of muscle weakness is extremely high (associated with NYHA Class IV or multiple severe factors). Urgent clinical evaluation and medical intervention are highly recommended."
    risk_idx = 2

# Display Result Box
st.markdown(f"""
<div style="background-color:{bg_color}; padding: 25px; border-radius: 10px; border-left: 8px solid {color};">
    <h2 style="color:{color}; margin:0;">Result: {risk_level}</h2>
    <p style="font-size:18px; color:#333; margin-top:10px;"><b>Clinical Advice:</b> {advice}</p>
</div>
""", unsafe_allow_html=True)

# Visual Risk Indicators
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("**Risk Level Indicators:**")
col_res1, col_res2, col_res3 = st.columns(3)
col_res1.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#28a745; color:white' if risk_idx==0 else '#f0f2f6'};'>🟢 Low Risk</div>", unsafe_allow_html=True)
col_res2.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#fd7e14; color:white' if risk_idx==1 else '#f0f2f6'};'>🟡 Intermediate Risk</div>", unsafe_allow_html=True)
col_res3.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#dc3545; color:white' if risk_idx==2 else '#f0f2f6'};'>🔴 High Risk</div>", unsafe_allow_html=True)

# --- Footer & Copyright ---
copyright_text = "Copyright© 2026 ChuntingSu. All Rights Reserved."
footer_style = """
<style>
.footer {
    position: fixed;
    bottom: 0; left: 0; width: 100%;
    background-color: #f0f2f6; padding: 10px 0;
    text-align: center; font-size: 0.8em; color: #4f4f4f;
    z-index: 1000; border-top: 1px solid #ddd;
}
</style>
"""
st.markdown(footer_style, unsafe_allow_html=True)
st.markdown(f'<div class="footer">{copyright_text}</div>', unsafe_allow_html=True)
