# 🚒 香港消防處服務儀表板

一個Streamlit應用程序，用於顯示和分析香港消防處的救護站和消防局數據。

## 📊 功能特色

### 1. 交互式地圖
- 顯示所有救護站（藍色標記）和消防局（紅色標記）的位置
- 點擊標記查看詳細信息
- 可縮放和拖動地圖

### 2. 數據可視化
- 各地區救護站和消防局數量分布圖表
- 實時統計摘要
- 響應式數據表格

### 3. 數據過濾和搜索
- 按地區過濾
- 按名稱或地址搜索
- 實時數據更新

### 4. 數據導出
- 下載CSV格式的數據
- 支持中文編碼

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 運行應用
```bash
streamlit run app.py
```

### 訪問應用
打開瀏覽器訪問：http://localhost:8501

## 📁 項目結構

```
hk_fire_services_dashboard/
├── app.py              # 主應用程序
├── requirements.txt    # Python依賴
├── README.md          # 項目文檔
├── .env.example       # 環境變量示例
└── setup.sh           # 一鍵安裝腳本
```

## 🔧 技術架構

### 後端技術
- **Streamlit** - 交互式Web應用框架
- **Pandas** - 數據處理和分析
- **GeoPandas** - 地理空間數據處理
- **Plotly** - 交互式圖表
- **Folium** - 交互式地圖

### 數據源
- **救護站API**: `https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634799003993_7633/MapServer/WFSServer`
- **消防局API**: `https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634798867463_89696/MapServer/WFSServer`

### 數據緩存
- 使用Streamlit緩存機制
- 數據每小時自動更新
- 手動刷新按鈕

## 📈 數據字段

### 救護站數據
- ID: 唯一標識符
- 消防處編號: FSDID
- 名稱: 中文名稱
- 英文名稱: 英文名稱
- 地址: 中文地址
- 英文地址: 英文地址
- 地區: 所屬地區
- 電話: 聯繫電話
- 緯度/經度: 地理坐標

### 消防局數據
- ID: 唯一標識符
- 消防處編號: FSDID
- 名稱: 中文名稱
- 英文名稱: 英文名稱
- 地址: 中文地址
- 英文地址: 英文地址
- 地區: 所屬地區
- 電話: 聯繫電話
- 緯度/經度: 地理坐標

## 🎯 使用場景

### 1. 應急服務規劃
- 分析服務覆蓋範圍
- 識別服務空白區域
- 優化資源分配

### 2. 公共安全研究
- 研究服務分布模式
- 分析地區服務密度
- 評估應急響應能力

### 3. 市民信息查詢
- 查找最近的救護站/消防局
- 獲取聯繫方式
- 了解服務範圍

## 🚢 部署選項

### 1. 本地開發
```bash
streamlit run app.py
```

### 2. Docker部署
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3. Streamlit Cloud部署
1. 上傳到GitHub
2. 訪問 https://streamlit.io/cloud
3. 連接GitHub倉庫
4. 自動部署

### 4. 其他雲平台
- **Heroku**、**AWS**、**Google Cloud**、**Azure**
- 支持容器化部署
- 自動擴展配置

## 🔐 安全考慮

### 數據安全
- API數據公開可用
- 不存儲敏感信息
- 使用HTTPS連接

### 應用安全
- 輸入驗證
- 錯誤處理
- 日誌記錄

## 📱 響應式設計

- 支持桌面和移動設備
- 自適應布局
- 觸摸友好的界面

## 🔄 更新計劃

### 短期計劃
- [ ] 添加實時交通數據
- [ ] 集成天氣信息
- [ ] 添加路線規劃功能

### 長期計劃
- [ ] 歷史數據分析
- [ ] 預測模型
- [ ] 多語言支持

## 🤝 貢獻指南

1. Fork項目
2. 創建功能分支
3. 提交更改
4. 創建Pull Request

## 📄 許可證

MIT License

## 📞 聯繫方式

如有問題或建議，請提交Issue或Pull Request。

## 🙏 致謝

- 香港政府地理數據平台
- Streamlit開發團隊
- 開源社區貢獻者