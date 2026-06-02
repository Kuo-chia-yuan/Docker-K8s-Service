import streamlit as st
import httpx  # 💡 需要安裝：pip install httpx (比 requests 更強大的非同步 HTTP 客戶端)
import asyncio
import time
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Mock AI Fab")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("🏭 模擬晶圓廠 AI 自動化影像辨識")
st.write("底層架構：FastAPI + Docker + K8s")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("產線控制台")
    wafer_id = st.text_input("晶圓批號 (Base ID)", "WFR-2026-")
    
    # 👇 新增一個可以調整「併發壓力測試數量」的拉桿
    concurrent_count = st.slider("🚀 併發檢測片數 (模擬多台設備同時發送)", 1, 500, 5)
    
    # 非同步發送單一請求的函式
    async def fetch_predict(client, i):
        try:
            response = await client.post("http://localhost:30001/predict", timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                data["wafer_id"] = f"{wafer_id}{100 + i}"
                data["timestamp"] = time.strftime("%H:%M:%S")
                return data
        except Exception as e:
            return None

    # 同時觸發多個連線的核心邏輯
    async def run_stress_test():
        async with httpx.AsyncClient() as client:
            # 同時建立複數個獨立的 TCP 隧道
            tasks = [fetch_predict(client, i) for i in range(concurrent_count)]
            results = await asyncio.gather(*tasks)
            return [r for r in results if r is not None]

    if st.button("🔥 啟動併發壓力測試", type="primary"):
        with st.spinner("K8s 負載平衡器全面分流中..."):
            # 執行非同步併發
            valid_results = asyncio.run(run_stress_test())
            
            if valid_results:
                st.session_state.history.extend(valid_results)
                st.success(f"⚡ 成功透過 K8s 負載平衡完成 {len(valid_results)} 筆晶圓並行推論！")
            else:
                st.error("連線 K8s 叢集失敗")

with col2:
    st.header("📊 即時統計與維運監控")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        # 1. 核心修改：計算每一時間點的良率 (Groupby)
        # 我們將資料按時間分組，計算該批次的良率
        df_stats = df.groupby('timestamp').apply(
            lambda x: (len(x[x['status'] == 'Pass']) / len(x)) * 100
        ).reset_index(name='yield_rate')

        # 2. 顯示總體指標
        total = len(df)
        defects = len(df[df["status"] == "Defect"])
        passes = total - defects 
        
        m1, m2 = st.columns(2)
        m1.metric("總檢測片數", total)
        m2.metric("不良率 (Defect Rate)", f"{(defects/total)*100:.1f}%")
        st.metric("當前良率 (Yield)", f"{(passes/total)*100:.1f}%")
        
        # 3. 修改圖表：Y 軸改為 yield_rate
        fig = px.line(df_stats, x="timestamp", y="yield_rate", 
                      title="產線即時良率趨勢圖 (Yield Rate)", markers=True)
        
        # Y軸設定為 0 到 105%
        fig.update_yaxes(range=[0, 105])
        
        # 加入 95% 良率門檻線
        fig.add_hline(y=95, line_dash="dash", line_color="red", 
                      annotation_text="目標良率 (95%)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 負載平衡分流日誌 (K8s Service Logs)")
        st.dataframe(df.tail(10))
    else:
        st.info("目前產線靜止中。")