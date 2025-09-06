# EAIO Stakeholder Agentic Workflows Analysis

## Overview
This document defines multi-agent workflows for the Energy AI Optimizer (EAIO) system based on 10 specific requirement scenarios. Each requirement has been analyzed to determine the optimal agent coordination patterns and implementation strategies for maximum energy optimization effectiveness.

## Requirements-Based Use Cases

Based on the detailed requirement analysis, the EAIO system addresses 10 core optimization scenarios:

1. **Tối Ưu Hóa Lịch Trình Hoạt Động HVAC** - HVAC schedule optimization for energy savings
2. **Phản Ứng Nhanh Với Bất Thường Năng Lượng** - Rapid response to energy anomalies  
3. **Phân Tích Tương Quan Tiêu Thụ Năng Lượng - Thời Tiết** - Weather-energy correlation analysis
4. **So Sánh Hiệu Quả Năng Lượng Giữa Các Tòa Nhà** - Building performance benchmarking
5. **Báo Cáo Hiệu Quả Tài Chính Của Các Sáng Kiến Năng Lượng** - Financial performance reporting
6. **Lập Kế Hoạch Ngân Sách Năng Lượng Dài Hạn** - Long-term energy budget planning
7. **Phân Tích Mẫu Tiêu Thụ Theo Thời Gian** - Time-based consumption pattern analysis
8. **Theo Dõi Tiến Độ Và Hiệu Quả Sau Triển Khai** - Post-implementation progress tracking
9. **Phân Tích Toàn Diện Hiệu Suất Năng Lượng Tòa Nhà** - Comprehensive building energy performance analysis
10. **Lập Kế Hoạch Đạt Carbon Net Zero** - Carbon net zero planning

## Agent Architecture Summary

The system employs 7 specialized agents coordinated through comprehensive workflows to address each requirement scenario effectively.

---

## 1. Requirement-Based Agent Workflows

### 1.1 Requirement #1: Tối Ưu Hóa Lịch Trình Hoạt Động HVAC

**Tình Huống**: Quản lý cơ sở muốn điều chỉnh lịch trình hoạt động hệ thống HVAC để giảm tiêu thụ năng lượng mà không ảnh hưởng đến thoải mái của người dùng.

**Tương Tác Mẫu**:
- Quản lý: "Tối muốn tối ưu hóa lịch trình HVAC cho tòa nhà A. Có gợi ý nào không?"
- Trợ lý: "Dựa trên phân tích dữ liệu tiêu thụ 30 ngày qua và mẫu sử dụng tòa nhà, tôi khuyến nghị..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Facility Manager
    participant Coord as Coordinator Agent
    participant Data as DataAnalysisAgent
    participant Adapter as AdapterAgent
    participant Forecast as ForecastingAgent
    participant Rec as RecommendationAgent
    participant DB as Database
    
    User->>Coord: "Optimize HVAC schedule for Building A"
    Coord->>Data: Analyze 30-day consumption patterns
    Data->>DB: Query: Historical HVAC consumption & occupancy
    DB-->>Data: Time-series data with patterns
    Data-->>Coord: Peak usage: 7AM-6PM, Low: nights/weekends
    
    Coord->>Adapter: Get building context & constraints  
    Adapter->>DB: Query: Building info & HVAC capabilities
    DB-->>Adapter: Building metadata & system specs
    Adapter-->>Coord: HVAC system supports scheduling
    
    Coord->>Forecast: Predict energy savings from schedule optimization
    Forecast->>DB: Query: Weather patterns & demand forecasting
    DB-->>Forecast: Seasonal patterns & efficiency projections
    Forecast-->>Coord: Potential 15-18% energy savings
    
    Coord->>Rec: Generate optimal HVAC schedule
    Rec-->>Coord: Recommended schedule with comfort constraints
    Coord-->>User: "Optimization complete: Start HVAC at 6AM instead of 5AM (save 5.2%), reduce night cooling 16:30-18:00, optimize peak hours 11-14:00, enable cooling mode on Saturdays"
```

**Expected Outcomes**:
1. Giảm tiêu thụ cơ sở đêm ~25% qua kiểm soát thiết bị không thiết yếu
2. Điều chỉnh lịch trình HVAC cho cuối tuần thứ Hai sau cuối tuần
3. Thực hiện quan lý phụ tải chủ động trong cao điểm mùa hè
4. Điều chỉnh các hoạt động tiêu thụ cao sang giờ thấp điểm

### 1.2 Requirement #2: Phản Ứng Nhanh Với Bất Thường Năng Lượng

**Tình Huống**: Phát hiện mức tiêu thụ điện đột biến bất thường trong tòa nhà cần được xử lý ngay lập tức.

**Tương Tác Mẫu**:
- Quản lý: "Tôi thấy có thông báo về mức tiêu thụ điện bất thường. Đó là gì và phải làm gì?"
- Trợ lý: "Phát hiện mức tiêu thụ điện cao bất thường (+45% so với bình thường) tại tầng 3 từ 22:00 tối qua đến 6:00 sáng nay..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant System as Monitoring System
    participant Coord as Coordinator Agent
    participant Data as DataAnalysisAgent
    participant Adapter as AdapterAgent
    participant Rec as RecommendationAgent
    participant Eval as EvaluatorAgent
    participant User as Facility Manager
    participant DB as Database
    
    System->>Coord: ALERT: Abnormal energy consumption detected
    Coord->>Data: Analyze consumption anomaly
    Data->>DB: Query: Real-time consumption vs baseline
    DB-->>Data: 45% increase at Floor 3, 22:00-06:00
    Data-->>Coord: Anomaly: HVAC system overconsumption
    
    Coord->>Adapter: Check system status & equipment health
    Adapter->>DB: Query: HVAC system diagnostics
    DB-->>Adapter: Potential BMS configuration issue
    Adapter-->>Coord: HVAC running in full mode unnecessarily
    
    Coord->>Rec: Generate immediate response actions
    Rec-->>Coord: 1. Check HVAC schedule at Floor 3, 2. Adjust thermostat settings, 3. Check sensor calibration
    
    Coord->>Eval: Estimate financial impact
    Eval->>DB: Query: Cost calculation & impact assessment
    DB-->>Eval: Estimated extra cost: 1.2 million VND/month
    Eval-->>Coord: High financial impact - immediate action needed
    
    Coord->>User: "ANOMALY ALERT: Floor 3 overconsumption detected. Recommended actions: 1. Check HVAC schedule, 2. Adjust thermostat, 3. Verify sensor calibration. Potential monthly cost: 1.2M VND"
```

**Expected Outcomes**:
- Kiểm tra ngay cài đặt lịch trình HVAC tại tầng 3
- Điều chỉnh bộ hẹn giờ và xác nhận cài đặt tự động  
- Kiểm tra cảm biến hiện diện và nhiệt độ trong khu vực
- Nếu được khắc phục ngay, có thể tiết kiệm khoảng 1.2 triệu đồng tiền điện mỗi tháng

### 1.3 Requirement #3: Phân Tích Tương Quan Tiêu Thụ Năng Lượng - Thời Tiết

**Tình Huống**: Nhà phân tích năng lượng muốn hiểu chi tiết về mối tương quan giữa điều kiện thời tiết và tiêu thụ năng lượng của tòa nhà.

**Tương Tác Mẫu**:
- Phân tích viên: "Phân tích mối tương quan giữa nhiệt độ ngoài trời và tiêu thụ điện của tòa nhà trong 3 tháng qua."
- Trợ lý: "Phân tích tương quan giữa nhiệt độ ngoài trời và tiêu thụ điện cho tháy..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Energy Analyst
    participant Coord as Coordinator Agent
    participant Adapter as AdapterAgent
    participant Data as DataAnalysisAgent  
    participant Forecast as ForecastingAgent
    participant Rec as RecommendationAgent
    participant DB as Database
    
    User->>Coord: "Analyze weather-energy correlation for past 3 months"
    Coord->>Adapter: Collect weather & energy data
    Adapter->>DB: Query: Weather data + energy consumption (3 months)
    DB-->>Adapter: Temperature, humidity, consumption time-series
    Adapter-->>Coord: Data prepared for correlation analysis
    
    Coord->>Data: Perform correlation analysis
    Data->>DB: Query: Statistical correlation calculations
    DB-->>Data: Correlation coefficients & patterns
    Data-->>Coord: Strong correlation (0.83) between temperature & consumption
    
    Coord->>Forecast: Forecast consumption based on weather patterns
    Forecast->>DB: Query: Weather predictions & demand modeling
    DB-->>Forecast: 4.2% increase per 1°C temperature rise
    Forecast-->>Coord: Weather sensitivity factor calculated
    
    Coord->>Rec: Generate weather-based optimization recommendations
    Rec-->>Coord: 1. Pre-cool building during weather forecasts >28°C, 2. Implement thermal storage strategy, 3. Adjust AHU setpoints based on outdoor conditions
    
    Coord-->>User: "Weather-Energy Correlation Analysis Complete: Strong correlation (0.83), 4.2% consumption increase per 1°C rise. Recommendations: Pre-cooling strategy, thermal storage, adaptive AHU control"
```

**Expected Outcomes**:
1. Tối ưu hóa điều cài đặt HVAC dựa trên dự báo thời tiết 48 giờ
2. Triển khai chiến lược tiền làm mát với nhiệt độ ngoài trời dự kiến >30°C
3. Điều chỉnh biến tần AHU sớm trước giờ cao điểm theo nhiệt độ ngoài trời

### 1.4 Requirement #4: So Sánh Hiệu Quả Năng Lượng Giữa Các Tòa Nhà

**Tình Huống**: Cần so sánh hiệu quả năng lượng giữa nhiều tòa nhà trong danh mục đầu tư để xác định cơ hội cải thiện.

**Tương Tác Mẫu**:
- Phân tích viên: "So sánh hiệu quả năng lượng giữa tòa nhà A, B và C trong quý vừa qua."
- Trợ lý: "Phân tích so sánh hiệu quả năng lượng của 3 tòa nhà trong Q2/2025..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Portfolio Manager
    participant Coord as Coordinator Agent
    participant Data as DataAnalysisAgent
    participant Memory as MemoryAgent
    participant Eval as EvaluatorAgent
    participant Rec as RecommendationAgent
    participant DB as Database
    
    User->>Coord: "Compare energy efficiency between Buildings A, B, C"
    Coord->>Data: Analyze performance metrics for 3 buildings
    Data->>DB: Query: EUI, consumption, efficiency metrics (Q2/2025)
    DB-->>Data: Building A: 182.3 kWh/m²/năm, B: 156.7, C: 215.8
    Data-->>Coord: Performance ranking: B > A > C
    
    Coord->>Memory: Store historical context & benchmarks
    Memory->>DB: Query: Historical performance trends
    DB-->>Memory: Performance trends & improvement opportunities
    Memory-->>Coord: Context established for comparison
    
    Coord->>Eval: Evaluate efficiency and ROI potential
    Eval->>DB: Query: Cost analysis & improvement potential
    DB-->>Eval: Building B: best performer, C: highest savings potential
    Eval-->>Coord: Building C needs priority intervention
    
    Coord->>Rec: Generate improvement recommendations
    Rec-->>Coord: Building C: Upgrade window systems (ROI: 24 months), Building A: LED transition (ROI: 18 months), Building C: Implement building management system (ROI: 15 months)
    
    Coord-->>User: "Building Efficiency Comparison Complete. Building B: Most efficient (COP 4.2), Building C: Needs immediate attention (overheating issues, 8.3% above baseline). Priority recommendations: Building C infrastructure upgrade, Building A LED conversion"
```

**Expected Outcomes**:
- Tòa nhà B có COP trung bình cao nhất: 4.2
- Tòa nhà C có tỷ lệ thất thoát nhiệt cao qua cửa số đơn lớp  
- Tòa nhà A sử dụng biến tần tiết kiệm 8.3% so với Q1

### 1.5 Requirement #5: Báo Cáo Hiệu Quả Tài Chính Của Các Sáng Kiến Năng Lượng

**Tình Huống**: Lãnh đạo cần báo cáo tổng quan về hiệu quả tài chính của các sáng kiến năng lượng đã triển khai.

**Tương Tác Mẫu**:
- Giám đốc: "Tôi cần hiệu quả tài chính các dự án năng lượng triển khai trong 6 tháng qua."
- Trợ lý: "Báo cáo hiệu quả tài chính các sáng kiến năng lượng (6 tháng qua)..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Executive
    participant Coord as Coordinator Agent
    participant Eval as EvaluatorAgent
    participant Memory as MemoryAgent
    participant Data as DataAnalysisAgent
    participant Rec as RecommendationAgent
    participant DB as Database
    
    User->>Coord: "Report financial effectiveness of energy initiatives (6 months)"
    Coord->>Eval: Calculate ROI and financial metrics
    Eval->>DB: Query: Investment costs, savings, ROI calculations
    DB-->>Eval: Total investment: 425M VND, Savings: 212M VND, ROI: 99.8%
    Eval-->>Coord: Strong financial performance - 12.1 month payback
    
    Coord->>Memory: Retrieve historical context & project details
    Memory->>DB: Query: Project implementation history
    DB-->>Memory: LED upgrade, HVAC optimization, building management system
    Memory-->>Coord: 3 major initiatives tracked
    
    Coord->>Data: Analyze performance by initiative type
    Data->>DB: Query: Performance by project type
    DB-->>Data: LED: 103.8% ROI, HVAC: 104% ROI, BMS: 84.4% ROI
    Data-->>Coord: All initiatives exceeding target ROI
    
    Coord->>Rec: Generate strategic next steps
    Rec-->>Coord: Expand LED to remaining buildings (ROI: 110%), Install solar panels (ROI: 85-15 years), Upgrade building management AI (ROI: 95-16 years)
    
    Coord-->>User: "Financial Performance Report: Total ROI 99.8% (12 months), CO2 reduction: 105 tons. Next phase recommendations: LED expansion, solar panels, AI management system upgrade"
```

**Expected Outcomes**:
1. Nâng cấp LED
   - Đầu tư: 185 triệu đồng
   - Tiết kiệm: 96 triệu đồng (6 tháng)  
   - ROI: 103.8% (12 tháng)
   - Hiệu suất cao hơn kỳ vọng 15%

2. Tối ưu hóa HVAC
   - Đầu tư: 150 triệu đồng
   - Tiết kiệm: 78 triệu đồng (6 tháng)
   - ROI: 104% (12 tháng)
   - Theo đúng kỳ vọng

3. Hệ thống quản lý năng lượng tòa nhà
   - Đầu tư: 90 triệu đồng
   - Tiết kiệm: 38 triệu đồng (6 tháng)
   - ROI: 84.4% (12 tháng)
   - Thấp hơn kỳ vọng 8% do thời gian đào tạo kéo dài

### 1.6 Requirement #6: Lập Kế Hoạch Ngân Sách Năng Lượng Dài Hạn

**Tình Huống**: Lãnh đạo cần dự báo chi phí năng lượng cho năm tới và đề xuất phân bổ ngân sách tối ưu.

**Tương Tác Mẫu**:
- Giám đốc: "Dự báo chi phí năng lượng cho năm tới và đề xuất phân bổ ngân sách tối ưu."
- Trợ lý: "Dự báo chi phí năng lượng cho FY2026 và đề xuất phân bổ ngân sách..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Executive
    participant Coord as Coordinator Agent
    participant Forecast as ForecastingAgent
    participant Adapter as AdapterAgent
    participant Rec as RecommendationAgent
    participant Eval as EvaluatorAgent
    participant DB as Database
    
    User->>Coord: "Forecast energy costs and optimize budget allocation for FY2026"
    Coord->>Forecast: Predict energy cost trends
    Forecast->>DB: Query: Historical costs, price trends, demand forecasting
    DB-->>Forecast: Electricity: +4.5% increase, Gas: +5.2% increase, Peak demand pricing impact
    Forecast-->>Coord: Total cost increase: 1.82 billion VND (+7.5% vs FY2025)
    
    Coord->>Adapter: Analyze market & regulatory changes
    Adapter->>DB: Query: Energy market trends, policy changes
    DB-->>Adapter: Carbon tax: +18% cost impact, Renewable incentives available
    Adapter-->>Coord: Policy factors identified
    
    Coord->>Rec: Generate budget optimization recommendations
    Rec-->>Coord: 1. Operating costs: 1.45B VND, 2. Efficiency projects: 255M VND, 3. Optimization investment: 550M VND (ROI <24 months)
    
    Coord->>Eval: Calculate ROI and financial projections
    Eval->>DB: Query: Investment analysis & cost-benefit calculations
    DB-->>Eval: Net savings potential: 18.5% cost reduction, Total ROI: 86% (12 months)
    Eval-->>Coord: Strong investment case validated
    
    Coord-->>User: "FY2026 Energy Budget Forecast: 1.82B VND base cost (+7.5%). Recommended allocation: 1.45B operations, 255M efficiency projects, 550M optimization investment. Expected savings: 18.5% through strategic investments"
```

**Expected Outcomes**:
**Dự báo chi phí cơ sở**:
- Tổng chi phí điện: 1.82 tỷ đồng (+7.5% so với FY2025)
- Tổng chi phí gas: 420 triệu đồng (+5.2% so với FY2025)  
- Chi phí định điểm: 552 triệu đồng (+12.3% do tăng giá giờ cao điểm)

**Yếu tố tác động chính**:
- Tăng giá điện dự kiến: +4.5% (Q3/2025)
- Dự báo mùa hè nóng hơn 1.8°C so với 2025
- Mở rộng quy định sử dụng tăng 5: +18% điện tích sử dụng

### 1.7 Requirement #7: Phân Tích Mẫu Tiêu Thụ Theo Thời Gian

**Tình Huống**: Cần hiểu rõ mẫu tiêu thụ năng lượng theo thời gian để phát hiện cơ hội tối ưu hóa.

**Tương Tác Mẫu**:
- Người dùng: "Phân tích xu hướng tiêu thụ điện hàng ngày, hàng tuần và theo mùa cho tòa nhà này."
- Trợ lý: "Phân tích xu hướng tiêu thụ điện cho tòa nhà..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Facility Manager
    participant Coord as Coordinator Agent
    participant Data as DataAnalysisAgent
    participant Forecast as ForecastingAgent
    participant Rec as RecommendationAgent
    participant Memory as MemoryAgent
    participant DB as Database
    
    User->>Coord: "Analyze consumption patterns: daily, weekly, seasonal for building"
    Coord->>Data: Analyze consumption patterns across time periods
    Data->>DB: Query: Hourly, daily, weekly consumption patterns
    DB-->>Data: Peak hours: 9-11AM, 2-4PM, Weekend patterns, Seasonal variations
    Data-->>Coord: Clear time-based patterns identified
    
    Coord->>Forecast: Predict future consumption patterns
    Forecast->>DB: Query: Pattern forecasting and seasonal adjustments
    DB-->>Forecast: Summer peak +32% vs average, Winter low -18% vs average
    Forecast-->>Coord: Seasonal forecasting models ready
    
    Coord->>Memory: Store pattern insights for optimization
    Memory->>DB: Query: Historical pattern effectiveness
    DB-->>Memory: Previous optimizations and their success rates
    Memory-->>Coord: Pattern-based optimization history available
    
    Coord->>Rec: Generate time-based optimization recommendations
    Rec-->>Coord: 1. Pre-cooling during 6-8AM (+32% efficiency), 2. Load shifting to off-peak hours, 3. Weekend schedule optimization, 4. Seasonal HVAC adjustments
    
    Coord-->>User: "Time Pattern Analysis Complete: Peak consumption 9-11AM & 2-4PM. Summer +32% vs winter. Recommendations: Pre-cooling strategy, load shifting, seasonal HVAC optimization. Potential 15-20% energy savings"
```

**Expected Outcomes**:
**Mẫu Hàng Ngày**:
- Cao điểm chính: 9:00-11:00 (mức tiêu thụ +42% so với trung bình)
- Cao điểm phụ: 14:00-16:00 (+35% so với trung bình)  
- Điểm thấp: 1:00-4:00 sáng (-65% so với trung bình)
- Tiêu thụ cơ sở đêm: ~35kW (chủ yếu từ máy chủ, an ninh, và HVAC bảo trì)
- Tỷ lệ ngày/đêm: 3.8:1

**Mẫu Hàng Tuần**:
- Ngày tiêu thụ cao nhất: Thứ Ba (+12% so với trung bình tuần)
- Ngày tiêu thụ thấp nhất: Chủ Nhật (-52% so với trung bình tuần)
- Tỷ lệ ngày làm việc/cuối tuần: 2.7:1
- Đặc điểm nổi bật: Các cuộc họp sáng thứ Hai tạo đỉnh tiêu thụ +15%

### 1.8 Requirement #8: Theo Dõi Tiến Độ Và Hiệu Quả Sau Triển Khai

**Tình Huống**: Cần theo dõi hiệu quả của các biện pháp tối ưu hóa năng lượng sau khi triển khai.

**Tương Tác Mẫu**:
- Người dùng: "Đánh giá hiệu quả của biện pháp tối ưu hóa HVAC sau 30 ngày triển khai."
- Trợ lý: "Đánh giá hiệu quả tối ưu hóa HVAC sau 30 ngày..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Project Manager
    participant Coord as Coordinator Agent
    participant Eval as EvaluatorAgent
    participant Data as DataAnalysisAgent
    participant Memory as MemoryAgent
    participant Rec as RecommendationAgent
    participant DB as Database
    
    User->>Coord: "Evaluate HVAC optimization effectiveness after 30 days"
    Coord->>Eval: Assess implementation results
    Eval->>DB: Query: Pre vs post implementation metrics
    DB-->>Eval: 92% completion rate, 15.3% actual energy savings, 27.8M VND cost savings
    Eval-->>Coord: Implementation successful, meeting technical targets
    
    Coord->>Data: Analyze detailed performance metrics
    Data->>DB: Query: System performance & efficiency comparisons
    DB-->>Data: Target vs actual performance analysis
    Data-->>Coord: Performance meets expectations with 94.7% target achievement
    
    Coord->>Memory: Store implementation lessons learned
    Memory->>DB: Query: Best practices & implementation insights
    DB-->>Memory: Success factors and improvement opportunities documented
    Memory-->>Coord: Implementation knowledge captured
    
    Coord->>Rec: Generate supplementary improvements
    Rec-->>Coord: 1. Early cooling optimization (save 15 minutes), 2. Sensor calibration adjustments, 3. Additional wind flow control based on CO2 levels
    
    Coord-->>User: "30-Day HVAC Optimization Review: 92% implementation success, 15.3% energy savings achieved, 27.8M VND saved. Recommendations: Fine-tune cooling schedule, calibrate sensors, implement CO2-based ventilation control"
```

**Expected Outcomes**:
**Tổng quan thực hiện**:
- Mức độ hoàn thành: 92% (23/25 điểm điều khiển đã được tối ưu)
- Chất lượng triển khai: Tốt (đạt tiêu chuẩn kỹ thuật)
- Vấn đề gặp phải: 2 bộ điều khiển VAV cần thay thế

**Kết quả tiết kiệm năng lượng**:
- Tiết kiệm thực tế: 15.3% tiêu thụ HVAC
- So với dự kiến: 94.7% mục tiêu ban đầu (dự kiến 16.2%)
- Tiết kiệm chi phí: 27.8 triệu đồng/tháng
- Giảm phát thải CO2: 6.2 tấn/tháng

### 1.9 Requirement #9: Phân Tích Toàn Diện Hiệu Suất Năng Lượng Tòa Nhà

**Tình Huống**: Cần đánh giá toàn diện hiệu suất năng lượng của tòa nhà và xác định cơ hội cải thiện.

**Tương Tác Mẫu**:
- Người dùng: "Đánh giá toàn diện hiệu quả năng lượng tòa nhà và đề xuất kế hoạch cải thiện."
- Trợ lý: "Đánh giá toàn diện hiệu quả năng lượng tòa nhà..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Building Manager
    participant Coord as Coordinator Agent
    participant Data as DataAnalysisAgent
    participant Rec as RecommendationAgent
    participant Forecast as ForecastingAgent
    participant Eval as EvaluatorAgent
    participant Memory as MemoryAgent
    participant Command as CommanderAgent
    participant DB as Database
    
    User->>Coord: "Comprehensive building energy performance assessment"
    
    par Multi-Agent Analysis
        Coord->>Data: Analyze comprehensive energy performance
        Data->>DB: Query: EUI, consumption patterns, system efficiency
        DB-->>Data: Current EUI: 174 kWh/m²/năm, EnergyStar: 68/100
        
        Coord->>Forecast: Predict optimization potential
        Forecast->>DB: Query: Optimization scenarios & projections
        DB-->>Forecast: 30-38% savings potential, ROI 5 năm: 224%
        
        Coord->>Eval: Evaluate current performance & ROI
        Eval->>DB: Query: Benchmark analysis & financial assessment
        DB-->>Eval: Below industry standard, high improvement potential
    end
    
    Coord->>Rec: Generate comprehensive improvement plan
    Rec-->>Coord: Multi-phase improvement strategy with timelines
    
    Coord->>Memory: Store analysis for continuous monitoring
    Memory-->>Coord: Analysis stored for tracking progress
    
    Coord->>Command: Coordinate implementation planning
    Command-->>Coord: Implementation roadmap with resource allocation
    
    Coord-->>User: "Comprehensive Assessment Complete: Current EUI 174 kWh/m² (23% above standard). 3-phase improvement plan: Short-term (8-12 months, ROI >100%), Medium-term (12-24 months, ROI 50-100%), Long-term (24-48 months, ROI 25-50%). Total savings potential: 32-38%, Investment payback: 5 years"
```

**Expected Outcomes**:
**Hiện trạng (so với chuẩn ngành)**:
- Cường độ năng lượng: 174 kWh/m²/năm (cao hơn 23% so với chuẩn ngành)
- Xếp hạng EnergyStar: 68/100 (khá, nhưng chưa đạt chứng nhận 275)
- Chỉ số năng lượng: 12.8 tỷ đồng/năm
- Phân bố tiêu thụ: HVAC 50%, Chiếu sáng 22%, Thiết bị 17%, Khác 5%

**Phân tích chi tiết**:
1. **Hệ thống HVAC**:
   - Hiệu suất COP trung bình 3.8 (thấp hơn 12% so với chuẩn hiện đại)
   - Vận đế: Vần hành không tối ưu, điểm đặt không thích ứng, điều khiển cực bộ
   - Tiềm năng tiết kiệm: 15-20%

2. **Hệ thống chiếu sáng**:
   - LED điểm tích (35% cần nâng cấp)
   - Kiểm soát: Thiếu cảm biến ánh sáng và hiện diện ở 40% điểm tích
   - Tiềm năng tiết kiệm: 22-28%

3. **Vỏ bao che tòa nhà**:
   - Cửa sổ: SMGC 0.65 (cao hơn 30% so với chuẩn hiện đại)
   - Cách nhiệt: R-value thấp tại mái và tường hướng tây
   - Tiềm năng tiết kiệm: 8-12%

### 1.10 Requirement #10: Lập Kế Hoạch Đạt Carbon Net Zero

**Tình Huống**: Doanh nghiệp muốn lập lộ trình đạt mục tiêu carbon net zero cho tòa nhà vào năm 2035.

**Tương Tác Mẫu**:
- Người dùng: "Lập kế hoạch carbon net zero cho tòa nhà vào năm 2035."
- Trợ lý: "Lộ trình carbon net zero đến năm 2035..."

**Agent Coordination Workflow**:
```mermaid
sequenceDiagram
    participant User as Executive
    participant Coord as Coordinator Agent
    participant Data as DataAnalysisAgent
    participant Forecast as ForecastingAgent
    participant Rec as RecommendationAgent
    participant Eval as EvaluatorAgent
    participant Adapter as AdapterAgent
    participant Memory as MemoryAgent
    participant Command as CommanderAgent
    participant DB as Database
    
    User->>Coord: "Develop carbon net zero roadmap for building by 2035"
    
    Coord->>Data: Analyze current emissions baseline
    Data->>DB: Query: Current emissions, energy sources, carbon intensity
    DB-->>Data: Current emissions: 850 tấn CO2e/năm, Phases 1-3 breakdown
    Data-->>Coord: Emissions baseline established
    
    Coord->>Forecast: Model emission reduction scenarios
    Forecast->>DB: Query: Reduction scenarios, technology projections
    DB-->>Forecast: Multiple pathways to net zero analyzed
    Forecast-->>Coord: 4-phase roadmap optimal approach
    
    par Multi-Agent Strategy Development
        Coord->>Rec: Generate net zero strategy recommendations
        Rec-->>Coord: Technology roadmap, investment priorities
        
        Coord->>Eval: Calculate costs and ROI for each phase
        Eval->>DB: Query: Cost-benefit analysis, financing options
        DB-->>Eval: Phase-by-phase investment analysis
        Eval-->>Coord: Financial roadmap validated
        
        Coord->>Adapter: Assess technology integration requirements
        Adapter-->>Coord: Integration feasibility and timeline
    end
    
    Coord->>Memory: Store comprehensive net zero plan
    Memory-->>Coord: Roadmap documented for tracking
    
    Coord->>Command: Coordinate implementation planning
    Command-->>Coord: Executive summary and action plan
    
    Coord-->>User: "Carbon Net Zero Roadmap 2035: 4-phase plan. Phase 1 (2025-2027): Energy efficiency (-30%), Phase 2 (2028-2030): Electrification (-20%), Phase 3 (2031-2034): Renewable energy (-25%), Phase 4 (2035): Carbon offsets (-10%). Total investment: 180M VND/năm, Net savings by 2035: ~70% energy costs"
```

**Expected Outcomes**:
**Hiện trạng phát thải**:
- Tổng phát thải: 850 tấn CO2e/năm
  - Phạm vi 1 (trực tiếp): 128 tấn CO2e
  - Phạm vi 2 (điện): 680 tấn CO2e  
  - Phạm vi 3 (gián tiếp): 50 tấn CO2e
- Cường độ carbon: 28.3 kg CO2e/m²/năm

**Kế hoạch giảm phát thải theo giai đoạn**:

**Giai đoạn 1 (2025-2027): Giảm 30% - Tối ưu hóa và hiệu quả**
- Tối ưu vận hành HVAC và kiểm soát nhờ cầu (-15%)
- Hoàn thiện chiều sáng LED và điều khiển thông minh (-8%)
- Cách nhiệt cái tiến và cỏ hiệu suất cao (-7%)
- Đầu tư: 1.4 tỷ đồng, ROI: 75% (5 năm)

**Giai đoạn 2 (2028-2030): Giảm thêm 35% - Điện khí hóa và tái tạo**
- Lắp đặt hệ thống nhiệt bơm thay lò hơi gas (-12%)
- Chuyển sang bơn nhiệt điện thay lò hơi gas (-12%)  
- Triển khai hệ thống quản lý năng lượng thông minh AI (-3%)
- Đầu tự: 3.8 tỷ đồng, ROI: 45% (10 năm)

**Giai đoạn 3 (2031-2034): Giảm thêm 25% - Tái tạo và lưu trữ**
- Mở rộng pin mặt trời lên 200kWp (-10%)
- Triển khai lưu trữ năng lượng 150kWh (-8%)
- Tham gia thị trường điện phân ứng nhanh (-7%)
- Đầu tư: 4.2 tỷ đồng, ROI: 32% (15 năm)

**Giai đoạn 4 (2035): 10% còn lại - Bù đắp carbon**
- Mua tín chỉ carbon có từ dự án được xác minh
- Đầu tự vào dự án carbon âm trong chuối cung ứng
- Đầu tự: 180 triệu đồng/năm

**Lợi ích bổ sung**:
- Giảm chi phí năng lượng: ~70% vào năm 2035
- Tăng giá trị tài sản: ~8-12%  
- Tuân thủ quy định phát thải trong tương lại
- Cải thiện thương hiệu doanh nghiệp

**Các mốc quan trọng cần đạt**:
2027: Giảm 30% phát thải, hoàn thành tối ưu hóa năng lượng
2030: Giảm 65% phát thải, hoàn thành điện khí hóa  
2034: Giảm 90% phát thải, hoàn thành hệ thống tái tạo
2035: Đạt Net Zero thông qua bù đắp carbon chất lượng cao

---

## 2. EAIO System Architecture

##### **"What's the current energy consumption status of Building A?"**
**Agent Mapping**: Energy Data Intelligence Agent  
**Query Mapping**: 
- Basic Energy Consumption Pattern Analysis (hourly patterns)
- Data Completeness Analysis (quality verification)
```sql
-- Primary Query: Current consumption status
SELECT DATE_TRUNC('hour', timestamp) as hour, meter_type, 
       AVG(value) as avg_consumption, SUM(value) as total_consumption
FROM energy.meter_readings 
WHERE building_id = 'Building_A' AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
AND quality = 'good' GROUP BY DATE_TRUNC('hour', timestamp), meter_type;
```

##### **"Are there any equipment failures or anomalies detected today?"**
**Agent Mapping**: Energy Data Intelligence Agent + Forecast Intelligence Agent  
**Query Mapping**: 
- Consumption Outlier Detection (statistical analysis)
- Equipment Failure Prediction (risk scoring)
```sql
-- Primary Query: Anomaly detection
WITH consumption_stats AS (SELECT meter_id, AVG(value) as mean_consumption, STDDEV(value) as std_consumption...)
-- Identifies outliers using IQR and statistical bounds
```

##### **"How is our building performing compared to yesterday/last week?"**
**Agent Mapping**: Energy Data Intelligence Agent  
**Query Mapping**: 
- Daily Consumption Trends by Building Type
- Peak Demand Analysis (load factor comparison)
```sql
-- Primary Query: Performance comparison
SELECT DATE_TRUNC('day', timestamp) as day, meter_type,
       SUM(value) as daily_consumption,
       LAG(SUM(value)) OVER (ORDER BY DATE_TRUNC('day', timestamp)) as previous_day
FROM energy.meter_readings WHERE building_id = $1...
```

##### **"Which systems are consuming the most energy right now?"**
**Agent Mapping**: Energy Data Intelligence Agent  
**Query Mapping**: 
- Basic Energy Consumption Pattern Analysis (by meter type)
- Peak Demand Analysis (current demand ranking)
```sql
-- Primary Query: Current system ranking
SELECT meter_type, meter_id, SUM(value) as current_consumption
FROM energy.meter_readings 
WHERE building_id = $1 AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
ORDER BY current_consumption DESC;
```

##### **"What maintenance alerts do I need to address immediately?"**
**Agent Mapping**: System Control Agent + Forecast Intelligence Agent  
**Query Mapping**: 
- System Status and Control Point Monitoring
- Equipment Failure Prediction (maintenance recommendations)
```sql
-- Primary Query: Critical maintenance alerts
SELECT meter_id, failure_risk_score, maintenance_recommendation
FROM (Equipment Failure Prediction Query)
WHERE failure_risk_score >= 4 ORDER BY failure_risk_score DESC;
```

#### Performance Optimization Questions:

##### **"What are the top 3 energy-saving opportunities for this month?"**
**Agent Mapping**: Optimization Strategy Specialist Agent  
**Query Mapping**: 
- Building-Specific Optimization Recommendations
- ROI Analysis for Energy Efficiency Measures
```sql
-- Primary Query: Top optimization opportunities
SELECT primary_recommendation, potential_savings, implementation_priority
FROM (Building-Specific Optimization Query)
WHERE implementation_priority IN ('high', 'medium') 
ORDER BY potential_savings DESC LIMIT 3;
```

##### **"How can I reduce peak demand during utility peak hours?"**
**Agent Mapping**: Forecast Intelligence Agent + System Control Agent  
**Query Mapping**: 
- Peak Demand and Load Shifting Analysis
- Automated Control Parameter Optimization
```sql
-- Primary Query: Demand response opportunities
SELECT utility_period, potential_load_reduction, dr_recommendation
FROM (Load Shifting Potential Analysis)
WHERE utility_period = 'utility_peak' AND potential_load_reduction > 0;
```

##### **"Which setpoint adjustments would save the most energy?"**
**Agent Mapping**: System Control Agent  
**Query Mapping**: 
- Automated Control Parameter Optimization
- Safety and Comfort Constraint Enforcement
```sql
-- Primary Query: Optimal setpoint recommendations
SELECT hour_of_day, occupancy_schedule, recommended_temp_setpoint, savings_potential
FROM (Setpoint Analysis Query)
WHERE savings_potential > 0 ORDER BY savings_potential DESC;
```

##### **"What's the optimal schedule for HVAC systems this week?"**
**Agent Mapping**: System Control Agent + Weather Intelligence Agent  
**Query Mapping**: 
- Automated Control Parameter Optimization (scheduling)
- Weather-Based Energy Demand Prediction
```sql
-- Primary Query: Weekly HVAC schedule
SELECT day_of_week, hour_of_day, control_command, 
       recommended_temp_setpoint, occupancy_schedule
FROM (Control Commands Query)
ORDER BY day_of_week, hour_of_day;
```

##### **"Are there any comfort complaints that need attention?"**
**Agent Mapping**: System Control Agent + Validator Agent  
**Query Mapping**: 
- Safety and Comfort Constraint Enforcement
- System Quality Assurance and Error Detection
```sql
-- Primary Query: Comfort constraint violations
SELECT building_id, meter_type, constraint_status, violation_severity_percent, safety_action
FROM (Constraint Violations Analysis)
WHERE constraint_status IN ('over_consumption', 'under_consumption');
```

#### Troubleshooting Questions:

##### **"Why did energy consumption spike at 2 PM yesterday?"**
**Agent Mapping**: Energy Data Intelligence Agent + Weather Intelligence Agent  
**Query Mapping**: 
- Unusual Pattern Detection
- Weather-Energy Correlation Analysis
```sql
-- Primary Query: Consumption spike analysis
SELECT timestamp, consumption, hour_of_day, time_category, consumption_ratio,
       avg_temperature, temp_correlation
FROM (Unusual Pattern Detection + Weather Correlation)
WHERE timestamp BETWEEN 'yesterday 1PM' AND 'yesterday 3PM';
```

##### **"Which meter is showing unusual readings?"**
**Agent Mapping**: Energy Data Intelligence Agent  
**Query Mapping**: 
- Consumption Outlier Detection
- Data Quality Assessment
```sql
-- Primary Query: Unusual meter identification
SELECT meter_id, outlier_type, z_score, consumption_value, mean_consumption
FROM (Outlier Detection Query)
WHERE outlier_type IN ('iqr_outlier', 'statistical_outlier');
```

##### **"How do I override the automated system for emergency maintenance?"**
**Agent Mapping**: System Control Agent + Validator Agent  
**Query Mapping**: 
- Safety and Comfort Constraint Enforcement
- System Quality Assurance (emergency protocols)
```sql
-- Primary Query: Emergency override validation
SELECT constraint_status, safety_action, recommended_setpoint
FROM (Safety Constraints Analysis)
WHERE safety_action LIKE '%EMERGENCY%';
```

##### **"What caused the temperature control issues in Zone 3?"**
**Agent Mapping**: System Control Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- System Status and Control Point Monitoring
- Consumption Outlier Detection (zone-specific)
```sql
-- Primary Query: Zone-specific issue analysis
SELECT meter_name, system_status, control_health_score, control_recommendation
FROM (Control Systems Monitoring)
WHERE meter_name LIKE '%Zone 3%' OR meter_name LIKE '%Zone_3%';
```

### 1.2 Building Owners/Property Managers Questions

#### Financial Performance Questions:

##### **"What's our monthly energy cost savings so far?"**
**Agent Mapping**: Optimization Strategy Specialist Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- ROI Analysis for Energy Efficiency Measures
- Building Baseline Energy Performance Analysis
```sql
-- Primary Query: Monthly cost savings tracking
SELECT DATE_TRUNC('month', timestamp) as month, 
       SUM(baseline_cost - optimized_cost) as monthly_savings,
       AVG((baseline_cost - optimized_cost) / baseline_cost * 100) as savings_percentage
FROM (ROI Analysis Query) WHERE timestamp >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY DATE_TRUNC('month', timestamp) ORDER BY month;
```

##### **"How is the ROI tracking against our 18-month target?"**
**Agent Mapping**: Optimization Strategy Specialist Agent  
**Query Mapping**: 
- ROI Analysis for Energy Efficiency Measures
- Building-Specific Optimization Recommendations
```sql
-- Primary Query: ROI tracking vs target
SELECT investment_date, total_investment, cumulative_savings, 
       (cumulative_savings / total_investment * 100) as current_roi,
       target_roi, months_elapsed, roi_trajectory
FROM (ROI Analysis Query) WHERE investment_date >= CURRENT_DATE - INTERVAL '18 months';
```

##### **"Which buildings in our portfolio are underperforming?"**
**Agent Mapping**: Energy Data Intelligence Agent + Validator Agent  
**Query Mapping**: 
- Building Performance Benchmarking
- Data Quality Assessment (validation)
```sql
-- Primary Query: Portfolio performance ranking
SELECT building_id, current_eui, benchmark_eui, 
       (current_eui - benchmark_eui) as performance_gap,
       performance_percentile, improvement_potential
FROM (Building Benchmarking Query)
WHERE performance_percentile < 25 ORDER BY performance_gap DESC;
```

##### **"What's the payback period for the HVAC upgrade proposal?"**
**Agent Mapping**: Optimization Strategy Specialist Agent + Forecast Intelligence Agent  
**Query Mapping**: 
- ROI Analysis for Energy Efficiency Measures
- Long-term Energy Forecasting
```sql
-- Primary Query: HVAC upgrade payback analysis
SELECT upgrade_cost, annual_savings, simple_payback_years,
       net_present_value, internal_rate_of_return,
       risk_adjusted_payback
FROM (Investment Analysis Query)
WHERE investment_type = 'hvac_upgrade';
```

##### **"How much have we saved compared to baseline?"**
**Agent Mapping**: Energy Data Intelligence Agent  
**Query Mapping**: 
- Building Baseline Energy Performance Analysis
- Daily Consumption Trends by Building Type
```sql
-- Primary Query: Baseline vs current performance
SELECT baseline_period, current_period, baseline_total_consumption,
       current_total_consumption, absolute_savings, percentage_savings,
       avoided_costs
FROM (Baseline Comparison Query)
WHERE building_id = $1 AND baseline_period = 'pre_optimization';
```

#### Strategic Planning Questions:

##### **"What are the best energy efficiency investments for next year?"**
**Agent Mapping**: Optimization Strategy Specialist Agent + Forecast Intelligence Agent  
**Query Mapping**: 
- Building-Specific Optimization Recommendations
- Equipment Failure Prediction (replacement planning)
```sql
-- Primary Query: Investment opportunity prioritization
SELECT investment_category, total_investment_required, annual_savings_potential,
       payback_period, risk_score, implementation_priority
FROM (Investment Opportunities Query)
WHERE implementation_year = EXTRACT(YEAR FROM CURRENT_DATE) + 1
ORDER BY payback_period ASC, annual_savings_potential DESC LIMIT 10;
```

##### **"How does our building rank against industry benchmarks?"**
**Agent Mapping**: Energy Data Intelligence Agent  
**Query Mapping**: 
- Building Performance Benchmarking
- Energy Use Intensity (EUI) Comparisons
```sql
-- Primary Query: Industry benchmark comparison
SELECT building_id, building_type, current_eui, industry_median_eui,
       industry_top_quartile_eui, percentile_ranking, certification_readiness
FROM (Building Benchmarking Query)
WHERE building_type = $1 AND certification_target = 'energy_star';
```

##### **"What's the potential value increase from Energy Star certification?"**
**Agent Mapping**: Optimization Strategy Specialist Agent  
**Query Mapping**: 
- Energy Star Score Estimation
- ROI Analysis for Energy Efficiency Measures (certification)
```sql
-- Primary Query: Energy Star certification value
SELECT current_energy_star_score, target_energy_star_score,
       required_improvements, estimated_asset_value_increase,
       certification_costs, net_value_creation
FROM (Energy Star Analysis)
WHERE building_id = $1 AND certification_level >= 75;
```

##### **"Which optimization measures have the highest ROI?"**
**Agent Mapping**: Optimization Strategy Specialist Agent  
**Query Mapping**: 
- Building-Specific Optimization Recommendations
- ROI Analysis for Energy Efficiency Measures
```sql
-- Primary Query: ROI-ranked optimization measures
SELECT optimization_measure, investment_cost, annual_savings,
       simple_payback_months, npv_10_year, implementation_complexity
FROM (Optimization ROI Ranking)
ORDER BY npv_10_year DESC, simple_payback_months ASC;
```

##### **"How can we achieve our 30% energy reduction target?"**
**Agent Mapping**: Optimization Strategy Specialist Agent + Forecast Intelligence Agent  
**Query Mapping**: 
- Building-Specific Optimization Recommendations
- Load Shifting Potential Analysis
```sql
-- Primary Query: Energy reduction pathway analysis
SELECT reduction_pathway, cumulative_savings_percent, total_investment,
       implementation_timeline, risk_factors, confidence_level
FROM (Energy Reduction Scenarios)
WHERE target_reduction_percent >= 30 
ORDER BY total_investment ASC, confidence_level DESC;
```

#### Compliance & Reporting Questions:

##### **"Generate our Energy Star submission report"**
**Agent Mapping**: Validator Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- Energy Star Score Estimation
- Data Quality Assessment (compliance verification)
```sql
-- Primary Query: Energy Star submission data
SELECT building_id, reporting_year, total_energy_use, gross_floor_area,
       occupancy_hours, energy_star_score, percentile_ranking,
       data_quality_flags, submission_readiness
FROM (Energy Star Reporting Query)
WHERE reporting_year = EXTRACT(YEAR FROM CURRENT_DATE) - 1;
```

##### **"What's our current carbon footprint and reduction progress?"**
**Agent Mapping**: Energy Data Intelligence Agent + Weather Intelligence Agent  
**Query Mapping**: 
- Carbon Footprint Analysis by Energy Source
- Weather-Energy Correlation Analysis (seasonal adjustments)
```sql
-- Primary Query: Carbon footprint tracking
SELECT reporting_period, total_emissions_mtco2e, scope1_emissions,
       scope2_emissions, emissions_intensity, reduction_from_baseline,
       renewable_energy_percentage
FROM (Carbon Footprint Analysis)
ORDER BY reporting_period DESC;
```

##### **"Are we meeting all regulatory compliance requirements?"**
**Agent Mapping**: Validator Agent  
**Query Mapping**: 
- System Quality Assurance and Error Detection
- Safety and Comfort Constraint Enforcement
```sql
-- Primary Query: Compliance status check
SELECT regulation_type, compliance_status, last_assessment_date,
       next_assessment_due, violations_count, remediation_actions
FROM (Regulatory Compliance Assessment)
WHERE compliance_status IN ('non_compliant', 'at_risk');
```

##### **"Prepare ESG performance summary for investors"**
**Agent Mapping**: Energy Data Intelligence Agent + Optimization Strategy Specialist Agent  
**Query Mapping**: 
- Building Performance Benchmarking
- ROI Analysis for Energy Efficiency Measures
```sql
-- Primary Query: ESG performance metrics
SELECT reporting_period, energy_intensity_reduction, carbon_reduction_percent,
       green_building_certifications, esg_score, investor_metrics,
       sustainability_investments, performance_vs_peers
FROM (ESG Performance Dashboard)
WHERE reporting_period >= CURRENT_DATE - INTERVAL '12 months';
```

##### **"How do we compare to ASHRAE 90.1 standards?"**
**Agent Mapping**: Validator Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- Safety and Comfort Constraint Enforcement (standards compliance)
- Building Performance Benchmarking
```sql
-- Primary Query: ASHRAE 90.1 compliance analysis
SELECT system_type, current_performance, ashrae_standard_requirement,
       compliance_status, gap_analysis, upgrade_recommendations
FROM (ASHRAE Compliance Assessment)
WHERE standard_version = '90.1-2019';
```

### 1.3 Energy/Sustainability Consultants Questions

#### Technical Analysis Questions:

##### **"Perform a comprehensive energy audit analysis for Building B"**
**Agent Mapping**: Energy Data Intelligence Agent + Weather Intelligence Agent + Forecast Intelligence Agent  
**Query Mapping**: 
- Basic Energy Consumption Pattern Analysis
- Weather-Energy Correlation Analysis
- Equipment Failure Prediction
```sql
-- Primary Query: Comprehensive energy audit data
SELECT audit_period, total_energy_use, energy_by_end_use,
       load_profile_analysis, efficiency_opportunities,
       weather_correlation_factors, equipment_condition_scores
FROM (Comprehensive Energy Audit Query)
WHERE building_id = 'Building_B';
```

##### **"What are the weather correlation patterns for heating/cooling loads?"**
**Agent Mapping**: Weather Intelligence Agent  
**Query Mapping**: 
- Weather-Energy Correlation Analysis
- Heating/Cooling Degree Day Analysis
```sql
-- Primary Query: Weather correlation analysis
SELECT season, temperature_range, heating_correlation_coefficient,
       cooling_correlation_coefficient, base_load, weather_sensitivity_factor
FROM (Weather Correlation Analysis)
WHERE meter_type IN ('heating', 'cooling', 'electricity');
```

##### **"Analyze the effectiveness of the recently implemented measures"**
**Agent Mapping**: Validator Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- System Quality Assurance and Error Detection
- Building Baseline Energy Performance Analysis
```sql
-- Primary Query: Measure effectiveness analysis
SELECT measure_name, implementation_date, pre_performance, post_performance,
       actual_savings, predicted_savings, effectiveness_ratio,
       persistence_factor
FROM (Measure Effectiveness Analysis)
WHERE implementation_date >= CURRENT_DATE - INTERVAL '12 months';
```

##### **"Compare performance across different building types in the portfolio"**
**Agent Mapping**: Energy Data Intelligence Agent  
**Query Mapping**: 
- Building Performance Benchmarking
- Energy Use Intensity (EUI) Comparisons
```sql
-- Primary Query: Portfolio performance comparison
SELECT building_type, COUNT(*) as building_count, AVG(eui) as avg_eui,
       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY eui) as q1_eui,
       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY eui) as q3_eui,
       best_performer, worst_performer
FROM (Portfolio Benchmarking)
GROUP BY building_type ORDER BY avg_eui;
```

##### **"Export raw data for third-party modeling and verification"**
**Agent Mapping**: Energy Data Intelligence Agent + Validator Agent  
**Query Mapping**: 
- Data Quality Assessment
- Raw Energy Data Export
```sql
-- Primary Query: Data export with quality metrics
SELECT timestamp, meter_id, value, unit, quality, confidence_score,
       data_source, validation_status
FROM energy.meter_readings 
WHERE building_id = $1 AND timestamp BETWEEN $2 AND $3
AND quality IN ('good', 'fair') ORDER BY timestamp;
```

#### Advanced Optimization Questions:

##### **"What are the optimal demand response strategies for this building?"**
**Agent Mapping**: Forecast Intelligence Agent + System Control Agent  
**Query Mapping**: 
- Peak Demand and Load Shifting Analysis
- Automated Control Parameter Optimization
```sql
-- Primary Query: Demand response optimization
SELECT dr_event_type, optimal_response_strategy, load_reduction_potential,
       financial_incentive, comfort_impact_score, automation_feasibility
FROM (Demand Response Optimization)
WHERE building_id = $1 ORDER BY load_reduction_potential DESC;
```

##### **"How can we implement advanced control algorithms?"**
**Agent Mapping**: System Control Agent + Forecast Intelligence Agent  
**Query Mapping**: 
- Automated Control Parameter Optimization
- Equipment Failure Prediction (control system health)
```sql
-- Primary Query: Advanced control implementation
SELECT control_strategy, algorithm_type, implementation_complexity,
       expected_savings, required_sensors, integration_requirements
FROM (Advanced Control Analysis)
WHERE building_id = $1 AND feasibility_score >= 0.7;
```

##### **"What's the potential for renewable energy integration?"**
**Agent Mapping**: Weather Intelligence Agent + Optimization Strategy Specialist Agent  
**Query Mapping**: 
- Weather-Based Energy Demand Prediction
- ROI Analysis for Energy Efficiency Measures (renewable)
```sql
-- Primary Query: Renewable energy potential
SELECT renewable_type, generation_potential_kwh, capacity_factor,
       installation_cost, payback_period, grid_integration_requirements
FROM (Renewable Energy Assessment)
WHERE building_id = $1 ORDER BY payback_period ASC;
```

##### **"Analyze the building envelope performance impact"**
**Agent Mapping**: Weather Intelligence Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- Weather-Energy Correlation Analysis
- Building Thermal Performance Analysis
```sql
-- Primary Query: Building envelope analysis
SELECT envelope_component, thermal_performance, air_leakage_rate,
       weather_sensitivity, upgrade_recommendations, energy_impact
FROM (Building Envelope Analysis)
WHERE building_id = $1 ORDER BY energy_impact DESC;
```

##### **"What are the opportunities for thermal energy storage?"**
**Agent Mapping**: Forecast Intelligence Agent + System Control Agent  
**Query Mapping**: 
- Peak Demand and Load Shifting Analysis
- System Status and Control Point Monitoring
```sql
-- Primary Query: Thermal storage opportunities
SELECT storage_type, capacity_potential, load_shifting_value,
       installation_requirements, operational_strategy, financial_benefits
FROM (Thermal Storage Analysis)
WHERE building_id = $1 AND feasibility_score >= 0.6;
```

#### Validation & Verification Questions:

##### **"Validate the savings claims from the optimization system"**
**Agent Mapping**: Validator Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- System Quality Assurance and Error Detection
- Building Baseline Energy Performance Analysis
```sql
-- Primary Query: Savings validation analysis
SELECT validation_period, claimed_savings, validated_savings,
       validation_confidence, measurement_uncertainty, adjustment_factors
FROM (Savings Validation Analysis)
WHERE building_id = $1 AND validation_method = 'IPMVP_Option_C';
```

##### **"Perform M&V analysis according to IPMVP protocols"**
**Agent Mapping**: Validator Agent + Weather Intelligence Agent  
**Query Mapping**: 
- System Quality Assurance and Error Detection
- Weather-Energy Correlation Analysis (normalization)
```sql
-- Primary Query: IPMVP M&V analysis
SELECT reporting_period, baseline_model, adjusted_baseline,
       reporting_period_consumption, avoided_consumption,
       uncertainty_bounds, cv_rmse
FROM (IPMVP_MV_Analysis)
WHERE building_id = $1 AND protocol_option = 'Option_C';
```

##### **"What's the measurement uncertainty in our savings calculations?"**
**Agent Mapping**: Validator Agent  
**Query Mapping**: 
- System Quality Assurance and Error Detection
- Data Quality Assessment
```sql
-- Primary Query: Measurement uncertainty analysis
SELECT uncertainty_source, uncertainty_magnitude, impact_on_savings,
       confidence_interval, measurement_accuracy, calibration_status
FROM (Measurement Uncertainty Analysis)
WHERE building_id = $1 ORDER BY uncertainty_magnitude DESC;
```

##### **"Generate third-party audit documentation"**
**Agent Mapping**: Validator Agent + Energy Data Intelligence Agent  
**Query Mapping**: 
- System Quality Assurance and Error Detection
- Data Quality Assessment
```sql
-- Primary Query: Third-party audit documentation
SELECT audit_requirement, documentation_status, data_completeness,
       validation_evidence, compliance_status, audit_trail
FROM (Third_Party_Audit_Documentation)
WHERE building_id = $1 AND audit_standard = 'ISO_50001';
```

##### **"Compare actual vs predicted performance"**
**Agent Mapping**: Forecast Intelligence Agent + Validator Agent  
**Query Mapping**: 
- Long-term Energy Forecasting
- System Quality Assurance and Error Detection
```sql
-- Primary Query: Actual vs predicted performance
SELECT forecast_period, predicted_consumption, actual_consumption,
       variance_percent, prediction_accuracy, model_performance_metrics
FROM (Performance_Prediction_Validation)
WHERE building_id = $1 ORDER BY forecast_period DESC;
```

---

## 2. EAIO System Architecture

### 2.1 Complete System Architecture Overview

```mermaid
graph TB
    subgraph "Stakeholder Layer"
        FM[🔧 Facility Managers]
        BO[💼 Building Owners]
        EC[🔬 Energy Consultants]
    end
    
    subgraph "Input/Output Layer"
        CI[📥 Chat Input<br/>Stakeholder Questions]
        CO[📤 Chat Output<br/>Analysis Results]
    end
    
    subgraph "Coordination Layer"
        COORD[🎯 Coordinator Agent<br/>GPT-4o-mini<br/>Query Routing & Synthesis]
    end
    
    subgraph "Specialized Agent Layer"
        EDA[⚡ Energy Data Intelligence Agent<br/>Consumption Patterns<br/>Anomaly Detection]
        WIA[🌤️ Weather Intelligence Agent<br/>Weather Correlations<br/>Climate Analysis]
        OSA[🎯 Optimization Strategy Agent<br/>ROI Analysis<br/>Investment Planning]
        FIA[📈 Forecast Intelligence Agent<br/>Predictive Modeling<br/>Demand Forecasting]
        SCA[⚙️ System Control Agent<br/>HVAC Optimization<br/>Automated Control]
        VA[🛡️ Validator Agent<br/>Data Quality<br/>Compliance Verification]
    end
    
    subgraph "Database Layer"
        TSDB[(🗄️ EAIO TimescaleDB<br/>Real-time Energy Data<br/>Historical Analytics)]
    end
    
    subgraph "External Systems"
        BMS[🏢 Building Management System]
        WEATHER[🌡️ Weather Services]
        GRID[⚡ Energy Grid]
    end
    
    %% Stakeholder Flows
    FM --> CI
    BO --> CI
    EC --> CI
    
    %% Main Processing Flow
    CI --> COORD
    COORD --> CO
    
    %% Coordinator to Agents
    COORD -.->|Route Query| EDA
    COORD -.->|Route Query| WIA
    COORD -.->|Route Query| OSA
    COORD -.->|Route Query| FIA
    COORD -.->|Route Query| SCA
    COORD -.->|Route Query| VA
    
    %% Agents to Database
    EDA --> TSDB
    WIA --> TSDB
    OSA --> TSDB
    FIA --> TSDB
    SCA --> TSDB
    VA --> TSDB
    
    %% Database to External Systems
    TSDB <--> BMS
    TSDB <--> WEATHER
    TSDB <--> GRID
    
    %% Response Flow
    EDA -.->|Analysis Results| COORD
    WIA -.->|Analysis Results| COORD
    OSA -.->|Analysis Results| COORD
    FIA -.->|Analysis Results| COORD
    SCA -.->|Analysis Results| COORD
    VA -.->|Analysis Results| COORD
    
    %% Styling
    classDef stakeholder fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef coordinator fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef agent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef database fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef external fill:#fff8e1,stroke:#ff8f00,stroke-width:1px
    
    class FM,BO,EC stakeholder
    class COORD coordinator
    class EDA,WIA,OSA,FIA,SCA,VA agent
    class TSDB database
    class BMS,WEATHER,GRID external
```

### 2.2 Agent Specialization Matrix

```mermaid
graph LR
    subgraph "Stakeholder Needs"
        direction TB
        FM_NEEDS["🔧 Facility Managers<br/>• Real-time Monitoring<br/>• Equipment Alerts<br/>• Performance Tracking<br/>• Maintenance Scheduling"]
        BO_NEEDS["💼 Building Owners<br/>• Financial Performance<br/>• ROI Analysis<br/>• Strategic Planning<br/>• Compliance Reports"]
        EC_NEEDS["🔬 Energy Consultants<br/>• Technical Analysis<br/>• Advanced Optimization<br/>• Validation & Verification<br/>• Custom Modeling"]
    end
    
    subgraph "Agent Expertise"
        direction TB
        EDA_EXP["⚡ Energy Data Intelligence<br/>• Consumption Patterns<br/>• Anomaly Detection<br/>• Baseline Analysis<br/>• Performance Benchmarking"]
        WIA_EXP["🌤️ Weather Intelligence<br/>• Weather Correlations<br/>• Climate Impact<br/>• Seasonal Patterns<br/>• Degree Day Analysis"]
        OSA_EXP["🎯 Optimization Strategy<br/>• ROI Calculations<br/>• Investment Analysis<br/>• Cost-Benefit Studies<br/>• Energy Star Certification"]
        FIA_EXP["📈 Forecast Intelligence<br/>• Predictive Modeling<br/>• Demand Forecasting<br/>• Equipment Failure Prediction<br/>• Load Shifting Analysis"]
        SCA_EXP["⚙️ System Control<br/>• HVAC Optimization<br/>• Setpoint Management<br/>• Automated Control<br/>• Comfort Constraints"]
        VA_EXP["🛡️ Validator<br/>• Data Quality Assurance<br/>• Compliance Verification<br/>• Safety Validation<br/>• Error Detection"]
    end
    
    %% Primary Mappings
    FM_NEEDS -.->|Primary| EDA_EXP
    FM_NEEDS -.->|Primary| SCA_EXP
    FM_NEEDS -.->|Secondary| FIA_EXP
    FM_NEEDS -.->|Validation| VA_EXP
    
    BO_NEEDS -.->|Primary| OSA_EXP
    BO_NEEDS -.->|Supporting| EDA_EXP
    BO_NEEDS -.->|Forecasting| FIA_EXP
    BO_NEEDS -.->|Compliance| VA_EXP
    
    EC_NEEDS -.->|Analysis| EDA_EXP
    EC_NEEDS -.->|Correlation| WIA_EXP
    EC_NEEDS -.->|Strategy| OSA_EXP
    EC_NEEDS -.->|Modeling| FIA_EXP
    EC_NEEDS -.->|Control| SCA_EXP
    EC_NEEDS -.->|Validation| VA_EXP
    
    classDef stakeholder fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef agent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class FM_NEEDS,BO_NEEDS,EC_NEEDS stakeholder
    class EDA_EXP,WIA_EXP,OSA_EXP,FIA_EXP,SCA_EXP,VA_EXP agent
```

### 2.3 Database Integration Architecture

```mermaid
graph TB
    subgraph "EAIO TimescaleDB Schema"
        direction TB
        BUILDINGS[(🏢 energy.buildings<br/>Building Metadata<br/>EUI, Ratings, Characteristics)]
        METERS[(📊 energy.energy_meters<br/>Meter Registry<br/>Installation & Status)]
        READINGS[(📈 energy.meter_readings<br/>Time-series Data<br/>Hypertable - 108 chunks)]
        WEATHER[(🌡️ energy.weather_data<br/>Weather Time-series<br/>Hypertable - 25 chunks)]
        ANALYTICS[(🧠 energy.energy_analytics<br/>AI Analysis Results<br/>Insights & Recommendations)]
        HOURLY[(⏰ energy.meter_readings_hourly<br/>Hourly Aggregations<br/>Materialized View)]
        DAILY[(📅 energy.daily_building_consumption<br/>Daily Aggregations<br/>Materialized View)]
        MONTHLY[(📆 energy.monthly_building_profiles<br/>Monthly Aggregations<br/>Materialized View)]
    end
    
    subgraph "Agent Query Patterns"
        direction TB
        EDA_Q["⚡ Energy Data Intelligence<br/>• Consumption Patterns<br/>• Anomaly Detection<br/>• Baseline Analysis"]
        WIA_Q["🌤️ Weather Intelligence<br/>• Weather Correlations<br/>• Degree Day Analysis<br/>• Climate Impact"]
        OSA_Q["🎯 Optimization Strategy<br/>• ROI Analysis<br/>• Investment Calculations<br/>• Performance Benchmarking"]
        FIA_Q["📈 Forecast Intelligence<br/>• Predictive Modeling<br/>• Equipment Failure Prediction<br/>• Load Forecasting"]
        SCA_Q["⚙️ System Control<br/>• Control Optimization<br/>• Setpoint Analysis<br/>• Safety Constraints"]
        VA_Q["🛡️ Validator<br/>• Data Quality Assessment<br/>• Compliance Verification<br/>• Error Detection"]
    end
    
    %% Primary Data Flows
    BUILDINGS --> EDA_Q
    BUILDINGS --> OSA_Q
    BUILDINGS --> VA_Q
    
    METERS --> EDA_Q
    METERS --> SCA_Q
    METERS --> VA_Q
    
    READINGS --> EDA_Q
    READINGS --> FIA_Q
    READINGS --> SCA_Q
    
    WEATHER --> WIA_Q
    WEATHER --> FIA_Q
    
    HOURLY --> EDA_Q
    HOURLY --> OSA_Q
    HOURLY --> FIA_Q
    
    DAILY --> EDA_Q
    DAILY --> OSA_Q
    DAILY --> WIA_Q
    
    MONTHLY --> OSA_Q
    MONTHLY --> FIA_Q
    
    ANALYTICS --> VA_Q
    ANALYTICS --> OSA_Q
    
    classDef table fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef hypertable fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
    classDef view fill:#dcedc8,stroke:#558b2f,stroke-width:2px
    classDef agent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    
    class BUILDINGS,METERS,ANALYTICS table
    class READINGS,WEATHER hypertable
    class HOURLY,DAILY,MONTHLY view
    class EDA_Q,WIA_Q,OSA_Q,FIA_Q,SCA_Q,VA_Q agent
```

---

## 3. Multi-Agent Workflow Designs

### 3.1 Facility Manager Daily Operations Workflow

```mermaid
sequenceDiagram
    participant FM as Facility Manager
    participant Coordinator as LangGraph Coordinator
    participant EnergyAgent as Energy Data Intelligence Agent
    participant WeatherAgent as Weather Intelligence Agent
    participant ControlAgent as System Control Agent
    participant ValidatorAgent as Validator Agent
    participant DB as BDG2 Database
    participant BMS as Building Management System

    FM->>Coordinator: "Show me today's building performance dashboard"
    
    Coordinator->>EnergyAgent: Get current consumption & anomalies
    EnergyAgent->>DB: Execute consumption pattern queries
    DB-->>EnergyAgent: Real-time consumption data
    EnergyAgent->>DB: Execute anomaly detection queries  
    DB-->>EnergyAgent: Anomaly analysis results
    EnergyAgent-->>Coordinator: Current status + detected issues
    
    Coordinator->>WeatherAgent: Get weather impact analysis
    WeatherAgent->>DB: Execute weather correlation queries
    DB-->>WeatherAgent: Weather-energy correlations
    WeatherAgent-->>Coordinator: Weather impact summary
    
    Coordinator->>ControlAgent: Check system health & alerts
    ControlAgent->>DB: Execute BMS monitoring queries
    ControlAgent->>BMS: Get real-time system status
    BMS-->>ControlAgent: Equipment status & alerts
    DB-->>ControlAgent: Control effectiveness metrics
    ControlAgent-->>Coordinator: System health summary
    
    Coordinator->>ValidatorAgent: Validate recommendations safety
    ValidatorAgent->>DB: Execute safety constraint queries
    DB-->>ValidatorAgent: Safety validation results
    ValidatorAgent-->>Coordinator: Safety clearance
    
    Coordinator-->>FM: Comprehensive dashboard with:<br/>- Current consumption<br/>- Detected anomalies<br/>- Weather impacts<br/>- System alerts<br/>- Recommended actions
    
    FM->>Coordinator: "Implement energy savings recommendation #3"
    Coordinator->>ControlAgent: Execute approved optimization
    ControlAgent->>BMS: Apply setpoint adjustments
    BMS-->>ControlAgent: Confirmation of changes
    ControlAgent-->>FM: Optimization implemented successfully
```

### 3.2 Building Owner ROI Analysis Workflow

```mermaid
sequenceDiagram
    participant BO as Building Owner
    participant Coordinator as LangGraph Coordinator
    participant OptimizationAgent as Optimization Strategy Agent
    participant ForecastAgent as Forecast Intelligence Agent
    participant EnergyAgent as Energy Data Intelligence Agent
    participant ValidatorAgent as Validator Agent
    participant DB as BDG2 Database

    BO->>Coordinator: "Show me ROI analysis for our energy optimization program"
    
    Coordinator->>EnergyAgent: Get baseline performance data
    EnergyAgent->>DB: Execute EUI baseline queries
    EnergyAgent->>DB: Execute historical consumption queries
    DB-->>EnergyAgent: Baseline metrics & trends
    EnergyAgent-->>Coordinator: Baseline performance established
    
    Coordinator->>OptimizationAgent: Calculate investment ROI
    OptimizationAgent->>DB: Execute ROI analysis queries
    OptimizationAgent->>DB: Execute payback period queries
    DB-->>OptimizationAgent: Financial performance data
    OptimizationAgent-->>Coordinator: ROI calculations & recommendations
    
    Coordinator->>ForecastAgent: Project future savings
    ForecastAgent->>DB: Execute long-term forecasting queries
    ForecastAgent->>DB: Execute seasonal pattern queries
    DB-->>ForecastAgent: Forecast models & projections
    ForecastAgent-->>Coordinator: Future savings projections
    
    Coordinator->>ValidatorAgent: Validate financial claims
    ValidatorAgent->>DB: Execute performance verification queries
    DB-->>ValidatorAgent: Validation metrics
    ValidatorAgent-->>Coordinator: Validated performance data
    
    Coordinator-->>BO: ROI Analysis Report:<br/>- Current savings: $125K/year<br/>- ROI: 285% over 18 months<br/>- Payback: 14.2 months<br/>- Asset value increase: 8.5%<br/>- Future projections: $200K/year<br/>- Risk assessment: Low
    
    BO->>Coordinator: "What additional investments would maximize ROI?"
    Coordinator->>OptimizationAgent: Analyze investment opportunities
    OptimizationAgent->>DB: Execute optimization scenarios queries
    DB-->>OptimizationAgent: Investment opportunity analysis
    OptimizationAgent-->>BO: Top 5 investment recommendations<br/>with ROI projections
```

### 3.3 Energy Consultant Deep Analysis Workflow

```mermaid
sequenceDiagram
    participant EC as Energy Consultant
    participant Coordinator as LangGraph Coordinator
    participant EnergyAgent as Energy Data Intelligence Agent
    participant WeatherAgent as Weather Intelligence Agent
    participant OptimizationAgent as Optimization Strategy Agent
    participant ForecastAgent as Forecast Intelligence Agent
    participant ValidatorAgent as Validator Agent
    participant DB as BDG2 Database

    EC->>Coordinator: "Perform comprehensive energy audit analysis for Building XYZ"
    
    Note over Coordinator: Initialize multi-agent analysis workflow
    
    par Parallel Data Collection
        Coordinator->>EnergyAgent: Analyze consumption patterns & anomalies
        EnergyAgent->>DB: Execute pattern analysis queries
        EnergyAgent->>DB: Execute anomaly detection queries
        EnergyAgent->>DB: Execute data quality queries
        DB-->>EnergyAgent: Comprehensive energy data analysis
        
        Coordinator->>WeatherAgent: Analyze weather correlations
        WeatherAgent->>DB: Execute weather correlation queries
        WeatherAgent->>DB: Execute degree-day analysis queries
        WeatherAgent->>DB: Execute climate zone queries
        DB-->>WeatherAgent: Weather impact analysis
        
        Coordinator->>ForecastAgent: Analyze equipment performance
        ForecastAgent->>DB: Execute equipment failure prediction queries
        ForecastAgent->>DB: Execute demand response queries
        DB-->>ForecastAgent: Equipment & demand analysis
    end
    
    Coordinator->>OptimizationAgent: Generate optimization strategies
    OptimizationAgent->>DB: Execute optimization recommendation queries
    OptimizationAgent->>DB: Execute risk assessment queries
    DB-->>OptimizationAgent: Optimization strategy analysis
    
    Coordinator->>ValidatorAgent: Validate all findings
    ValidatorAgent->>DB: Execute validation queries
    ValidatorAgent->>DB: Execute system health queries
    DB-->>ValidatorAgent: Validation & quality assessment
    
    Coordinator-->>EC: Comprehensive Audit Report:<br/>- Energy performance analysis<br/>- Weather impact assessment<br/>- Equipment condition report<br/>- Optimization opportunities<br/>- Risk assessment<br/>- M&V recommendations<br/>- Raw data export
    
    EC->>Coordinator: "Export detailed data for third-party modeling"
    Coordinator->>EnergyAgent: Prepare data export
    EnergyAgent->>DB: Execute data export queries
    DB-->>EnergyAgent: Structured data export
    EnergyAgent-->>EC: CSV/JSON export files with metadata
```

### 3.4 Emergency Response Workflow

```mermaid
sequenceDiagram
    participant System as EAIO System
    participant Coordinator as LangGraph Coordinator
    participant EnergyAgent as Energy Data Intelligence Agent
    participant ControlAgent as System Control Agent
    participant ValidatorAgent as Validator Agent
    participant FM as Facility Manager
    participant DB as BDG2 Database
    participant BMS as Building Management System

    System->>Coordinator: CRITICAL ALERT: Consumption spike detected
    
    Coordinator->>EnergyAgent: Immediate anomaly analysis
    EnergyAgent->>DB: Execute emergency anomaly queries
    DB-->>EnergyAgent: Anomaly details & severity
    EnergyAgent-->>Coordinator: CRITICAL: 300% consumption spike in HVAC Zone 2
    
    Coordinator->>ControlAgent: Check safety constraints
    ControlAgent->>DB: Execute safety constraint queries
    ControlAgent->>BMS: Check equipment status
    BMS-->>ControlAgent: Equipment operating beyond limits
    DB-->>ControlAgent: Safety violation detected
    ControlAgent-->>Coordinator: SAFETY RISK: Equipment overload
    
    Coordinator->>ValidatorAgent: Validate emergency response
    ValidatorAgent->>DB: Execute emergency validation queries
    DB-->>ValidatorAgent: Emergency protocols validated
    ValidatorAgent-->>Coordinator: APPROVED: Emergency shutdown recommended
    
    Coordinator->>FM: EMERGENCY ALERT:<br/>Equipment overload in HVAC Zone 2<br/>Immediate action required<br/>Recommended: Emergency shutdown
    
    FM->>Coordinator: "Execute emergency shutdown"
    Coordinator->>ControlAgent: Execute emergency protocol
    ControlAgent->>BMS: Initiate emergency shutdown
    BMS-->>ControlAgent: Emergency shutdown completed
    ControlAgent-->>FM: Emergency resolved - Zone 2 secured
    
    Coordinator->>EnergyAgent: Generate incident report
    EnergyAgent->>DB: Execute incident analysis queries
    DB-->>EnergyAgent: Incident timeline & impact
    EnergyAgent-->>FM: Incident Report:<br/>- Root cause analysis<br/>- Timeline of events<br/>- Impact assessment<br/>- Prevention recommendations
```

### 3.5 Cross-Stakeholder Collaborative Workflow

```mermaid
sequenceDiagram
    participant BO as Building Owner
    participant FM as Facility Manager
    participant EC as Energy Consultant
    participant Coordinator as LangGraph Coordinator
    participant AllAgents as Multi-Agent System
    participant DB as BDG2 Database

    BO->>Coordinator: "Plan quarterly optimization review meeting"
    
    Coordinator->>AllAgents: Prepare stakeholder-specific reports
    
    par Parallel Report Generation
        AllAgents->>DB: Execute owner ROI queries
        AllAgents->>DB: Execute manager operational queries
        AllAgents->>DB: Execute consultant technical queries
    end
    
    DB-->>AllAgents: Comprehensive data for all stakeholders
    AllAgents-->>Coordinator: Generated reports for each stakeholder
    
    Coordinator-->>BO: Executive Summary:<br/>- Financial performance<br/>- Strategic recommendations
    Coordinator-->>FM: Operational Summary:<br/>- System performance<br/>- Maintenance needs
    Coordinator-->>EC: Technical Summary:<br/>- Detailed analytics<br/>- Optimization opportunities
    
    Note over BO,EC: Virtual Meeting Begins
    
    FM->>Coordinator: "Report operational concerns about Zone 3 efficiency"
    Coordinator->>AllAgents: Analyze Zone 3 performance
    AllAgents->>DB: Execute zone-specific analysis
    DB-->>AllAgents: Zone 3 detailed analysis
    AllAgents-->>Coordinator: Zone 3 needs HVAC recalibration
    
    EC->>Coordinator: "What's the technical feasibility and ROI for Zone 3 upgrade?"
    Coordinator->>AllAgents: Calculate upgrade feasibility
    AllAgents->>DB: Execute upgrade analysis queries
    DB-->>AllAgents: Technical & financial feasibility
    AllAgents-->>Coordinator: Upgrade recommended: 18-month payback
    
    BO->>Coordinator: "Approve Zone 3 upgrade if ROI > 200%"
    Coordinator-->>BO: ROI = 285% - APPROVED for implementation
    Coordinator-->>FM: Implementation scheduled for next month
    Coordinator-->>EC: Technical oversight requested for upgrade
```

---

## 4. Agent Orchestration Patterns

### 4.1 Sequential Processing Pattern
Used for: Complex analysis requiring step-by-step data processing
- **Flow**: User Query → Agent 1 → Agent 2 → Agent 3 → Response
- **Example**: Energy audit requiring baseline → weather analysis → optimization → validation

### 4.2 Parallel Processing Pattern  
Used for: Independent data collection that can run simultaneously
- **Flow**: User Query → Parallel(Agent 1, Agent 2, Agent 3) → Merge → Response
- **Example**: Dashboard generation requiring current data from multiple sources

### 4.3 Conditional Branching Pattern
Used for: Decision-driven workflows based on data analysis
- **Flow**: User Query → Analysis Agent → Decision Point → Appropriate Specialist Agent → Response
- **Example**: Alert handling routing to appropriate response protocol

### 4.4 Iterative Refinement Pattern
Used for: Optimization and learning workflows
- **Flow**: User Query → Initial Analysis → Refinement Loop → Validation → Response
- **Example**: Optimization strategy development with iterative improvement

---

## 5. Implementation Considerations

### 5.1 Agent Communication Protocols
- **State Management**: Shared context across agent interactions
- **Data Formatting**: Standardized data exchange between agents
- **Error Handling**: Graceful degradation when agents fail
- **Performance Monitoring**: Track agent response times and accuracy

### 5.2 Database Query Optimization
- **Query Caching**: Cache frequently used query results
- **Parallel Execution**: Run independent queries simultaneously
- **Result Streaming**: Stream large datasets to prevent timeouts
- **Incremental Updates**: Update only changed data for efficiency

### 5.3 User Experience Design
- **Progressive Disclosure**: Show summary first, details on demand
- **Real-time Updates**: Live updates for monitoring workflows
- **Contextual Help**: Agent-specific guidance and explanations
- **Multi-modal Output**: Charts, tables, and narrative summaries

### 5.4 Security and Compliance
- **Data Privacy**: Ensure sensitive data protection
- **Access Control**: Role-based access to different agent capabilities
- **Audit Logging**: Track all agent interactions and decisions
- **Regulatory Compliance**: Meet energy reporting requirements

---

## 6. Success Metrics and KPIs

### 6.1 Stakeholder Satisfaction Metrics
- **Facility Managers**: Response time < 30 seconds, 95% accuracy
- **Building Owners**: ROI reports delivered in < 2 minutes
- **Energy Consultants**: Data export completed in < 5 minutes

### 6.2 System Performance Metrics
- **Agent Coordination**: Successful multi-agent workflows > 98%
- **Database Performance**: Query response time < 5 seconds
- **Error Recovery**: Automatic error recovery > 95%

### 6.3 Business Impact Metrics
- **Energy Savings**: 20-30% reduction in energy consumption
- **Cost Savings**: $50K-$500K annually per building
- **User Adoption**: 90% active user engagement within 3 months

---

*This agentic workflow design ensures that each stakeholder receives tailored, accurate, and actionable information through coordinated multi-agent interactions, leveraging the full capabilities of the EAIO system's specialized agents and comprehensive database queries.*