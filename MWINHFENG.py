import streamlit as st

# --- Core Calculation Functions ---

def calculate_age_scores(age: int) -> tuple[int, int]:
    """Dual scoring rules for Age"""
    # 1. Overall Risk Score Rule: Age > 75 adds 10 points
    overall_age_score = 10 if age > 75 else 0
    # 2. AHEAD SCORE Rule: Age > 70 adds 1 point
    ahead_age_score = 1 if age > 70 else 0
    return overall_age_score, ahead_age_score

def calculate_hgb_ahead_score(gender_is_male: bool, hgb: float) -> int:
    """AHEAD SCORE Hemoglobin rule (Male < 13 / Female < 12)"""
    if gender_is_male:
        return 1 if hgb < 13.0 else 0
    else: # Female
        return 1 if hgb < 12.0 else 0

# --- Streamlit Interface and Logic ---

st.set_page_config(page_title="Muscle Call in HF", layout="centered")

# --- Updated Title Section ---
st.title("Muscle Call in Heart Failure")
st.markdown("##### *This is a muscle weakness risk calculator in heart failure patients*")
st.markdown("---")

# --- 1. Data Input Section ---
st.header("📋 Clinical Data Entry")

# 1. Sex
st.markdown("## 1. Gender")
gender = st.selectbox("Please select patient gender", ['Male', 'Female'])
gender_is_male = (gender == 'Male')

# 2. Age
st.markdown("## 2. Age")
st.markdown("""
<style> .custom-caption { font-size: 0.85rem; color: #666; margin-bottom: 2px; } </style>
<div class="custom-caption">1. <b>Overall Score:</b> Age > 75 adds <b>10 pts</b></div>
<div class="custom-caption">2. <b>AHEAD Score:</b> Age > 70 adds <b>1 pt</b></div>
""", unsafe_allow_html=True)
age_input = st.number_input("Enter patient's age (years)", min_value=1, max_value=120, value=65, step=1)
overall_age_score, ahead_age_score = calculate_age_scores(age_input)

# 3. NYHA Class
st.markdown("## 3. NYHA Functional Class")
st.caption("Class II: +7 pts | Class IV: +3 pts")
nyha_input = st.radio("Select NYHA Classification", ['I', 'II', 'III', 'IV'], index=0, horizontal=True, key='nyha')

if nyha_input == 'II':
    nyha_score = 7
elif nyha_input == 'IV':
    nyha_score = 3
else:
    nyha_score = 0

st.markdown("---")

# 4. AHEAD SCORE & Lab Values
st.markdown("## 4. AHEAD Score Components & Labs")
ahead_score_placeholder = st.empty() 

col_a, col_b = st.columns(2)

with col_a:
    # 4-1. Af (Atrial Fibrillation)
    st.markdown("### 4-1. Atrial Fibrillation (Af)")
    af_input = st.radio("History of Atrial Fibrillation?", ['No', 'Yes'], index=0, horizontal=True, key='af')
    af_score = 1 if af_input == 'Yes' else 0

    # 4-2. Hemoglobin (Hb)
    st.markdown("### 4-2. Hemoglobin (Hb)")
    st.markdown("""
    <div class="custom-caption">1. <b>Overall Score:</b> Hb ≤ 15.8 adds <b>3 pts</b></div>
    <div class="custom-caption">2. <b>AHEAD Score:</b> Male < 13 / Female < 12 adds <b>1 pt</b></div>
    """, unsafe_allow_html=True)
    hgb_input = st.number_input("Hemoglobin level (g/dL)", min_value=1.0, max_value=25.0, value=14.0, step=0.1, key='hgb')
    
    hgb_ahead_contribution = calculate_hgb_ahead_score(gender_is_male, hgb_input)
    hgb_overall_score = 3 if hgb_input <= 15.8 else 0

with col_b:
    # 4-3. HbA1C
    st.markdown("### 4-3. HbA1C")
    st.caption("≥ 6.5% adds 1 pt to AHEAD Score")
    hba1c_input = st.number_input("HbA1C level (%)", min_value=1.0, max_value=20.0, value=5.5, step=0.1, key='hba1c')
    hba1c_ahead_score = 1 if hba1c_input >= 6.5 else 0

    # 4-4. Creatinine (Cr)
    st.markdown("### 4-4. Creatinine (Cr)")
    st.caption("> 1.47 mg/dL adds 1 pt to AHEAD Score")
    cr_input = st.number_input("Creatinine level (mg/dL)", min_value=0.1, value=1.0, step=0.01, key='cr') 
    cr_ahead_score = 1 if cr_input > 1.47 else 0

# 5. eGFR
st.markdown("---")
st.markdown("## 5. eGFR")
st.caption("If ≤ 56.45 mL/min/1.73m², adds **4 pts** to Overall Score")
egfr_input = st.number_input("eGFR value", min_value=1.0, max_value=200.0, value=70.0, step=0.1, key='egfr')
egfr_score = 4 if egfr_input <= 56.45 else 0

# 6. BMI
st.markdown("## 6. BMI")
st.caption("If ≤ 22.5 kg/m², adds **2 pts** to Overall Score")
bmi_input = st.number_input("BMI value (kg/m²)", min_value=5.0, max_value=60.0, value=25.0, step=0.1, key='bmi')
bmi_score = 2 if bmi_input <= 22.5 else 0

# --- 2. Score Calculations ---

AHEAD_TOTAL = ahead_age_score + af_score + hgb_ahead_contribution + cr_ahead_score + hba1c_ahead_score
ahead_score_placeholder.info(f"Intermediate Calculation: **AHEAD Score = {AHEAD_TOTAL} pts**")

# AHEAD contribution to Overall Score
ahead_contribution_pts = 1 if AHEAD_TOTAL > 1.5 else 0

# Final Overall Risk Score Calculation
FINAL_SCORE = (
    overall_age_score    
    + nyha_score         
    + ahead_contribution_pts 
    + egfr_score         
    + hgb_overall_score  
    + bmi_score          
)

# --- 3. Results Section ---
st.markdown("---")
st.header("✨ Risk Assessment Result")

# Risk Level Determination
if FINAL_SCORE <= 10:
    risk_status = "Low Risk"
    risk_color = "#28a745" # Green
    idx = 0
elif 11 <= FINAL_SCORE <= 20:
    risk_status = "Intermediate Risk"
    risk_color = "#fd7e14" # Orange
    idx = 1
else:
    risk_status = "High Risk"
    risk_color = "#dc3545" # Red
    idx = 2

# Results Display
res_col1, res_col2 = st.columns([1, 1])

with res_col1:
    st.metric(label="Overall Muscle Weakness Score", value=f"{FINAL_SCORE} pts")
    st.markdown(f"Result: <span style='font-size:24px; color:{risk_color}; font-weight:bold;'>{risk_status}</span>", unsafe_allow_html=True)

with res_col2:
    st.markdown("**Risk Stratification:**")
    st.markdown(f"""
    <div style="border-left: 5px solid #28a745; padding-left: 10px; margin-bottom: 5px; background-color: {'#e8f5e9' if idx==0 else 'transparent'};">
        <b>0 - 10 pts</b>: Low Risk
    </div>
    <div style="border-left: 5px solid #fd7e14; padding-left: 10px; margin-bottom: 5px; background-color: {'#fff3e0' if idx==1 else 'transparent'};">
        <b>11 - 20 pts</b>: Intermediate Risk
    </div>
    <div style="border-left: 5px solid #dc3545; padding-left: 10px; margin-bottom: 5px; background-color: {'#fdecea' if idx==2 else 'transparent'};">
        <b>21+ pts</b>: High Risk
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("📊 Score Breakdown")
st.markdown(f"""
| Risk Parameter | Condition Met | Contribution |
| :--- | :--- | :--- |
| **Age (Overall)** | Age > 75 | **{overall_age_score} pts** |
| **NYHA Class** | Class II (+7) or IV (+3) | **{nyha_score} pts** |
| **AHEAD Score Check** | Total AHEAD > 1.5 | **{ahead_contribution_pts} pts** |
| **eGFR** | eGFR ≤ 56.45 | **{egfr_score} pts** |
| **Hemoglobin (Overall)** | Hb ≤ 15.8 | **{hgb_overall_score} pts** |
| **BMI** | BMI ≤ 22.5 | **{bmi_score} pts** |
""")

# --- Footer Copyright ---
copyright_text = "Copyright© 2025 ChuntingSu. All Rights Reserved."
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
