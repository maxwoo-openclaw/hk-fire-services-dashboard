#!/usr/bin/env python3
"""
香港消防處服務儀表板 - 最終修復版本
確保頁面正常顯示所有功能
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import folium
from streamlit_folium import folium_static

# 設置頁面配置
st.set_page_config(
    page_title="香港消防處服務儀表板",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API端點
AMBULANCE_API = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634799003993_7633/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=AmbDepots&outputFormat=geojson"
FIRE_STATION_API = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634798867463_89696/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=FireStations&outputFormat=geojson"

# 香港中心坐標
HK_CENTER = [22.3193, 114.1694]

@st.cache_data(ttl=3600)  # 緩存1小時
def fetch_ambulance_data():
    """獲取救護站數據"""
    try:
        response = requests.get(AMBULANCE_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        records = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            records.append({
                "ID": props.get("OBJECTID"),
                "消防處編號": props.get("FSDID"),
                "名稱": props.get("Name_TC"),
                "英文名稱": props.get("Name_ENG"),
                "地址": props.get("Address_TC"),
                "英文地址": props.get("Address_ENG"),
                "地區": props.get("District_TC"),
                "英文地區": props.get("District_ENG"),
                "電話": props.get("Telephone"),
                "緯度": props.get("Latitude"),
                "經度": props.get("Longitude"),
                "類型": "救護站"
            })
        
        df = pd.DataFrame(records)
        df = df.dropna(subset=['名稱', '地區', '緯度', '經度']).fillna('')
        return df
    except Exception as e:
        st.error(f"獲取救護站數據失敗: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_fire_station_data():
    """獲取消防局數據"""
    try:
        response = requests.get(FIRE_STATION_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        records = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            records.append({
                "ID": props.get("OBJECTID"),
                "消防處編號": props.get("FSDID"),
                "名稱": props.get("Name_TC"),
                "英文名稱": props.get("Name_ENG"),
                "地址": props.get("Address_TC"),
                "英文地址": props.get("Address_ENG"),
                "地區": props.get("District_TC"),
                "英文地區": props.get("District_ENG"),
                "電話": props.get("Telephone"),
                "緯度": props.get("Latitude"),
                "經度": props.get("Longitude"),
                "類型": "消防局"
            })
        
        df = pd.DataFrame(records)
        df = df.dropna(subset=['名稱', '地區', '緯度', '經度']).fillna('')
        return df
    except Exception as e:
        st.error(f"獲取消防局數據失敗: {e}")
        return pd.DataFrame()

def create_interactive_map(ambulance_df, fire_station_df, zoom=11):
    """創建交互式Folium地圖"""
    try:
        # 創建地圖
        m = folium.Map(location=HK_CENTER, zoom_start=zoom, tiles='CartoDB positron')
        
        # 添加救護站標記
        if not ambulance_df.empty:
            for idx, row in ambulance_df.iterrows():
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; min-width: 250px;">
                    <h4 style="color: #1f77b4; margin-bottom: 10px;">🚑 {row['名稱']}</h4>
                    <p><strong>類型:</strong> 救護站</p>
                    <p><strong>地址:</strong> {row['地址']}</p>
                    <p><strong>地區:</strong> {row['地區']}</p>
                    <p><strong>電話:</strong> {row['電話']}</p>
                    <p><strong>消防處編號:</strong> {row['消防處編號']}</p>
                    <p><small>坐標: {row['緯度']:.6f}, {row['經度']:.6f}</small></p>
                </div>
                """
                
                folium.Marker(
                    location=[row['緯度'], row['經度']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"救護站: {row['名稱']}",
                    icon=folium.Icon(color='blue', icon='plus', prefix='fa')
                ).add_to(m)
        
        # 添加消防局標記
        if not fire_station_df.empty:
            for idx, row in fire_station_df.iterrows():
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; min-width: 250px;">
                    <h4 style="color: #d62728; margin-bottom: 10px;">🚒 {row['名稱']}</h4>
                    <p><strong>類型:</strong> 消防局</p>
                    <p><strong>地址:</strong> {row['地址']}</p>
                    <p><strong>地區:</strong> {row['地區']}</p>
                    <p><strong>電話:</strong> {row['電話']}</p>
                    <p><strong>消防處編號:</strong> {row['消防處編號']}</p>
                    <p><small>坐標: {row['緯度']:.6f}, {row['經度']:.6f}</small></p>
                </div>
                """
                
                folium.Marker(
                    location=[row['緯度'], row['經度']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"消防局: {row['名稱']}",
                    icon=folium.Icon(color='red', icon='fire', prefix='fa')
                ).add_to(m)
        
        # 添加圖例
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 160px; height: 110px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 5px;">
            <p style="margin: 0 0 5px 0;"><strong>圖例</strong></p>
            <p style="margin: 5px 0;"><span style="color: blue;">●</span> 救護站</p>
            <p style="margin: 5px 0;"><span style="color: red;">●</span> 消防局</p>
            <p style="margin: 5px 0; font-size: 12px; color: #666;">點擊標記查看詳情</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    except Exception as e:
        st.error(f"創建地圖失敗: {e}")
        return None

def main():
    """主函數"""
    # 頁面標題
    st.title("🚒 香港消防處服務儀表板")
    st.markdown("顯示香港救護站和消防局的實時數據")
    
    # 側邊欄
    with st.sidebar:
        st.header("🔧 控制面板")
        
        show_ambulance = st.checkbox("顯示救護站", value=True)
        show_fire_stations = st.checkbox("顯示消防局", value=True)
        
        map_zoom = st.slider("地圖縮放級別", 9, 15, 11)
        
        if st.button("🔄 刷新數據"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("**數據來源:** 香港政府地理數據平台")
        st.markdown(f"**最後更新:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加載數據
    with st.spinner("正在加載數據..."):
        ambulance_df = fetch_ambulance_data() if show_ambulance else pd.DataFrame()
        fire_station_df = fetch_fire_station_data() if show_fire_stations else pd.DataFrame()
    
    # 顯示統計摘要 - 使用Streamlit原生metrics
    st.header("📈 統計摘要")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ambulance_count = len(ambulance_df) if not ambulance_df.empty else 0
        st.metric("救護站總數", ambulance_count)
    
    with col2:
        fire_station_count = len(fire_station_df) if not fire_station_df.empty else 0
        st.metric("消防局總數", fire_station_count)
    
    with col3:
        total_count = ambulance_count + fire_station_count
        st.metric("總服務點數", total_count)
    
    # 顯示交互式地圖
    st.header("🗺️ 交互式地圖")
    
    if (not ambulance_df.empty or not fire_station_df.empty):
        with st.spinner("正在生成地圖..."):
            map_obj = create_interactive_map(ambulance_df, fire_station_df, zoom=map_zoom)
            
            if map_obj:
                # 顯示地圖
                folium_static(map_obj, width=1200, height=600)
                
                st.markdown("""
                **地圖使用說明:**
                - **點擊標記**查看詳細信息
                - **滾動縮放**地圖
                - **拖動移動**地圖視角
                - **圖例**在左下角
                """)
            else:
                st.error("無法創建地圖，請檢查數據")
    else:
        st.info("請選擇要顯示的數據類型")
    
    # 顯示詳細數據表格
    st.header("📋 詳細數據")
    
    # 救護站數據
    if not ambulance_df.empty:
        st.subheader(f"救護站列表 ({len(ambulance_df)} 個)")
        
        # 簡單搜索
        search_term = st.text_input("搜索救護站名稱或地址", key="amb_search")
        
        # 應用搜索
        filtered_amb = ambulance_df.copy()
        if search_term:
            filtered_amb = filtered_amb[
                filtered_amb['名稱'].str.contains(search_term, case=False, na=False) |
                filtered_amb['地址'].str.contains(search_term, case=False, na=False)
            ]
        
        if len(filtered_amb) != len(ambulance_df):
            st.success(f"找到 {len(filtered_amb)} 個救護站")
        
        # 顯示表格
        st.dataframe(
            filtered_amb[['名稱', '地址', '地區', '電話']].reset_index(drop=True),
            use_container_width=True,
            height=300
        )
    
    # 消防局數據
    if not fire_station_df.empty:
        st.subheader(f"消防局列表 ({len(fire_station_df)} 個)")
        
        # 簡單搜索
        search_term = st.text_input("搜索消防局名稱或地址", key="fire_search")
        
        # 應用搜索
        filtered_fire = fire_station_df.copy()
        if search_term:
            filtered_fire = filtered_fire[
                filtered_fire['名稱'].str.contains(search_term, case=False, na=False) |
                filtered_fire['地址'].str.contains(search_term, case=False, na=False)
            ]
        
        if len(filtered_fire) != len(fire_station_df):
            st.success(f"找到 {len(filtered_fire)} 個消防局")
        
        # 顯示表格
        st.dataframe(
            filtered_fire[['名稱', '地址', '地區', '電話']].reset_index(drop=True),
            use_container_width=True,
            height=300
        )
    
    # 頁腳
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: gray;">
        <p>香港消防處服務儀表板 • 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()