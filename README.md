# Docker-K8s-Service

本專案是一個基於 Kubernetes (K8s) 與 Docker 的高效能晶圓瑕疵辨識推論服務。透過自動擴縮容 (HPA) 機制，確保服務能在高流量下維持穩定推論效能，並有效管理資源。

## 專案架構
* **推論引擎**: Python-based AI Inference API
* **容器化**: Docker
* **協調與調度**: Kubernetes (Deployment + Service)
* **自動化監控**: Horizontal Pod Autoscaler (HPA)

---

## 🚀 安裝與部署指南

在開始之前，請確保已安裝 [Docker](https://www.docker.com/) 與 [kubectl](https://kubernetes.io/docs/tasks/tools/)，並啟動你的 K8s 叢集 (如 KinD 或 Minikube)。

### 1. 建置 Docker Image
首先將你的程式碼封裝為容器鏡像，以便在 K8s 中部署：

```bash
# 在 Dockerfile 所在目錄執行
docker build -t mock-wafer-ai:v1 .
```

### 2. 部署服務至 Kubernetes
將定義檔套用至你的叢集。此動作會建立 Deployment, Service 以及 HPA：
```
# 部署至 K8s 叢集
kubectl apply -f k8s-deploy.yaml
```

### 3. 驗證服務狀態
確認所有組件是否正確啟動並運行：
```
# 確認 Pod 是否正常執行 (Ready 顯示 1/1)
kubectl get pods

# 確認 Service 是否已建立
kubectl get svc

# 查看 HPA 監控狀態
kubectl get hpa
```


### 4. 啟動推論服務與壓力測試
若要進行測試，請依序開啟兩個終端機視窗：
```
# 終端機 A：將本機 30001 埠導向至叢集內 80 埠
kubectl port-forward svc/wafer-ai-service 30001:80
```
```
# 終端機 B：執行模擬流量的壓力測試程式
streamlit run demo_app.py
```

## 📊 即時監控指南

為確保 AI 推論服務運作順暢，建議同時開啟兩個終端機視窗，分別進行狀態監控與資源分析。

| 監控項目 | 指令 | 說明 |
| :--- | :--- | :--- |
| **Pod 運作狀態** | `kubectl get pods` | 檢查 Pod 是否處於 `Running` 狀態，以及重啟次數。 |
| **資源消耗監控** | `kubectl top pods` | 檢查 Pod 目前的 CPU 核心數與實體記憶體佔用量。 |

### 進階：自動化監控技巧 (PowerShell)
若你想觀察「壓力測試」過程中系統資源的動態變化，可以使用以下指令讓監控畫面自動循環更新：

```powershell
# 每秒自動更新資源監控畫面
while($true) { kubectl top pods; Start-Sleep -Seconds 1; cls }
```
<img width="2880" height="1706" alt="Demo" src="https://github.com/user-attachments/assets/2446e9c4-00c0-467c-94ec-03bada4ab00a" />

## 🛠 關鍵維運指令

當你的服務部署到 Kubernetes 後，可以使用以下指令進行日常的監控與管理。

| 功能 | 指令 | 解釋 |
| :--- | :--- | :--- |
| **監控效能** | `kubectl top pods` | 查看叢集中各 Pod 的即時 CPU 與記憶體消耗。 |
| **查看即時 Log** | `stern wafer-ai` | 即時監控 Pod 推論過程的日誌輸出與錯誤紀錄。 |
| **手動擴縮容** | `kubectl scale deployment wafer-ai-deployment --replicas=n` | 手動將 Pod 數量調整為 n 個。 |
| **清除資源** | `kubectl delete -f k8s-deploy.yaml` | 根據設定檔徹底刪除所有已部署的 K8s 資源物件。 |

> **提示：** 執行 `stern` 指令前，請確保已安裝 [stern](https://github.com/stern/stern) 工具，它能同時彙整多個 Pod 的日誌輸出，非常適合偵錯 AI 推論流程。

## 📊 HPA 自動擴容設定說明
本專案採用 HorizontalPodAutoscaler (HPA) 自動化管理：

* 觸發指標: CPU 使用率。
* 邏輯: 當 CPU 使用率超過 50% 時，HPA 會根據設定進行擴容。
* 穩定機制: 設定 scaleUp 策略為每次擴增 1 個 Pod，確保資源不會瞬間過度分配。
* 資源清理: 當流量降低並維持穩定後，K8s 會自動終止冗餘 Pod 並釋放記憶體，無需手動介入。
