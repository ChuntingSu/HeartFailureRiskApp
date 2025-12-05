import streamlit as st

# --- 核心計算函數區 ---

def calculate_hgb_score(gender_is_male: bool, hgb: float) -> int:
    """計算血紅蛋白 (Hemoglobin) 對 AHEAD SCORE 的分數貢獻。"""
    if gender_is_male:
        return 1 if hgb < 13.0 else 0
    else: # 女性
        return 1 if hgb < 12.0 else 0

def calculate_age_scores(age: int) -> tuple[int, int]:
    """
    計算年齡的雙重賦分規則。
    Returns: (overall_age_score, ahead_age_score)
    """
    # 規則 1: 整體分數年齡分 (大於 75 歲 +5 分)
    overall_age_score = 5 if age > 75 else 0
    
    # 規則 2: AHEAD SCORE 年齡分 (大於 70 歲 +1 分)
    ahead_age_score = 1 if age > 70 else 0
    
    return overall_age_score, ahead_age_score

# --- Streamlit 介面與計算邏輯 ---

# 設置新標題
st.title("心臟衰竭肌肉無力預測風險評估")
st.markdown("---")

# 初始化最終總分 (Overall Score)
OVERALL_SCORE = 0

# --- 1. 輸入區塊 ---
st.header("📋 數據輸入")

# 1. 性別 (Sex) - **主項目**
st.markdown("## 1. 性別")
gender = st.selectbox("請選擇性別", ['男性 (Male)', '女性 (Female)'])
gender_is_male = (gender == '男性 (Male)')

# 2. Age (年齡) - **主項目**
st.markdown("## 2. 年紀")
age_input = st.number_input("請輸入患者年齡 (歲)", min_value=18, max_value=120, value=65, step=1)
overall_age_score, ahead_age_score = calculate_age_scores(age_input)

# 3. NYHA - **主項目**
st.markdown("## 3. NYHA")
st.caption("II 或 IV 則整體分數 **+4分**")
nyha_input = st.radio("請選擇 NYHA 分級", ['I', 'II', 'III', 'IV'], index=0, horizontal=True, key='nyha')
nyha_score = 4 if nyha_input in ['II', 'IV'] else 0

st.markdown("---")

# 4. AHEAD SCORE (自動加總分數) - **主項目**
st.markdown("## 4. AHEAD SCORE")

# AHEAD SCORE 總分將在這裡自動呈現
ahead_score_placeholder = st.empty() 

col_a, col_b = st.columns(2)

# 4-1. Af
with col_a:
    st.markdown("### 4-1. Af (心房顫動)")
    st.caption("是則 AHEAD SCORE +1分")
    af_input = st.radio("是否患有心房顫動", ['否', '是'], index=0, horizontal=True, key='af')
    af_score = 1 if af_input == '是' else 0

# 4-2. Hemoglobin
    st.markdown("### 4-2. Hemoglobin (Hb)")
    hgb_desc = f"男性 < 13.0 g/dL 或 女性 < 12.0 g/dL 則 AHEAD SCORE +1分"
    st.caption(hgb_desc)
    hgb_input = st.number_input("請輸入血紅蛋白數值 (g/dL)", min_value=5.0, max_value=20.0, value=14.0, step=0.1, key='hgb')
    hgb_score = calculate_hgb_score(gender_is_male, hgb_input)

# 4-3. HbA1C
with col_b:
    st.markdown("### 4-3. HbA1C")
    st.caption(">= 6.5% 則 AHEAD SCORE +1分 (糖尿病)")
    hba1c_input = st.number_input("請輸入 HbA1C 數值 (%)", min_value=4.0, max_value=15.0, value=5.5, step=0.1, key='hba1c')
    hba1c_score = 1 if hba1c_input >= 6.5 else 0

# 4-4. Creatinine (Cr)
    st.markdown("### 4-4. Creatinine (Cr)")
    st.caption("> 1.47 mg/dL 則 AHEAD SCORE +1分")
    # Creatinine 移除 max_value 限制
    cr_input = st.number_input("請輸入 Creatinine 數值 (mg/dL)", min_value=0.5, value=1.0, step=0.01, key='cr') 
    cr_score = 1 if cr_input > 1.47 else 0

# 5. eGFR - **主項目** (重新排序為 5)
st.markdown("---")
st.markdown("## 5. eGFR")
st.caption("小於或等於 56.45 mL/min/1.73m²，則整體分數 **+2分**")
egfr_input = st.number_input("請輸入 eGFR 數值 (mL/min/1.73m²)", min_value=10.0, max_value=150.0, value=70.0, step=0.1, key='egfr')
egfr_score = 2 if egfr_input <= 56.45 else 0

# 6. BMI - **主項目** (重新排序為 6)
st.markdown("## 6. BMI")
st.caption("小於或等於 22.5 kg/m²，則整體分數 **+1分**")
bmi_input = st.number_input("請輸入 BMI 數值 (kg/m²)", min_value=15.0, max_value=40.0, value=25.0, step=0.1, key='bmi')
bmi_score = 1 if bmi_input <= 22.5 else 0

# --- 2. 雙重分數計算與加總 ---

# A. 計算 AHEAD SCORE 總分 (使用年齡規則: > 70歲 +1分)
AHEAD_SCORE = ahead_age_score + af_score + hgb_score + cr_score + hba1c_score

# B. 在這裡更新 AHEAD SCORE 總分顯示
ahead_score_placeholder.info(f"AHEAD SCORE 總分自動加總結果為: **{AHEAD_SCORE} 分**")

# C. 根據 AHEAD SCORE 總分計算其對整體分數的貢獻
# 規則: AHEAD SCORE 總分 > 1.5分 則整體分數 +3分
ahead_overall_score = 3 if AHEAD_SCORE > 1.5 else 0

# D. 計算整體分數 (OVERALL_SCORE) 總和
OVERALL_SCORE = (
    overall_age_score   
    + nyha_score        
    + ahead_overall_score 
    + egfr_score        
    + bmi_score         
)

# --- 3. 結果呈現區 ---
st.markdown("---")
st.header("✨ 評估結果")

# 風險分級判斷
if OVERALL_SCORE <= 6:
    risk_level_zh = "低風險 (Low Risk)"
    color = "green"
elif 7 <= OVERALL_SCORE <= 10:
    risk_level_zh = "中等風險 (Intermediate Risk)"
    color = "orange"
else: # OVERALL_SCORE >= 11
    risk_level_zh = "高風險 (High Risk)"
    color = "red"

# 最終總分呈現 (符合要求格式)
st.metric(
    label="你的肌肉無力預測因子總分為", 
    value=f"{OVERALL_SCORE} 分"
)

# 風險分級結果呈現
st.markdown(f"該分數屬於: <span style='font-size:28px; color:{color};'>**{risk_level_zh}**</span>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("💡 整體分數構成明細")
st.markdown(f"""
| 獨立風險因子 | 觸發條件 | 分數貢獻 |
| :--- | :--- | :--- |
| **2. 年紀** | $> 75$ 歲 | **{overall_age_score} 分** |
| **3. NYHA** | II 或 IV 級 | **{nyha_score} 分** |
| **4. AHEAD 總分判斷** | $> 1.5$ 分 | **{ahead_overall_score} 分** |
| **5. eGFR** | $\le 56.45$ mL/min/1.73m² | **{egfr_score} 分** |
| **6. BMI** | $\le 22.5$ kg/m² | **{bmi_score} 分** |
""")
