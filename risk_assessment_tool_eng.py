import streamlit as st
import datetime

# --- A. Fixed Footer CSS/HTML Setup (Kept at the top for priority loading) ---

# Copyright text as requested
copyright_text = "Copyright© 2025 ChuntingSu. All Rights Reserved."
current_year = datetime.date.today().year

footer_style = """
<style>
/* Hide Streamlit's default footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Custom footer styles */
.footer {
    position: fixed; /* Fix to the bottom of the browser window */
    bottom: 0;      
    left: 0;        
    width: 100%;    
    background-color: #f0f2f6; /* Background color */
    padding: 10px 0; 
    text-align: center;
    font-size: 0.8em;
    color: #4f4f4f; 
    z-index: 1000; 
    border-top: 1px solid #ddd; 
}
</style>
"""

footer_content = f"""
<div class="footer">
    {copyright_text}
</div>
"""
# Insert CSS and HTML into the Streamlit page
st.markdown(footer_style, unsafe_allow_html=True)
st.markdown(footer_content, unsafe_allow_html=True)


# --- Core Calculation Functions ---
def calculate_hgb_score(gender_is_male: bool, hgb: float) -> int:
    """Calculates the score contribution of Hemoglobin (Hb) to the AHEAD Score."""
    if gender_is_male:
        return 1 if hgb < 13.0 else 0
    else: # Female
        return 1 if hgb < 12.0 else 0

def calculate_age_scores(age: int) -> tuple[int, int]:
    """
    Calculates the dual scoring rules for age.
    
    Rule 1: Overall Score Age Factor (> 75 years +5 points)
    Rule 2: AHEAD Score Age Factor (> 70 years +1 point)

    Returns: (overall_age_score, ahead_age_score)
    """
    # Rule 1: Overall Score Age Factor (> 75 years +5 points)
    overall_age_score = 5 if age > 75 else 0
    
    # Rule 2: AHEAD Score Age Factor (> 70 years +1 point)
    ahead_age_score = 1 if age > 70 else 0
    
    return overall_age_score, ahead_age_score

# --- Streamlit Interface and Calculation Logic ---

# Set page title - MODIFIED FOR PROFESSIONAL TONE
st.title("Predictive Risk Assessment for Muscle Weakness in Heart Failure")
st.markdown("---")

# --- 1. Input Section ---
st.header("📋 Data Input")

# 1. Sex - **Main Factor**
st.markdown("## 1. Sex")
gender = st.selectbox("Select Gender", ['Male', 'Female'])
# The logic must be updated to match the new selectbox values ('Male'/'Female')
gender_is_male = (gender == 'Male')

# 2. Age - **Main Factor**
st.markdown("## 2. Age")
age_input = st.number_input("Enter Patient Age (Years)", min_value=18, max_value=120, value=65, step=1)
overall_age_score, ahead_age_score = calculate_age_scores(age_input)

# 3. NYHA - **Main Factor**
st.markdown("## 3. NYHA")
st.caption("Score **+4** if NYHA is II or IV")
nyha_input = st.radio("Select NYHA Classification", ['I', 'II', 'III', 'IV'], index=0, horizontal=True, key='nyha')
nyha_score = 4 if nyha_input in ['II', 'IV'] else 0

st.markdown("---")

# 4. AHEAD SCORE (Automatic Summation) - **Main Factor**
st.markdown("## 4. AHEAD SCORE (Modified Model based on A, H, E, A, D factors)")

# AHEAD SCORE total will be displayed here (using st.empty() as a placeholder)
ahead_score_placeholder = st.empty() 

col_a, col_b = st.columns(2)

# 4-1. Af
with col_a:
    st.markdown("### 4-1. Af (Atrial Fibrillation)")
    st.caption("+1 point if Yes")
    af_input = st.radio("Has Atrial Fibrillation", ['No', 'Yes'], index=0, horizontal=True, key='af')
    # Update logic to match the new radio button values ('No'/'Yes')
    af_score = 1 if af_input == 'Yes' else 0

# 4-2. Hemoglobin
    st.markdown("### 4-2. Hemoglobin (Hb)")
    hgb_desc = f"AHEAD SCORE +1 point if Male < 13.0 g/dL or Female < 12.0 g/dL"
    st.caption(hgb_desc)
    hgb_input = st.number_input("Enter Hemoglobin Value (g/dL)", min_value=5.0, max_value=20.0, value=14.0, step=0.1, key='hgb')
    hgb_score = calculate_hgb_score(gender_is_male, hgb_input)

# 4-3. HbA1C
with col_b:
    st.markdown("### 4-3. HbA1C")
    st.caption(">= 6.5% gives AHEAD SCORE +1 point (Diabetes factor)")
    hba1c_input = st.number_input("Enter HbA1C Value (%)", min_value=4.0, max_value=15.0, value=5.5, step=0.1, key='hba1c')
    hba1c_score = 1 if hba1c_input >= 6.5 else 0

# 4-4. Creatinine (Cr)
    st.markdown("### 4-4. Creatinine (Cr)")
    st.caption("> 1.47 mg/dL gives AHEAD SCORE +1 point")
    cr_input = st.number_input("Enter Creatinine Value (mg/dL)", min_value=0.5, value=1.0, step=0.01, key='cr') 
    cr_score = 1 if cr_input > 1.47 else 0

# 5. eGFR - **Main Factor**
st.markdown("---")
st.markdown("## 5. eGFR")
st.caption("Overall Score **+2** if value is $\le 56.45$ mL/min/1.73m²")
egfr_input = st.number_input("Enter eGFR Value (mL/min/1.73m²)", min_value=10.0, max_value=150.0, value=70.0, step=0.1, key='egfr')
egfr_score = 2 if egfr_input <= 56.45 else 0

# 6. BMI - **Main Factor**
st.markdown("## 6. BMI")
st.caption("Overall Score **+1** if value is $\le 22.5$ kg/m²")
bmi_input = st.number_input("Enter BMI Value (kg/m²)", min_value=15.0, max_value=40.0, value=25.0, step=0.1, key='bmi')
bmi_score = 1 if bmi_input <= 22.5 else 0

# --- 2. Dual Score Calculation and Summation ---

# A. Calculate AHEAD SCORE total (using Age Rule: > 70 years +1 point)
AHEAD_SCORE = ahead_age_score + af_score + hgb_score + cr_score + hba1c_score

# B. Update AHEAD SCORE total display
ahead_score_placeholder.info(f"AHEAD SCORE Total: **{AHEAD_SCORE} Points** (Age Factor Contribution: {ahead_age_score} Points)")

# C. Calculate AHEAD SCORE contribution to the Overall Score
# Rule: AHEAD SCORE Total > 1.5 points gives Overall Score +3 points
ahead_overall_score = 3 if AHEAD_SCORE > 1.5 else 0

# D. Calculate the total Overall Score (OVERALL_SCORE)
OVERALL_SCORE = (
    overall_age_score     # Rule 1: Age > 75 years (+5 Points)
    + nyha_score          # NYHA II/IV (+4 Points)
    + ahead_overall_score # AHEAD Total Score > 1.5 (+3 Points)
    + egfr_score          # eGFR <= 56.45 (+2 Points)
    + bmi_score           # BMI <= 22.5 (+1 Point)
)

# --- 3. Results Presentation ---
st.markdown("---")
st.header("✨ Assessment Results")

# Risk level determination
if OVERALL_SCORE <= 6:
    risk_level_en = "Low Risk"
    color = "green"
elif 7 <= OVERALL_SCORE <= 10:
    risk_level_en = "Intermediate Risk"
    color = "orange"
else: # OVERALL_SCORE >= 11
    risk_level_en = "High Risk"
    color = "red"

# Final total score presentation 
st.metric(
    label="Total Score for Muscle Weakness Predictors", 
    value=f"{OVERALL_SCORE} Points"
)

# Risk level result presentation
st.markdown(f"This score indicates: <span style='font-size:28px; color:{color};'>**{risk_level_en}**</span>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("📊 Overall Score Breakdown")
st.markdown(f"""
| Risk Factor | Trigger Condition | Score Contribution |
| :--- | :--- | :--- |
| **2. Age** | $> 75$ Years | **{overall_age_score} Points** |
| **3. NYHA** | II or IV Classification | **{nyha_score} Points** |
| **4. AHEAD Total Score** | $> 1.5$ Points | **{ahead_overall_score} Points** |
| **5. eGFR** | $\le 56.45$ mL/min/1.73m² | **{egfr_score} Points** |
| **6. BMI** | $\le 22.5$ kg/m² | **{bmi_score} Points** |
""")
