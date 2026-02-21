#!/usr/bin/env python3
"""
香港消防處服務查看器 - 啟動腳本
超簡單版本，只需Python 3，無需安裝任何額外包
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
import sys

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
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"  錯誤: 獲取數據失敗 - {e}")
        return None

def fetch_data():
    """獲取數據並緩存"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在更新數據...")
        
        # 獲取救護站數據
        print("  獲取救護站數據...")
        ambulance_data = fetch_url(AMBULANCE_API)
        if not ambulance_data:
            print("  警告: 無法獲取救護站數據")
            return
        
        # 獲取消防局數據
        print("  獲取消防局數據...")
        fire_station_data = fetch_url(FIRE_STATION_API)
        if not fire_station_data:
            print("  警告: 無法獲取消防局數據")
            return
        
        # 處理救護站數據
        ambulance_records = []
        for feature in ambulance_data.get("features", []):
            props = feature.get("properties", {})
            ambulance_records.append({
                "id": props.get("OBJECTID"),
                "fsd_id": props.get("FSDID"),
                "name": props.get("Name_TC", ""),
                "name_en": props.get("Name_ENG", ""),
                "address": props.get("Address_TC", ""),
                "address_en": props.get("Address_ENG", ""),
                "district": props.get("District_TC", ""),
                "district_en": props.get("District_ENG", ""),
                "phone": props.get("Telephone", ""),
                "lat": props.get("Latitude"),
                "lng": props.get("Longitude")
            })
        
        # 處理消防局數據
        fire_station_records = []
        for feature in fire_station_data.get("features", []):
            props = feature.get("properties", {})
            fire_station_records.append({
                "id": props.get("OBJECTID"),
                "fsd_id": props.get("FSDID"),
                "name": props.get("Name_TC", ""),
                "name_en": props.get("Name_ENG", ""),
                "address": props.get("Address_TC", ""),
                "address_en": props.get("Address_ENG", ""),
                "district": props.get("District_TC", ""),
                "district_en": props.get("District_ENG", ""),
                "phone": props.get("Telephone", ""),
                "lat": props.get("Latitude"),
                "lng": props.get("Longitude")
            })
        
        data_cache['ambulance'] = ambulance_records
        data_cache['fire_station'] = fire_station_records
        data_cache['timestamp'] = datetime.now()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 數據更新完成")
        print(f"  救護站: {len(ambulance_records)} 個")
        print(f"  消防局: {len(fire_station_records)} 個")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 數據更新失敗: {e}")

def background_data_fetcher():
    """後台數據更新線程"""
    while True:
        fetch_data()
        # 每小時更新一次
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 下次更新: 1小時後")
        time.sleep(3600)

def generate_html(data_type="all", search_term="", district=""):
    """生成HTML頁面"""
    ambulance_data = data_cache['ambulance']
    fire_station_data = data_cache['fire_station']
    timestamp = data_cache['timestamp'] or datetime.now()
    
    # 過濾數據
    if data_type == "ambulance":
        display_data = ambulance_data
        title = "救護站數據"
    elif data_type == "fire":
        display_data = fire_station_data
        title = "消防局數據"
    else:
        display_data = ambulance_data + fire_station_data
        title = "香港消防處服務數據"
    
    # 應用搜索過濾
    if search_term:
        search_lower = search_term.lower()
        filtered_data = []
        for item in display_data:
            if (search_lower in item.get('name', '').lower() or
                search_lower in item.get('address', '').lower() or
                search_lower in item.get('district', '').lower()):
                filtered_data.append(item)
        display_data = filtered_data
    
    # 應用地區過濾
    if district:
        filtered_data = []
        for item in display_data:
            if district == item.get('district', ''):
                filtered_data.append(item)
        display_data = filtered_data
    
    # 獲取所有地區
    all_districts = set()
    for item in ambulance_data:
        district_val = item.get('district')
        if district_val:
            all_districts.add(district_val)
    for item in fire_station_data:
        district_val = item.get('district')
        if district_val:
            all_districts.add(district_val)
    
    # 生成HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 香港消防處服務查看器</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header {{
            background-color: #d32f2f;
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            margin-bottom: 20px;
        }}
        h1 {{ margin: 0; font-size: 24px; }}
        .subtitle {{ margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }}
        
        .controls {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .search-box, .district-select {{
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-right: 10px;
            margin-bottom: 10px;
        }}
        .search-box {{ width: 300px; }}
        .button {{
            padding: 8px 16px;
            background-color: #1976d2;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        .button:hover {{ background-color: #1565c0; }}
        
        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            flex: 1;
            min-width: 200px;
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-card.fire {{ background-color: #ffebee; }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #1976d2;
        }}
        .stat-card.fire .stat-number {{ color: #d32f2f; }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:hover {{ background-color: #f5f5f5; }}
        
        .type-badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .ambulance-badge {{ background-color: #1976d2; color: white; }}
        .fire-badge {{ background-color: #d32f2f; color: white; }}
        
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        .map-link {{ color: #1976d2; text-decoration: none; }}
        .map-link:hover {{ text-decoration: underline; }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            .search-box {{ width: 100%; }}
            .stats {{ flex-direction: column; }}
            table {{ font-size: 14px; }}
            th, td {{ padding: 8px; }}
            .controls input, .controls select {{
                width: 100%;
                margin-right: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚒 香港消防處服務查看器</h1>
            <p class="subtitle">實時顯示救護站和消防局數據 • 最後更新: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="controls">
            <form method="GET" action="/">
                <input type="text" name="search" placeholder="搜索名稱或地址..." value="{html.escape(search_term)}" class="search-box">
                <select name="district" class="district-select">
                    <option value="">所有地區</option>"""
    
    # 添加地區選項
    for district_option in sorted(all_districts):
        selected = "selected" if district == district_option else ""
        html_content += f'<option value="{html.escape(district_option)}" {selected}>{html.escape(district_option)}</option>'
    
    html_content += f"""
                </select>
                <select name="type" class="district-select">
                    <option value="all" {"selected" if data_type == "all" else ""}>所有類型</option>
                    <option value="ambulance" {"selected" if data_type == "ambulance" else ""}>只顯示救護站</option>
                    <option value="fire" {"selected" if data_type == "fire" else ""}>只顯示消防局</option>
                </select>
                <br>
                <button type="submit" class="button">搜索</button>
                <a href="/" class="button" style="margin-left: 10px;">重置</a>
            </form>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(ambulance_data)}</div>
                <div class="stat-label">救護站總數</div>
            </div>
            <div class="stat-card fire">
                <div class="stat-number">{len(fire_station_data)}</div>
                <div class="stat-label">消防局總數</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(item['district'] for item in ambulance_data if item.get('district')))}</div>
                <div class="stat-label">救護站地區數</div>
            </div>
            <div class="stat-card fire">
                <div class="stat-number">{len(set(item['district'] for item in fire_station_data if item.get('district')))}</div>
                <div class="stat-label">消防局地區數</div>
            </div>
        </div>
        
        <h2>{title} ({len(display_data)} 個結果)</h2>
        
        <table>
            <thead>
                <tr>
                    <th>類型</th>
                    <th>名稱</th>
                    <th>地址</th>
                    <th>地區</th>
                    <th>電話</th>
                    <th>坐標</th>
                    <th>地圖</th>
                </tr>
            </thead>
            <tbody>"""
    
    # 添加數據行
    for item in display_data:
        item_type = "救護站" if item in ambulance_data else "消防局"
        badge_class = "ambulance-badge" if item_type == "救護站" else "fire-badge"
        
        # 生成地圖鏈接
        lat = item.get('lat')
        lng = item.get('lng')
        if lat and lng:
            map_link = f"https://www.google.com/maps?q={lat},{lng}"
            coordinates = f"{lat:.6f}, {lng:.6f}"
        else:
            address = item.get('address', '')
            map_link = f"https://www.google.com/maps/search/{html.escape(address)}"
            coordinates = "N/A"
        
        html_content += f"""
                <tr>
                    <td><span class="type-badge {badge_class}">{item_type}</span></td>
                    <td><strong>{html.escape(item.get('name', 'N/A'))}</strong><br><small>{html.escape(item.get('name_en', ''))}</small></td>
                    <td>{html.escape(item.get('address', 'N/A'))}<br><small>{html.escape(item.get('address_en', ''))}</small></td>
                    <td>{html.escape(item.get('district', 'N/A'))}</td>
                    <td>{html.escape(item.get('phone', 'N/A'))}</td>
                    <td><small>{coordinates}</small></td>
                    <td><a href="{map_link}" target="_blank" class="map-link">查看地圖</a></td>
                </tr>"""
    
    html_content += """
            </tbody>
        </table>
        
        <div class="footer">
            <p>數據來源: 香港政府地理數據平台 (portal.csdi.gov.hk)</p>
            <p>© 2024 香港消防處服務查看器 • 此頁面每小時自動更新</p>
            <p><small>提示: 點擊"查看地圖"可在Google地圖中查看位置</small></p>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

class FireServiceHandler(http.server.SimpleHTTPRequestHandler):
    """自定義HTTP請求處理器"""
    
    def do_GET(self):
        """處理GET請求"""
        # 只處理根路徑
        if self.path == '/' or self.path.startswith('/?'):
            # 解析查詢參數
            query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
            query_params = urllib.parse.parse_qs(query_string)
            
            # 獲取查詢參數
            data_type = query_params.get('type', ['all'])[0]
            search_term = query_params.get('search', [''])[0]
            district = query_params.get('district', [''])[0]
            
            # 生成HTML響應
            html_content = generate_html(data_type, search_term, district)
            
            # 發送響應
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            # 其他路徑返回404
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>404 - Page Not Found</h1><p>只有主頁面可用。</p>')
    
    def log_message(self, format, *args):
        """自定義日誌格式"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} - {format % args}")

def main():
    """主函數"""
    print("=" * 60)
    print("  香港消防處服務查看器 -