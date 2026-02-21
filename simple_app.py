#!/usr/bin/env python3
"""
香港消防處服務儀表板 - 簡化版本
只需要streamlit和requests
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# 設置頁面配置
st.set_page_config(
    page_title="香港消防處服務儀表板",
    page_icon="🚒",
    layout="wide"
)

# API端點
AMBULANCE_API = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634799003993_7633/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=AmbDepots&outputFormat=geojson"
FIRE_STATION_API = "https://portal.csdi.gov.hk/server/services/common/hkfsd_rcd_1634798867463_89696/MapServer/WFSServer?service=wfs&request=GetFeature&typenames=FireStations&outputFormat=geojson"

@st.cache_data(ttl=3600)
def fetch_ambulance_data():
    """獲取救護站數據"""
    try:
        response = requests.get(AMBULANCE_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 轉換為DataFrame
        features = data.get("features", [])
        records = []
        for feature in features:
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
                "經度": props.get("Longitude")
            })
        
        df = pd.DataFrame(records)
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
        
        # 轉換為DataFrame
        features = data.get("features", [])
        records = []
        for feature in features:
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
                "經度": props.get("Longitude")
            })
        
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        st.error(f"獲取消防局數據失敗: {e}")
        return pd.DataFrame()

def create_summary_stats(ambulance_df, fire_station_df):
    """創建統計摘要"""
    stats = {}
    
    if not ambulance_df.empty:
        stats['救護站總數'] = len(ambulance_df)
        stats['救護站地區數'] = ambulance_df['地區'].nunique()
    
    if not fire_station_df.empty:
        stats['消防局總數'] = len(fire_station_df)
        stats['消防局地區數'] = fire_station_df['地區'].nunique()
    
    return stats

def main():
    """主函數"""
    # 頁面標題
    st.title("🚒 香港消防處服務儀表板")
    st.markdown("顯示香港救護站和消防局的實時數據")
    
    # 側邊欄
    with st.sidebar:
        st.header("🔧 控制面板")
        
        st.subheader("數據顯示")
        show_ambulance = st.checkbox("顯示救護站", value=True)
        show_fire_stations = st.checkbox("顯示消防局", value=True)
        
        st.subheader("數據更新")
        if st.button("🔄 刷新數據"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 數據來源")
        st.markdown("""
        - **救護站數據**: [香港政府地理數據平台](https://portal.csdi.gov.hk)
        - **消防局數據**: [香港政府地理數據平台](https://portal.csdi.gov.hk)
        """)
        
        st.markdown("### 📅 最後更新")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 加載數據
    with st.spinner("正在加載數據..."):
        ambulance_df = fetch_ambulance_data() if show_ambulance else pd.DataFrame()
        fire_station_df = fetch_fire_station_data() if show_fire_stations else pd.DataFrame()
    
    # 顯示統計摘要
    st.header("📈 統計摘要")
    
    if not ambulance_df.empty or not fire_station_df.empty:
        stats = create_summary_stats(ambulance_df, fire_station_df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        if '救護站總數' in stats:
            with col1:
                st.metric("救護站總數", stats['救護站總數'])
        
        if '消防局總數' in stats:
            with col2:
                st.metric("消防局總數", stats['消防局總數'])
        
        if '救護站地區數' in stats:
            with col3:
                st.metric("救護站地區數", stats['救護站地區數'])
        
        if '消防局地區數' in stats:
            with col4:
                st.metric("消防局地區數", stats['消防局地區數'])
    
    # 顯示地區分布
    st.header("📊 地區分布")
    
    if not ambulance_df.empty and not fire_station_df.empty:
        # 統計各地區的救護站數量
        ambulance_counts = ambulance_df['地區'].value_counts().reset_index()
        ambulance_counts.columns = ['地區', '救護站數量']
        
        # 統計各地區的消防局數量
        fire_station_counts = fire_station_df['地區'].value_counts().reset_index()
        fire_station_counts.columns = ['地區', '消防局數量']
        
        # 合併數據
        merged_counts = pd.merge(ambulance_counts, fire_station_counts, on='地區', how='outer').fillna(0)
        
        # 顯示表格
        st.dataframe(merged_counts, use_container_width=True)
    
    # 顯示數據表格
    st.header("📋 詳細數據")
    
    tab1, tab2 = st.tabs(["救護站數據", "消防局數據"])
    
    with tab1:
        if not ambulance_df.empty:
            st.subheader("救護站列表")
            
            # 搜索和過濾
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("搜索救護站名稱或地址", key="amb_search")
            
            with col2:
                district_filter = st.multiselect(
                    "按地區過濾",
                    options=sorted(ambulance_df['地區'].dropna().unique()),
                    key="amb_district"
                )
            
            # 應用過濾
            filtered_df = ambulance_df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['名稱'].str.contains(search_term, case=False, na=False) |
                    filtered_df['地址'].str.contains(search_term, case=False, na=False)
                ]
            
            if district_filter:
                filtered_df = filtered_df[filtered_df['地區'].isin(district_filter)]
            
            # 顯示表格
            st.dataframe(
                filtered_df.reset_index(drop=True),
                use_container_width=True,
                height=400
            )
            
            # 下載按鈕
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載救護站數據 (CSV)",
                data=csv,
                file_name=f"香港救護站數據_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("未加載救護站數據")
    
    with tab2:
        if not fire_station_df.empty:
            st.subheader("消防局列表")
            
            # 搜索和過濾
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("搜索消防局名稱或地址", key="fire_search")
            
            with col2:
                district_filter = st.multiselect(
                    "按地區過濾",
                    options=sorted(fire_station_df['地區'].dropna().unique()),
                    key="fire_district"
                )
            
            # 應用過濾
            filtered_df = fire_station_df.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['名稱'].str.contains(search_term, case=False, na=False) |
                    filtered_df['地址'].str.contains(search_term, case=False, na=False)
                ]
            
            if district_filter:
                filtered_df = filtered_df[filtered_df['地區'].isin(district_filter)]
            
            # 顯示表格
            st.dataframe(
                filtered_df.reset_index(drop=True),
                use_container_width=True,
                height=400
            )
            
            # 下載按鈕
            csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載消防局數據 (CSV)",
                data=csv,
                file_name=f"香港消防局數據_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("未加載消防局數據")
    
    # 顯示地圖鏈接
    st.header("🗺️ 地圖視圖")
    st.markdown("""
    由於地圖庫依賴較多，這裡提供替代方案：
    
    1. **Google地圖查看**:
       - 救護站: [查看位置](https://www.google.com/maps/search/香港救護站)
       - 消防局: [查看位置](https://www.google.com/maps/search/香港消防局)
    
    2. **數據下載後使用其他工具**:
       - 下載CSV數據
       - 使用Excel或Google Sheets的地圖功能
       - 使用在線地圖工具如[kepler.gl](https://kepler.gl)
    
    3. **完整版本功能**:
       - 安裝完整依賴後可使用交互式地圖
       - 運行 `pip install streamlit pandas geopandas plotly requests folium streamlit-folium`
    """)
    
    # 頁腳
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray;">
        <p>香港消防處服務儀表板 • 數據來源: 香港政府地理數據平台</p>
        <p>最後更新: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()