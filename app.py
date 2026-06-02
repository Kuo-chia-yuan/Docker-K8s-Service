import logging
import os
import random
import time
import asyncio
import pandas as pd
import streamlit as st
import httpx
import plotly.express as px
from fastapi import FastAPI
from pydantic import BaseModel

# ==========================================
# FastAPI 後端邏輯
# ==========================================
MODEL_VERSION = "v1.0.0"
app = FastAPI()

class WaferPredictResponse(BaseModel):
    model_version: str
    defect_score: float
    status: str
    inference_time_ms: float

# 修改 app.py 中的 predict_wafer 函數
@app.post("/predict", response_model=WaferPredictResponse)
async def predict_wafer():
    start_time = time.perf_counter()
    score = random.random()  # 產生 0.0 到 1.0 的數值
    
    # 【正確邏輯】：
    # 讓 95% 的機率是 Pass，5% 是 Defect
    # 如果 score 大於等於 0.05，標記為 Pass (95% 機率)
    # 如果 score 小於 0.05，標記為 Defect (5% 機率)
    is_defect = score < 0.05 
    
    response = WaferPredictResponse(
        model_version=MODEL_VERSION,
        defect_score=round(score, 4),
        status="Pass" if not is_defect else "Defect", # 確保 95% 為 Pass
        inference_time_ms=round((time.perf_counter() - start_time) * 1000, 2)
    )
    return response

# ==========================================
# Streamlit 前端邏輯
# ==========================================
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    if "history" not in st.session_state: st.session_state.history = []

    st.title("🏭 模擬晶圓廠 AI 推論戰情室")
    col1, col2 = st.columns([1, 2])

    with col1:
        concurrent_count = st.slider("🚀 併發檢測片數", 1, 500, 10)
        
        async def fetch(client, i):
            try:
                # 直接指向 NodePort 30001
                resp = await client.post("http://localhost:30001/predict", timeout=5.0)
                if resp.status_code == 200:
                    data = resp.json()
                    data.update({"timestamp": time.strftime("%H:%M:%S")})
                    return data
            except: return None

        if st.button("🔥 啟動併發壓力測試", type="primary"):
            async def run():
                async with httpx.AsyncClient() as client:
                    tasks = [fetch(client, i) for i in range(concurrent_count)]
                    return [r for r in await asyncio.gather(*tasks) if r]
            
            with st.spinner("K8s 負載平衡中..."):
                results = asyncio.run(run())
                st.session_state.history.extend(results)
            st.rerun()

    with col2:
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.metric("總檢測數", len(df))
            st.line_chart(df.set_index("timestamp")["defect_score"])
            st.dataframe(df.tail(10))
        else:
            st.info("目前產線靜止中。")