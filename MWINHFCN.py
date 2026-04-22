import streamlit as st

# --- 核心計算函數區 ---

def calculate_muscle_call_risk(age, nyha, egfr, bmi, hb):
    """根據統計權重計算總分"""
    score = 0
    # 1. NYHA IV 級
    if nyha == 'IV': score += 28140
    # 2. Age > 75.5
    if age > 75.5: score += 938
    # 3. eGFR < 56.45
    if egfr < 56.45: score += 134
    # 4. BMI <= 22.5
    if bmi <= 22.5: score += 67
    # 5. Hb < 11.5
    if hb < 11.5: score += 5
    # 6. NYHA II 級
    if nyha == 'II': score += 1
    return score

# --- Streamlit 介面與計算邏輯 ---

st.set_page_config(page_title="Muscle Call 風險預測系統", layout="centered")
st.title("心力叫瘁（Muscle Call in Heart Failure）風險預測系統")
st.markdown("本系統透過臨床指標，協助評估心臟衰竭患者肌肉無力（Muscle Weakness）之風險傾向。")
st.markdown("---")

# --- 1. 數據輸入區 ---
st.header("📋 數據輸入")

col1, col2 = st.columns(2)

with col1:
    # 1. 年齡 (Age)
    st.markdown("### 1. 年齡 (Age)")
    age_input = st.number_input("請輸入患者年齡 (歲)", min_value=1.0, max_value=120.0, value=65.0, step=0.1)

    # 2. 血紅素 (Hemoglobin; Hb)
    st.markdown("### 2. 血紅素 (Hb)")
    hgb_input = st.number_input("請輸入血紅素數值 (g/dL)", min_value=1.0, max_value=25.0, value=13.0, step=0.1)

    # 3. 身體質量指數 (BMI)
    st.markdown("### 3. 身體質量指數 (BMI)")
    bmi_input = st.number_input("請輸入 BMI 數值 (kg/m²)", min_value=5.0, max_value=60.0, value=24.0, step=0.1)

with col2:
    # 4. 估算腎絲球濾過率 (eGFR)
    st.markdown("### 4. 腎絲球濾過率 (eGFR)")
    egfr_input = st.number_input("請輸入 eGFR 數值 (mL/min/1.73m²)", min_value=1.0, max_value=200.0, value=70.0, step=0.1)

    # 5. NYHA 活動分級
    st.markdown("### 5. 心臟功能分級 (NYHA)")
    nyha_input = st.radio("請選擇 NYHA 分級", ['I', 'II', 'III', 'IV'], index=0, horizontal=True)

# --- 2. 邏輯計算 ---
total_score = calculate_muscle_call_risk(age_input, nyha_input, egfr_input, bmi_input, hgb_input)

# --- 3. 結果呈現區 ---
st.markdown("---")
st.header("✨ 評估結果")

# 根據 ROC 切點定義風險 (5.0 與 206.0)
if total_score < 5.0:
    risk_level = "低風險 (Low Risk)"
    color = "#28a745"  # 綠色
    bg_color = "#e8f5e9"
    advice = "患者目前各項生理指標相對穩定，建議維持現有運動習慣與追蹤。"
    risk_idx = 0
elif 5.0 <= total_score <= 206.0:
    risk_level = "中等風險 (Intermediate Risk)"
    color = "#fd7e14"  # 橘色
    bg_color = "#fff3e0"
    advice = "患者存在潛在肌肉無力風險（如高齡或部分生化指標異常），建議加強營養補充並在指導下進行肌力訓練。"
    risk_idx = 1
else:
    risk_level = "高風險 (High Risk)"
    color = "#dc3545"  # 紅色
    bg_color = "#fdecea"
    advice = "【高度警示】患者目前肌肉無力風險極高（通常包含 NYHA IV 級）。強烈建議儘速由專業醫療團隊進行全面評估與醫療介入。"
    risk_idx = 2

# 呈現燈號與建議
st.markdown(f"""
<div style="background-color:{bg_color}; padding: 25px; border-radius: 10px; border-left: 8px solid {color};">
    <h2 style="color:{color}; margin:0;">評估結果：{risk_level}</h2>
    <p style="font-size:18px; color:#333; margin-top:10px;"><b>建議：</b>{advice}</p>
</div>
""", unsafe_allow_html=True)

# 顯示風險區段參考 (不顯示分數數字)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("**風險燈號參考：**")
col_res1, col_res2, col_res3 = st.columns(3)
col_res1.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#28a745; color:white' if risk_idx==0 else '#f0f2f6'};'>🟢 低風險</div>", unsafe_allow_html=True)
col_res2.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#fd7e14; color:white' if risk_idx==1 else '#f0f2f6'};'>🟡 中等風險</div>", unsafe_allow_html=True)
col_res3.markdown(f"<div style='text-align:center; padding:10px; border-radius:5px; background-color:{'#dc3545; color:white' if risk_idx==2 else '#f0f2f6'};'>🔴 高風險</div>", unsafe_allow_html=True)

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
