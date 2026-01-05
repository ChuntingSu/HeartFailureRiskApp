import streamlit as st

# --- 核心計算函數區 ---

def calculate_age_scores(age: int) -> tuple[int, int]:
    """規則: 年齡的雙重賦分"""
    # 1. Overall Risk Score 規則: 大於 75 歲加 10 分
    overall_age_score = 10 if age > 75 else 0
    # 2. AHEAD SCORE 規則: 大於 70 歲加 1 分
    ahead_age_score = 1 if age > 70 else 0
    return overall_age_score, ahead_age_score

def calculate_hgb_ahead_score(gender_is_male: bool, hgb: float) -> int:
    """規則: AHEAD SCORE 的 Hb 賦分規則 (男<13/女<12)"""
    if gender_is_male:
        return 1 if hgb < 13.0 else 0
    else: # 女性
        return 1 if hgb < 12.0 else 0

# --- Streamlit 介面與計算邏輯 ---

st.set_page_config(page_title="心力叫瘁風險預測系統", layout="centered")
st.title("心力叫瘁（Muscle Call in Heart Failure）風險預測系統")
st.markdown("---")

# --- 1. 數據輸入區 ---
st.header("📋 數據輸入")

# 1. 性別
st.markdown("## 1. 性別")
gender = st.selectbox("請選擇性別", ['男性 (Male)', '女性 (Female)'])
gender_is_male = (gender == '男性 (Male)')

# 2. 年紀
st.markdown("## 2. 年紀")
st.markdown("""
<style> .custom-caption { font-size: 0.85rem; color: #666; margin-bottom: 2px; } </style>
<div class="custom-caption">1. <b>Overall Score:</b> > 75 歲 加 <b>10分</b></div>
<div class="custom-caption">2. <b>AHEAD Score:</b> > 70 歲 加 <b>1分</b></div>
""", unsafe_allow_html=True)
age_input = st.number_input("請輸入患者年齡 (歲)", min_value=1, max_value=120, value=65, step=1)
overall_age_score, ahead_age_score = calculate_age_scores(age_input)

# 3. NYHA
st.markdown("## 3. NYHA")
st.caption("II 級 **+7分** / IV 級 **+3分**")
nyha_input = st.radio("請選擇 NYHA 分級", ['I', 'II', 'III', 'IV'], index=0, horizontal=True, key='nyha')

if nyha_input == 'II':
    nyha_score = 7
elif nyha_input == 'IV':
    nyha_score = 3
else:
    nyha_score = 0

st.markdown("---")

# 4. AHEAD SCORE & HB 雙重規則
st.markdown("## 4. AHEAD SCORE & 檢驗數值")
ahead_score_placeholder = st.empty() 

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### 4-1. Af (心房顫動)")
    af_input = st.radio("是否患有心房顫動", ['否', '是'], index=0, horizontal=True, key='af')
    af_score = 1 if af_input == '是' else 0

    st.markdown("### 4-2. Hemoglobin (Hb)")
    st.markdown("""
    <div class="custom-caption">1. <b>Overall Score:</b> Hb ≤ 15.8 加 <b>3分</b></div>
    <div class="custom-caption">2. <b>AHEAD Score:</b> 男 < 13 / 女 < 12 加 <b>1分</b></div>
    """, unsafe_allow_html=True)
    hgb_input = st.number_input("請輸入血紅蛋白數值 (g/dL)", min_value=1.0, max_value=25.0, value=14.0, step=0.1, key='hgb')
    
    hgb_ahead_contribution = calculate_hgb_ahead_score(gender_is_male, hgb_input)
    hgb_overall_score = 3 if hgb_input <= 15.8 else 0

with col_b:
    st.markdown("### 4-3. HbA1C")
    st.caption("≥ 6.5% 則 AHEAD SCORE +1分")
    hba1c_input = st.number_input("請輸入 HbA1C 數值 (%)", min_value=1.0, max_value=20.0, value=5.5, step=0.1, key='hba1c')
    hba1c_ahead_score = 1 if hba1c_input >= 6.5 else 0

    st.markdown("### 4-4. Creatinine (Cr)")
    st.caption("> 1.47 mg/dL 則 AHEAD SCORE +1分")
    cr_input = st.number_input("請輸入 Creatinine 數值 (mg/dL)", min_value=0.1, value=1.0, step=0.01, key='cr') 
    cr_ahead_score = 1 if cr_input > 1.47 else 0

# 5. eGFR
st.markdown("---")
st.markdown("## 5. eGFR")
st.caption("小於或等於 56.45 mL/min/1.73m²，則整體分數 **+4分**")
egfr_input = st.number_input("請輸入 eGFR 數值 (mL/min/1.73m²)", min_value=1.0, max_value=200.0, value=70.0, step=0.1, key='egfr')
egfr_score = 4 if egfr_input <= 56.45 else 0

# 6. BMI
st.markdown("## 6. BMI")
st.caption("小於或等於 22.5 kg/m²，則整體分數 **+2分**")
bmi_input = st.number_input("請輸入 BMI 數值 (kg/m²)", min_value=5.0, max_value=60.0, value=25.0, step=0.1, key='bmi')
bmi_score = 2 if bmi_input <= 22.5 else 0

# --- 2. 雙重分數計算與加總 ---

AHEAD_SCORE = ahead_age_score + af_score + hgb_ahead_contribution + cr_ahead_score + hba1c_ahead_score
ahead_score_placeholder.info(f"AHEAD SCORE 總分自動加總結果為: **{AHEAD_SCORE} 分**")

ahead_overall_score = 1 if AHEAD_SCORE > 1.5 else 0

OVERALL_SCORE = (
    overall_age_score    
    + nyha_score         
    + ahead_overall_score 
    + egfr_score         
    + hgb_overall_score  
    + bmi_score          
)

# --- 3. 結果呈現區 ---
st.markdown("---")
st.header("✨ 評估結果")

# 風險分級與顏色
if OVERALL_SCORE <= 10:
    risk_level_zh = "低風險 (Low Risk)"
    color = "#28a745" # Green
    risk_idx = 0
elif 11 <= OVERALL_SCORE <= 20:
    risk_level_zh = "中等風險 (Intermediate Risk)"
    color = "#fd7e14" # Orange
    risk_idx = 1
else:
    risk_level_zh = "高風險 (High Risk)"
    color = "#dc3545" # Red
    risk_idx = 2

# 使用兩欄顯示：分數與風險區段定義
res_col1, res_col2 = st.columns([1, 1])

with res_col1:
    st.metric(label="預測因子總分", value=f"{OVERALL_SCORE} 分")
    st.markdown(f"該分數屬於: <span style='font-size:24px; color:{color}; font-weight:bold;'>{risk_level_zh}</span>", unsafe_allow_html=True)

with res_col2:
    st.markdown("**風險區段定義：**")
    # 建立一個簡單的 HTML 背景色區塊來顯示區段
    st.markdown(f"""
    <div style="border-left: 5px solid #28a745; padding-left: 10px; margin-bottom: 5px; background-color: {'#e8f5e9' if risk_idx==0 else 'transparent'};">
        <b>0 - 10 分</b>：低風險
    </div>
    <div style="border-left: 5px solid #fd7e14; padding-left: 10px; margin-bottom: 5px; background-color: {'#fff3e0' if risk_idx==1 else 'transparent'};">
        <b>11 - 20 分</b>：中等風險
    </div>
    <div style="border-left: 5px solid #dc3545; padding-left: 10px; margin-bottom: 5px; background-color: {'#fdecea' if risk_idx==2 else 'transparent'};">
        <b>21 分以上</b>：高風險
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("📊 整體分數構成明細")
st.markdown(f"""
| 獨立風險因子 | 觸發條件 | 分數貢獻 |
| :--- | :--- | :--- |
| **年紀 (Overall)** | $> 75$ 歲 | **{overall_age_score} 分** |
| **NYHA** | II 級 (+7) 或 IV 級 (+3) | **{nyha_score} 分** |
| **AHEAD 總分判斷** | $> 1.5$ 分 | **{ahead_overall_score} 分** |
| **eGFR** | $\le 56.45$ | **{egfr_score} 分** |
| **HB (Overall)** | $\le 15.8$ | **{hgb_overall_score} 分** |
| **BMI** | $\le 22.5$ | **{bmi_score} 分** |
""")

# --- 頁尾版權 ---
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
