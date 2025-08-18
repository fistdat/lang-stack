import streamlit as st
import requests
import os
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from streamlit_echarts import st_echarts

# Prophet import with error handling
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    st.warning("⚠️ Prophet not available. Install with: pip install prophet")

st.set_page_config(
    page_title="Energy AI Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def generate_sample_energy_data():
    """Generate sample energy consumption data for 5 buildings"""
    buildings = [
        'Hog_education_Janell', 
        'Fox_education_Willis', 
        'Rat_office_Colby', 
        'Hog_office_Nia', 
        'Bear_education_Wilton'
    ]
    
    # Generate 6 months of data
    months = pd.date_range(start='2024-01-01', periods=6, freq='ME')
    
    # Sample consumption data (kWh) with realistic trends
    np.random.seed(42)
    data = []
    
    base_consumptions = [2_000_000, 1_800_000, 1_600_000, 1_400_000, 1_200_000]
    
    for i, building in enumerate(buildings):
        base = base_consumptions[i]
        for j, month in enumerate(months):
            # Add seasonal variation and growth trend
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * j / 12)
            growth_factor = 1 + (j * 0.05)  # 5% monthly growth
            noise = np.random.normal(0, 0.05)  # 5% noise
            
            consumption = base * seasonal_factor * growth_factor * (1 + noise)
            
            data.append({
                'Building': building,
                'Month': month.strftime('%Y-%m'),
                'Date': month,
                'Energy_Consumption_kWh': int(consumption),
                'Building_Type': 'Education' if 'education' in building else 'Office'
            })
    
    return pd.DataFrame(data)

def create_energy_trend_chart(df):
    """Create interactive energy consumption trend chart"""
    fig = go.Figure()
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    for i, building in enumerate(df['Building'].unique()):
        building_data = df[df['Building'] == building]
        
        fig.add_trace(go.Scatter(
            x=building_data['Date'],
            y=building_data['Energy_Consumption_kWh'],
            mode='lines+markers',
            name=building,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>{building}</b><br>' +
                         'Tháng: %{x|%Y-%m}<br>' +
                         'Tiêu thụ: %{y:,.0f} kWh<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': '📊 Xu hướng tiêu thụ năng lượng điện của 5 tòa nhà',
            'x': 0.5,
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title='Tháng',
        yaxis_title='Tiêu thụ năng lượng (kWh)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig

def create_energy_comparison_chart(df):
    """Create bar chart comparing total energy consumption by building"""
    total_consumption = df.groupby('Building')['Energy_Consumption_kWh'].sum().reset_index()
    total_consumption = total_consumption.sort_values('Energy_Consumption_kWh', ascending=False)
    
    fig = go.Figure(data=[
        go.Bar(
            x=total_consumption['Building'],
            y=total_consumption['Energy_Consumption_kWh'],
            marker_color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'],
            hovertemplate='<b>%{x}</b><br>' +
                         'Tổng tiêu thụ: %{y:,.0f} kWh<br>' +
                         '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': '🏆 Top 5 tòa nhà tiêu thụ năng lượng nhiều nhất',
            'x': 0.5,
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis_title='Tòa nhà',
        yaxis_title='Tổng tiêu thụ năng lượng (kWh)',
        template='plotly_white',
        height=500,
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig

def create_echarts_energy_trend(df):
    """Create ECharts energy consumption trend chart"""
    buildings = df['Building'].unique().tolist()
    months = df['Date'].dt.strftime('%Y-%m').unique().tolist()
    
    # Prepare series data
    series_data = []
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    for i, building in enumerate(buildings):
        building_data = df[df['Building'] == building].sort_values('Date')
        data_values = building_data['Energy_Consumption_kWh'].tolist()
        
        series_data.append({
            'name': building,
            'type': 'line',
            'smooth': True,
            'lineStyle': {'width': 3, 'color': colors[i % len(colors)]},
            'itemStyle': {'color': colors[i % len(colors)]},
            'emphasis': {'focus': 'series'},
            'data': data_values
        })
    
    option = {
        'title': {
            'text': '📊 Xu hướng tiêu thụ năng lượng điện của 5 tòa nhà',
            'left': 'center',
            'textStyle': {'fontSize': 18, 'color': '#2c3e50', 'fontWeight': 'bold'}
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'cross'},
            'formatter': '{b}<br/>{a}: {c} kWh'
        },
        'legend': {
            'data': buildings,
            'top': '10%',
            'textStyle': {'fontSize': 12}
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '10%',
            'top': '20%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'category',
            'boundaryGap': False,
            'data': months,
            'axisLabel': {'fontSize': 11},
            'name': 'Tháng',
            'nameLocation': 'middle',
            'nameGap': 25
        },
        'yAxis': {
            'type': 'value',
            'axisLabel': {
                'fontSize': 11,
                'formatter': '{value}'
            },
            'name': 'Tiêu thụ năng lượng (kWh)',
            'nameLocation': 'middle',
            'nameGap': 50,
            'splitLine': {'lineStyle': {'color': 'rgba(128,128,128,0.2)'}}
        },
        'series': series_data,
        'animation': True,
        'animationDuration': 1000
    }
    
    return option

def create_echarts_energy_comparison(df):
    """Create ECharts bar chart comparing total energy consumption"""
    total_consumption = df.groupby('Building')['Energy_Consumption_kWh'].sum().reset_index()
    total_consumption = total_consumption.sort_values('Energy_Consumption_kWh', ascending=False)
    
    buildings = total_consumption['Building'].tolist()
    values = total_consumption['Energy_Consumption_kWh'].tolist()
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    option = {
        'title': {
            'text': '🏆 Top 5 tòa nhà tiêu thụ năng lượng nhiều nhất',
            'left': 'center',
            'textStyle': {'fontSize': 18, 'color': '#2c3e50', 'fontWeight': 'bold'}
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'shadow'},
            'formatter': '{b}<br/>Tổng tiêu thụ: {c} kWh'
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '15%',
            'top': '15%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'category',
            'data': buildings,
            'axisLabel': {'fontSize': 10, 'rotate': 45},
            'name': 'Tòa nhà',
            'nameLocation': 'middle',
            'nameGap': 35
        },
        'yAxis': {
            'type': 'value',
            'axisLabel': {
                'fontSize': 11,
                'formatter': '{value}'
            },
            'name': 'Tổng tiêu thụ năng lượng (kWh)',
            'nameLocation': 'middle',
            'nameGap': 50,
            'splitLine': {'lineStyle': {'color': 'rgba(128,128,128,0.2)'}}
        },
        'series': [{
            'type': 'bar',
            'data': [{'value': val, 'itemStyle': {'color': colors[i % len(colors)]}} 
                    for i, val in enumerate(values)],
            'barWidth': '60%',
            'emphasis': {'itemStyle': {'shadowBlur': 10, 'shadowColor': 'rgba(0,0,0,0.3)'}}
        }],
        'animation': True,
        'animationDuration': 1000
    }
    
    return option

def create_echarts_energy_pie(df):
    """Create ECharts pie chart for energy distribution"""
    total_consumption = df.groupby('Building')['Energy_Consumption_kWh'].sum().reset_index()
    
    pie_data = []
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    
    for i, row in total_consumption.iterrows():
        pie_data.append({
            'value': row['Energy_Consumption_kWh'],
            'name': row['Building'],
            'itemStyle': {'color': colors[i % len(colors)]}
        })
    
    option = {
        'title': {
            'text': '🥧 Phân bố tiêu thụ năng lượng',
            'left': 'center',
            'textStyle': {'fontSize': 18, 'color': '#2c3e50', 'fontWeight': 'bold'}
        },
        'tooltip': {
            'trigger': 'item',
            'formatter': '{b}<br/>{c} kWh ({d}%)'
        },
        'legend': {
            'orient': 'vertical',
            'left': 'left',
            'top': 'middle',
            'textStyle': {'fontSize': 11}
        },
        'series': [{
            'type': 'pie',
            'radius': ['40%', '70%'],
            'center': ['60%', '50%'],
            'avoidLabelOverlap': False,
            'label': {
                'show': True,
                'position': 'outside',
                'formatter': '{b}: {d}%',
                'fontSize': 11
            },
            'labelLine': {'show': True},
            'data': pie_data,
            'emphasis': {
                'itemStyle': {
                    'shadowBlur': 10,
                    'shadowOffsetX': 0,
                    'shadowColor': 'rgba(0, 0, 0, 0.5)'
                }
            },
            'animationType': 'scale',
            'animationEasing': 'elasticOut'
        }]
    }
    
    return option

def generate_enhanced_energy_data():
    """Generate more realistic energy data for Prophet forecasting"""
    buildings = [
        'Hog_education_Janell', 
        'Fox_education_Willis', 
        'Rat_office_Colby', 
        'Hog_office_Nia', 
        'Bear_education_Wilton'
    ]
    
    # Generate 2 years of daily data for better forecasting
    start_date = pd.to_datetime('2023-01-01')
    end_date = pd.to_datetime('2024-12-31')
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    np.random.seed(42)
    data = []
    
    base_consumptions = [2_000_000, 1_800_000, 1_600_000, 1_400_000, 1_200_000]
    
    for i, building in enumerate(buildings):
        base = base_consumptions[i]
        
        for date in dates:
            # Seasonal patterns
            yearly_cycle = 1 + 0.2 * np.sin(2 * np.pi * date.dayofyear / 365.25)
            weekly_cycle = 1 + 0.1 * np.sin(2 * np.pi * date.weekday() / 7)
            
            # Holiday effects (reduced consumption on weekends)
            holiday_effect = 0.7 if date.weekday() >= 5 else 1.0
            
            # Trend (slight growth over time)
            days_since_start = (date - start_date).days
            trend = 1 + (days_since_start / 730) * 0.1  # 10% growth over 2 years
            
            # Random noise
            noise = np.random.normal(1, 0.05)
            
            consumption = base * yearly_cycle * weekly_cycle * holiday_effect * trend * noise
            
            data.append({
                'Building': building,
                'Date': date,
                'Energy_Consumption_kWh': max(int(consumption), 0),  # Ensure positive
                'Building_Type': 'Education' if 'education' in building else 'Office'
            })
    
    return pd.DataFrame(data)

def create_prophet_forecast(df, building_name, forecast_days=90):
    """Create Prophet forecast for a specific building"""
    if not PROPHET_AVAILABLE:
        return None, None
    
    # Filter data for specific building
    building_data = df[df['Building'] == building_name].copy()
    building_data = building_data.sort_values('Date')
    
    # Prepare data for Prophet
    prophet_df = building_data[['Date', 'Energy_Consumption_kWh']].rename(
        columns={'Date': 'ds', 'Energy_Consumption_kWh': 'y'}
    )
    
    # Initialize Prophet model with seasonality
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10.0
    )
    
    # Fit model
    with st.spinner(f"🔮 Training Prophet model for {building_name}..."):
        model.fit(prophet_df)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=forecast_days)
    forecast = model.predict(future)
    
    return model, forecast

def create_prophet_plotly_chart(model, forecast, building_name):
    """Create interactive Plotly chart from Prophet forecast"""
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=forecast['ds'][:len(model.history_dates)],
        y=forecast['yhat'][:len(model.history_dates)],
        mode='lines',
        name='Historical',
        line=dict(color='#667eea', width=2)
    ))
    
    # Forecast
    forecast_start = len(model.history_dates)
    fig.add_trace(go.Scatter(
        x=forecast['ds'][forecast_start:],
        y=forecast['yhat'][forecast_start:],
        mode='lines',
        name='Forecast',
        line=dict(color='#f5576c', width=2, dash='dash')
    ))
    
    # Confidence intervals
    fig.add_trace(go.Scatter(
        x=list(forecast['ds'][forecast_start:]) + list(forecast['ds'][forecast_start:][::-1]),
        y=list(forecast['yhat_upper'][forecast_start:]) + list(forecast['yhat_lower'][forecast_start:][::-1]),
        fill='tonexty',
        fillcolor='rgba(245, 87, 108, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Interval',
        showlegend=False
    ))
    
    fig.update_layout(
        title=f'🔮 Energy Consumption Forecast - {building_name}',
        xaxis_title='Date',
        yaxis_title='Energy Consumption (kWh)',
        template='plotly_white',
        height=500
    )
    
    return fig

def create_prophet_echarts_chart(model, forecast, building_name):
    """Create ECharts version of Prophet forecast"""
    if not model or forecast is None:
        return None
    
    # Prepare data
    historical_dates = [d.strftime('%Y-%m-%d') for d in forecast['ds'][:len(model.history_dates)]]
    historical_values = forecast['yhat'][:len(model.history_dates)].tolist()
    
    forecast_start = len(model.history_dates)
    forecast_dates = [d.strftime('%Y-%m-%d') for d in forecast['ds'][forecast_start:]]
    forecast_values = forecast['yhat'][forecast_start:].tolist()
    forecast_upper = forecast['yhat_upper'][forecast_start:].tolist()
    forecast_lower = forecast['yhat_lower'][forecast_start:].tolist()
    
    option = {
        'title': {
            'text': f'🔮 Energy Consumption Forecast - {building_name}',
            'left': 'center',
            'textStyle': {'fontSize': 18, 'color': '#2c3e50', 'fontWeight': 'bold'}
        },
        'tooltip': {
            'trigger': 'axis',
            'axisPointer': {'type': 'cross'}
        },
        'legend': {
            'data': ['Historical', 'Forecast', 'Confidence Range'],
            'top': '10%'
        },
        'grid': {
            'left': '3%',
            'right': '4%',
            'bottom': '10%',
            'top': '20%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'category',
            'data': historical_dates + forecast_dates,
            'axisLabel': {'fontSize': 11}
        },
        'yAxis': {
            'type': 'value',
            'axisLabel': {'fontSize': 11},
            'name': 'Energy Consumption (kWh)',
            'nameLocation': 'middle',
            'nameGap': 50
        },
        'series': [
            {
                'name': 'Historical',
                'type': 'line',
                'data': historical_values + [None] * len(forecast_values),
                'lineStyle': {'color': '#667eea', 'width': 3},
                'itemStyle': {'color': '#667eea'},
                'smooth': True
            },
            {
                'name': 'Forecast',
                'type': 'line',
                'data': [None] * len(historical_values) + forecast_values,
                'lineStyle': {'color': '#f5576c', 'width': 3, 'type': 'dashed'},
                'itemStyle': {'color': '#f5576c'},
                'smooth': True
            },
            {
                'name': 'Confidence Range',
                'type': 'line',
                'data': [None] * len(historical_values) + forecast_upper,
                'lineStyle': {'opacity': 0},
                'areaStyle': {'color': 'rgba(245, 87, 108, 0.2)'},
                'stack': 'confidence',
                'symbol': 'none'
            },
            {
                'name': 'Confidence Range Lower',
                'type': 'line',
                'data': [None] * len(historical_values) + forecast_lower,
                'lineStyle': {'opacity': 0},
                'areaStyle': {'color': 'rgba(245, 87, 108, 0.2)'},
                'stack': 'confidence',
                'symbol': 'none',
                'showInLegend': False
            }
        ],
        'animation': True,
        'animationDuration': 1000
    }
    
    return option

def langflow_api_call(input_value: str, api_key: str, url: str) -> Optional[Dict[Any, Any]]:
    """
    Make API call to Langflow
    """
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": input_value
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Only add API key if provided
    if api_key and api_key.strip() and api_key != "your_api_key_here":
        headers["x-api-key"] = api_key
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request error: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {e}")
        return None

def main():
    # Sidebar for configuration and controls
    with st.sidebar:
        st.title("🔧 System Configuration")
        
        # Connection status
        st.subheader("📡 Connection Status")
        api_url = os.environ.get("LANGFLOW_API_URL", "")
        if api_url:
            st.success("✅ AI System Connected")
            st.caption(f"🔗 Endpoint: ...{api_url[-30:]}")
        else:
            st.error("❌ AI System Disconnected")
            st.caption("Check environment configuration")
        
        st.divider()
        
        # Chat controls
        st.subheader("💬 Chat Controls")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            total_messages = len(st.session_state.get("messages", []))
            st.metric("Messages", total_messages)
        
        st.divider()
        
        # Chart type selection
        st.subheader("📊 Chart Type")
        chart_type = st.selectbox(
            "Choose visualization:",
            options=["plotly", "echarts"],
            format_func=lambda x: "📈 Plotly Charts" if x == "plotly" else "🎨 ECharts"
        )
        st.session_state.chart_engine = chart_type
        
        # Prophet forecasting option
        st.subheader("🔮 Advanced Analytics")
        enable_prophet = st.checkbox(
            "Enable Prophet Forecasting", 
            value=False,
            help="Use Facebook Prophet for AI-powered energy consumption forecasting",
            disabled=not PROPHET_AVAILABLE
        )
        st.session_state.enable_prophet = enable_prophet
        
        if enable_prophet and PROPHET_AVAILABLE:
            forecast_days = st.slider(
                "Forecast Period (days):",
                min_value=30,
                max_value=365,
                value=90,
                step=30,
                help="Number of days to forecast into the future"
            )
            st.session_state.forecast_days = forecast_days
            
            building_for_forecast = st.selectbox(
                "Building for detailed forecast:",
                options=['Hog_education_Janell', 'Fox_education_Willis', 'Rat_office_Colby', 
                        'Hog_office_Nia', 'Bear_education_Wilton'],
                help="Select building for Prophet time series analysis"
            )
            st.session_state.forecast_building = building_for_forecast
        elif not PROPHET_AVAILABLE:
            st.info("📦 Install Prophet to enable forecasting:\n```\npip install prophet\n```")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        if st.button("📊 Top 5 Energy Consumers", use_container_width=True):
            st.session_state.quick_prompt = "Liệt kê 5 tòa nhà tiêu thụ điện nhiều nhất"
            st.session_state.show_chart = "comparison"
        if st.button("💡 Optimization Tips", use_container_width=True):
            st.session_state.quick_prompt = "Đưa ra 3 đề xuất tối ưu hóa năng lượng"
        if st.button("📈 Energy Trends", use_container_width=True):
            st.session_state.quick_prompt = "Phân tích xu hướng tiêu thụ năng lượng"
            st.session_state.show_chart = "trend"
        if st.button("🥧 Energy Distribution", use_container_width=True):
            st.session_state.quick_prompt = "Phân bố tiêu thụ năng lượng theo tòa nhà"
            st.session_state.show_chart = "pie"
        if st.button("📊 Vẽ biểu đồ xu hướng", use_container_width=True):
            st.session_state.quick_prompt = "Vẽ biểu đồ phân tích xu hướng tiêu thụ năng lượng điện của 5 tòa nhà"
            st.session_state.show_chart = "trend"
        if st.button("🔮 Dự báo năng lượng", use_container_width=True, disabled=not PROPHET_AVAILABLE):
            st.session_state.quick_prompt = "Dự báo tiêu thụ năng lượng 3 tháng tới"
            st.session_state.show_chart = "forecast"
        
        st.divider()
        
        # About section
        st.subheader("ℹ️ About")
        st.caption("🎓 **FPT University**")
        st.caption("📝 Master Thesis Project")
        st.caption("👨‍💻 Hoang Tuan Dat")
        st.caption("👨‍🏫 Assoc. Prof. Phan Duy Hung")
        st.caption("© 2025")

    # Custom CSS for modern styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin: 0.5rem 0;
        font-weight: 300;
    }
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        min-height: 600px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border: 1px solid #e0e6ed;
    }
    .stChatMessage {
        margin-bottom: 1rem;
    }
    .example-queries {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .metric-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e0e6ed;
        padding: 0.75rem 1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Modern header with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Energy AI Optimizer</h1>
        <p>Multi-Agent System for Building Energy Analysis & Optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get API configuration from environment (hidden from UI)
    api_key = os.environ.get("LANGFLOW_API_KEY", "")
    api_url = os.environ.get("LANGFLOW_API_URL", "http://host.docker.internal:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761")
    
    # Feature overview cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Energy Analysis</h4>
            <p>Advanced analytics for building energy consumption patterns and trends</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 AI Optimization</h4>
            <p>Intelligent recommendations for energy efficiency improvements</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📈 Real-time Insights</h4>
            <p>Live monitoring and predictive analytics for optimal performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Example queries section
    st.markdown("""
    <div class="example-queries">
        <h4>💡 Example Queries</h4>
        <p>Try asking about:</p>
        <ul>
            <li>📊 "Liệt kê 5 tòa nhà tiêu thụ điện nhiều nhất"</li>
            <li>📈 "Vẽ biểu đồ phân tích xu hướng tiêu thụ năng lượng điện của 5 tòa nhà"</li>
            <li>💡 "Đưa ra 3 đề xuất tối ưu hóa năng lượng"</li>
            <li>🏢 "So sánh hiệu suất năng lượng giữa các tòa nhà"</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Modern chat interface with container styling
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.subheader("💬 AI Assistant Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "👋 Chào mừng bạn đến với Energy AI Optimizer!\n\nTôi là AI assistant chuyên về phân tích và tối ưu hóa năng lượng tòa nhà. Tôi có thể giúp bạn:\n\n🔍 **Phân tích dữ liệu**: Xem xét các mẫu tiêu thụ năng lượng\n💡 **Đề xuất tối ưu**: Cải thiện hiệu suất năng lượng\n📊 **Báo cáo chi tiết**: Thống kê và xu hướng\n🏢 **So sánh tòa nhà**: Đánh giá hiệu suất tương đối\n\nHãy bắt đầu bằng cách hỏi tôi về năng lượng tòa nhà của bạn!"
        })
    
    # Display chat messages with enhanced styling
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle quick action prompts
    if hasattr(st.session_state, 'quick_prompt'):
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the quick prompt
        if api_url:
            with st.chat_message("assistant"):
                with st.spinner("🤔 Đang xử lý..."):
                    response = langflow_api_call(prompt, api_key, api_url)
                    
                    if response:
                        response_text = "No response text found"
                        try:
                            if isinstance(response, dict) and "outputs" in response:
                                outputs = response["outputs"]
                                if isinstance(outputs, list) and len(outputs) > 0:
                                    first_output = outputs[0]
                                    if "outputs" in first_output and isinstance(first_output["outputs"], list) and len(first_output["outputs"]) > 0:
                                        nested_output = first_output["outputs"][0]
                                        if "results" in nested_output and "message" in nested_output["results"]:
                                            message = nested_output["results"]["message"]
                                            if "text" in message:
                                                response_text = message["text"]
                                            elif "data" in message and "text" in message["data"]:
                                                response_text = message["data"]["text"]
                            
                            if response_text == "No response text found":
                                if "result" in response:
                                    response_text = str(response["result"])
                                elif "message" in response:
                                    response_text = str(response["message"])
                                else:
                                    response_text = json.dumps(response, indent=2)
                                    
                        except Exception as e:
                            response_text = f"Error parsing response: {str(e)}"
                        
                        st.markdown(response_text)
                        
                        # Show chart if requested
                        if hasattr(st.session_state, 'show_chart'):
                            chart_type = st.session_state.show_chart
                            del st.session_state.show_chart
                            
                            df = generate_sample_energy_data()
                            chart_engine = getattr(st.session_state, 'chart_engine', 'plotly')
                            
                            if chart_engine == "echarts":
                                if chart_type == "trend":
                                    option = create_echarts_energy_trend(df)
                                    st_echarts(options=option, height="500px")
                                elif chart_type == "comparison":
                                    option = create_echarts_energy_comparison(df)
                                    st_echarts(options=option, height="500px")
                                elif chart_type == "pie":
                                    option = create_echarts_energy_pie(df)
                                    st_echarts(options=option, height="500px")
                            else:
                                if chart_type == "trend":
                                    fig = create_energy_trend_chart(df)
                                    st.plotly_chart(fig, use_container_width=True)
                                elif chart_type == "comparison":
                                    fig = create_energy_comparison_chart(df)
                                    st.plotly_chart(fig, use_container_width=True)
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_text
                        })
        st.rerun()
    
    # Enhanced chat input with placeholder
    if prompt := st.chat_input("💬 Hỏi về tối ưu hóa năng lượng... (ví dụ: 'Liệt kê 5 tòa nhà tiêu thụ điện nhiều nhất')"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Check if user is asking for charts first
        chart_keywords = [
            "biểu đồ", "chart", "graph", "vẽ", "xu hướng", "trend", 
            "phân tích", "analysis", "so sánh", "compare", "top 5",
            "phân bố", "distribution", "pie", "tròn", 
            "dự báo", "forecast", "prediction", "tương lai", "future"
        ]
        should_show_chart = any(keyword in prompt.lower() for keyword in chart_keywords)
        
        # Debug info in sidebar
        if should_show_chart:
            with st.sidebar:
                st.success(f"🎯 Chart detected! Keywords found: {[k for k in chart_keywords if k in prompt.lower()]}")
        else:
            with st.sidebar:
                st.info(f"🔍 No chart keywords in: '{prompt[:50]}...'")
        
        # Get response from Langflow
        if api_url:
            with st.chat_message("assistant"):
                with st.spinner("🤔 Đang phân tích..."):
                    response = langflow_api_call(prompt, api_key, api_url)
                    
                    if response:
                        # Extract the actual response text from Langflow
                        response_text = "No response text found"
                        try:
                            # Try to extract meaningful response from the nested structure
                            if isinstance(response, dict) and "outputs" in response:
                                outputs = response["outputs"]
                                if isinstance(outputs, list) and len(outputs) > 0:
                                    first_output = outputs[0]
                                    if "outputs" in first_output and isinstance(first_output["outputs"], list) and len(first_output["outputs"]) > 0:
                                        nested_output = first_output["outputs"][0]
                                        if "results" in nested_output and "message" in nested_output["results"]:
                                            message = nested_output["results"]["message"]
                                            if "text" in message:
                                                response_text = message["text"]
                                            elif "data" in message and "text" in message["data"]:
                                                response_text = message["data"]["text"]
                            
                            # Fallback: try other common paths
                            if response_text == "No response text found":
                                if "result" in response:
                                    response_text = str(response["result"])
                                elif "message" in response:
                                    response_text = str(response["message"])
                                else:
                                    response_text = json.dumps(response, indent=2)
                                    
                        except Exception as e:
                            response_text = f"Error parsing response: {str(e)}"
                        
                        st.markdown(response_text)
                        
                        # Show charts if requested
                        if should_show_chart:
                            st.info("🎨 Generating chart visualization...")
                        
                        # Always show chart if keywords detected
                        if should_show_chart:
                            # Check if Prophet forecasting is requested
                            enable_prophet = getattr(st.session_state, 'enable_prophet', False)
                            is_forecast_request = any(word in prompt.lower() for word in ["dự báo", "forecast", "prediction", "tương lai", "future"])
                            
                            if is_forecast_request and enable_prophet and PROPHET_AVAILABLE:
                                # Use enhanced data for Prophet
                                df = generate_enhanced_energy_data()
                                forecast_building = getattr(st.session_state, 'forecast_building', 'Hog_education_Janell')
                                forecast_days = getattr(st.session_state, 'forecast_days', 90)
                                chart_engine = getattr(st.session_state, 'chart_engine', 'plotly')
                                
                                st.subheader(f"🔮 Prophet Forecast - {forecast_building}")
                                
                                # Create Prophet forecast
                                model, forecast = create_prophet_forecast(df, forecast_building, forecast_days)
                                
                                if model and forecast is not None:
                                    if chart_engine == "echarts":
                                        option = create_prophet_echarts_chart(model, forecast, forecast_building)
                                        if option:
                                            st_echarts(options=option, height="600px")
                                    else:
                                        fig = create_prophet_plotly_chart(model, forecast, forecast_building)
                                        st.plotly_chart(fig, use_container_width=True)
                                    
                                    # Show forecast summary
                                    with st.expander("📈 Forecast Summary"):
                                        forecast_df = forecast.tail(forecast_days)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
                                        forecast_df.columns = ['Date', 'Predicted (kWh)', 'Lower Bound', 'Upper Bound']
                                        st.dataframe(forecast_df, hide_index=True)
                                        
                                        # Key insights
                                        avg_forecast = forecast['yhat'].tail(forecast_days).mean()
                                        current_avg = df[df['Building'] == forecast_building]['Energy_Consumption_kWh'].tail(30).mean()
                                        change_pct = ((avg_forecast - current_avg) / current_avg) * 100
                                        
                                        st.metric(
                                            "Predicted Average Consumption", 
                                            f"{avg_forecast:,.0f} kWh",
                                            f"{change_pct:+.1f}% vs last 30 days"
                                        )
                                else:
                                    st.error("❌ Failed to generate Prophet forecast")
                            else:
                                # Use regular data for standard charts
                                df = generate_sample_energy_data()
                                chart_engine = getattr(st.session_state, 'chart_engine', 'plotly')
                            
                            if any(word in prompt.lower() for word in ["xu hướng", "trend", "biểu đồ"]):
                                st.subheader("📊 Biểu đồ xu hướng tiêu thụ năng lượng")
                                if chart_engine == "echarts":
                                    option = create_echarts_energy_trend(df)
                                    st_echarts(options=option, height="500px")
                                else:
                                    fig = create_energy_trend_chart(df)
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Show data table
                                with st.expander("📋 Xem dữ liệu chi tiết"):
                                    st.dataframe(df.pivot(index='Month', columns='Building', values='Energy_Consumption_kWh'))
                            
                            if any(word in prompt.lower() for word in ["top 5", "liệt kê", "so sánh", "nhiều nhất"]):
                                st.subheader("🏆 Bảng xếp hạng tiêu thụ năng lượng")
                                if chart_engine == "echarts":
                                    option = create_echarts_energy_comparison(df)
                                    st_echarts(options=option, height="500px")
                                else:
                                    fig = create_energy_comparison_chart(df)
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Show ranking table
                                with st.expander("📊 Bảng thống kê"):
                                    total_consumption = df.groupby('Building')['Energy_Consumption_kWh'].sum().reset_index()
                                    total_consumption = total_consumption.sort_values('Energy_Consumption_kWh', ascending=False)
                                    total_consumption['Rank'] = range(1, len(total_consumption) + 1)
                                    total_consumption['Energy_Consumption_kWh'] = total_consumption['Energy_Consumption_kWh'].apply(lambda x: f"{x:,.0f} kWh")
                                    st.dataframe(total_consumption[['Rank', 'Building', 'Energy_Consumption_kWh']], hide_index=True)
                            
                            if any(word in prompt.lower() for word in ["phân bố", "distribution", "pie", "tròn"]):
                                st.subheader("🥧 Phân bố tiêu thụ năng lượng")
                                if chart_engine == "echarts":
                                    option = create_echarts_energy_pie(df)
                                    st_echarts(options=option, height="500px")
                                else:
                                    st.info("Pie chart chỉ có sẵn với ECharts engine. Vui lòng chọn ECharts trong sidebar.")
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_text
                        })
                    else:
                        error_msg = "Sorry, I couldn't process your request. Please check the API configuration."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
        else:
            with st.chat_message("assistant"):
                error_msg = "Hệ thống AI chưa được cấu hình. Tôi sẽ hiển thị biểu đồ dữ liệu mẫu cho bạn."
                st.markdown(error_msg)
                
                # Show charts even without API
                if should_show_chart:
                    # Check if Prophet forecasting is requested
                    enable_prophet = getattr(st.session_state, 'enable_prophet', False)
                    is_forecast_request = any(word in prompt.lower() for word in ["dự báo", "forecast", "prediction", "tương lai", "future"])
                    
                    if is_forecast_request and enable_prophet and PROPHET_AVAILABLE:
                        # Use enhanced data for Prophet
                        df = generate_enhanced_energy_data()
                        forecast_building = getattr(st.session_state, 'forecast_building', 'Hog_education_Janell')
                        forecast_days = getattr(st.session_state, 'forecast_days', 90)
                        chart_engine = getattr(st.session_state, 'chart_engine', 'plotly')
                        
                        st.subheader(f"🔮 Prophet Forecast - {forecast_building}")
                        
                        # Create Prophet forecast
                        model, forecast = create_prophet_forecast(df, forecast_building, forecast_days)
                        
                        if model and forecast is not None:
                            if chart_engine == "echarts":
                                option = create_prophet_echarts_chart(model, forecast, forecast_building)
                                if option:
                                    st_echarts(options=option, height="600px")
                            else:
                                fig = create_prophet_plotly_chart(model, forecast, forecast_building)
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Show forecast summary
                            with st.expander("📈 Forecast Summary"):
                                forecast_df = forecast.tail(forecast_days)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
                                forecast_df.columns = ['Date', 'Predicted (kWh)', 'Lower Bound', 'Upper Bound']
                                st.dataframe(forecast_df, hide_index=True)
                        else:
                            st.error("❌ Failed to generate Prophet forecast")
                    else:
                        # Use regular data for standard charts
                        df = generate_sample_energy_data()
                        chart_engine = getattr(st.session_state, 'chart_engine', 'plotly')
                    
                    if any(word in prompt.lower() for word in ["xu hướng", "trend", "biểu đồ"]):
                        st.subheader("📊 Biểu đồ xu hướng tiêu thụ năng lượng")
                        if chart_engine == "echarts":
                            option = create_echarts_energy_trend(df)
                            st_echarts(options=option, height="500px")
                        else:
                            fig = create_energy_trend_chart(df)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📋 Xem dữ liệu chi tiết"):
                            st.dataframe(df.pivot(index='Month', columns='Building', values='Energy_Consumption_kWh'))
                    
                    if any(word in prompt.lower() for word in ["top 5", "liệt kê", "so sánh", "nhiều nhất"]):
                        st.subheader("🏆 Bảng xếp hạng tiêu thụ năng lượng")
                        if chart_engine == "echarts":
                            option = create_echarts_energy_comparison(df)
                            st_echarts(options=option, height="500px")
                        else:
                            fig = create_energy_comparison_chart(df)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📊 Bảng thống kê"):
                            total_consumption = df.groupby('Building')['Energy_Consumption_kWh'].sum().reset_index()
                            total_consumption = total_consumption.sort_values('Energy_Consumption_kWh', ascending=False)
                            total_consumption['Rank'] = range(1, len(total_consumption) + 1)
                            total_consumption['Energy_Consumption_kWh'] = total_consumption['Energy_Consumption_kWh'].apply(lambda x: f"{x:,.0f} kWh")
                            st.dataframe(total_consumption[['Rank', 'Building', 'Energy_Consumption_kWh']], hide_index=True)
                    
                    if any(word in prompt.lower() for word in ["phân bố", "distribution", "pie", "tròn"]):
                        st.subheader("🥧 Phân bố tiêu thụ năng lượng")
                        if chart_engine == "echarts":
                            option = create_echarts_energy_pie(df)
                            st_echarts(options=option, height="500px")
                        else:
                            st.info("Pie chart chỉ có sẵn với ECharts engine. Vui lòng chọn ECharts trong sidebar.")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })

if __name__ == "__main__":
    main()