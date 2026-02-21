#!/bin/bash

# 香港消防處服務儀表板 - 安裝腳本

set -e

echo "========================================="
echo "  香港消防處服務儀表板 - 安裝腳本"
echo "========================================="
echo ""

# 檢查Python版本
echo "🔍 檢查Python版本..."
python3 --version || {
    echo "❌ 請安裝Python 3.7或更高版本"
    exit 1
}

# 檢查pip
echo "🔍 檢查pip..."
python3 -m pip --version || {
    echo "❌ 請安裝pip"
    exit 1
}

# 創建虛擬環境
echo "🔧 創建虛擬環境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虛擬環境創建成功"
else
    echo "✅ 虛擬環境已存在"
fi

# 激活虛擬環境
echo "🔧 激活虛擬環境..."
source venv/bin/activate

# 升級pip
echo "📦 升級pip..."
python3 -m pip install --upgrade pip

# 安裝依賴
echo "📦 安裝依賴包..."
python3 -m pip install -r requirements.txt

# 創建環境變量文件
echo "⚙️  創建環境配置..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已創建 .env 文件"
        echo "⚠️  請編輯 .env 文件設置你的配置"
    else
        echo "⚠️  找不到 .env.example 文件"
    fi
else
    echo "✅ .env 文件已存在"
fi

# 創建必要目錄
echo "📁 創建必要目錄..."
mkdir -p data logs

echo ""
echo "========================================="
echo "      🎉 安裝完成！"
echo "========================================="
echo ""
echo "🚀 啟動應用程序："
echo ""
echo "  1. 激活虛擬環境:"
echo "     source venv/bin/activate"
echo ""
echo "  2. 運行應用:"
echo "     streamlit run app.py"
echo ""
echo "🌐 訪問地址："
echo "  http://localhost:8501"
echo ""
echo "📊 功能特色："
echo "  - 交互式地圖顯示救護站和消防局"
echo "  - 數據統計和可視化"
echo "  - 數據搜索和過濾"
echo "  - CSV數據導出"
echo ""
echo "🔧 開發命令："
echo "  streamlit run app.py --server.port=8501 --server.address=0.0.0.0"
echo ""
echo "========================================="