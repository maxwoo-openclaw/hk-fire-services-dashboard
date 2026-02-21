#!/usr/bin/env python3
"""
運行完整Streamlit版本並允許網絡訪問
"""

import subprocess
import sys
import socket
import time
import os

def get_local_ip():
    """獲取本機IP地址"""
    try:
        # 創建一個臨時socket來獲取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_port_available(port):
    """檢查端口是否可用"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", port))
        sock.close()
        return True
    except:
        return False

def find_available_port(start_port=8501):
    """查找可用端口"""
    port = start_port
    while not check_port_available(port):
        port += 1
        if port > 8600:
            return None
    return port

def main():
    """主函數"""
    print("=" * 60)
    print("  香港消防處服務儀表板 - 完整網絡版本")
    print("=" * 60)
    print()
    
    # 獲取本機IP
    local_ip = get_local_ip()
    print(f"📡 本機IP地址: {local_ip}")
    
    # 查找可用端口
    port = find_available_port(8501)
    if not port:
        print("❌ 找不到可用端口 (8501-8600)")
        return False
    
    print(f"🔌 使用端口: {port}")
    
    # 檢查是否在虛擬環境中
    venv_path = os.path.join(os.path.dirname(__file__), "venv")
    if os.path.exists(venv_path):
        python_path = os.path.join(venv_path, "bin", "python")
        streamlit_path = os.path.join(venv_path, "bin", "streamlit")
    else:
        python_path = sys.executable
        streamlit_path = "streamlit"
    
    print(f"🐍 Python路徑: {python_path}")
    
    # 構建Streamlit命令
    cmd = [
        streamlit_path, "run", "app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.serverAddress", local_ip,
        "--browser.gatherUsageStats", "false",
        "--theme.base", "light",
        "--theme.primaryColor", "#d32f2f",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f0f2f6",
        "--theme.textColor", "#262730",
        "--theme.font", "sans serif"
    ]
    
    print()
    print("🚀 啟動參數:")
    print(f"   服務器地址: 0.0.0.0 (允許所有IP訪問)")
    print(f"   服務器端口: {port}")
    print(f"   本機IP: {local_ip}")
    print()
    
    print("📡 訪問地址:")
    print(f"   本機訪問: http://localhost:{port}")
    print(f"   局域網訪問: http://{local_ip}:{port}")
    print()
    
    print("🌐 其他機器訪問:")
    print(f"   在手機/其他電腦瀏覽器輸入:")
    print(f"   http://{local_ip}:{port}")
    print()
    
    print("🔧 網絡配置:")
    print("   1. 確保防火牆允許端口", port)
    print("   2. 確保路由器未阻止該端口")
    print("   3. 確保所有設備在同一網絡")
    print()
    
    print("🔄 正在啟動Streamlit服務器...")
    print("   按 Ctrl+C 停止服務")
    print("=" * 60)
    
    try:
        # 運行Streamlit
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        
        # 實時輸出日誌
        for line in process.stdout:
            print(line, end='')
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\n\n🛑 服務器正在停止...")
        process.terminate()
        process.wait()
        print("✅ 服務器已停止")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # 檢查依賴
    print("檢查依賴包...")
    try:
        import streamlit
        import pandas
        import geopandas
        import plotly
        import folium
        print("✅ 所有依賴包已安裝")
    except ImportError as e:
        print(f"❌ 缺少依賴包: {e}")
        print("請運行: pip install streamlit pandas geopandas plotly folium streamlit-folium")
        sys.exit(1)
    
    # 運行主函數
    success = main()
    sys.exit(0 if success else 1)