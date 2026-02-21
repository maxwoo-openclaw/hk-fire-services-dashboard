#!/usr/bin/env python3
"""
網絡配置信息檢查
顯示如何從其他機器訪問服務
"""

import socket
import subprocess
import os
import json
from datetime import datetime

def get_network_info():
    """獲取網絡信息"""
    info = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'services': {},
        'network': {},
        'access_urls': []
    }
    
    # 獲取本機IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        info['network']['local_ip'] = local_ip
    except:
        info['network']['local_ip'] = '127.0.0.1'
    
    # 獲取公共IP
    try:
        import requests
        public_ip = requests.get('https://api.ipify.org', timeout=5).text
        info['network']['public_ip'] = public_ip
    except:
        info['network']['public_ip'] = '無法獲取'
    
    # 檢查運行中的服務
    ports = [8000, 8501, 8502, 9001]
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            service_name = {
                8000: '超簡單版本',
                8501: 'Streamlit簡化版',
                8502: 'Streamlit完整版',
                9001: '入口頁面'
            }.get(port, f'端口 {port}')
            
            info['services'][port] = {
                'name': service_name,
                'status': '運行中',
                'urls': [
                    f'http://localhost:{port}',
                    f'http://{info["network"]["local_ip"]}:{port}'
                ]
            }
            
            if info['network']['public_ip'] != '無法獲取':
                info['services'][port]['urls'].append(f'http://{info["network"]["public_ip"]}:{port}')
    
    return info

def generate_html_report(info):
    """生成HTML報告"""
    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>網絡訪問信息 - 香港消防處服務儀表板</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #d32f2f;
        }}
        h1 {{
            color: #d32f2f;
            margin: 0;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        .card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #1976d2;
        }}
        .card.success {{
            border-left-color: #4CAF50;
        }}
        .card.warning {{
            border-left-color: #FF9800;
        }}
        .card-title {{
            font-size: 18px;
            font-weight: bold;
            margin: 0 0 15px 0;
            color: #333;
        }}
        .url-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .url-list li {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .url {{
            font-family: monospace;
            color: #1976d2;
            word-break: break-all;
        }}
        .copy-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }}
        .copy-btn:hover {{
            background: #45a049;
        }}
        .qr-section {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f0f7ff;
            border-radius: 10px;
        }}
        .instructions {{
            background: #fff8e1;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }}
        .instructions h3 {{
            margin-top: 0;
            color: #ff8f00;
        }}
        .network-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .info-box {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .info-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        .info-value {{
            font-size: 18px;
            font-weight: bold;
            color: #1976d2;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            .network-info {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚒 香港消防處服務儀表板 - 網絡訪問信息</h1>
            <div class="timestamp">生成時間: {info['timestamp']}</div>
        </header>
        
        <div class="network-info">
            <div class="info-box">
                <div class="info-label">本機IP地址</div>
                <div class="info-value">{info['network']['local_ip']}</div>
            </div>
            <div class="info-box">
                <div class="info-label">公共IP地址</div>
                <div class="info-value">{info['network']['public_ip']}</div>
            </div>
            <div class="info-box">
                <div class="info-label">運行服務</div>
                <div class="info-value">{len(info['services'])} 個</div>
            </div>
        </div>
        
        <h2>📡 可用服務</h2>
        """
    
    if info['services']:
        for port, service in info['services'].items():
            html += f"""
            <div class="card success">
                <div class="card-title">🔗 {service['name']} (端口: {port})</div>
                <p>狀態: <strong style="color: #4CAF50;">{service['status']}</strong></p>
                <p>訪問地址:</p>
                <ul class="url-list">
            """
            
            for url in service['urls']:
                html += f"""
                    <li>
                        <span class="url">{url}</span>
                        <button class="copy-btn" onclick="copyToClipboard('{url}')">複製</button>
                    </li>
                """
            
            html += """
                </ul>
            </div>
            """
    else:
        html += """
        <div class="card warning">
            <div class="card-title">⚠️ 沒有運行中的服務</div>
            <p>請先啟動服務：</p>
            <code>cd hk_fire_services_dashboard && ./start_full.sh</code>
        </div>
        """
    
    html += f"""
        <div class="qr-section">
            <h3>📱 手機快速訪問</h3>
            <p>掃描二維碼或點擊鏈接：</p>
            <div id="qrcode"></div>
            <p><a href="http://{info['network']['local_ip']}:8502" target="_blank" style="color: #1976d2; font-weight: bold;">
                http://{info['network']['local_ip']}:8502
            </a></p>
        </div>
        
        <div class="instructions">
            <h3>🔧 網絡配置指南</h3>
            <p><strong>1. 局域網訪問：</strong></p>
            <ul>
                <li>確保所有設備連接同一WiFi/網絡</li>
                <li>在手機瀏覽器輸入：<code>http://{info['network']['local_ip']}:8502</code></li>
                <li>或掃描上方二維碼</li>
            </ul>
            
            <p><strong>2. 互聯網訪問（需要端口轉發）：</strong></p>
            <ul>
                <li>在路由器設置端口轉發：外部端口 8502 → 內部 {info['network']['local_ip']}:8502</li>
                <li>外部訪問地址：<code>http://{info['network']['public_ip']}:8502</code></li>
                <li>注意：可能需要配置防火牆</li>
            </ul>
            
            <p><strong>3. 故障排除：</strong></p>
            <ul>
                <li>檢查防火牆是否允許端口 8502</li>
                <li>確保服務正在運行：<code>curl http://localhost:8502/_stcore/health</code></li>
                <li>重啟服務：<code>pkill -f streamlit && ./start_full.sh</code></li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 40px; color: #666; font-size: 12px;">
            <p>香港消防處服務儀表板 • 網絡信息頁面</p>
            <p>此頁面每5分鐘自動刷新</p>
        </div>
    </div>
    
    <script>
        // 複製到剪貼板
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('已複製到剪貼板: ' + text);
            }});
        }}
        
        // 生成二維碼
        function generateQRCode() {{
            const url = 'http://{info['network']['local_ip']}:8502';
            const qrcodeDiv = document.getElementById('qrcode');
            
            // 簡單的文本二維碼（如果沒有QR庫）
            qrcodeDiv.innerHTML = `
                <div style="background: white; padding: 20px; display: inline-block; border: 2px solid #ddd;">
                    <div style="font-family: monospace; line-height: 1;">
                        ██████████████<br>
                        █∙∙∙∙∙∙∙∙∙∙∙∙█<br>
                        █∙████∙███∙∙█<br>
                        █∙████∙███∙∙█<br>
                        █∙████∙███∙∙█<br>
                        █∙∙∙∙∙∙∙∙∙∙∙∙█<br>
                        █████∙███∙███<br>
                        █∙∙∙∙∙███∙∙∙∙█<br>
                        █∙███████∙███<br>
                        █∙███████∙███<br>
                        █∙∙∙∙∙∙∙∙∙∙∙∙█<br>
                        ██████████████<br>
                    </div>
                    <div style="margin-top: 10px; font-size: 12px; color: #666;">
                        掃描二維碼訪問
                    </div>
                </div>
            `;
        }}
        
        // 頁面加載完成後生成二維碼
        document.addEventListener('DOMContentLoaded', generateQRCode);
        
        // 每5分鐘刷新頁面
        setTimeout(() => {{
            location.reload();
        }}, 5 * 60 * 1000);
    </script>
</body>
</html>
    """
    
    return html

def main():
    """主函數"""
    print("=" * 60)
    print("  網絡配置信息檢查")
    print("=" * 60)
    
    # 獲取網絡信息
    info = get_network_info()
    
    print(f"\n📊 網絡信息:")
    print(f"   本機IP: {info['network']['local_ip']}")
    print(f"   公共IP: {info['network']['public_ip']}")
    print(f"   時間: {info['timestamp']}")
    
    print(f"\n📡 運行中的服務 ({len(info['services'])} 個):")
    if info['services']:
        for port, service in info['services'].items():
            print(f"\n   🔗 {service['name']} (端口: {port})")
            print(f"      狀態: {service['status']}")
            for url in service['urls']:
                print(f"      地址: {url}")
    else:
        print("   ⚠️  沒有運行中的服務")
    
    print(f"\n🌐 推薦訪問地址:")
    print(f"   本機: http://localhost:8502")
    print(f"   局域網: http://{info['network']['local_ip']}:8502")
    
    if info['network']['public_ip'] != '無法獲取':
        print(f"   互聯網: http://{info['network']['public_ip']}:8502")
    
    print(f"\n📱 手機訪問:")
    print(f"   在手機瀏覽器輸入: http://{info['network']['local_ip']}:8502")
    
    print(f"\n🔧 網絡提示:")
    print("   1. 確保所有設備在同一網絡")
    print("   2. 檢查防火牆設置")
    print("   3. 路由器可能需要端口轉發")
    
    # 生成HTML報告
    html_report = generate_html_report(info)
    with open("network_info.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    
    print(f"\n📄 HTML報告已生成: network_info.html")
    print(f"   訪問: http://localhost:9001/network_info.html")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()