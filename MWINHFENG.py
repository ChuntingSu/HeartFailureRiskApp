import streamlit as st
import pandas as pd

# --- 1. Core Scoring Function ---
def calculate_detailed_scores(age, nyha, hb, egfr, bmi):
    """
    Calculate the total score and return detailed contributions for each variable.
    Based on Framingham-style Logistic Regression weights.
    Reference groups (0 points): NYHA I/II, Age <= 75.5, Hb > 11.55, BMI > 22.5, eGFR > 74.65
    """
    details = []
    
    # 1. NYHA Classification (Reference: Class I/II)
    nyha_score = 0
    if nyha == 'IV': 
        nyha_score = 18
    elif nyha == 'III': 
        nyha_score = 9
    details.append({
        'Clinical Variable': '2. New York Heart Association (NYHA) Class', 
        'Status': f'Class {nyha}', 
        'Score': nyha_score
    })
        
    # 2. Age
    age_score = 11 if age > 75.5 else 0
    details.append({
        'Clinical Variable': '1. Age', 
        'Status': '> 75.5 years' if age > 75.5 else '≤ 75.5 years', 
        'Score': age_score
    })
        
    # 3. Hemoglobin (Hb)
    hb_score = 5 if hb <= 11.55 else 0
    details.append({
        'Clinical Variable': '3. Hemoglobin (Hb)', 
        'Status': '≤ 11.55 g/dL' if hb <= 11.55 else '> 11.55 g/dL', 
        'Score': hb_score
    })
        
    # 4. eGFR
    egfr_score = 1 if egfr <= 74.65 else 0
    details.append({
        'Clinical Variable': '4. estimated Glomerular Filtration Rate (eGFR)', 
        'Status': '≤ 74.65' if egfr <= 74.65 else '> 74.65', 
        'Score': egfr_score
    })

    # 5. BMI
    bmi_score = 5 if bmi <= 22.5 else 0
    details.append({
        'Clinical Variable': '5. Body Mass Index (BMI)', 
        'Status': '≤ 22.5 kg/m²' if bmi <= 22.5 else '> 22.5 kg/m²', 
        'Score': bmi_score
    })
        
    total_score = sum(d['Score'] for d in details)
    return total_score, details

# --- Streamlit Interface Configuration ---
st.set_page_config(page_title="Muscle Call Risk Prediction System", layout="centered")
st.title("Muscle Call in Heart Failure Risk Prediction System")
st.markdown("---")

# --- 2. Data Input Section ---
st.header("📋 Clinical Data Input")

# Variable 1: Age
st.markdown("### 1. Age")
age_input = st.number_input("Enter patient's age (years)", min_value=1.0, max_value=120.0, value=65.0, step=0.1)

# Variable 2: NYHA
st.markdown("### 2. New York Heart Association (NYHA) Functional Classification")
nyha_input = st.radio("Select NYHA Class", ['I', 'II', 'III', 'IV'], index=1, horizontal=True)

# Variable 3: Hb
st.markdown("### 3. Hemoglobin (Hb)")
hb_input = st.number_input("Enter Hemoglobin level (g/dL)", min_value=1.0, max_value=25.0, value=13.0, step=0.1)

# Variable 4: eGFR
st.markdown("### 4. estimated Glomerular Filtration Rate (eGFR)")
egfr_input = st.number_input("Enter eGFR value (mL/min/1.73m²)", min_value=1.0, max_value=200.0, value=75.0, step=0.1)

# Variable 5: BMI
st.markdown("### 5. Body Mass Index (BMI)")
bmi_input = st.number_input("Enter BMI value (kg/m²)", min_value=5.0, max_value=60.0, value=24.0, step=0.1)

# --- 3. Score Calculation ---
total_score, score_details = calculate_detailed_scores(age_input, nyha_input, hb_input, egfr_input, bmi_input)

# ROC Cut-off values (Please update these values based on your ROC analysis results)
CUTOFF_LOW_MOD = 10.0  
CUTOFF_MOD_HIGH = 25.0 

# --- 4. Results Presentation ---
st.markdown("---")
st.header("✨ Assessment Results")

if total_score < CUTOFF_LOW_MOD:
    risk_level, color, bg_color = "🟢 Low Risk", "#28a745", "#e8f5e9"
    advice = "Maintain regular physical activity and monitor changes in muscle strength."
    msg_func = st.success
elif total_score < CUTOFF_MOD_HIGH:
    risk_level, color, bg_color = "🟡 Intermediate Risk", "#fd7e14", "#fff3e0"
    advice = "Refer to a nutritionist and a physical therapist for consultation on nutrition and exercise interventions."
    msg_func = st.warning
else:
    risk_level, color, bg_color = "🔴 High Risk", "#dc3545", "#fdecea"
    advice = "Refer to the interdisciplinary team, closely monitor, and prevent falls."
    msg_func = st.error

# Display Score Highlight Box
st.markdown(f"""
<div style="background-color:{bg_color}; padding: 25px; border-radius: 10px; text-align: center; border: 2px solid {color};">
    <h2 style="color:{color}; margin:0;">{risk_level}</h2>
    <p style="font-size:26px; color:#333; margin:10px 0 0 0;">Total Risk Score: <b>{total_score}</b> / 50</p>
</div>
""", unsafe_allow_html=True)

# --- 5. Clinical Recommendation Section ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📌 Clinical Recommendations")
msg_func(f"**{advice}**")

# --- 6. Detailed Score Breakdown Table ---
st.markdown("### 📝 Variable Contribution Breakdown")
st.table(pd.DataFrame(score_details))

st.info("💡 Note: This system is developed based on the Framingham Risk Score framework. NYHA Class I/II and other normal physiological ranges are used as the reference baseline (0 points).")

# --- 7. Footer & Copyright ---
st.markdown(f"""
<div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #f0f2f6; 
            padding: 10px 0; text-align: center; font-size: 0.8em; color: #4f4f4f; border-top: 1px solid #ddd; z-index: 100;">
    Copyright© 2026 ChuntingSu. All Rights Reserved.
</div>
""", unsafe_allow_html=True)
