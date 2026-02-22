#!/usr/bin/env python3
"""
香港消防處服務儀表板 - 增強版本
添加橫行統計摘要和表格過濾功能
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
    st.markdown("### 增強版本 - 橫行統計摘要 + 表格過濾功能")
    
    # 側邊欄
    with st.sidebar:
        st.header("🔧 控制面板")
        
        st.subheader("數據顯示")
        show_ambulance = st.checkbox("顯示救護站", value=True)
        show_fire_stations = st.checkbox("顯示消防局", value=True)
        
        st.subheader("地圖設置")
        map_zoom = st.slider("地圖縮放級別", 9, 15, 11)
        
        st.subheader("數據更新")
        if st.button("🔄 刷新數據", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 數據來源")
        st.markdown("""
        - **救護站數據**: [香港政府地理數據平台](https://portal.csdi.gov.hk)
        - **消防局數據**: [香港政府地理數據平台](https://portal.csdi.gov.hk)
        """)
        
        st.markdown("### 📅 系統信息")
        st.write(f"最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
        st.markdown("### 🚨 緊急聯繫")
        st.write("**緊急電話: 999**")
        st.write("消防處熱線: 2723 2233")
    
    # 加載數據
    with st.spinner("正在加載數據..."):
        ambulance_df = fetch_ambulance_data() if show_ambulance else pd.DataFrame()
        fire_station_df = fetch_fire_station_data() if show_fire_stations else pd.DataFrame()
    
    # 顯示橫行統計摘要
    st.header("📈 統計摘要")
    
    # 計算統計數據
    ambulance_count = len(ambulance_df) if not ambulance_df.empty else 0
    fire_station_count = len(fire_station_df) if not fire_station_df.empty else 0
    total_count = ambulance_count + fire_station_count
    
    # 使用Streamlit的columns創建橫行顯示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #1f77b4 0%, #2c8fd6 100%);
                border-radius: 15px;
                padding: 25px;
                color: white;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            ">
                <div style="font-size: 36px; margin-bottom: 10px;">🚑</div>
                <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">{ambulance_count}</div>
                <div style="font-size: 18px; opacity: 0.9;">救護站總數</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #d62728 0%, #ff4d4d 100%);
                border-radius: 15px;
                padding: 25px;
                color: white;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            ">
                <div style="font-size: 36px; margin-bottom: 10px;">🚒</div>
                <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">{fire_station_count}</div>
                <div style="font-size: 18px; opacity: 0.9;">消防局總數</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                border-radius: 15px;
                padding: 25px;
                color: white;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            ">
                <div style="font-size: 36px; margin-bottom: 10px;">📊</div>
                <div style="font-size: 48px; font-weight: bold; margin: 10px 0;">{total_count}</div>
                <div style="font-size: 18px; opacity: 0.9;">總服務點數</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
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
    
    # 顯示詳細數據表格（帶過濾功能）
    st.header("📋 詳細數據（帶過濾功能）")
    
    # 創建選項卡
    tab1, tab2 = st.tabs(["救護站數據", "消防局數據"])
    
    with tab1:
        if not ambulance_df.empty:
            st.subheader(f"救護站列表 ({len(ambulance_df)} 個)")
            
            # 創建過濾選項
            with st.expander("🔍 過濾選項", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # 名稱搜索
                    name_search = st.text_input(
                        "搜索救護站名稱",
                        key="amb_name_search",
                        placeholder="輸入名稱關鍵字..."
                    )
                
                with col2:
                    # 地址搜索
                    address_search = st.text_input(
                        "搜索救護站地址",
                        key="amb_address_search",
                        placeholder="輸入地址關鍵字..."
                    )
                
                with col3:
                    # 地區過濾
                    districts = sorted(ambulance_df['地區'].unique())
                    district_filter = st.multiselect(
                        "按地區過濾救護站",
                        options=districts,
                        key="amb_district_filter",
                        placeholder="選擇地區..."
                    )
            
            # 應用過濾
            filtered_df = ambulance_df.copy()
            
            if name_search:
                filtered_df = filtered_df[
                    filtered_df['名稱'].str.contains(name_search, case=False, na=False)
                ]
            
            if address_search:
                filtered_df = filtered_df[
                    filtered_df['地址'].str.contains(address_search, case=False, na=False)
                ]
            
            if district_filter:
                filtered_df = filtered_df[filtered_df['地區'].isin(district_filter)]
            
            # 顯示過濾結果統計
            if len(filtered_df) != len(ambulance_df):
                st.success(f"✅ 找到 {len(filtered_df)} 個救護站（已過濾 {len(ambulance_df) - len(filtered_df)} 個）")
            
            # 顯示數據表格
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df[['名稱', '地址', '地區', '電話', '緯度', '經度']].reset_index(drop=True),
                    use_container_width=True,
                    height=400,
                    column_config={
                        "名稱": st.column_config.TextColumn("名稱", width="medium"),
                        "地址": st.column_config.TextColumn("地址", width="large"),
                        "地區": st.column_config.TextColumn("地區", width="small"),
                        "電話": st.column_config.TextColumn("電話", width="small"),
                        "緯度": st.column_config.NumberColumn("緯度", format="%.6f"),
                        "經度": st.column_config.NumberColumn("經度", format="%.6f")
                    }
                )
                
                # 下載按鈕
                csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載救護站數據 (CSV)",
                    data=csv,
                    file_name=f"香港救護站數據_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="amb_download"
                )
            else:
                st.warning("⚠️ 沒有找到符合條件的救護站")
        else:
            st.info("未加載救護站數據")
    
    with tab2:
        if not fire_station_df.empty:
            st.subheader(f"消防局列表 ({len(fire_station_df)} 個)")
            
            # 創建過濾選項
            with st.expander("🔍 過濾選項", expanded=True):
                col1, col2, col3