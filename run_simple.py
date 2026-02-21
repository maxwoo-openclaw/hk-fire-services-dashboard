#!/usr/bin/env python3
"""
香港消防處服務查看器 - 最簡單版本
只需Python 3，無需安裝任何額外包
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.parse
from datetime import datetime
import threading
import time
import html

# API端點
AMBULANCE_API = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634799003993_7633/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=AmbDepots&outputFormat=geojson"
FIRE_STATION_API = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634798867463_89696/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=FireStations&outputFormat=geojson"

# 緩存數據
data_cache = {
    'ambulance': [],
    'fire_station': [],
    'timestamp': None
}

def fetch_url(url):
    """獲取URL內容"""
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"錯誤: {e}")
        return None

def fetch_data():
    """獲取數據並緩存"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在更新數據...")
        
        # 獲取救護站數據
        ambulance_data = fetch_url(AMBULANCE_API)
        if ambulance_data:
            ambulance_records = []
            for feature in ambulance_data.get("features", []):
                props = feature.get("properties", {})
                ambulance_records.append({
                    "name": props.get("Name_TC", ""),
                    "address": props.get("Address_TC", ""),
                    "district": props.get("District_TC", ""),
                    "phone": props.get("Telephone", ""),
                    "lat": props.get("Latitude"),
                    "lng": props.get("Longitude")
                })
            data_cache['ambulance'] = ambulance_records
        
        # 獲取消防局數據
        fire_station_data = fetch_url(FIRE_STATION_API)
        if fire_station_data:
            fire_station_records = []
            for feature in fire_station_data.get("features", []):
                props = feature.get("properties", {})
                fire_station_records.append({
                    "name": props.get("Name_TC", ""),
                    "address": props.get("Address_TC", ""),
                    "district": props.get("District_TC", ""),
                    "phone": props.get("Telephone", ""),
                    "lat": props.get("Latitude"),
                    "lng": props.get("Longitude")
                })
            data_cache['fire_station'] = fire_station_records
        
        data_cache['timestamp'] = datetime.now()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 數據更新完成")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 數據更新失敗: {e}")

def generate_html():
    """生成HTML頁面"""
    ambulance_data = data_cache['ambulance']
    fire_station_data = data_cache['fire_station']
    timestamp = data_cache['timestamp'] or datetime.now()
    
    # 統計
    ambulance_count = len(ambulance_data)
    fire_station_count = len(fire_station_data)
    
    # 獲取所有地區
    all_districts = set()
    for item in ambulance_data:
        if item.get('district'):
            all_districts.add(item['district'])
    for item in fire_station_data:
        if item.get('district'):
            all_districts.add(item['district'])
    
    # 生成HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>香港消防處服務查看器</title>
    <style>
        body {{ font-family: Arial; margin: 20px; background: #f0f0f0; }}
        .container {{ max-width: 1000px; margin: auto; background: white; padding: 20px; border-radius: 10px; }}
        header {{ background: #d32f2f; color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        h1 {{ margin: 0; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ flex: 1; text-align: center; padding: 15px; background: #e3f2fd; border-radius: 5px; }}
        .stat.fire {{ background: #ffebee; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
        th {{ background: #f2f2f2; }}
        .ambulance {{ color: #1976d2; font-weight: bold; }}
        .fire {{ color: #d32f2f; font-weight: bold; }}
        .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚒 香港消防處服務查看器</h1>
            <p>最後更新: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="stats">
            <div class="stat">
                <h2>{ambulance_count}</h2>
                <p>救護站</p>
            </div>
            <div class="stat fire">
                <h2>{fire_station_count}</h2>
                <p>消防局</p>
            </div>
        </div>
        
        <h2>救護站列表</h2>
        <table>
            <tr><th>名稱</th><th>地址</th><th>地區</th><th>電話</th></tr>"""
    
    for item in ambulance_data[:20]:  # 只顯示前20個
        html_content += f"""
            <tr>
                <td class="ambulance">{html.escape(item.get('name', ''))}</td>
                <td>{html.escape(item.get('address', ''))}</td>
                <td>{html.escape(item.get('district', ''))}</td>
                <td>{html.escape(item.get('phone', ''))}</td>
            </tr>"""
    
    html_content += """
        </table>
        
        <h2>消防局列表</h2>
        <table>
            <tr><th>名稱</th><th>地址</th><th>地區</th><th>電話</th></tr>"""
    
    for item in fire_station_data[:20]:  # 只顯示前20個
        html_content += f"""
            <tr>
                <td class="fire">{html.escape(item.get('name', ''))}</td>
                <td>{html.escape(item.get('address', ''))}</td>
                <td>{html.escape(item.get('district', ''))}</td>
                <td>{html.escape(item.get('phone', ''))}</td>
            </tr>"""
    
    html_content += f"""
        </table>
        
        <div class="footer">
            <p>數據來源: 香港政府地理數據平台</p>
            <p>總共 {ambulance_count} 個救護站, {fire_station_count} 個消防局</p>
            <p>地區: {', '.join(sorted(all_districts)[:10])}{'...' if len(all_districts) > 10 else ''}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            html_content = generate_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def main():
    print("=" * 50)
    print("香港消防處服務查看器")
    print("=" * 50)
    
    # 初始加載數據
    fetch_data()
    
    # 啟動服務器
    port = 8000
    with socketserver.TCPServer(("", port), SimpleHandler) as httpd:
        print(f"服務器已啟動: http://localhost:{port}")
        print("按 Ctrl+C 停止")
        
        # 簡單的後台更新
        def update_data():
            while True:
                time.sleep(3600)  # 每小時更新
                fetch_data()
        
        import threading
        thread = threading.Thread(target=update_data, daemon=True)
        thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服務器已停止")

if __name__ == "__main__":
    main()