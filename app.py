#!/usr/bin/env python3
"""
香港消防處服務儀表板 - Streamlit應用
顯示救護站和消防局數據
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from datetime import datetime
import folium
from streamlit_folium import folium_static
import numpy as np

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

@st.cache_data(ttl=3600)  # 緩存1小時
def fetch_ambulance_data():
    """獲取救護站數據"""
    try:
        response = requests.get(AMBULANCE_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 轉換為GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(data["features"])
        
        # 重命名列為中文
        column_mapping = {
            'OBJECTID': 'ID',
            'FSDID': '消防處編號',
            'Name_TC': '名稱',
            'Name_ENG': '英文名稱',
            'Address_TC': '地址',
            'Address_ENG': '英文地址',
            'District_TC': '地區',
            'District_ENG': '英文地區',
            'Telephone': '電話',
            'Latitude': '緯度',
            'Longitude': '經度',
            'Northing': '北向坐標',
            'Easting': '東向坐標'
        }
        
        gdf = gdf.rename(columns=column_mapping)
        
        # 只保留需要的列
        columns_to_keep = ['ID', '消防處編號', '名稱', '英文名稱', '地址', '英文地址', 
                          '地區', '英文地區', '電話', '緯度', '經度', 'geometry']
        gdf = gdf[[col for col in columns_to_keep if col in gdf.columns]]
        
        return gdf
    except Exception as e:
        st.error(f"獲取救護站數據失敗: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_fire_station_data():
    """獲取消防局數據"""
    try:
        response = requests.get(FIRE_STATION_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 轉換為GeoDataFrame
        gdf = gpd.GeoDataFrame.from_features(data["features"])
        
        # 重命名列為中文
        column_mapping = {
            'OBJECTID': 'ID',
            'FSDID': '消防處編號',
            'Name_TC': '名稱',
            'Name_ENG': '英文名稱',
            'Address_TC': '地址',
            'Address_ENG': '英文地址',
            'District_TC': '地區',
            'District_ENG': '英文地區',
            'Telephone': '電話',
            'Latitude': '緯度',
            'Longitude': '經度',
            'Northing': '北向坐標',
            'Easting': '東向坐標'
        }
        
        gdf = gdf.rename(columns=column_mapping)
        
        # 只保留需要的列
        columns_to_keep = ['ID', '消防處編號', '名稱', '英文名稱', '地址', '英文地址', 
                          '地區', '英文地區', '電話', '緯度', '經度', 'geometry']
        gdf = gdf[[col for col in columns_to_keep if col in gdf.columns]]
        
        return gdf
    except Exception as e:
        st.error(f"獲取消防局數據失敗: {e}")
        return None

def create_map(ambulance_gdf, fire_station_gdf):
    """創建交互式地圖"""
    # 創建香港中心點的地圖
    hk_center = [22.3193, 114.1694]
    m = folium.Map(location=hk_center, zoom_start=11, tiles='CartoDB positron')
    
    # 添加救護站標記（藍色）
    if ambulance_gdf is not None and not ambulance_gdf.empty:
        for idx, row in ambulance_gdf.iterrows():
            if pd.notnull(row['緯度']) and pd.notnull(row['經度']):
                popup_html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h4 style="color: #1f77b4; margin-bottom: 5px;">🚑 {row['名稱']}</h4>
                    <p><strong>地址:</strong> {row['地址']}</p>
                    <p><strong>地區:</strong> {row['地區']}</p>
                    <p><strong>電話:</strong> {row['電話']}</p>
                    <p><strong>消防處編號:</strong> {row['消防處編號']}</p>
                </div>
                """
                folium.Marker(
                    location=[row['緯度'], row['經度']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"救護站: {row['名稱']}",
                    icon=folium.Icon(color='blue', icon='plus', prefix='fa')
                ).add_to(m)
    
    # 添加消防局標記（紅色）
    if fire_station_gdf is not None and not fire_station_gdf.empty:
        for idx, row in fire_station_gdf.iterrows():
            if pd.notnull(row['緯度']) and pd.notnull(row['經度']):
                popup_html = f"""
                <div style="font-family: Arial, sans-serif;">
                    <h4 style="color: #d62728; margin-bottom: 5px;">🚒 {row['名稱']}</h4>
                    <p><strong>地址:</strong> {row['地址']}</p>
                    <p><strong>地區:</strong> {row['地區']}</p>
                    <p><strong>電話:</strong> {row['電話']}</p>
                    <p><strong>消防處編號:</strong> {row['消防處編號']}</p>
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
                bottom: 50px; left: 50px; width: 150px; height: 90px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px; border-radius: 5px;">
        <p style="margin: 0;"><strong>圖例</strong></p>
        <p style="margin: 5px 0;"><span style="color: blue;">●</span> 救護站</p>
        <p style="margin: 5px 0;"><span style="color: red;">●</span> 消防局</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def create_district_chart(ambulance_gdf, fire_station_gdf):
    """創建地區分布圖表"""
    if ambulance_gdf is None or fire_station_gdf is None:
        return None
    
    # 統計各地區的救護站數量
    ambulance_counts = ambulance_gdf['地區'].value_counts().reset_index()
    ambulance_counts.columns = ['地區', '救護站數量']
    
    # 統計各地區的消防局數量
    fire_station_counts = fire_station_gdf['地區'].value_counts().reset_index()
    fire_station_counts.columns = ['地區', '消防局數量']
    
    # 合併數據
    merged_counts = pd.merge(ambulance_counts, fire_station_counts, on='地區', how='outer').fillna(0)
    
    # 創建柱狀圖
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=merged_counts['地區'],
        y=merged_counts['救護站數量'],
        name='救護站',
        marker_color='#1f77b4',
        text=merged_counts['救護站數量'],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        x=merged_counts['地區'],
        y=merged_counts['消防局數量'],
        name='消防局',
        marker_color='#d62728',
        text=merged_counts['消防局數量'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='各地區救護站和消防局數量',
        xaxis_title='地區',
        yaxis_title='數量',
        barmode='group',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_summary_stats(ambulance_gdf, fire_station_gdf):
    """創建統計摘要"""
    stats = {}
    
    if ambulance_gdf is not None:
        stats['救護站總數'] = len(ambulance_gdf)
        stats['救護站地區數'] = ambulance_gdf['地區'].nunique()
        stats['救護站平均緯度'] = ambulance_gdf['緯度'].mean()
        stats['救護站平均經度'] = ambulance_gdf['經度'].mean()
    
    if fire_station_gdf is not None:
        stats['消防局總數'] = len(fire_station_gdf)
        stats['消防局地區數'] = fire_station_gdf['地區'].nunique()
        stats['消防局平均緯度'] = fire_station_gdf['緯度'].mean()
        stats['消防局平均經度'] = fire_station_gdf['經度'].mean()
    
    return stats

def main():
    """主函數"""
    # 頁面標題
    st.title("🚒 香港消防處服務儀表板")
    st.markdown("顯示香港救護站和消防局的實時數據")
    
    # 側邊欄
    with st.sidebar:
        st.header("🔧 控制面板")
        
        st.subheader("數據過濾")
        show_ambulance = st.checkbox("顯示救護站", value=True)
        show_fire_stations = st.checkbox("顯示消防局", value=True)
        
        st.subheader("地圖設置")
        map_zoom = st.slider("地圖縮放級別", 9, 15, 11)
        
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
        ambulance_gdf = fetch_ambulance_data() if show_ambulance else None
        fire_station_gdf = fetch_fire_station_data() if show_fire_stations else None
    
    # 顯示統計摘要
    st.header("📈 統計摘要")
    
    if ambulance_gdf is not None or fire_station_gdf is not None:
        stats = create_summary_stats(ambulance_gdf, fire_station_gdf)
        
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
    
    # 顯示地圖
    st.header("🗺️ 服務位置地圖")
    
    if show_ambulance or show_fire_stations:
        m = create_map(ambulance_gdf, fire_station_gdf)
        folium_static(m, width=1200, height=600)
    else:
        st.warning("請至少選擇一種服務類型來顯示地圖")
    
    # 顯示地區分布圖表
    if ambulance_gdf is not None and fire_station_gdf is not None:
        st.header("📊 地區分布")
        fig = create_district_chart(ambulance_gdf, fire_station_gdf)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 顯示數據表格
    st.header("📋 詳細數據")
    
    tab1, tab2 = st.tabs(["救護站數據", "消防局數據"])
    
    with tab1:
        if ambulance_gdf is not None:
            st.subheader("救護站列表")
            
            # 搜索和過濾
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("搜索救護站名稱或地址", key="amb_search")
            
            with col2:
                district_filter = st.multiselect(
                    "按地區過濾",
                    options=sorted(ambulance_gdf['地區'].unique()),
                    key="amb_district"
                )
            
            # 應用過濾
            filtered_df = ambulance_gdf.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['名稱'].str.contains(search_term, case=False, na=False) |
                    filtered_df['地址'].str.contains(search_term, case=False, na=False)
                ]
            
            if district_filter:
                filtered_df = filtered_df[filtered_df['地區'].isin(district_filter)]
            
            # 顯示表格
            st.dataframe(
                filtered_df.drop(columns=['geometry']).reset_index(drop=True),
                use_container_width=True,
                height=400
            )
            
            # 下載按鈕
            csv = filtered_df.drop(columns=['geometry']).to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載救護站數據 (CSV)",
                data=csv,
                file_name=f"香港救護站數據_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("未加載救護站數據")
    
    with tab2:
        if fire_station_gdf is not None:
            st.subheader("消防局列表")
            
            # 搜索和過濾
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("搜索消防局名稱或地址", key="fire_search")
            
            with col2:
                district_filter = st.multiselect(
                    "按地區過濾",
                    options=sorted(fire_station_gdf['地區'].unique()),
                    key="fire_district"
                )
            
            # 應用過濾
            filtered_df = fire_station_gdf.copy()
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['名稱'].str.contains(search_term, case=False, na=False) |
                    filtered_df['地址'].str.contains(search_term, case=False, na=False)
                ]
            
            if district_filter:
                filtered_df = filtered_df[filtered_df['地區'].isin(district_filter)]
            
            # 顯示表格
            st.dataframe(
                filtered_df.drop(columns=['geometry']).reset_index(drop=True),
                use_container_width=True,
                height=400
            )
            
            # 下載按鈕
            csv = filtered_df.drop(columns=['geometry']).to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載消防局數據 (CSV)",
                data=csv,
                file_name=f"香港消防局數據_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("未加載消防局數據")
    
    # 頁腳
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray;">
        <p>