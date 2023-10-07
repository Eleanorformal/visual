import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as plt
import datetime
import altair as alt
import plotly.express as px
import plotly.graph_objects as go

# 创建侧边栏
st.sidebar.title('选择文件并筛选日期')

# 上传文档
uploaded_file = st.sidebar.file_uploader("上传CSV文件", type=["csv"])

# 初始化一个虚拟的数据框
data = pd.DataFrame()

# 检查是否成功上传文件
if uploaded_file is not None:
    st.sidebar.success("文件上传成功！")

    # 加载数据
    data = pd.read_csv(uploaded_file, encoding='GBK')

    # 将日期列转换为日期时间格式
    if 'data_date' in data.columns:
        data['data_date'] = pd.to_datetime(data['data_date'])

        # 获取日期范围
        min_date = data['data_date'].min()
        max_date = data['data_date'].max()

        # 计算默认日期为当前日期前一天
        default_date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=1))

        selected_start_date = pd.to_datetime(st.sidebar.date_input("选择起始日期", min_value=min_date, max_value=max_date, value=default_date))
        selected_end_date = pd.to_datetime(st.sidebar.date_input("选择结束日期", min_value=min_date, max_value=max_date, value=max_date))

    # 根据所选日期范围筛选数据
    if 'data_date' in data.columns:
        data = data[(data['data_date'] >= selected_start_date) & (data['data_date'] <= selected_end_date)]

        st.title('ott 每周数据展示')
        
        for _ in range(2):
            st.markdown("<br>", unsafe_allow_html=True)
            
            
        latest_date = data['data_date'].max()
        latest_data_mau = data[(data['data_date'] == latest_date) & (data['region'] == '总体')]
        latest_data_conversion = data[(data['data_date'] == latest_date) & (data['region'] == '总体')]
        col1, col2 = st.columns(2)
        if not latest_data_mau.empty:
            latest_mau = latest_data_mau['duration_uv_30_days'].values[0]
            col1.markdown(f'<div style="font-size: 20px; background-color: deepskyblue; color: white; padding: 9px; text-align: center; border-radius: 15px;">'
                        f'<span style="font-size: 20px;">OTT 在线视频用户规模 MAU</span><br/><span style="font-size: 36px;">{latest_mau}</span>'
                        f'</div>', unsafe_allow_html=True)
        else:
            st.warning('找不到总体 MAU 数据')
            

        if not latest_data_conversion.empty:
            latest_conversion = latest_data_conversion['mau conversion'].values[0]

            col2.markdown(f'<div style="font-size: 20px; background-color: dodgerblue; color: white; padding: 9px; text-align: center; border-radius: 15px;">'
                        f'<span style="font-size: 20px;">30 天 SDK 调起到实际起播转化率</span><br/><span style="font-size: 36px;">{latest_conversion}</span>'
                        f'</div>', unsafe_allow_html=True)
        else:
            st.warning('找不到总体转化率数据')

        for _ in range(2):
            st.markdown("<br>", unsafe_allow_html=True)
            
            
        st.write('#### OTT 访问人数趋势图')
        selected_region = st.selectbox('折线图选择区域', data['region'].unique())
        filtered_data = data[data['region'] == selected_region]
        fig = px.line(filtered_data, x='data_date', y='ott_show_uv_last_day',text='ott_show_uv_last_day')
        fig.update_layout(yaxis=dict(overlaying='y', side='left'))
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig)
        
        
        st.write('#### 总体 OTT 转化率漏斗图')
        selected_region1 = st.selectbox('漏斗图选择区域', data['region'].unique())
        filtered_data = data[data['region'] == selected_region1]
        latest_data = filtered_data.iloc[-1]
        fig1 = go.Figure()
        fig1.add_trace(go.Funnel(
            name='ott_show_uv_last_day',
            y=['ott_show_uv_last_day', 'ott_real_show_uv', 'prepare_uv_last_day', 'duration_uv_last_day'],
            x=latest_data[['ott_show_uv_last_day', 'ott_real_show_uv', 'prepare_uv_last_day', 'duration_uv_last_day']],
            textinfo="value+text+percent initial",
            text=latest_data[['ott_show_uv_last_day', 'ott_real_show_uv', 'prepare_uv_last_day', 'duration_uv_last_day']].astype(str) + ' (' + ((latest_data[['ott_show_uv_last_day', 'ott_real_show_uv', 'prepare_uv_last_day', 'duration_uv_last_day']].astype(float) / latest_data['ott_show_uv_last_day']).round(2)).astype(str) + ')',
            marker=dict(
                color=['blue', 'dodgerblue', 'deepskyblue', 'aqua']  # 为每个阶段指定颜色
            )
        ))
        fig1.update_layout(
            funnelmode="overlay",  # 设置漏斗模式为 'overlay'
            showlegend=True,
        )
        st.plotly_chart(fig1)
        
        
        st.write('#### 详情页播放时长趋势图')
        fig2 = px.line(data, x='data_date', y='average_video_duration_in_minutes_last_day', color='region', text='average_video_duration_in_minutes_last_day')
        fig2.update_xaxes(showgrid=False)
        fig2.update_yaxes(showgrid=False)
        st.plotly_chart(fig2)
        
        
        st.write('#### OTT 人均播放时长详情页播放时长趋势图')
        fig3 = px.line(data, x='data_date', y='average_duration_in_minutes', color='region', text='average_duration_in_minutes')
        fig3.update_xaxes(showgrid=False)
        fig3.update_yaxes(showgrid=False)
        st.plotly_chart(fig3)
        selected_regions = st.multiselect('选择地区', data['region'].unique(), default=['东南亚', '南亚', '中东'])
        filtered_data = data[data['region'].isin(selected_regions)]
        st.write('#### 在线视频用户规模 DAU 堆积图')
        fig = px.area(filtered_data, x='data_date', y='duration_uv_last_day', color='region', text='duration_uv_last_day')
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig)
        
        
        st.write('### 历史数据')
        st.dataframe(data)