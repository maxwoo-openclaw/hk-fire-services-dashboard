#!/bin/bash

# 香港消防處服務儀表板 - 完整版本啟動腳本
# 允許網絡訪問，支持其他機器瀏覽

set -e

echo "========================================================"
echo "  香港消防處服務儀表板 - 完整網絡版本"
echo "========================================================"
echo ""

# 進入項目目錄
cd "$(dirname "$0")"

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "❌ 虛擬環境不存在，請先運行 setup.sh"
    exit 1
fi

# 激活虛擬環境
source venv/bin/activate

# 檢查依賴
echo "🔍 檢查依賴包..."
python3 -c "
try:
    import streamlit, pandas, geopandas, plotly, folium, requests, numpy
    print('✅ 所有依賴包已安裝')
except ImportError as e:
    print(f'❌ 缺少依賴包: {e}')
    exit(1)
"

# 獲取本機IP
echo "📡 獲取網絡信息..."
LOCAL_IP=$(hostname -I | awk '{print $1}')
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="127.0.0.1"
fi

echo "  本機IP地址: $LOCAL_IP"

# 設置端口
PORT=${1:-8502}
echo "  使用端口: $PORT"

# 檢查端口是否可用
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口 $PORT 已被佔用，嘗試其他端口..."
    PORT=$((PORT + 1))
    while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; do
        PORT=$((PORT + 1))
        if [ $PORT -gt 8600 ]; then
            echo "❌ 找不到可用端口 (8502-8600)"
            exit 1
        fi
    done
    echo "  改用端口: $PORT"
fi

echo ""
echo "🚀 啟動參數:"
echo "   服務器地址: 0.0.0.0 (允許所有IP訪問)"
echo "   服務器端口: $PORT"
echo "   本機IP: $LOCAL_IP"
echo ""

echo "📡 訪問地址:"
echo "   本機訪問: http://localhost:$PORT"
echo "   局域網訪問: http://$LOCAL_IP:$PORT"
echo ""

echo "🌐 其他機器訪問:"
echo "   在手機/其他電腦瀏覽器輸入:"
echo "   http://$LOCAL_IP:$PORT"
echo ""

echo "🔧 網絡提示:"
echo "   1. 確保所有設備在同一WiFi/網絡"
echo "   2. 手機可掃描二維碼快速訪問"
echo "   3. 按 Ctrl+C 停止服務"
echo ""

echo "🔄 正在啟動Streamlit服務器..."
echo "========================================================"

# 生成二維碼（如果可用）
if command -v qrencode &> /dev/null; then
    echo "📱 掃描二維碼在手機訪問:"
    qrencode -t UTF8 "http://$LOCAL_IP:$PORT"
    echo ""
elif command -v python3 &> /dev/null; then
    echo "📱 手機訪問鏈接: http://$LOCAL_IP:$PORT"
    echo "   可複製鏈接到手機瀏覽器"
    echo ""
fi

# 運行Streamlit
streamlit run app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.serverAddress $LOCAL_IP \
    --browser.gatherUsageStats false \
    --theme.base light \
    --theme.primaryColor "#d32f2f" \
    --theme.backgroundColor "#ffffff" \
    --theme.secondaryBackgroundColor "#f0f2f6" \
    --theme.textColor "#262730" \
    --theme.font "sans serif"