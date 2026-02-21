# 🚒 香港消防處服務查看器 - 超簡單版本

一個完全無需安裝任何額外依賴嘅Python Web應用，顯示香港消防處救護站和消防局數據。

## 🎯 特點

### ✅ 零依賴
- **只需Python 3** - 無需安裝任何額外包
- **內置HTTP服務器** - 使用Python標準庫
- **無需配置** - 下載即用

### ✅ 完整功能
- **實時數據** - 從香港政府API獲取最新數據
- **統計顯示** - 救護站和消防局數量
- **列表查看** - 顯示所有服務點信息
- **自動更新** - 每小時自動更新數據

### ✅ 簡單易用
- **一鍵啟動** - 只需運行一個Python文件
- **跨平台** - Windows、Mac、Linux都支持
- **響應式設計** - 支持手機和電腦瀏覽

## 🚀 快速開始

### 方法1：直接運行（最簡單）
```bash
# 下載文件
git clone https://github.com/maxwoo-openclaw/hk-fire-services-dashboard.git
cd hk-fire-services-dashboard

# 運行應用
python3 run_simple.py
```

### 方法2：使用Streamlit版本（需要安裝）
```bash
# 安裝依賴
pip install streamlit pandas requests

# 運行Streamlit應用
streamlit run simple_app.py
```

### 方法3：使用完整版本（功能最全）
```bash
# 安裝所有依賴
pip install -r requirements.txt

# 運行完整應用
streamlit run app.py
```

## 📊 數據顯示

### 1. 統計摘要
- 救護站總數
- 消防局總數
- 各地區分布

### 2. 詳細列表
- 救護站名稱、地址、地區、電話
- 消防局名稱、地址、地區、電話
- 地圖鏈接（Google Maps）

### 3. 搜索功能
- 按名稱搜索
- 按地址搜索
- 按地區過濾

## 🔗 API數據源

### 救護站數據
```
https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634799003993_7633/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=AmbDepots&outputFormat=geojson
```

### 消防局數據
```
https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634798867463_89696/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=FireStations&outputFormat=geojson
```

## 📁 文件說明

### 主要文件
- **`run_simple.py`** - 超簡單版本（推薦）
- **`simple_app.py`** - Streamlit簡化版本
- **`app.py`** - Streamlit完整版本

### 輔助文件
- **`test_api.py`** - API測試工具
- **`requirements.txt`** - Python依賴包列表
- **`simple_requirements.txt`** - 簡化依賴列表

## 🖥️ 運行示例

### 啟動服務器
```bash
$ python3 run_simple.py
==================================================
香港消防處服務查看器
==================================================
[02:22:19] 正在更新數據...
[02:22:19] 數據更新完成
服務器已啟動: http://localhost:8000
按 Ctrl+C 停止
```

### 訪問應用
打開瀏覽器訪問：http://localhost:8000

### 頁面顯示
```
🚒 香港消防處服務查看器
最後更新: 2026-02-22 02:22:19

📊 統計
救護站: 45個
消防局: 95個

📋 救護站列表
1. 香港仔救護站 - 南區 - 2541 6644
2. 寶馬山救護站 - 東區 - 2562 1234
...

📋 消防局列表
1. 香港仔消防局 - 南區 - 2552 5280
2. 機場南消防局 - 離島區 - 2186 9111
...
```

## 🔧 技術實現

### 超簡單版本 (`run_simple.py`)
- **Python標準庫**: `http.server`, `socketserver`, `json`, `urllib`
- **無外部依賴**: 完全使用內置庫
- **輕量級**: 代碼不到100行

### Streamlit版本 (`simple_app.py`)
- **Streamlit**: 現代化Web應用框架
- **Pandas**: 數據處理
- **Requests**: HTTP請求

### 完整版本 (`app.py`)
- **完整功能**: 地圖、圖表、搜索、過濾
- **生產就緒**: 錯誤處理、緩存、日誌
- **企業級**: 用戶管理、數據導出

## 🚢 部署選項

### 1. 本地運行（最簡單）
```bash
python3 run_simple.py
```

### 2. 後台運行
```bash
# Linux/Mac
nohup python3 run_simple.py > server.log 2>&1 &

# Windows
start python run_simple.py
```

### 3. Docker部署
```dockerfile
FROM python:3.9-alpine
COPY run_simple.py .
EXPOSE 8000
CMD ["python", "run_simple.py"]
```

### 4. 雲服務器
```bash
# SSH到服務器
ssh user@server

# 下載代碼
git clone https://github.com/maxwoo-openclaw/hk-fire-services-dashboard.git
cd hk-fire-services-dashboard

# 後台運行
nohup python3 run_simple.py > /var/log/fire-services.log 2>&1 &
```

## 📱 移動端訪問

### 手機瀏覽
- 確保電腦和手機在同一網絡
- 查找電腦的IP地址
- 手機瀏覽器訪問：http://電腦IP:8000

### 示例
```
電腦IP: 192.168.1.100
手機訪問: http://192.168.1.100:8000
```

## 🔄 數據更新

### 自動更新
- 應用每小時自動更新數據
- 無需手動操作
- 確保數據最新

### 手動更新
```bash
# 停止服務器
Ctrl+C

# 重新啟動
python3 run_simple.py
```

## 🛠️ 故障排除

### 問題1：端口被佔用
```bash
# 更改端口
python3 run_simple.py --port 8080
# 或
python3 run_simple.py 8080
```

### 問題2：API連接失敗
- 檢查網絡連接
- 確認API地址可訪問
- 等待幾分鐘後重試

### 問題3：頁面無法加載
- 確認服務器正在運行
- 檢查防火牆設置
- 嘗試其他瀏覽器

## 📈 數據示例

### 救護站數據
```json
{
  "name": "香港仔救護站",
  "address": "香港仔南風道1號",
  "district": "南區",
  "phone": "2541 6644",
  "lat": 22.25036991,
  "lng": 114.17386696
}
```

### 消防局數據
```json
{
  "name": "香港仔消防局",
  "address": "香港香港仔南風道1號",
  "district": "南區",
  "phone": "2552 5280",
  "lat": 22.25036991,
  "lng": 114.17386696
}
```

## 🤝 貢獻

歡迎提交問題和改進建議！

## 📄 許可證

MIT License

## 📞 聯繫

如有問題，請提交GitHub Issue。

---

**立即開始使用：**
```bash
git clone https://github.com/maxwoo-openclaw/hk-fire-services-dashboard.git
cd hk-fire-services-dashboard
python3 run_simple.py
```

打開瀏覽器訪問：http://localhost:8000