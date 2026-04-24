import streamlit as st
import pandas as pd

# --- 1. 核心計算函數區 ---
def calculate_detailed_scores(age, nyha, hb, egfr, bmi):
    details = []
    
    # 1. NYHA 分級 (基準 I/II 為 0)
    nyha_score = 0
    if nyha == 'IV': nyha_score = 18
    elif nyha == 'III': nyha_score = 9
    details.append({'臨床變項': '2. NYHA 活動分級', '判定狀況': f'Class {nyha}', '獲得分數': nyha_score})
        
    # 2. 年齡
    age_score = 11 if age > 75.5 else 0
    details.append({'臨床變項': '1. 年齡 (Age)', '判定狀況': '> 75.5 歲' if age > 75.5 else '≤ 75.5 歲', '獲得分數': age_score})
        
    # 3. 血紅素
    hb_score = 5 if hb <= 11.55 else 0
    details.append({'臨床變項': '3. 血紅素 (Hb)', '判定狀況': '≤ 11.55 g/dL' if hb <= 11.55 else '> 11.55 g/dL', '獲得分數': hb_score})
        
    # 4. eGFR
    egfr_score = 1 if egfr <= 74.65 else 0
    details.append({'臨床變項': '4. 估算腎絲球過濾率 (eGFR)', '判定狀況': '≤ 74.65' if egfr <= 74.65 else '> 74.65', '獲得分數': egfr_score})

    # 5. BMI
    bmi_score = 5 if bmi <= 22.5 else 0
    details.append({'臨床變項': '5. 身體質量指數 (BMI)', '判定狀況': '≤ 22.5 kg/m²' if bmi <= 22.5 else '> 22.5 kg/m²', '獲得分數': bmi_score})
        
    total_score = sum(d['獲得分數'] for d in details)
    return total_score, details

# --- Streamlit 介面配置 ---
st.set_page_config(page_title="Muscle Call 風險預測系統", layout="centered")
st.title("心力叫瘁（Muscle Call）風險預測系統")
st.markdown("---")

# --- 2. 數據輸入區 ---
st.header("📋 臨床數據輸入")
age_input = st.number_input("1. 請輸入患者年齡 (歲)", min_value=1.0, max_value=120.0, value=65.0, step=0.1)
nyha_input = st.radio("2. 美國紐約心臟病學會 (NYHA) 活動分級", ['I', 'II', 'III', 'IV'], index=1, horizontal=True)
hb_input = st.number_input("3. 請輸入血紅素數值 (Hb, g/dL)", min_value=1.0, max_value=25.0, value=13.0, step=0.1)
egfr_input = st.number_input("4. 估算腎絲球過濾率 (eGFR, mL/min/1.73m²)", min_value=1.0, max_value=200.0, value=75.0, step=0.1)
bmi_input = st.number_input("5. 請輸入 BMI 數值 (kg/m²)", min_value=5.0, max_value=60.0, value=24.0, step=0.1)

# --- 3. 計算結果 ---
total_score, score_details = calculate_detailed_scores(age_input, nyha_input, hb_input, egfr_input, bmi_input)

# ROC 切點 (請根據您跑出來的結果修改)
CUTOFF_LOW_MOD = 10.0  
CUTOFF_MOD_HIGH = 25.0 

# --- 4. 結果呈現區 ---
st.markdown("---")
st.header("✨ 評估結果呈現")

if total_score < CUTOFF_LOW_MOD:
    risk_level, color, bg_color = "🟢 低風險 (Low Risk)", "#28a745", "#e8f5e9"
    msg_type = "success"
elif total_score < CUTOFF_MOD_HIGH:
    risk_level, color, bg_color = "🟡 中等風險 (Intermediate Risk)", "#fd7e14", "#fff3e0"
    msg_type = "warning"
else:
    risk_level, color, bg_color = "🔴 高風險 (High Risk)", "#dc3545", "#fdecea"
    msg_type = "error"

st.markdown(f"""
<div style="background-color:{bg_color}; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid {color};">
    <h2 style="color:{color}; margin:0;">{risk_level}</h2>
    <p style="font-size:24px; color:#333; margin:10px 0 0 0;">總評估分數：<b>{total_score}</b> / 50</p>
</div>
""", unsafe_allow_html=True)

# --- 5. 互動式臨床建議 (新增區塊) ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📌 查看專業臨床介入建議", expanded=True):
    if total_score < CUTOFF_LOW_MOD:
        st.success("**【建議方針：預防與衛教】**")
        st.write("* **體能維持：** 鼓勵進行中等強度的有氧運動（如快走）。")
        st.write("* **營養追蹤：** 維持均衡飲食，特別注意蛋白質攝取。")
        st.write("* **定期追蹤：** 建議每 6-12 個月重新評估一次 Muscle Call 分數。")
    elif total_score < CUTOFF_MOD_HIGH:
        st.warning("**【建議方針：早期干預與監測】**")
        st.write("* **運動處方：** 建議由物理治療師評估，加入輕度阻力訓練以防止肌肉流失。")
        st.write("* **營養支持：** 評估是否需要補充支鏈胺基酸 (BCAA) 或維生素 D。")
        st.write("* **共病管理：** 嚴密監控貧血 (Hb) 與腎功能 (eGFR) 惡化狀況。")
    else:
        st.error("**【建議方針：積極醫療介入】**")
        st.write("* **醫療會診：** 建議立即照會心臟復健科與營養師。")
        st.write("* **生活調整：** 評估日常生活活動度 (ADL) 受損狀況，預防跌倒風險。")
        st.write("* **心衰優化：** 調整心衰藥物 (GDMT) 以改善 NYHA 分級狀況。")

# --- 6. 分數明細表 ---
st.markdown("### 📝 各變項得分明細")
st.table(pd.DataFrame(score_details))

# --- 7. 頁尾 ---
st.markdown(f"""
<div style="position: fixed; bottom: 0; left: 0; width: 100%; background-color: #f0f2f6; 
            padding: 10px 0; text-align: center; font-size: 0.8em; color: #4f4f4f; border-top: 1px solid #ddd;">
    Copyright© 2026 ChuntingSu. All Rights Reserved.
</div>
""", unsafe_allow_html=True)
