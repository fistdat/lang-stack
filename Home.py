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

# Try to import leafmap, fallback to folium if not available
try:
    import leafmap.foliumap as leafmap
    LEAFMAP_AVAILABLE = True
except ImportError:
    import folium
    LEAFMAP_AVAILABLE = False

# Prophet import with error handling
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

st.set_page_config(
    page_title="Energy AI Optimizer - EAIO",
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

def langflow_api_call(input_value: str, api_key: str, url: str) -> Optional[Dict[Any, Any]]:
    """Make API call to Langflow"""
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

def create_gis_map():
    """Create GIS map as secondary feature"""
    # Energy infrastructure data for Vietnam
    energy_plants = [
        {"name": "Hoa Lac Solar", "lat": 21.0094, "lon": 105.5238, "type": "Solar", "capacity": "450 MW", "status": "Active"},
        {"name": "Mui Dinh Wind", "lat": 11.6847, "lon": 109.2432, "type": "Wind", "capacity": "99 MW", "status": "Active"},
        {"name": "Song Hau Thermal", "lat": 10.1699, "lon": 105.6037, "type": "Thermal", "capacity": "1200 MW", "status": "Active"},
        {"name": "Da Mi Hydro", "lat": 11.9500, "lon": 108.4500, "type": "Hydro", "capacity": "175 MW", "status": "Active"},
        {"name": "Ninh Thuan Solar", "lat": 11.6739, "lon": 108.8629, "type": "Solar", "capacity": "330 MW", "status": "Active"},
        {"name": "Bac Lieu Wind", "lat": 9.2847, "lon": 105.7222, "type": "Wind", "capacity": "80 MW", "status": "Maintenance"},
        {"name": "Ialy Hydro", "lat": 14.1167, "lon": 108.0333, "type": "Hydro", "capacity": "720 MW", "status": "Active"},
        {"name": "Vinh Tan Thermal", "lat": 11.4167, "lon": 108.9333, "type": "Thermal", "capacity": "2200 MW", "status": "Active"}
    ]
    
    if LEAFMAP_AVAILABLE:
        m = leafmap.Map(center=[14.0, 108.0], zoom=6)
        m.add_basemap("OpenStreetMap")
        
        # Add markers for each plant
        for plant in energy_plants:
            # Color based on type
            if plant["type"] == "Solar":
                color = "orange"
            elif plant["type"] == "Wind":
                color = "blue"
            elif plant["type"] == "Hydro":
                color = "green"
            else:  # Thermal
                color = "red"
            
            # Different icon for maintenance
            if plant["status"] == "Maintenance":
                color = "gray"
            
            popup_content = f"""
            <b>{plant['name']}</b><br>
            Type: {plant['type']}<br>
            Capacity: {plant['capacity']}<br>
            Status: {plant['status']}
            """
            
            m.add_marker(
                location=[plant["lat"], plant["lon"]],
                popup=popup_content,
                icon_color=color
            )
        
        return m
    else:
        # Fallback to folium
        import streamlit.components.v1 as components
        
        m = folium.Map(location=[14.0, 108.0], zoom_start=6)
        
        for plant in energy_plants:
            # Color based on type
            if plant["type"] == "Solar":
                color = "orange"
            elif plant["type"] == "Wind":
                color = "blue"
            elif plant["type"] == "Hydro":
                color = "green"
            else:  # Thermal
                color = "red"
            
            # Different icon for maintenance
            if plant["status"] == "Maintenance":
                color = "gray"
            
            popup_content = f"""
            {plant['name']}<br>
            Type: {plant['type']}<br>
            Capacity: {plant['capacity']}<br>
            Status: {plant['status']}
            """
            
            folium.Marker(
                location=[plant["lat"], plant["lon"]],
                popup=popup_content,
                icon=folium.Icon(color=color)
            ).add_to(m)
        
        return m

def main():
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white !important;
        font-size: 1.6rem;
        margin-bottom: 0.3rem;
        font-weight: 600;
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 0.9rem;
        margin: 0.2rem 0;
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
        min-height: 400px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border: 1px solid #e0e6ed;
    }
    .gis-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border: 1px solid #e0e6ed;
    }
    .stChatMessage {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration and controls
    with st.sidebar:
        st.title("🔧 EAIO System")
        
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
        
        # Display mode selection
        st.subheader("🎛️ Display Mode")
        display_mode = st.radio(
            "Select primary focus:",
            options=["EAIO Chatbot", "GIS Map + Chat"],
            index=0,
            help="Choose whether to focus on chatbot or show GIS alongside"
        )
        st.session_state.display_mode = display_mode
        
        # Chart type selection
        st.subheader("📊 Chart Engine")
        chart_type = st.selectbox(
            "Choose visualization:",
            options=["plotly", "echarts"],
            format_func=lambda x: "📈 Plotly Charts" if x == "plotly" else "🎨 ECharts"
        )
        st.session_state.chart_engine = chart_type
        
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
        if st.button("🗺️ Show GIS Infrastructure", use_container_width=True):
            st.session_state.quick_prompt = "Hiển thị bản đồ cơ sở hạ tầng năng lượng Việt Nam"
            st.session_state.show_gis = True
        
        st.divider()
        
        # About section
        st.subheader("ℹ️ About")
        st.caption("🎓 **FPT University**")
        st.caption("📝 Master Thesis Project")
        st.caption("👨‍💻 Hoang Tuan Dat")
        st.caption("👨‍🏫 Assoc. Prof. Phan Duy Hung")
        st.caption("© 2025")

    # Modern header with gradient background
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Energy AI Optimizer (EAIO)</h1>
        <p>Intelligent Multi-Agent System for Building Energy Analysis & Optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get API configuration from environment (hidden from UI)
    api_key = os.environ.get("LANGFLOW_API_KEY", "")
    api_url = os.environ.get("LANGFLOW_API_URL", "")
    
    # Modified layout based on display mode - GIS now wider
    if st.session_state.get("display_mode", "EAIO Chatbot") == "GIS Map + Chat":
        # Two column layout: Chat (smaller) + GIS (larger and wider)
        col1, col2 = st.columns([1, 3])  # Changed from [1, 2] to [1, 3] for wider GIS
        
        with col1:
            st.subheader("🤖 EAIO Assistant")
            render_chat_interface(api_url, api_key)
        
        with col2:
            st.subheader("🗺️ Energy Infrastructure")
            
            # Create and display GIS map with increased height for wider display
            gis_map = create_gis_map()
            if LEAFMAP_AVAILABLE:
                gis_map.to_streamlit(height=700)  # Increased from 600 to 700
            else:
                import streamlit.components.v1 as components
                map_html = gis_map._repr_html_()
                components.html(map_html, height=700)  # Increased from 600 to 700
    else:
        # Main chat interface - removed example queries
        st.subheader("🤖 EAIO Assistant Chat")
        render_chat_interface(api_url, api_key)

def render_chat_interface(api_url, api_key):
    """Render the main chat interface"""
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "👋 Chào mừng bạn đến với Energy AI Optimizer (EAIO)!\n\nTôi là AI assistant chuyên về phân tích và tối ưu hóa năng lượng tòa nhà. Tôi có thể giúp bạn:\n\n🔍 **Phân tích dữ liệu**: Xem xét các mẫu tiêu thụ năng lượng\n💡 **Đề xuất tối ưu**: Cải thiện hiệu suất năng lượng\n📊 **Báo cáo chi tiết**: Thống kê và xu hướng\n🏢 **So sánh tòa nhà**: Đánh giá hiệu suất tương đối\n🗺️ **Hiển thị GIS**: Bản đồ cơ sở hạ tầng năng lượng\n\nHãy bắt đầu bằng cách hỏi tôi về năng lượng tòa nhà của bạn!"
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])
    
    # Handle quick action prompts
    if hasattr(st.session_state, 'quick_prompt'):
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the quick prompt
        process_user_input(prompt, api_url, api_key)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("💬 Hỏi EAIO về tối ưu hóa năng lượng... (ví dụ: 'Liệt kê 5 tòa nhà tiêu thụ điện nhiều nhất')"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process user input
        process_user_input(prompt, api_url, api_key)

def process_user_input(prompt, api_url, api_key):
    """Process user input and generate response"""
    # Check if user is asking for charts or GIS
    chart_keywords = [
        "biểu đồ", "chart", "graph", "vẽ", "xu hướng", "trend", 
        "phân tích", "analysis", "so sánh", "compare", "top 5"
    ]
    gis_keywords = [
        "bản đồ", "map", "gis", "cơ sở hạ tầng", "infrastructure", 
        "địa lý", "geographic", "vị trí", "location"
    ]
    
    should_show_chart = any(keyword in prompt.lower() for keyword in chart_keywords)
    should_show_gis = any(keyword in prompt.lower() for keyword in gis_keywords)
    
    # Get response from Langflow
    if api_url:
        with st.chat_message("assistant"):
            with st.spinner("🤔 EAIO đang phân tích..."):
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
                    
                    # Show visualizations if requested
                    if should_show_chart:
                        show_energy_charts(prompt)
                    
                    if should_show_gis or hasattr(st.session_state, 'show_gis'):
                        if hasattr(st.session_state, 'show_gis'):
                            del st.session_state.show_gis
                        show_gis_map()
                    
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
            error_msg = "Hệ thống EAIO chưa được cấu hình. Tôi sẽ hiển thị dữ liệu mẫu cho bạn."
            st.markdown(error_msg)
            
            # Show visualizations even without API
            if should_show_chart:
                show_energy_charts(prompt)
            
            if should_show_gis or hasattr(st.session_state, 'show_gis'):
                if hasattr(st.session_state, 'show_gis'):
                    del st.session_state.show_gis
                show_gis_map()
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": error_msg
            })

def show_energy_charts(prompt):
    """Show energy consumption charts"""
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

def show_gis_map():
    """Show GIS map as secondary feature"""
    st.subheader("🗺️ Bản đồ cơ sở hạ tầng năng lượng Việt Nam")
    
    # Create and display GIS map with wider display
    gis_map = create_gis_map()
    if LEAFMAP_AVAILABLE:
        gis_map.to_streamlit(height=600)  # Increased height for better visibility
    else:
        import streamlit.components.v1 as components
        map_html = gis_map._repr_html_()
        components.html(map_html, height=600)

if __name__ == "__main__":
    main()