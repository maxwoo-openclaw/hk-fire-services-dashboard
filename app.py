#!/usr/bin/env python3
"""
香港消防處服務儀表板 - 完整最終版本
包含所有功能：統計、圖表、搜索、過濾、導出
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

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
        df = df.dropna(subset=['名稱', '地區']).fillna('')
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
        df = df.dropna(subset=['名稱', '地區']).fillna('')
        return df
    except Exception as e:
        st.error(f"獲取消防局數據失敗: {e}")
        return pd.DataFrame()

def create_stats(ambulance_df, fire_station_df):
    """創建統計數據"""
    stats = {}
    
    if not ambulance_df.empty:
        stats['救護站總數'] = len(ambulance_df)
        stats['救護站地區數'] = ambulance_df['地區'].nunique()
    
    if not fire_station_df.empty:
        stats['消防局總數'] = len(fire_station_df)
        stats['消防局地區數'] = fire_station_df['地區'].nunique()
    
    if not ambulance_df.empty and not fire_station_df.empty:
        all_data = pd.concat([ambulance_df, fire_station_df])
        stats['總服務點數'] = len(all_data)
        stats['總地區數'] = all_data['地區'].nunique()
    
    return stats

def create_district_chart(ambulance_df, fire_station_df):
    """創建地區分布圖表"""
    if ambulance_df.empty or fire_station_df.empty:
        return None
    
    ambulance_counts = ambulance_df['地區'].value_counts().reset_index()
    ambulance_counts.columns = ['地區', '救護站數量']
    
    fire_station_counts = fire_station_df['地區'].value_counts().reset_index()
    fire_station_counts.columns = ['地區', '消防局數量']
    
    merged_counts = pd.merge(ambulance_counts, fire_station_counts, on='地區', how='outer').fillna(0)
    merged_counts = merged_counts.sort_values('救護站數量', ascending=False)
    
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
        title='各地區服務點分布',
        xaxis_title='地區',
        yaxis_title='數量',
        barmode='group',
        height=400,
        showlegend=True
    )
    
    return fig

def create_location_map(ambulance_df, fire_station_df):
    """創建位置散點圖"""
    if ambulance_df.empty and fire_station_df.empty:
        return None
    
    all_data = pd.DataFrame()
    if not ambulance_df.empty:
        all_data = pd.concat([all_data, ambulance_df])
    if not fire_station_df.empty:
        all_data = pd.concat([all_data, fire_station_df])
    
    # 過濾有效坐標
    valid_data = all_data.dropna(subset=['緯度', '經度'])
    if valid_data.empty:
        return None
    
    fig = px.scatter(
        valid_data,
        x='經度',
        y='緯度',
        color='類型',
        color_discrete_map={'救護站': 'blue', '消防局': 'red'},
        hover_name='名稱',
        hover_data=['地址', '地區', '電話'],
        title='服務點位置分布'
    )
    
    fig.update_layout(
        height=500,
        xaxis_title='經度',
        yaxis_title='緯度'
    )
    
    return fig

def main():
    """主函數"""
    # 頁面標題
    st.title("🚒 香港消防處服務儀表板")
    st.markdown("### 實時顯示香港救護站和消防局數據")
    
    # 側邊欄
    with st.sidebar:
        st.header("🔧 控制面板")
        
        st.subheader("數據顯示")
        show_ambulance = st.checkbox("顯示救護站", value=True)
        show_fire_stations = st.checkbox("顯示消防局", value=True)
        
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
    
    # 顯示統計摘要
    st.header("📈 統計摘要")
    
    if not ambulance_df.empty or not fire_station_df.empty:
        stats = create_stats(ambulance_df, fire_station_df)
        
        # 創建指標卡片
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
    
    # 顯示地區分布圖表
    if not ambulance_df.empty and not fire_station_df.empty:
        st.header("📊 地區分布")
        fig = create_district_chart(ambulance_df, fire_station_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # 顯示位置分布圖
    if (not ambulance_df.empty or not fire_station_df.empty):
        st.header("🗺️ 位置分布")
        map_fig = create_location_map(ambulance_df, fire_station_df)
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.info("無有效坐標數據顯示地圖")
    
    # 顯示詳細數據表格
    st.header("📋 詳細數據")
    
    # 創建選項卡
    tab1, tab2 = st.tabs(["救護站數據", "消防局數據"])
    
    with tab1:
        if not ambulance_df.empty:
            st.subheader(f"救護站列表 ({len(ambulance_df)} 個)")
            
            # 搜索和過濾
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("搜索救護站名稱或地址", key="amb_search")
            
            with col2:
                district_filter = st.multiselect(
                    "按地區過濾",
                    options=sorted(ambulance_df['地區'].unique()),
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
                filtered_df[['名稱', '地址', '地區', '電話', '緯度', '經度']].reset_index(drop=True),
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
            st.subheader(f"消防局列表 ({len(fire_station_df)} 個)")
            
            # 搜索和過濾
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("搜索消防局名稱或地址", key="fire_search")
            
            with col2:
                district_filter = st.multiselect(
                    "按地區過濾",
                    options=sorted(fire_station_df['地區'].unique()),
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
                filtered_df[['名稱', '地址', '地區', '電話', '緯度', '經度']].reset_index(drop=True),
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
    
    # 顯示合併數據
    if not ambulance_df.empty and not fire_station_df.empty:
        st.header("🔗 合併數據分析")
        
        all_data = pd.concat([ambulance_df, fire_station_df])
        
        # 地區統計
        st.subheader("各地區服務點總數")
        district_summary = all_data.groupby('地區').size().reset_index(name='服務點數量')
        district_summary = district_summary.sort_values('服務點數量', ascending=False)
        
        st.dataframe(
            district_summary,
            use_container_width=True,
            height=300
        )
        
        # 下載合併數據
        csv_all = all_data.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載所有數據 (CSV)",
            data=csv_all,
            file_name=f"香港消防處所有服務點_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # 頁腳
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray;">
        <p>香港消防處服務儀表板 • 數據來源: 香港政府地理數據平台</p>
        <p>最後更新: {}</p>
        <p>版本: 1.0 • <a href="https://github.com/maxwoo-openclaw/hk-fire-services-dashboard" target="_blank">GitHub項目</a></p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()