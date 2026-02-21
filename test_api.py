#!/usr/bin/env python3
"""
測試香港消防處API
"""

import requests
import json
from datetime import datetime

def test_ambulance_api():
    """測試救護站API"""
    print("🚑 測試救護站API...")
    
    url = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634799003993_7633/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=AmbDepots&outputFormat=geojson&count=5"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ API響應成功")
        print(f"   狀態碼: {response.status_code}")
        print(f"   救護站數量: {len(data.get('features', []))}")
        print(f"   響應時間: {response.elapsed.total_seconds():.2f}秒")
        
        if data.get('features'):
            print("\n📋 前5個救護站:")
            for i, feature in enumerate(data['features'][:5], 1):
                props = feature.get('properties', {})
                print(f"   {i}. {props.get('Name_TC', '未知')} - {props.get('District_TC', '未知地區')}")
        
        return True
        
    except Exception as e:
        print(f"❌ API測試失敗: {e}")
        return False

def test_fire_station_api():
    """測試消防局API"""
    print("\n🚒 測試消防局API...")
    
    url = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634798867463_89696/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=FireStations&outputFormat=geojson&count=5"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"✅ API響應成功")
        print(f"   狀態碼: {response.status_code}")
        print(f"   消防局數量: {len(data.get('features', []))}")
        print(f"   響應時間: {response.elapsed.total_seconds():.2f}秒")
        
        if data.get('features'):
            print("\n📋 前5個消防局:")
            for i, feature in enumerate(data['features'][:5], 1):
                props = feature.get('properties', {})
                print(f"   {i}. {props.get('Name_TC', '未知')} - {props.get('District_TC', '未知地區')}")
        
        return True
        
    except Exception as e:
        print(f"❌ API測試失敗: {e}")
        return False

def test_data_processing():
    """測試數據處理"""
    print("\n🔧 測試數據處理...")
    
    try:
        import pandas as pd
        import geopandas as gpd
        
        # 測試救護站API
        url = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634799003993_7633/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=AmbDepots&outputFormat=geojson&count=3"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # 轉換為GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(data["features"])
        
        print(f"✅ 數據處理成功")
        print(f"   數據框形狀: {gdf.shape}")
        print(f"   列名: {list(gdf.columns)}")
        
        # 顯示基本信息
        print(f"   中文名稱列: {'Name_TC' in gdf.columns}")
        print(f"   地址列: {'Address_TC' in gdf.columns}")
        print(f"   地區列: {'District_TC' in gdf.columns}")
        print(f"   坐標列: {'Latitude' in gdf.columns and 'Longitude' in gdf.columns}")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據處理失敗: {e}")
        return False

def main():
    """主函數"""
    print("=" * 50)
    print("  香港消防處API測試工具")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 測試API
    ambulance_ok = test_ambulance_api()
    fire_station_ok = test_fire_station_api()
    processing_ok = test_data_processing()
    
    print("\n" + "=" * 50)
    print("測試結果摘要:")
    print("=" * 50)
    
    results = {
        "救護站API": "✅ 通過" if ambulance_ok else "❌ 失敗",
        "消防局API": "✅ 通過" if fire_station_ok else "❌ 失敗",
        "數據處理": "✅ 通過" if processing_ok else "❌ 失敗"
    }
    
    for test, result in results.items():
        print(f"  {test}: {result}")
    
    all_passed = ambulance_ok and fire_station_ok and processing_ok
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有測試通過！應用程序可以正常運行。")
    else:
        print("⚠️  部分測試失敗，請檢查網絡連接和API狀態。")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n測試被用戶中斷")
        exit(1)
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        exit(1)