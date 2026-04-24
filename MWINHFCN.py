import streamlit as st

# --- 1. 核心計算函數區 (更新為 50 分制系統) ---

def calculate_muscle_call_50_score(age, nyha, egfr, bmi, hb):
    """
    根據 Framingham-style Logistic Regression 結果計算總分 (總分 50)
    基準組 (0分): NYHA I & II, Age <= 75.5, Hb > 11.55, BMI > 22.5, eGFR > 74.65
    """
    score = 0
    
    # 1. NYHA 分級權重
    if nyha == 'IV': 
        score += 18
    elif nyha == 'III': 
        score += 9
    # NYHA I 與 II 為基準組，加 0 分
    
    # 2. 年齡 (Age > 75.5)
    if age > 75.5: 
        score += 11
        
    # 3. 血紅素 (Hb <= 11.55)
    if hb <= 11.55: 
        score += 5
        
    # 4. 身體質量指數 (BMI <= 22.5)
    if bmi <= 22.5: 
        score += 5
        
    # 5. 腎功能 (eGFR <= 74.65)
    if egfr <= 74.65: 
        score += 1
        
    return score

# --- Streamlit 介面配置 ---

st.set_page_config(page_title="Muscle Call 風險預測系統 v2.0", layout="centered")
st.title("心力叫瘁（Muscle Call）風險預測系統")
st.subheader("基於 Framingham 邏輯之 50 分計分架構")
st.markdown("本系統採用邏輯斯回歸權重轉化，協助評估心衰患者之肌肉無力風險。")
st.markdown("---")

# --- 2. 數據輸入區 ---
st.header("📋 臨床數據輸入")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. 基本生理指標")
    age_input = st.number_input("患者年齡 (歲)", min_value=1.0, max_value=120.0, value=65.0, step=0.1)
    bmi_input = st.number_input("BMI 數值 (kg/m²)", min_value=5.0, max_value=60.0, value=24.0, step=0.1)
    hgb_input = st.number_input("血紅素 Hb (g/dL)", min_value=1.0, max_value=25.0, value=13.0, step=0.1)

with col2:
    st.markdown("### 2. 器官功能指標")
    egfr_input = st.number_input("eGFR (mL/min/1.73m²)", min_value=1.0, max_value=200.0, value=70.0, step=0.1)
    st.write("") # 間隔
    nyha_input = st.radio("NYHA 心功能分級", ['I', 'II', 'III', 'IV'], index=1, horizontal=True)
    st.caption("註：系統將 I 級與 II 級視為初步風險基準。")

# --- 3. 邏輯計算與切點定義 ---
# 注意：此處的切點需替換為你執行新 ROC 程式碼後得到的數值
# 假設值預估：Low/Mod ≈ 10, Mod/High ≈ 25 (請依實際跑出的結果修改下面兩行)
CUTOFF_LOW_MOD = 10.0  
CUTOFF_MOD_HIGH = 25.0 

total_score = calculate_muscle_call_50_score(age_input, nyha_input, egfr_input, bmi_input, hgb_input)

# --- 4. 結果呈現區 ---
st.markdown("---")
st.header("✨ 評估結果")

# 風險分級判斷邏輯
if total_score < CUTOFF_LOW_MOD:
    risk_level = "低風險 (Low Risk)"
    color = "#28a745"  # 綠色
    bg_color = "#e8f5e9"
    advice = "患者目前各項生理指標指標在風險門檻以下。建議維持常規追蹤與均衡營養。"
    risk_idx = 0
elif total_score < CUTOFF_MOD_HIGH:
    risk_level = "中等風險 (Intermediate Risk)"
    color = "#fd7e14"  # 橘色
    bg_color = "#fff3e0"
    advice = "患者存在部分風險因子（總分 50 分制已反映其权重）。建議進行個別化營養評估並規律監測肌力。"
    risk_idx = 1
else:
    risk_level = "高風險 (High Risk)"
    color = "#dc3545"  # 紅色
    bg_color = "#fdecea"
    advice = "【臨床高度警示】患者風險得分已達高危門檻。強烈建議儘速進行復健介入及預防衰弱治療。"
    risk_idx = 2

# 呈現得分與建議
st.markdown(f"""
<div style="background-color:{bg_color}; padding: 25px; border-radius: 10px; border-left: 8px solid {color};">
    <h2 style="color:{color}; margin:0;">評估結果：{risk_level}</h2>
    <p style="font-size:22px; color:#333; margin-top:10px;">總風險得分：<b>{total_score}</b> / 50</p>
    <p style="font-size:18px; color:#333; margin-top:5px;"><b>專業建議：</b>{advice}</p>
</div>
""", unsafe_allow_html=True)

# 風險燈號可視化
st.markdown("<br>", unsafe_allow_html=True)
col_res1, col_res2, col_res3 = st.columns(3)
col_res1.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#28a745; color:white' if risk_idx==0 else '#f0f2f6'};'>🟢 低風險</div>", unsafe_allow_html=True)
col_res2.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#fd7e14; color:white' if risk_idx==1 else '#f0f2f6'};'>🟡 中等風險</div>", unsafe_allow_html=True)
col_res3.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#dc3545; color:white' if risk_idx==2 else '#f0f2f6'};'>🔴 高風險</div>", unsafe_allow_html=True)

# --- 5. 頁尾版權 ---
copyright_text = "Copyright© 2026 ChuntingSu. All Rights Reserved."
st.markdown(f"""
<style>
.footer {{
    position: fixed; bottom: 0; left: 0; width: 100%;
    background-color: #f0f2f6; padding: 10px 0;
    text-align: center; font-size: 0.8em; color: #4f4f4f;
    border-top: 1px solid #ddd;
}}
</style>
<div class="footer">{copyright_text}</div>
""", unsafe_allow_html=True)
