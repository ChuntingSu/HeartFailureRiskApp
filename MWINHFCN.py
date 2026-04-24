import streamlit as st
import pandas as pd

# --- 1. 核心計算函數區 (回傳總分與各分項明細) ---

def calculate_detailed_scores(age, nyha, hb, egfr, bmi):
    """計算總分並回傳各項貢獻分數"""
    details = {}
    
    # 1. NYHA 分級權重 (基準 I/II 為 0)
    if nyha == 'IV': 
        details['NYHA 活動分級'] = 18
    elif nyha == 'III': 
        details['NYHA 活動分級'] = 9
    else:
        details['NYHA 活動分級'] = 0
        
    # 2. 年齡 (Age > 75.5)
    details['年齡'] = 11 if age > 75.5 else 0
        
    # 3. 血紅素 (Hb <= 11.55)
    details['血紅素'] = 5 if hb <= 11.55 else 0
        
    # 4. 身體質量指數 (BMI <= 22.5)
    details['身體質量指數'] = 5 if bmi <= 22.5 else 0
        
    # 5. 腎絲球過濾率 (eGFR <= 74.65)
    details['腎絲球過濾率'] = 1 if egfr <= 74.65 else 0
        
    total_score = sum(details.values())
    return total_score, details

# --- Streamlit 介面配置 ---

st.set_page_config(page_title="Muscle Call 風險預測系統", layout="centered")
st.title("心力叫瘁（Muscle Call）風險預測系統")
st.markdown("---")

# --- 2. 數據輸入區 ---
st.header("📋 臨床數據輸入")

# 依照您的要求調整順序與名稱
# 1. 年齡
st.markdown("### 1. 年齡 (Age)")
age_input = st.number_input("請輸入患者年齡 (歲)", min_value=1.0, max_value=120.0, value=65.0, step=0.1)

# 2. NYHA
st.markdown("### 2. 美國紐約心臟病學會 (New York Heart Association, NYHA) 活動分級")
nyha_input = st.radio("請選擇分級", ['I', 'II', 'III', 'IV'], index=1, horizontal=True)
st.caption("註：系統將 I 級與 II 級視為初步風險基準 (0分)。")

# 3. Hb
st.markdown("### 3. 血紅素 (Hemoglobin, Hb)")
hb_input = st.number_input("請輸入血紅素數值 (g/dL)", min_value=1.0, max_value=25.0, value=13.0, step=0.1)

# 4. eGFR
st.markdown("### 4. 估算腎絲球過濾率 (estimated glomerular filtration rate, eGFR)")
egfr_input = st.number_input("請輸入 eGFR 數值 (mL/min/1.73m²)", min_value=1.0, max_value=200.0, value=75.0, step=0.1)

# 5. BMI
st.markdown("### 5. 身體質量指數 (body mass index, BMI)")
bmi_input = st.number_input("請輸入 BMI 數值 (kg/m²)", min_value=5.0, max_value=60.0, value=24.0, step=0.1)

# --- 3. 計算結果 ---
total_score, score_details = calculate_detailed_scores(age_input, nyha_input, hb_input, egfr_input, bmi_input)

# 設定 ROC 切點 (請根據您跑出來的結果修改這兩個數值)
CUTOFF_LOW_MOD = 10.0  
CUTOFF_MOD_HIGH = 25.0 

# --- 4. 結果呈現區 ---
st.markdown("---")
st.header("✨ 評估結果呈現")

# 顯示總分
col_score, col_status = st.columns([1, 2])
with col_score:
    st.metric(label="最終評估總分", value=f"{total_score} / 50")

# 判斷風險等級
if total_score < CUTOFF_LOW_MOD:
    risk_level, color, bg_color = "低風險 (Low Risk)", "#28a745", "#e8f5e9"
    advice = "患者指標相對穩定，建議維持現有追蹤。"
elif total_score < CUTOFF_MOD_HIGH:
    risk_level, color, bg_color = "中等風險 (Intermediate Risk)", "#fd7e14", "#fff3e0"
    advice = "患者存在潛在風險，建議加強營養與肌力監測。"
else:
    risk_level, color, bg_color = "高風險 (High Risk)", "#dc3545", "#fdecea"
    advice = "【高度警示】建議儘速進行臨床介入與復健評估。"

with col_status:
    st.markdown(f"""
    <div style="background-color:{bg_color}; padding: 15px; border-radius: 10px; border-left: 5px solid {color};">
        <h3 style="color:{color}; margin:0;">{risk_level}</h3>
        <p style="margin:5px 0 0 0;">{advice}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. 顯示各變項貢獻分數 (橫向長條圖) ---
st.markdown("### 📊 各變項風險權重貢獻")
df_details = pd.DataFrame({
    '臨床變項': list(score_details.keys()),
    '貢獻分數': list(score_details.values())
})

# 使用 Streamlit 原生長條圖顯示
st.bar_chart(df_details.set_index('臨床變項'))

# 使用表格呈現精確明細
with st.expander("檢視詳細分數明細表"):
    st.table(df_details)

# --- 6. 頁尾版權 ---
st.markdown(f"""
<div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #f0f2f6; 
            padding: 10px 0; text-align: center; font-size: 0.8em; color: #4f4f4f; border-top: 1px solid #ddd;">
    Copyright© 2026 ChuntingSu. All Rights Reserved.
</div>
""", unsafe_allow_html=True)
