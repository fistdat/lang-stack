# EAIO Agent Database Queries

## Overview
This document contains SQL queries designed for each specialized agent in the Energy AI Optimizer (EAIO) system. All queries are optimized for the TimescaleDB-powered EAIO energy database and leverage the time-series capabilities for efficient energy analytics.

---

## 1. Energy Data Intelligence Agent

### Time-series Analysis Queries

#### Basic Energy Consumption Pattern Analysis
```sql
-- Hourly energy consumption patterns for a specific building
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    meter_type,
    AVG(value) as avg_consumption,
    SUM(value) as total_consumption,
    MIN(value) as min_consumption,
    MAX(value) as max_consumption,
    COUNT(*) as reading_count
FROM energy.meter_readings 
WHERE building_id = $1 
    AND timestamp >= $2 
    AND timestamp <= $3
    AND quality = 'good'
GROUP BY DATE_TRUNC('hour', timestamp), meter_type
ORDER BY hour, meter_type;
```

#### Daily Consumption Trends by Building Type
```sql
-- Daily consumption analysis by building usage type
SELECT 
    b.primary_space_usage,
    b.sub_primary_space_usage,
    DATE_TRUNC('day', mr.timestamp) as day,
    AVG(mr.value) as avg_daily_consumption,
    SUM(mr.value) as total_daily_consumption,
    COUNT(DISTINCT mr.building_id) as building_count
FROM energy.meter_readings mr
JOIN energy.buildings b ON mr.building_id = b.building_id
WHERE mr.timestamp >= $1 
    AND mr.timestamp <= $2
    AND mr.meter_type = $3
    AND mr.quality = 'good'
GROUP BY b.primary_space_usage, b.sub_primary_space_usage, DATE_TRUNC('day', mr.timestamp)
ORDER BY day, avg_daily_consumption DESC;
```

### Anomaly Detection Queries

#### Consumption Outlier Detection
```sql
-- Detect consumption outliers using statistical analysis
WITH consumption_stats AS (
    SELECT 
        meter_id,
        building_id,
        meter_type,
        AVG(value) as mean_consumption,
        STDDEV(value) as std_consumption,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as q3
    FROM energy.meter_readings
    WHERE timestamp >= $1 
        AND timestamp <= $2
        AND quality = 'good'
        AND building_id = $3
    GROUP BY meter_id, building_id, meter_type
),
outlier_bounds AS (
    SELECT *,
        q1 - 1.5 * (q3 - q1) as lower_bound,
        q3 + 1.5 * (q3 - q1) as upper_bound,
        mean_consumption - 3 * std_consumption as stat_lower_bound,
        mean_consumption + 3 * std_consumption as stat_upper_bound
    FROM consumption_stats
)
SELECT 
    mr.timestamp,
    mr.meter_id,
    mr.building_id,
    mr.meter_type,
    mr.value as consumption_value,
    ob.mean_consumption,
    ob.std_consumption,
    CASE 
        WHEN mr.value < ob.lower_bound OR mr.value > ob.upper_bound THEN 'iqr_outlier'
        WHEN mr.value < ob.stat_lower_bound OR mr.value > ob.stat_upper_bound THEN 'statistical_outlier'
        ELSE 'normal'
    END as outlier_type,
    ABS(mr.value - ob.mean_consumption) / NULLIF(ob.std_consumption, 0) as z_score
FROM energy.meter_readings mr
JOIN outlier_bounds ob ON mr.meter_id = ob.meter_id
WHERE mr.timestamp >= $1 
    AND mr.timestamp <= $2
    AND mr.building_id = $3
    AND (mr.value < ob.lower_bound OR mr.value > ob.upper_bound 
         OR mr.value < ob.stat_lower_bound OR mr.value > ob.stat_upper_bound)
ORDER BY mr.timestamp DESC;
```

#### Unusual Pattern Detection
```sql
-- Detect unusual consumption patterns (e.g., high consumption during off-hours)
SELECT 
    building_id,
    meter_id,
    meter_type,
    timestamp,
    value as consumption,
    EXTRACT(hour FROM timestamp) as hour_of_day,
    EXTRACT(dow FROM timestamp) as day_of_week,
    CASE 
        WHEN EXTRACT(hour FROM timestamp) BETWEEN 22 AND 6 THEN 'off_hours'
        WHEN EXTRACT(dow FROM timestamp) IN (0, 6) THEN 'weekend'
        ELSE 'business_hours'
    END as time_category,
    value / NULLIF(
        LAG(value, 1) OVER (
            PARTITION BY meter_id 
            ORDER BY timestamp
        ), 0
    ) as consumption_ratio
FROM energy.meter_readings
WHERE building_id = $1
    AND timestamp >= $2
    AND timestamp <= $3
    AND quality = 'good'
    AND (
        (EXTRACT(hour FROM timestamp) BETWEEN 22 AND 6 AND value > $4) -- High off-hours consumption
        OR 
        (EXTRACT(dow FROM timestamp) IN (0, 6) AND value > $5) -- High weekend consumption
    )
ORDER BY timestamp DESC;
```

### Baseline Performance Analysis

#### Energy Use Intensity (EUI) Baseline
```sql
-- Calculate building EUI baseline and compare with benchmarks
SELECT 
    b.building_id,
    b.primary_space_usage,
    b.square_feet,
    b.occupants,
    b.year_built,
    b.energy_star_score,
    b.eui as official_eui,
    SUM(CASE WHEN mr.meter_type = 'electricity' THEN mr.value ELSE 0 END) as total_electricity_kwh,
    SUM(CASE WHEN mr.meter_type = 'gas' THEN mr.value ELSE 0 END) as total_gas_usage,
    SUM(mr.value) as total_energy_consumption,
    (SUM(mr.value) * 3412) / NULLIF(b.square_feet, 0) as calculated_eui, -- Convert to BTU/sq ft
    CASE 
        WHEN b.energy_star_score >= 75 THEN 'excellent'
        WHEN b.energy_star_score >= 50 THEN 'good'
        WHEN b.energy_star_score >= 25 THEN 'average'
        ELSE 'below_average'
    END as energy_performance_category
FROM energy.buildings b
JOIN energy.meter_readings mr ON b.building_id = mr.building_id
WHERE mr.timestamp >= $1 
    AND mr.timestamp <= $2
    AND mr.quality = 'good'
    AND b.building_id = $3
GROUP BY b.building_id, b.primary_space_usage, b.square_feet, b.occupants, 
         b.year_built, b.energy_star_score, b.eui;
```

#### Peak Demand Analysis
```sql
-- Analyze peak demand patterns and load factors
WITH hourly_consumption AS (
    SELECT 
        building_id,
        meter_id,
        meter_type,
        DATE_TRUNC('hour', timestamp) as hour,
        AVG(value) as avg_hourly_consumption,
        MAX(value) as peak_hourly_consumption
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= $2
        AND timestamp <= $3
        AND quality = 'good'
    GROUP BY building_id, meter_id, meter_type, DATE_TRUNC('hour', timestamp)
)
SELECT 
    building_id,
    meter_type,
    MAX(peak_hourly_consumption) as absolute_peak_demand,
    AVG(avg_hourly_consumption) as average_demand,
    AVG(avg_hourly_consumption) / NULLIF(MAX(peak_hourly_consumption), 0) as load_factor,
    EXTRACT(hour FROM hour) as peak_hour,
    EXTRACT(dow FROM hour) as peak_day_of_week
FROM hourly_consumption
WHERE peak_hourly_consumption = (
    SELECT MAX(peak_hourly_consumption) 
    FROM hourly_consumption hc2 
    WHERE hc2.meter_type = hourly_consumption.meter_type
)
GROUP BY building_id, meter_type, hour
ORDER BY absolute_peak_demand DESC;
```

### Data Quality Assessment

#### Data Completeness Analysis
```sql
-- Assess data completeness and quality scores
WITH expected_readings AS (
    SELECT 
        em.meter_id,
        em.building_id,
        em.meter_type,
        em.data_start_date,
        em.data_end_date,
        EXTRACT(epoch FROM (COALESCE(em.data_end_date::timestamp, CURRENT_TIMESTAMP) - em.data_start_date::timestamp)) / 3600 as expected_hours
    FROM energy.energy_meters em
    WHERE em.building_id = $1
        AND em.status = 'active'
),
actual_readings AS (
    SELECT 
        meter_id,
        COUNT(*) as actual_reading_count,
        COUNT(CASE WHEN quality = 'good' THEN 1 END) as good_quality_count,
        COUNT(CASE WHEN is_outlier = true THEN 1 END) as outlier_count,
        AVG(confidence_score) as avg_confidence_score
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= $2
        AND timestamp <= $3
    GROUP BY meter_id
)
SELECT 
    er.meter_id,
    er.building_id,
    er.meter_type,
    er.expected_hours,
    COALESCE(ar.actual_reading_count, 0) as actual_readings,
    COALESCE(ar.good_quality_count, 0) as good_quality_readings,
    COALESCE(ar.outlier_count, 0) as outlier_readings,
    COALESCE(ar.avg_confidence_score, 0) as avg_confidence_score,
    (COALESCE(ar.actual_reading_count, 0) * 100.0) / NULLIF(er.expected_hours, 0) as completeness_percentage,
    (COALESCE(ar.good_quality_count, 0) * 100.0) / NULLIF(ar.actual_reading_count, 0) as quality_percentage
FROM expected_readings er
LEFT JOIN actual_readings ar ON er.meter_id = ar.meter_id
ORDER BY completeness_percentage DESC;
```

---

## 2. Weather Intelligence Agent

### Weather Pattern Analysis

#### Weather-Energy Correlation Analysis
```sql
-- Analyze correlation between weather conditions and energy consumption
SELECT 
    DATE_TRUNC('hour', mr.timestamp) as hour,
    mr.meter_type,
    AVG(mr.value) as avg_consumption,
    AVG(wd.air_temperature) as avg_temperature,
    AVG(wd.dew_temperature) as avg_dew_point,
    AVG(wd.wind_speed) as avg_wind_speed,
    AVG(wd.cloud_coverage) as avg_cloud_coverage,
    AVG(wd.sea_level_pressure) as avg_pressure,
    CORR(mr.value, wd.air_temperature) as temp_correlation,
    CORR(mr.value, wd.wind_speed) as wind_correlation
FROM energy.meter_readings mr
JOIN energy.buildings b ON mr.building_id = b.building_id
JOIN energy.weather_data wd ON b.site_id = wd.site_id 
    AND DATE_TRUNC('hour', mr.timestamp) = DATE_TRUNC('hour', wd.timestamp)
WHERE mr.building_id = $1
    AND mr.timestamp >= $2
    AND mr.timestamp <= $3
    AND mr.quality = 'good'
    AND wd.quality_flag = 'good'
GROUP BY DATE_TRUNC('hour', mr.timestamp), mr.meter_type
ORDER BY hour;
```

#### Cooling/Heating Degree Days Analysis
```sql
-- Calculate cooling and heating degree days with energy impact
WITH daily_weather AS (
    SELECT 
        wd.site_id,
        DATE_TRUNC('day', wd.timestamp) as day,
        AVG(wd.air_temperature) as avg_daily_temp,
        MAX(wd.air_temperature) as max_daily_temp,
        MIN(wd.air_temperature) as min_daily_temp
    FROM energy.weather_data wd
    JOIN energy.buildings b ON wd.site_id = b.site_id
    WHERE b.building_id = $1
        AND wd.timestamp >= $2
        AND wd.timestamp <= $3
        AND wd.quality_flag = 'good'
    GROUP BY wd.site_id, DATE_TRUNC('day', wd.timestamp)
),
degree_days AS (
    SELECT 
        site_id,
        day,
        avg_daily_temp,
        GREATEST(0, 65 - avg_daily_temp) as heating_degree_day, -- Base 65°F
        GREATEST(0, avg_daily_temp - 65) as cooling_degree_day
    FROM daily_weather
),
daily_consumption AS (
    SELECT 
        building_id,
        meter_type,
        DATE_TRUNC('day', timestamp) as day,
        SUM(value) as total_daily_consumption
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= $2
        AND timestamp <= $3
        AND quality = 'good'
    GROUP BY building_id, meter_type, DATE_TRUNC('day', timestamp)
)
SELECT 
    dd.day,
    dd.avg_daily_temp,
    dd.heating_degree_day,
    dd.cooling_degree_day,
    dc.meter_type,
    dc.total_daily_consumption,
    CORR(dd.heating_degree_day, dc.total_daily_consumption) OVER (PARTITION BY dc.meter_type) as heating_correlation,
    CORR(dd.cooling_degree_day, dc.total_daily_consumption) OVER (PARTITION BY dc.meter_type) as cooling_correlation
FROM degree_days dd
JOIN energy.buildings b ON dd.site_id = b.site_id
JOIN daily_consumption dc ON b.building_id = dc.building_id AND dd.day = dc.day
WHERE b.building_id = $1
ORDER BY dd.day, dc.meter_type;
```

### Weather Forecasting for Energy Planning

#### Weather-Based Energy Demand Prediction
```sql
-- Historical weather patterns for predictive modeling
WITH weather_features AS (
    SELECT 
        wd.site_id,
        wd.timestamp,
        wd.air_temperature,
        wd.dew_temperature,
        wd.wind_speed,
        wd.cloud_coverage,
        LAG(wd.air_temperature, 1) OVER (PARTITION BY wd.site_id ORDER BY wd.timestamp) as prev_temp,
        LAG(wd.air_temperature, 24) OVER (PARTITION BY wd.site_id ORDER BY wd.timestamp) as temp_24h_ago,
        EXTRACT(hour FROM wd.timestamp) as hour_of_day,
        EXTRACT(dow FROM wd.timestamp) as day_of_week,
        EXTRACT(month FROM wd.timestamp) as month_of_year
    FROM energy.weather_data wd
    WHERE wd.timestamp >= $1
        AND wd.timestamp <= $2
        AND wd.quality_flag = 'good'
),
consumption_features AS (
    SELECT 
        mr.timestamp,
        mr.building_id,
        mr.meter_type,
        mr.value as consumption,
        LAG(mr.value, 1) OVER (PARTITION BY mr.meter_id ORDER BY mr.timestamp) as prev_consumption,
        LAG(mr.value, 24) OVER (PARTITION BY mr.meter_id ORDER BY mr.timestamp) as consumption_24h_ago
    FROM energy.meter_readings mr
    WHERE mr.building_id = $3
        AND mr.timestamp >= $1
        AND mr.timestamp <= $2
        AND mr.quality = 'good'
)
SELECT 
    cf.timestamp,
    cf.building_id,
    cf.meter_type,
    cf.consumption,
    cf.prev_consumption,
    cf.consumption_24h_ago,
    wf.air_temperature,
    wf.dew_temperature,
    wf.wind_speed,
    wf.cloud_coverage,
    wf.prev_temp,
    wf.temp_24h_ago,
    wf.hour_of_day,
    wf.day_of_week,
    wf.month_of_year,
    -- Temperature change indicators
    wf.air_temperature - wf.prev_temp as temp_change_1h,
    wf.air_temperature - wf.temp_24h_ago as temp_change_24h
FROM consumption_features cf
JOIN energy.buildings b ON cf.building_id = b.building_id
JOIN weather_features wf ON b.site_id = wf.site_id AND cf.timestamp = wf.timestamp
ORDER BY cf.timestamp;
```

### Climate Zone Analysis

#### Building Performance by Climate Conditions
```sql
-- Analyze building performance across different climate conditions
WITH climate_categories AS (
    SELECT 
        wd.site_id,
        DATE_TRUNC('month', wd.timestamp) as month,
        AVG(wd.air_temperature) as avg_monthly_temp,
        SUM(wd.precip_depth_1hr) as total_monthly_precip,
        AVG(wd.wind_speed) as avg_monthly_wind,
        CASE 
            WHEN AVG(wd.air_temperature) < 32 THEN 'cold'
            WHEN AVG(wd.air_temperature) BETWEEN 32 AND 65 THEN 'mild'
            WHEN AVG(wd.air_temperature) BETWEEN 65 AND 80 THEN 'warm'
            ELSE 'hot'
        END as climate_category
    FROM energy.weather_data wd
    WHERE wd.timestamp >= $1
        AND wd.timestamp <= $2
        AND wd.quality_flag = 'good'
    GROUP BY wd.site_id, DATE_TRUNC('month', wd.timestamp)
),
monthly_consumption AS (
    SELECT 
        mr.building_id,
        mr.meter_type,
        DATE_TRUNC('month', mr.timestamp) as month,
        SUM(mr.value) as total_monthly_consumption,
        AVG(mr.value) as avg_monthly_consumption
    FROM energy.meter_readings mr
    WHERE mr.timestamp >= $1
        AND mr.timestamp <= $2
        AND mr.quality = 'good'
    GROUP BY mr.building_id, mr.meter_type, DATE_TRUNC('month', mr.timestamp)
)
SELECT 
    cc.climate_category,
    mc.meter_type,
    COUNT(DISTINCT mc.building_id) as building_count,
    AVG(mc.total_monthly_consumption) as avg_consumption_by_climate,
    AVG(cc.avg_monthly_temp) as avg_temp_by_climate,
    AVG(cc.total_monthly_precip) as avg_precip_by_climate,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY mc.total_monthly_consumption) as median_consumption
FROM climate_categories cc
JOIN energy.buildings b ON cc.site_id = b.site_id
JOIN monthly_consumption mc ON b.building_id = mc.building_id AND cc.month = mc.month
WHERE ($3 IS NULL OR b.building_id = $3)
GROUP BY cc.climate_category, mc.meter_type
ORDER BY cc.climate_category, mc.meter_type;
```

---

## 3. Optimization Strategy Specialist Agent

### Multi-objective Optimization Analysis

#### ROI Analysis for Energy Efficiency Measures
```sql
-- Calculate potential ROI for various optimization strategies
WITH baseline_consumption AS (
    SELECT 
        building_id,
        meter_type,
        AVG(value) as avg_hourly_consumption,
        SUM(value) as total_consumption,
        COUNT(*) as reading_count
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= $2
        AND timestamp <= $3
        AND quality = 'good'
    GROUP BY building_id, meter_type
),
building_characteristics AS (
    SELECT 
        b.building_id,
        b.primary_space_usage,
        b.square_feet,
        b.year_built,
        b.heating_type,
        b.occupants,
        b.energy_star_score,
        b.eui,
        CASE 
            WHEN b.year_built < 1980 THEN 'old'
            WHEN b.year_built BETWEEN 1980 AND 2000 THEN 'medium'
            ELSE 'modern'
        END as building_age_category
    FROM energy.buildings b
    WHERE b.building_id = $1
)
SELECT 
    bc.building_id,
    bc.primary_space_usage,
    bc.building_age_category,
    bc.square_feet,
    bc.energy_star_score,
    baseline.meter_type,
    baseline.total_consumption,
    baseline.avg_hourly_consumption,
    -- Optimization potential calculations
    CASE 
        WHEN bc.energy_star_score < 50 AND bc.building_age_category = 'old' THEN baseline.total_consumption * 0.25
        WHEN bc.energy_star_score < 50 THEN baseline.total_consumption * 0.20
        WHEN bc.energy_star_score < 75 THEN baseline.total_consumption * 0.15
        ELSE baseline.total_consumption * 0.10
    END as potential_savings,
    -- Cost estimates (simplified)
    CASE 
        WHEN baseline.meter_type = 'electricity' THEN baseline.total_consumption * 0.12 -- $0.12/kWh
        WHEN baseline.meter_type = 'gas' THEN baseline.total_consumption * 0.08 -- $0.08/therm
        ELSE baseline.total_consumption * 0.05
    END as current_annual_cost,
    -- ROI calculations
    CASE 
        WHEN bc.building_age_category = 'old' THEN bc.square_feet * 15 -- $15/sqft retrofit cost
        WHEN bc.building_age_category = 'medium' THEN bc.square_feet * 10
        ELSE bc.square_feet * 5
    END as estimated_implementation_cost
FROM building_characteristics bc
JOIN baseline_consumption baseline ON bc.building_id = baseline.building_id
ORDER BY potential_savings DESC;
```

#### Building-Specific Optimization Recommendations
```sql
-- Generate tailored recommendations based on building characteristics and usage patterns
WITH usage_patterns AS (
    SELECT 
        building_id,
        meter_type,
        EXTRACT(hour FROM timestamp) as hour_of_day,
        AVG(value) as avg_hourly_consumption,
        STDDEV(value) as consumption_variability
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= $2
        AND timestamp <= $3
        AND quality = 'good'
    GROUP BY building_id, meter_type, EXTRACT(hour FROM timestamp)
),
peak_usage_hours AS (
    SELECT 
        building_id,
        meter_type,
        hour_of_day,
        avg_hourly_consumption,
        RANK() OVER (PARTITION BY building_id, meter_type ORDER BY avg_hourly_consumption DESC) as consumption_rank
    FROM usage_patterns
),
building_profile AS (
    SELECT 
        b.building_id,
        b.primary_space_usage,
        b.heating_type,
        b.square_feet,
        b.occupants,
        b.year_built,
        b.energy_star_score,
        COALESCE(b.square_feet / NULLIF(b.occupants, 0), 0) as sqft_per_occupant
    FROM energy.buildings b
    WHERE b.building_id = $1
)
SELECT 
    bp.building_id,
    bp.primary_space_usage,
    bp.heating_type,
    bp.energy_star_score,
    bp.sqft_per_occupant,
    puh.meter_type,
    puh.hour_of_day as peak_hour,
    puh.avg_hourly_consumption as peak_consumption,
    -- Specific recommendations based on building type and patterns
    CASE 
        WHEN bp.primary_space_usage = 'Office' AND puh.hour_of_day BETWEEN 18 AND 8 
        THEN 'Implement occupancy-based HVAC scheduling'
        WHEN bp.primary_space_usage = 'Office' AND puh.meter_type = 'electricity' 
        THEN 'LED lighting retrofit with daylight sensors'
        WHEN bp.heating_type = 'Electric' AND puh.meter_type = 'electricity'
        THEN 'Heat pump upgrade for improved efficiency'
        WHEN bp.sqft_per_occupant > 1000 
        THEN 'Zone-based HVAC control for unused areas'
        WHEN bp.energy_star_score < 50
        THEN 'Comprehensive energy audit and building envelope improvements'
        ELSE 'Fine-tune existing systems for optimal performance'
    END as primary_recommendation,
    -- Priority scoring
    CASE 
        WHEN bp.energy_star_score < 30 THEN 'high'
        WHEN bp.energy_star_score < 60 THEN 'medium'
        ELSE 'low'
    END as implementation_priority
FROM building_profile bp
CROSS JOIN peak_usage_hours puh
WHERE puh.building_id = bp.building_id
    AND puh.consumption_rank <= 3 -- Top 3 peak hours
ORDER BY puh.consumption_rank, puh.meter_type;
```

### Investment Priority Analysis

#### Payback Period Analysis
```sql
-- Calculate payback periods for different optimization measures
WITH current_performance AS (
    SELECT 
        mr.building_id,
        mr.meter_type,
        SUM(mr.value) as annual_consumption,
        AVG(mr.value) as avg_consumption
    FROM energy.meter_readings mr
    WHERE mr.building_id = $1
        AND mr.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '12 months')
        AND mr.quality = 'good'
    GROUP BY mr.building_id, mr.meter_type
),
optimization_scenarios AS (
    SELECT 
        $1 as building_id,
        'HVAC Upgrade' as measure_name,
        0.20 as efficiency_improvement,
        25000 as implementation_cost,
        15 as measure_lifetime_years
    UNION ALL
    SELECT 
        $1, 'LED Lighting', 0.30, 15000, 10
    UNION ALL
    SELECT 
        $1, 'Building Automation System', 0.15, 35000, 20
    UNION ALL
    SELECT 
        $1, 'Window Replacement', 0.18, 45000, 25
    UNION ALL
    SELECT 
        $1, 'Insulation Upgrade', 0.12, 20000, 30
),
energy_rates AS (
    SELECT 
        'electricity' as meter_type,
        0.12 as rate_per_unit
    UNION ALL
    SELECT 
        'gas' as meter_type,
        0.08 as rate_per_unit
)
SELECT 
    os.measure_name,
    os.efficiency_improvement,
    os.implementation_cost,
    os.measure_lifetime_years,
    cp.meter_type,
    cp.annual_consumption,
    cp.annual_consumption * os.efficiency_improvement as annual_savings_kwh,
    (cp.annual_consumption * os.efficiency_improvement * er.rate_per_unit) as annual_cost_savings,
    os.implementation_cost / NULLIF((cp.annual_consumption * os.efficiency_improvement * er.rate_per_unit), 0) as simple_payback_years,
    ((cp.annual_consumption * os.efficiency_improvement * er.rate_per_unit) * os.measure_lifetime_years) - os.implementation_cost as lifetime_net_savings
FROM optimization_scenarios os
CROSS JOIN current_performance cp
JOIN energy_rates er ON cp.meter_type = er.meter_type
WHERE cp.building_id = os.building_id
ORDER BY simple_payback_years ASC;
```

### Feasibility and Risk Assessment

#### Implementation Risk Analysis
```sql
-- Assess implementation risks and constraints
WITH building_constraints AS (
    SELECT 
        b.building_id,
        b.year_built,
        b.square_feet,
        b.primary_space_usage,
        b.occupants,
        b.heating_type,
        em.meter_type,
        COUNT(DISTINCT em.meter_id) as meter_count,
        AVG(em.quality_score) as avg_meter_quality,
        -- Risk factors
        CASE 
            WHEN b.year_built < 1970 THEN 'high_structural_risk'
            WHEN b.year_built < 1990 THEN 'medium_structural_risk'
            ELSE 'low_structural_risk'
        END as structural_risk,
        CASE 
            WHEN b.primary_space_usage IN ('Hospital', 'Data Center') THEN 'critical_operations'
            WHEN b.primary_space_usage IN ('Office', 'Retail') THEN 'standard_operations'
            ELSE 'flexible_operations'
        END as operational_criticality
    FROM energy.buildings b
    JOIN energy.energy_meters em ON b.building_id = em.building_id
    WHERE b.building_id = $1
        AND em.status = 'active'
    GROUP BY b.building_id, b.year_built, b.square_feet, b.primary_space_usage, 
             b.occupants, b.heating_type, em.meter_type
),
data_reliability AS (
    SELECT 
        building_id,
        meter_type,
        COUNT(*) as total_readings,
        COUNT(CASE WHEN quality = 'good' THEN 1 END) as good_readings,
        COUNT(CASE WHEN is_outlier = true THEN 1 END) as outlier_readings,
        AVG(confidence_score) as avg_confidence
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= (CURRENT_TIMESTAMP - INTERVAL '3 months')
    GROUP BY building_id, meter_type
)
SELECT 
    bc.building_id,
    bc.meter_type,
    bc.structural_risk,
    bc.operational_criticality,
    bc.avg_meter_quality,
    dr.good_readings::float / NULLIF(dr.total_readings, 0) as data_quality_score,
    dr.avg_confidence,
    -- Overall risk scoring
    CASE 
        WHEN bc.structural_risk = 'high_structural_risk' OR bc.operational_criticality = 'critical_operations' 
        THEN 'high_risk'
        WHEN bc.structural_risk = 'medium_structural_risk' AND bc.operational_criticality = 'standard_operations'
        THEN 'medium_risk'
        ELSE 'low_risk'
    END as overall_implementation_risk,
    -- Recommendations based on risk
    CASE 
        WHEN bc.structural_risk = 'high_structural_risk' 
        THEN 'Require detailed structural assessment before implementation'
        WHEN bc.operational_criticality = 'critical_operations'
        THEN 'Phase implementation to minimize operational disruption'
        WHEN dr.good_readings::float / NULLIF(dr.total_readings, 0) < 0.8
        THEN 'Improve data collection quality before optimization'
        ELSE 'Proceed with standard implementation approach'
    END as risk_mitigation_strategy
FROM building_constraints bc
LEFT JOIN data_reliability dr ON bc.building_id = dr.building_id AND bc.meter_type = dr.meter_type
ORDER BY bc.meter_type;
```

---

## 4. Forecast Intelligence Agent

### Short-term and Long-term Energy Forecasting

#### Short-term Energy Consumption Prediction (24-48 hours)
```sql
-- Generate features for short-term energy forecasting model
WITH recent_consumption AS (
    SELECT 
        building_id,
        meter_id,
        meter_type,
        timestamp,
        value as consumption,
        LAG(value, 1) OVER (PARTITION BY meter_id ORDER BY timestamp) as lag_1h,
        LAG(value, 24) OVER (PARTITION BY meter_id ORDER BY timestamp) as lag_24h,
        LAG(value, 168) OVER (PARTITION BY meter_id ORDER BY timestamp) as lag_168h, -- 1 week
        AVG(value) OVER (
            PARTITION BY meter_id 
            ORDER BY timestamp 
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) as rolling_24h_avg,
        AVG(value) OVER (
            PARTITION BY meter_id 
            ORDER BY timestamp 
            ROWS BETWEEN 167 PRECEDING AND CURRENT ROW
        ) as rolling_7day_avg,
        EXTRACT(hour FROM timestamp) as hour_of_day,
        EXTRACT(dow FROM timestamp) as day_of_week,
        EXTRACT(month FROM timestamp) as month_of_year
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= (CURRENT_TIMESTAMP - INTERVAL '30 days')
        AND quality = 'good'
        AND meter_type = $2
),
weather_features AS (
    SELECT 
        wd.timestamp,
        wd.site_id,
        wd.air_temperature,
        wd.dew_temperature,
        wd.wind_speed,
        LAG(wd.air_temperature, 1) OVER (ORDER BY wd.timestamp) as temp_lag_1h,
        AVG(wd.air_temperature) OVER (
            ORDER BY wd.timestamp 
            ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
        ) as temp_24h_avg
    FROM energy.weather_data wd
    JOIN energy.buildings b ON wd.site_id = b.site_id
    WHERE b.building_id = $1
        AND wd.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '30 days')
        AND wd.quality_flag = 'good'
)
SELECT 
    rc.timestamp,
    rc.building_id,
    rc.meter_type,
    rc.consumption,
    rc.lag_1h,
    rc.lag_24h,
    rc.lag_168h,
    rc.rolling_24h_avg,
    rc.rolling_7day_avg,
    rc.hour_of_day,
    rc.day_of_week,
    rc.month_of_year,
    wf.air_temperature,
    wf.temp_lag_1h,
    wf.temp_24h_avg,
    wf.air_temperature - wf.temp_lag_1h as temp_change_1h,
    -- Seasonality features
    SIN(2 * PI() * rc.hour_of_day / 24) as hour_sin,
    COS(2 * PI() * rc.hour_of_day / 24) as hour_cos,
    SIN(2 * PI() * rc.day_of_week / 7) as day_sin,
    COS(2 * PI() * rc.day_of_week / 7) as day_cos
FROM recent_consumption rc
LEFT JOIN weather_features wf ON rc.timestamp = wf.timestamp
WHERE rc.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '7 days')
ORDER BY rc.timestamp DESC;
```

#### Long-term Seasonal Forecasting
```sql
-- Long-term seasonal and trend analysis for energy forecasting
WITH monthly_patterns AS (
    SELECT 
        building_id,
        meter_type,
        EXTRACT(year FROM timestamp) as year,
        EXTRACT(month FROM timestamp) as month,
        SUM(value) as monthly_consumption,
        AVG(value) as avg_monthly_consumption,
        COUNT(*) as reading_count
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= (CURRENT_TIMESTAMP - INTERVAL '3 years')
        AND quality = 'good'
    GROUP BY building_id, meter_type, EXTRACT(year FROM timestamp), EXTRACT(month FROM timestamp)
),
seasonal_decomposition AS (
    SELECT 
        *,
        AVG(monthly_consumption) OVER (PARTITION BY month) as seasonal_component,
        AVG(monthly_consumption) OVER (
            PARTITION BY building_id, meter_type 
            ORDER BY year, month 
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) as trend_component,
        monthly_consumption - AVG(monthly_consumption) OVER (PARTITION BY month) as detrended
    FROM monthly_patterns
),
forecast_base AS (
    SELECT 
        building_id,
        meter_type,
        month,
        AVG(seasonal_component) as avg_seasonal,
        AVG(trend_component) as avg_trend,
        STDDEV(monthly_consumption) as consumption_volatility
    FROM seasonal_decomposition
    GROUP BY building_id, meter_type, month
)
SELECT 
    fb.building_id,
    fb.meter_type,
    fb.month,
    fb.avg_seasonal,
    fb.avg_trend,
    fb.consumption_volatility,
    -- Generate 12-month forecast
    CASE 
        WHEN EXTRACT(month FROM CURRENT_DATE) <= fb.month 
        THEN fb.avg_seasonal + fb.avg_trend
        ELSE fb.avg_seasonal + fb.avg_trend * 1.02 -- 2% growth assumption
    END as forecasted_monthly_consumption,
    -- Confidence intervals
    (fb.avg_seasonal + fb.avg_trend) - (1.96 * fb.consumption_volatility) as lower_confidence_95,
    (fb.avg_seasonal + fb.avg_trend) + (1.96 * fb.consumption_volatility) as upper_confidence_95
FROM forecast_base fb
ORDER BY fb.meter_type, fb.month;
```

### Equipment Performance Prediction

#### Equipment Failure Prediction
```sql
-- Predict potential equipment failures based on consumption anomalies
WITH meter_performance AS (
    SELECT 
        em.meter_id,
        em.building_id,
        em.meter_type,
        em.installation_date,
        em.manufacturer,
        em.model,
        EXTRACT(days FROM (CURRENT_DATE - em.installation_date)) as days_in_service,
        em.total_readings,
        em.missing_readings,
        em.quality_score,
        em.last_reading_time
    FROM energy.energy_meters em
    WHERE em.building_id = $1
        AND em.status = 'active'
),
recent_anomalies AS (
    SELECT 
        meter_id,
        COUNT(CASE WHEN is_outlier = true THEN 1 END) as outlier_count_30d,
        COUNT(CASE WHEN quality != 'good' THEN 1 END) as poor_quality_count_30d,
        COUNT(*) as total_readings_30d,
        AVG(confidence_score) as avg_confidence_30d,
        MAX(timestamp) as last_reading_timestamp
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= (CURRENT_TIMESTAMP - INTERVAL '30 days')
    GROUP BY meter_id
),
consumption_trends AS (
    SELECT 
        meter_id,
        AVG(value) as avg_consumption_30d,
        STDDEV(value) as std_consumption_30d,
        AVG(value) - LAG(AVG(value)) OVER (PARTITION BY meter_id ORDER BY DATE_TRUNC('week', timestamp)) as consumption_trend
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= (CURRENT_TIMESTAMP - INTERVAL '30 days')
        AND quality = 'good'
    GROUP BY meter_id, DATE_TRUNC('week', timestamp)
)
SELECT 
    mp.meter_id,
    mp.meter_type,
    mp.manufacturer,
    mp.model,
    mp.days_in_service,
    mp.quality_score,
    ra.outlier_count_30d,
    ra.poor_quality_count_30d,
    ra.total_readings_30d,
    ra.avg_confidence_30d,
    ct.consumption_trend,
    -- Failure risk scoring
    CASE 
        WHEN mp.days_in_service > 3650 THEN 2 -- > 10 years
        WHEN mp.days_in_service > 1825 THEN 1 -- > 5 years
        ELSE 0
    END +
    CASE 
        WHEN mp.quality_score < 70 THEN 2
        WHEN mp.quality_score < 85 THEN 1
        ELSE 0
    END +
    CASE 
        WHEN (ra.outlier_count_30d::float / NULLIF(ra.total_readings_30d, 0)) > 0.1 THEN 2
        WHEN (ra.outlier_count_30d::float / NULLIF(ra.total_readings_30d, 0)) > 0.05 THEN 1
        ELSE 0
    END as failure_risk_score,
    -- Maintenance recommendations
    CASE 
        WHEN mp.days_in_service > 3650 AND mp.quality_score < 70 
        THEN 'Schedule immediate inspection - high failure risk'
        WHEN (ra.outlier_count_30d::float / NULLIF(ra.total_readings_30d, 0)) > 0.1
        THEN 'Investigate data quality issues - potential equipment degradation'
        WHEN mp.days_in_service > 1825 AND mp.quality_score < 85
        THEN 'Schedule preventive maintenance'
        ELSE 'Continue normal monitoring'
    END as maintenance_recommendation
FROM meter_performance mp
LEFT JOIN recent_anomalies ra ON mp.meter_id = ra.meter_id
LEFT JOIN (
    SELECT DISTINCT ON (meter_id) meter_id, consumption_trend 
    FROM consumption_trends 
    ORDER BY meter_id, consumption_trend DESC
) ct ON mp.meter_id = ct.meter_id
ORDER BY failure_risk_score DESC;
```

### Demand Response Opportunities

#### Peak Demand and Load Shifting Analysis
```sql
-- Identify demand response opportunities and load shifting potential
WITH hourly_patterns AS (
    SELECT 
        building_id,
        meter_type,
        EXTRACT(hour FROM timestamp) as hour_of_day,
        EXTRACT(dow FROM timestamp) as day_of_week,
        AVG(value) as avg_hourly_consumption,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY value) as p90_consumption,
        COUNT(*) as observation_count
    FROM energy.meter_readings
    WHERE building_id = $1
        AND timestamp >= (CURRENT_TIMESTAMP - INTERVAL '6 months')
        AND quality = 'good'
    GROUP BY building_id, meter_type, EXTRACT(hour FROM timestamp), EXTRACT(dow FROM timestamp)
),
peak_periods AS (
    SELECT 
        building_id,
        meter_type,
        hour_of_day,
        day_of_week,
        avg_hourly_consumption,
        RANK() OVER (PARTITION BY building_id, meter_type, day_of_week ORDER BY avg_hourly_consumption DESC) as consumption_rank,
        -- Utility peak periods (typically 2-8 PM weekdays)
        CASE 
            WHEN day_of_week BETWEEN 1 AND 5 AND hour_of_day BETWEEN 14 AND 20 THEN 'utility_peak'
            WHEN day_of_week BETWEEN 1 AND 5 AND hour_of_day BETWEEN 10 AND 14 THEN 'shoulder'
            ELSE 'off_peak'
        END as utility_period
    FROM hourly_patterns
),
load_shifting_potential AS (
    SELECT 
        pp.building_id,
        pp.meter_type,
        pp.utility_period,
        AVG(pp.avg_hourly_consumption) as avg_period_consumption,
        MIN(pp.avg_hourly_consumption) as min_period_consumption,
        MAX(pp.avg_hourly_consumption) as max_period_consumption,
        MAX(pp.avg_hourly_consumption) - MIN(pp.avg_hourly_consumption) as consumption_range
    FROM peak_periods pp
    WHERE pp.day_of_week BETWEEN 1 AND 5 -- Weekdays only
    GROUP BY pp.building_id, pp.meter_type, pp.utility_period
)
SELECT 
    lsp.building_id,
    lsp.meter_type,
    lsp.utility_period,
    lsp.avg_period_consumption,
    lsp.consumption_range,
    -- Load shifting potential calculation
    CASE 
        WHEN lsp.utility_period = 'utility_peak' THEN 
            lsp.consumption_range * 0.3 -- 30% of range could potentially be shifted
        ELSE 0
    END as potential_load_reduction,
    -- Demand response value estimation
    CASE 
        WHEN lsp.utility_period = 'utility_peak' AND lsp.consumption_range > 100 THEN 
            (lsp.consumption_range * 0.3) * 25 -- $25/kW demand charge savings
        ELSE 0
    END as estimated_monthly_dr_value,
    -- Recommendations
    CASE 
        WHEN lsp.utility_period = 'utility_peak' AND lsp.consumption_range > 200 THEN 
            'High potential - implement automated demand response'
        WHEN lsp.utility_period = 'utility_peak' AND lsp.consumption_range > 100 THEN 
            'Medium potential - consider load scheduling optimization'
        WHEN lsp.utility_period = 'utility_peak' AND lsp.consumption_range > 50 THEN 
            'Low potential - manual load management during peak periods'
        ELSE 'Limited demand response opportunity'
    END as dr_recommendation
FROM load_shifting_potential lsp
ORDER BY estimated_monthly_dr_value DESC;
```

### Seasonal Operations Forecasting

#### Seasonal Pattern Optimization
```sql
-- Analyze seasonal patterns for proactive optimization planning
WITH seasonal_analysis AS (
    SELECT 
        mr.building_id,
        mr.meter_type,
        EXTRACT(quarter FROM mr.timestamp) as quarter,
        EXTRACT(month FROM mr.timestamp) as month,
        AVG(mr.value) as avg_consumption,
        SUM(mr.value) as total_consumption,
        AVG(wd.air_temperature) as avg_temperature,
        COUNT(*) as reading_count
    FROM energy.meter_readings mr
    JOIN energy.buildings b ON mr.building_id = b.building_id
    LEFT JOIN energy.weather_data wd ON b.site_id = wd.site_id 
        AND DATE_TRUNC('hour', mr.timestamp) = DATE_TRUNC('hour', wd.timestamp)
    WHERE mr.building_id = $1
        AND mr.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '2 years')
        AND mr.quality = 'good'
    GROUP BY mr.building_id, mr.meter_type, EXTRACT(quarter FROM mr.timestamp), EXTRACT(month FROM mr.timestamp)
),
seasonal_insights AS (
    SELECT 
        *,
        total_consumption - LAG(total_consumption) OVER (
            PARTITION BY building_id, meter_type, month 
            ORDER BY quarter
        ) as year_over_year_change,
        -- Temperature correlation
        CORR(avg_consumption, avg_temperature) OVER (
            PARTITION BY building_id, meter_type
        ) as temp_correlation,
        -- Seasonal efficiency
        MIN(avg_consumption) OVER (PARTITION BY building_id, meter_type) as annual_min_consumption,
        MAX(avg_consumption) OVER (PARTITION BY building_id, meter_type) as annual_max_consumption
    FROM seasonal_analysis
)
SELECT 
    si.building_id,
    si.meter_type,
    si.quarter,
    si.month,
    si.avg_consumption,
    si.total_consumption,
    si.avg_temperature,
    si.year_over_year_change,
    si.temp_correlation,
    (si.avg_consumption - si.annual_min_consumption) / 
        NULLIF((si.annual_max_consumption - si.annual_min_consumption), 0) as seasonal_intensity,
    -- Optimization opportunities
    CASE 
        WHEN si.quarter = 1 AND si.temp_correlation < -0.7 THEN 'Winter heating optimization needed'
        WHEN si.quarter = 3 AND si.temp_correlation > 0.7 THEN 'Summer cooling optimization needed'
        WHEN si.year_over_year_change > (si.avg_consumption * 0.15) THEN 'Investigate consumption increase'
        WHEN ABS(si.temp_correlation) < 0.3 THEN 'Weather-independent consumption - check equipment efficiency'
        ELSE 'Normal seasonal pattern'
    END as optimization_opportunity,
    -- Proactive planning recommendations
    CASE 
        WHEN si.quarter = 4 AND si.temp_correlation < -0.5 THEN 'Schedule winter heating system maintenance'
        WHEN si.quarter = 2 AND si.temp_correlation > 0.5 THEN 'Schedule summer cooling system maintenance'
        WHEN si.quarter IN (2, 4) THEN 'Shoulder season - optimal time for energy audits'
        ELSE 'Continue monitoring'
    END as maintenance_timing_recommendation
FROM seasonal_insights si
ORDER BY si.quarter, si.month, si.meter_type;
```

---

## 5. System Control Agent

### BMS Interface and Control Queries

#### System Status and Control Point Monitoring
```sql
-- Monitor building management system status and control points
WITH control_systems AS (
    SELECT DISTINCT
        em.building_id,
        em.meter_type,
        em.meter_name,
        em.installation_date,
        em.manufacturer,
        em.model,
        em.last_reading_time,
        CASE 
            WHEN em.last_reading_time > (CURRENT_TIMESTAMP - INTERVAL '2 hours') THEN 'online'
            WHEN em.last_reading_time > (CURRENT_TIMESTAMP - INTERVAL '24 hours') THEN 'delayed'
            ELSE 'offline'
        END as system_status
    FROM energy.energy_meters em
    WHERE em.building_id = $1
        AND em.status = 'active'
),
recent_performance AS (
    SELECT 
        mr.meter_id,
        mr.building_id,
        mr.meter_type,
        AVG(mr.value) as avg_recent_consumption,
        MIN(mr.value) as min_recent_consumption,
        MAX(mr.value) as max_recent_consumption,
        COUNT(CASE WHEN mr.quality != 'good' THEN 1 END) as quality_issues,
        COUNT(*) as total_recent_readings
    FROM energy.meter_readings mr
    WHERE mr.building_id = $1
        AND mr.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '24 hours')
    GROUP BY mr.meter_id, mr.building_id, mr.meter_type
),
control_effectiveness AS (
    SELECT 
        mr.building_id,
        mr.meter_type,
        DATE_TRUNC('hour', mr.timestamp) as hour,
        AVG(mr.value) as hourly_consumption,
        STDDEV(mr.value) as consumption_stability,
        -- Control system responsiveness indicator
        ABS(AVG(mr.value) - LAG(AVG(mr.value)) OVER (
            PARTITION BY mr.meter_type 
            ORDER BY DATE_TRUNC('hour', mr.timestamp)
        )) as hourly_variation
    FROM energy.meter_readings mr
    WHERE mr.building_id = $1
        AND mr.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '48 hours')
        AND mr.quality = 'good'
    GROUP BY mr.building_id, mr.meter_type, DATE_TRUNC('hour', mr.timestamp)
)
SELECT 
    cs.building_id,
    cs.meter_type,
    cs.meter_name,
    cs.system_status,
    cs.manufacturer,
    cs.model,
    rp.avg_recent_consumption,
    rp.quality_issues,
    AVG(ce.consumption_stability) as avg_stability,
    AVG(ce.hourly_variation) as avg_hourly_variation,
    -- Control system health scoring
    CASE 
        WHEN cs.system_status = 'offline' THEN 0
        WHEN cs.system_status = 'delayed' THEN 3
        WHEN rp.quality_issues > (rp.total_recent_readings * 0.1) THEN 5
        WHEN AVG(ce.consumption_stability) > 50 THEN 7
        ELSE 10
    END as control_health_score,
    -- Control recommendations
    CASE 
        WHEN cs.system_status = 'offline' THEN 'URGENT: System offline - check communication and power'
        WHEN cs.system_status = 'delayed' THEN 'WARNING: Delayed readings - check network connectivity'
        WHEN rp.quality_issues > (rp.total_recent_readings * 0.1) THEN 'Data quality issues - calibration needed'
        WHEN AVG(ce.consumption_stability) > 50 THEN 'High consumption variability - review control parameters'
        ELSE 'System operating normally'
    END as control_recommendation
FROM control_systems cs
LEFT JOIN recent_performance rp ON cs.building_id = rp.building_id AND cs.meter_type = rp.meter_type
LEFT JOIN control_effectiveness ce ON cs.building_id = ce.building_id AND cs.meter_type = ce.meter_type
GROUP BY cs.building_id, cs.meter_type, cs.meter_name, cs.system_status, 
         cs.manufacturer, cs.model, rp.avg_recent_consumption, rp.quality_issues, 
         rp.total_recent_readings
ORDER BY control_health_score ASC;
```

#### Automated Control Parameter Optimization
```sql
-- Optimize control parameters based on performance data
WITH setpoint_analysis AS (
    SELECT 
        mr.building_id,
        mr.meter_type,
        EXTRACT(hour FROM mr.timestamp) as hour_of_day,
        EXTRACT(dow FROM mr.timestamp) as day_of_week,
        AVG(mr.value) as avg_consumption,
        AVG(wd.air_temperature) as avg_outdoor_temp,
        COUNT(*) as observation_count,
        -- Identify optimal operating conditions
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY mr.value) as efficient_consumption_threshold
    FROM energy.meter_readings mr
    JOIN energy.buildings b ON mr.building_id = b.building_id
    LEFT JOIN energy.weather_data wd ON b.site_id = wd.site_id 
        AND ABS(EXTRACT(epoch FROM (mr.timestamp - wd.timestamp))) < 3600
    WHERE mr.building_id = $1
        AND mr.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '30 days')
        AND mr.quality = 'good'
    GROUP BY mr.building_id, mr.meter_type, EXTRACT(hour FROM mr.timestamp), EXTRACT(dow FROM mr.timestamp)
    HAVING COUNT(*) >= 5 -- Sufficient observations
),
optimal_schedules AS (
    SELECT 
        building_id,
        meter_type,
        hour_of_day,
        day_of_week,
        avg_consumption,
        avg_outdoor_temp,
        efficient_consumption_threshold,
        -- Calculate optimal setpoints
        CASE 
            WHEN meter_type = 'electricity' AND avg_outdoor_temp > 75 THEN 
                LEAST(78, avg_outdoor_temp + 3) -- Cooling setpoint
            WHEN meter_type = 'electricity' AND avg_outdoor_temp < 65 THEN 
                GREATEST(68, avg_outdoor_temp - 5) -- Heating setpoint
            ELSE NULL
        END as recommended_temp_setpoint,
        -- Occupancy-based scheduling
        CASE 
            WHEN day_of_week BETWEEN 1 AND 5 AND hour_of_day BETWEEN 8 AND 18 THEN 'occupied'
            WHEN day_of_week BETWEEN 1 AND 5 AND hour_of_day BETWEEN 6 AND 8 THEN 'pre_occupancy'
            WHEN day_of_week BETWEEN 1 AND 5 AND hour_of_day BETWEEN 18 AND 22 THEN 'post_occupancy'
            ELSE 'unoccupied'
        END as occupancy_schedule,
        -- Energy savings potential
        GREATEST(0, avg_consumption - efficient_consumption_threshold) as savings_potential
    FROM setpoint_analysis
),
control_commands AS (
    SELECT 
        os.building_id,
        os.meter_type,
        os.hour_of_day,
        os.day_of_week,
        os.occupancy_schedule,
        os.recommended_temp_setpoint,
        os.savings_potential,
        -- Generate control commands
        CASE 
            WHEN os.occupancy_schedule = 'unoccupied' THEN 
                'Implement setback: temp +/- 5°F from occupied setpoint'
            WHEN os.occupancy_schedule = 'pre_occupancy' THEN 
                'Implement optimal start control'
            WHEN os.savings_potential > (os.avg_consumption * 0.1) THEN 
                'Adjust setpoint for energy savings'
            ELSE 'Maintain current settings'
        END as control_command,
        -- Implementation priority
        CASE 
            WHEN os.savings_potential > 50 THEN 'high'
            WHEN os.savings_potential > 20 THEN 'medium' 
            ELSE 'low'
        END as implementation_priority
    FROM optimal_schedules os
    WHERE os.savings_potential > 0
)
SELECT 
    cc.building_id,
    cc.meter_type,
    cc.hour_of_day,
    cc.day_of_week,
    cc.occupancy_schedule,
    cc.recommended_temp_setpoint,
    cc.savings_potential,
    cc.control_command,
    cc.implementation_priority,
    -- Weekly schedule generation
    STRING_AGG(
        CONCAT(cc.hour_of_day, ':00 - ', cc.control_command), 
        '; ' ORDER BY cc.hour_of_day
    ) OVER (PARTITION BY cc.building_id, cc.meter_type, cc.day_of_week) as daily_schedule
FROM control_commands cc
ORDER BY cc.implementation_priority, cc.savings_potential DESC;
```

### Real-time Control Parameter Monitoring

#### Safety and Comfort Constraint Enforcement
```sql
-- Monitor and enforce safety/comfort constraints during optimization
WITH current_conditions AS (
    SELECT 
        mr.building_id,
        mr.meter_type,
        mr.timestamp,
        mr.value as current_consumption,
        wd.air_temperature as outdoor_temp,
        -- Calculate moving averages for stability
        AVG(mr.value) OVER (
            PARTITION BY mr.meter_id 
            ORDER BY mr.timestamp 
            ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
        ) as consumption_trend,
        -- Detect rapid changes
        ABS(mr.value - LAG(mr.value, 1) OVER (
            PARTITION BY mr.meter_id 
            ORDER BY mr.timestamp
        )) as consumption_change_rate
    FROM energy.meter_readings mr
    JOIN energy.buildings b ON mr.building_id = b.building_id
    LEFT JOIN energy.weather_data wd ON b.site_id = wd.site_id 
        AND ABS(EXTRACT(epoch FROM (mr.timestamp - wd.timestamp))) < 1800
    WHERE mr.building_id = $1
        AND mr.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '2 hours')
        AND mr.quality = 'good'
),
safety_constraints AS (
    SELECT 
        cc.*,
        -- Define safety/comfort limits based on building type and conditions
        CASE 
            WHEN cc.outdoor_temp > 85 THEN cc.current_consumption * 1.3 -- Allow higher cooling load
            WHEN cc.outdoor_temp < 32 THEN cc.current_consumption * 1.4 -- Allow higher heating load
            ELSE cc.current_consumption * 1.2
        END as max_safe_consumption,
        CASE 
            WHEN cc.outdoor_temp > 85 THEN cc.current_consumption * 0.6 -- Minimum cooling
            WHEN cc.outdoor_temp < 32 THEN cc.current_consumption * 0.7 -- Minimum heating
            ELSE cc.current_consumption * 0.5
        END as min_safe_consumption,
        -- Rapid change limits
        cc.current_consumption * 0.15 as max_allowable_change_rate
    FROM current_conditions cc
),
constraint_violations AS (
    SELECT 
        sc.*,
        -- Identify constraint violations
        CASE 
            WHEN sc.current_consumption > sc.max_safe_consumption THEN 'over_consumption'
            WHEN sc.current_consumption < sc.min_safe_consumption THEN 'under_consumption'
            WHEN sc.consumption_change_rate > sc.max_allowable_change_rate THEN 'rapid_change'
            ELSE 'within_limits'
        END as constraint_status,
        -- Calculate severity
        CASE 
            WHEN sc.current_consumption > sc.max_safe_consumption THEN 
                (sc.current_consumption - sc.max_safe_consumption) / sc.max_safe_consumption * 100
            WHEN sc.current_consumption < sc.min_safe_consumption THEN 
                (sc.min_safe_consumption - sc.current_consumption) / sc.min_safe_consumption * 100
            ELSE 0
        END as violation_severity_percent
    FROM safety_constraints sc
)
SELECT 
    cv.building_id,
    cv.meter_type,
    cv.timestamp,
    cv.current_consumption,
    cv.outdoor_temp,
    cv.consumption_trend,
    cv.consumption_change_rate,
    cv.constraint_status,
    cv.violation_severity_percent,
    -- Safety actions
    CASE 
        WHEN cv.constraint_status = 'over_consumption' AND cv.violation_severity_percent > 20 THEN 
            'EMERGENCY: Reduce load immediately - safety risk'
        WHEN cv.constraint_status = 'under_consumption' AND cv.violation_severity_percent > 30 THEN 
            'WARNING: Insufficient conditioning - comfort risk'
        WHEN cv.constraint_status = 'rapid_change' THEN 
            'CAUTION: Rapid consumption change - check system stability'
        ELSE 'Normal operation'
    END as safety_action,
    -- Control adjustments
    CASE 
        WHEN cv.constraint_status = 'over_consumption' THEN 
            LEAST(cv.max_safe_consumption, cv.current_consumption * 0.9)
        WHEN cv.constraint_status = 'under_consumption' THEN 
            GREATEST(cv.min_safe_consumption, cv.current_consumption * 1.1)
        ELSE cv.current_consumption
    END as recommended_setpoint
FROM constraint_violations cv
WHERE cv.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '30 minutes') -- Most recent data
ORDER BY cv.violation_severity_percent DESC, cv.timestamp DESC;
```

### Implementation Monitoring

#### Optimization Strategy Deployment Tracking
```sql
-- Track implementation of optimization strategies and measure effectiveness
WITH implementation_log AS (
    SELECT 
        ea.building_id,
        ea.analysis_type,
        ea.time_period_start,
        ea.time_period_end,
        ea.recommendations,
        ea.created_at as strategy_deployed_at,
        ea.status as implementation_status,
        -- Extract specific recommendations
        CASE 
            WHEN ea.recommendations @> '["HVAC Upgrade"]' THEN 'hvac_upgrade'
            WHEN ea.recommendations @> '["LED Lighting"]' THEN 'led_lighting'
            WHEN ea.recommendations @> '["Building Automation"]' THEN 'bms_upgrade'
            WHEN ea.recommendations @> '["Schedule Optimization"]' THEN 'schedule_opt'
            ELSE 'other'
        END as strategy_type
    FROM energy.energy_analytics ea
    WHERE ea.building_id = $1
        AND ea.analysis_type = 'optimization_strategy'
        AND ea.created_at >= $2 -- Since implementation start date
        AND ea.status = 'implemented'
),
pre_implementation_baseline AS (
    SELECT 
        il.building_id,
        il.strategy_type,
        il.strategy_deployed_at,
        AVG(mr.value) as baseline_avg_consumption,
        SUM(mr.value) as baseline_total_consumption,
        STDDEV(mr.value) as baseline_consumption_variability
    FROM implementation_log il
    JOIN energy.meter_readings mr ON il.building_id = mr.building_id
    WHERE mr.timestamp BETWEEN (il.strategy_deployed_at - INTERVAL '30 days') 
                            AND il.strategy_deployed_at
        AND mr.quality = 'good'
    GROUP BY il.building_id, il.strategy_type, il.strategy_deployed_at
),
post_implementation_performance AS (
    SELECT 
        il.building_id,
        il.strategy_type,
        il.strategy_deployed_at,
        AVG(mr.value) as post_avg_consumption,
        SUM(mr.value) as post_total_consumption,
        STDDEV(mr.value) as post_consumption_variability
    FROM implementation_log il
    JOIN energy.meter_readings mr ON il.building_id = mr.building_id
    WHERE mr.timestamp BETWEEN il.strategy_deployed_at 
                            AND (il.strategy_deployed_at + INTERVAL '30 days')
        AND mr.quality = 'good'
    GROUP BY il.building_id, il.strategy_type, il.strategy_deployed_at
),
effectiveness_analysis AS (
    SELECT 
        pb.building_id,
        pb.strategy_type,
        pb.strategy_deployed_at,
        pb.baseline_avg_consumption,
        pp.post_avg_consumption,
        pb.baseline_total_consumption,
        pp.post_total_consumption,
        -- Calculate improvement metrics
        (pb.baseline_avg_consumption - pp.post_avg_consumption) as avg_consumption_reduction,
        ((pb.baseline_avg_consumption - pp.post_avg_consumption) / NULLIF(pb.baseline_avg_consumption, 0)) * 100 as percent_improvement,
        (pb.baseline_total_consumption - pp.post_total_consumption) as total_energy_saved,
        -- Stability improvement
        (pb.baseline_consumption_variability - pp.post_consumption_variability) as variability_improvement,
        -- Implementation effectiveness score
        CASE 
            WHEN ((pb.baseline_avg_consumption - pp.post_avg_consumption) / NULLIF(pb.baseline_avg_consumption, 0)) * 100 > 15 THEN 'excellent'
            WHEN ((pb.baseline_avg_consumption - pp.post_avg_consumption) / NULLIF(pb.baseline_avg_consumption, 0)) * 100 > 10 THEN 'good'
            WHEN ((pb.baseline_avg_consumption - pp.post_avg_consumption) / NULLIF(pb.baseline_avg_consumption, 0)) * 100 > 5 THEN 'moderate'
            WHEN ((pb.baseline_avg_consumption - pp.post_avg_consumption) / NULLIF(pb.baseline_avg_consumption, 0)) * 100 > 0 THEN 'minimal'
            ELSE 'no_improvement'
        END as effectiveness_rating
    FROM pre_implementation_baseline pb
    JOIN post_implementation_performance pp ON pb.building_id = pp.building_id 
        AND pb.strategy_type = pp.strategy_type 
        AND pb.strategy_deployed_at = pp.strategy_deployed_at
)
SELECT 
    ea.building_id,
    ea.strategy_type,
    ea.strategy_deployed_at,
    ea.baseline_avg_consumption,
    ea.post_avg_consumption,
    ea.avg_consumption_reduction,
    ea.percent_improvement,
    ea.total_energy_saved,
    ea.effectiveness_rating,
    -- ROI calculation (simplified)
    CASE 
        WHEN ea.strategy_type = 'hvac_upgrade' THEN ea.total_energy_saved * 0.12 * 12 -- Annual savings
        WHEN ea.strategy_type = 'led_lighting' THEN ea.total_energy_saved * 0.12 * 12
        WHEN ea.strategy_type = 'schedule_opt' THEN ea.total_energy_saved * 0.12 * 12
        ELSE ea.total_energy_saved * 0.10 * 12
    END as estimated_annual_savings,
    -- Next actions
    CASE 
        WHEN ea.effectiveness_rating = 'no_improvement' THEN 'Review implementation - strategy not working'
        WHEN ea.effectiveness_rating = 'minimal' THEN 'Fine-tune parameters for better results'
        WHEN ea.effectiveness_rating = 'moderate' THEN 'Monitor and consider additional measures'
        WHEN ea.effectiveness_rating IN ('good', 'excellent') THEN 'Successful implementation - maintain and scale'
        ELSE 'Insufficient data for evaluation'
    END as next_action_recommendation
FROM effectiveness_analysis ea
ORDER BY ea.percent_improvement DESC;
```

---

## 6. Validator Agent

### Optimization Recommendation Validation

#### Safety and Feasibility Assessment
```sql
-- Validate optimization recommendations for safety and technical feasibility
WITH recommendation_analysis AS (
    SELECT 
        ea.id as analysis_id,
        ea.building_id,
        ea.analysis_type,
        ea.recommendations,
        ea.results,
        ea.confidence_score,
        ea.model_accuracy,
        ea.created_at,
        -- Extract recommendation details from JSON
        (ea.results->>'estimated_savings')::numeric as estimated_savings,
        (ea.results->>'implementation_cost')::numeric as implementation_cost,
        (ea.results->>'payback_period')::numeric as payback_period,
        ea.results->>'risk_level' as risk_level
    FROM energy.energy_analytics ea
    WHERE ea.building_id = $1
        AND ea.analysis_type = 'optimization_recommendation'
        AND ea.created_at >= $2
        AND ea.status = 'completed'
),
building_constraints AS (
    SELECT 
        b.building_id,
        b.primary_space_usage,
        b.year_built,
        b.square_feet,
        b.occupants,
        b.energy_star_score,
        -- Critical facility check
        CASE 
            WHEN b.primary_space_usage IN ('Hospital', 'Data Center', 'Laboratory') THEN true
            ELSE false
        END as is_critical_facility,
        -- Building age risk factor
        CASE 
            WHEN b.year_built < 1970 THEN 'high_risk'
            WHEN b.year_built < 1990 THEN 'medium_risk'
            ELSE 'low_risk'
        END as building_age_risk,
        -- Occupancy density
        b.square_feet / NULLIF(b.occupants, 0) as sqft_per_occupant
    FROM energy.buildings b
    WHERE b.building_id = $1
),
system_capacity_check AS (
    SELECT 
        em.building_id,
        em.meter_type,
        COUNT(*) as meter_count,
        AVG(em.quality_score) as avg_meter_quality,
        MIN(em.data_start_date) as data_history_start,
        -- Data sufficiency check
        CASE 
            WHEN MIN(em.data_start_date) > (CURRENT_DATE - INTERVAL '6 months') THEN 'insufficient_history'
            WHEN AVG(em.quality_score) < 70 THEN 'poor_data_quality'
            ELSE 'adequate'
        END as data_adequacy
    FROM energy.energy_meters em
    WHERE em.building_id = $1
        AND em.status = 'active'
    GROUP BY em.building_id, em.meter_type
),
validation_results AS (
    SELECT 
        ra.*,
        bc.is_critical_facility,
        bc.building_age_risk,
        bc.sqft_per_occupant,
        scc.data_adequacy,
        scc.avg_meter_quality,
        -- Safety validation
        CASE 
            WHEN bc.is_critical_facility = true AND ra.risk_level = 'high' THEN 'reject_safety'
            WHEN bc.building_age_risk = 'high_risk' AND ra.implementation_cost > (bc.square_feet * 20) THEN 'reject_cost'
            WHEN ra.confidence_score < 0.7 THEN 'reject_confidence'
            WHEN scc.data_adequacy = 'insufficient_history' THEN 'reject_data'
            WHEN ra.payback_period > 15 THEN 'reject_roi'
            ELSE 'approved'
        END as validation_status,
        -- Risk scoring
        CASE 
            WHEN bc.is_critical_facility = true THEN 3
            ELSE 0
        END +
        CASE 
            WHEN bc.building_age_risk = 'high_risk' THEN 2
            WHEN bc.building_age_risk = 'medium_risk' THEN 1
            ELSE 0
        END +
        CASE 
            WHEN ra.confidence_score < 0.6 THEN 3
            WHEN ra.confidence_score < 0.8 THEN 1
            ELSE 0
        END as total_risk_score
    FROM recommendation_analysis ra
    JOIN building_constraints bc ON ra.building_id = bc.building_id
    LEFT JOIN system_capacity_check scc ON ra.building_id = scc.building_id
)
SELECT 
    vr.analysis_id,
    vr.building_id,
    vr.recommendations,
    vr.estimated_savings,
    vr.implementation_cost,
    vr.payback_period,
    vr.confidence_score,
    vr.validation_status,
    vr.total_risk_score,
    vr.is_critical_facility,
    vr.building_age_risk,
    vr.data_adequacy,
    -- Detailed validation feedback
    CASE 
        WHEN vr.validation_status = 'reject_safety' THEN 
            'Recommendation rejected: High risk for critical facility operations'
        WHEN vr.validation_status = 'reject_cost' THEN 
            'Recommendation rejected: Implementation cost exceeds building value threshold'
        WHEN vr.validation_status = 'reject_confidence' THEN 
            'Recommendation rejected: Model confidence below acceptable threshold (70%)'
        WHEN vr.validation_status = 'reject_data' THEN 
            'Recommendation rejected: Insufficient historical data for reliable analysis'
        WHEN vr.validation_status = 'reject_roi' THEN 
            'Recommendation rejected: Payback period exceeds acceptable limit (15 years)'
        ELSE 'Recommendation approved for implementation'
    END as validation_feedback,
    -- Implementation conditions
    CASE 
        WHEN vr.validation_status = 'approved' AND vr.total_risk_score > 3 THEN 
            'Approved with conditions: Phased implementation recommended'
        WHEN vr.validation_status = 'approved' AND vr.is_critical_facility = true THEN 
            'Approved with conditions: Extended testing period required'
        WHEN vr.validation_status = 'approved' THEN 
            'Approved: Proceed with standard implementation'
        ELSE 'Implementation not recommended'
    END as implementation_guidance
FROM validation_results vr
ORDER BY vr.total_risk_score ASC, vr.estimated_savings DESC;
```

### Implementation Effectiveness Monitoring

#### Performance Verification and Measurement
```sql
-- Monitor and verify the effectiveness of implemented optimization measures
WITH implementation_timeline AS (
    SELECT 
        ea.building_id,
        ea.analysis_id,
        ea.recommendations,
        ea.created_at as recommendation_date,
        ea.results->>'implementation_date' as implementation_date_str,
        (ea.results->>'implementation_date')::timestamp as implementation_date,
        (ea.results->>'expected_savings')::numeric as expected_savings,
        (ea.results->>'baseline_period_start')::timestamp as baseline_start,
        (ea.results->>'baseline_period_end')::timestamp as baseline_end
    FROM energy.energy_analytics ea
    WHERE ea.building_id = $1
        AND ea.analysis_type = 'optimization_implementation'
        AND ea.status = 'monitoring'
        AND (ea.results->>'implementation_date') IS NOT NULL
),
baseline_performance AS (
    SELECT 
        it.building_id,
        it.analysis_id,
        AVG(mr.value) as baseline_avg_consumption,
        SUM(mr.value) as baseline_total_consumption,
        STDDEV(mr.value) as baseline_std_deviation,
        COUNT(*) as baseline_reading_count
    FROM implementation_timeline it
    JOIN energy.meter_readings mr ON it.building_id = mr.building_id
    WHERE mr.timestamp BETWEEN it.baseline_start AND it.baseline_end
        AND mr.quality = 'good'
    GROUP BY it.building_id, it.analysis_id
),
post_implementation_performance AS (
    SELECT 
        it.building_id,
        it.analysis_id,
        AVG(mr.value) as actual_avg_consumption,
        SUM(mr.value) as actual_total_consumption,
        STDDEV(mr.value) as actual_std_deviation,
        COUNT(*) as actual_reading_count,
        -- Measure consistency of savings
        COUNT(CASE WHEN mr.value < bp.baseline_avg_consumption THEN 1 END) as consistent_savings_count
    FROM implementation_timeline it
    JOIN baseline_performance bp ON it.analysis_id = bp.analysis_id
    JOIN energy.meter_readings mr ON it.building_id = mr.building_id
    WHERE mr.timestamp BETWEEN it.implementation_date AND (it.implementation_date + INTERVAL '60 days')
        AND mr.quality = 'good'
    GROUP BY it.building_id, it.analysis_id, bp.baseline_avg_consumption
),
effectiveness_metrics AS (
    SELECT 
        it.building_id,
        it.analysis_id,
        it.recommendations,
        it.expected_savings,
        it.implementation_date,
        bp.baseline_avg_consumption,
        pp.actual_avg_consumption,
        bp.baseline_total_consumption,
        pp.actual_total_consumption,
        -- Calculate actual savings
        bp.baseline_avg_consumption - pp.actual_avg_consumption as actual_avg_savings,
        bp.baseline_total_consumption - pp.actual_total_consumption as actual_total_savings,
        -- Performance ratios
        (bp.baseline_avg_consumption - pp.actual_avg_consumption) / NULLIF(bp.baseline_avg_consumption, 0) * 100 as actual_savings_percent,
        (pp.actual_avg_consumption / NULLIF(bp.baseline_avg_consumption, 0) * 100) as performance_ratio,
        -- Consistency metrics
        pp.consistent_savings_count::float / NULLIF(pp.actual_reading_count, 0) * 100 as savings_consistency_percent,
        -- Variability comparison
        pp.actual_std_deviation / NULLIF(bp.baseline_std_deviation, 0) as variability_ratio,
        -- Expected vs actual comparison
        (bp.baseline_total_consumption - pp.actual_total_consumption) / NULLIF(it.expected_savings, 0) * 100 as savings_achievement_percent
    FROM implementation_timeline it
    JOIN baseline_performance bp ON it.analysis_id = bp.analysis_id
    JOIN post_implementation_performance pp ON it.analysis_id = pp.analysis_id
),
validation_assessment AS (
    SELECT 
        em.*,
        -- Performance validation
        CASE 
            WHEN em.actual_savings_percent >= 80 AND em.savings_consistency_percent >= 70 THEN 'excellent'
            WHEN em.actual_savings_percent >= 60 AND em.savings_consistency_percent >= 60 THEN 'good'
            WHEN em.actual_savings_percent >= 40 AND em.savings_consistency_percent >= 50 THEN 'moderate'
            WHEN em.actual_savings_percent >= 20 AND em.savings_consistency_percent >= 40 THEN 'poor'
            ELSE 'failed'
        END as performance_validation,
        -- Stability assessment
        CASE 
            WHEN em.variability_ratio <= 0.8 THEN 'improved_stability'
            WHEN em.variability_ratio <= 1.2 THEN 'stable'
            ELSE 'increased_variability'
        END as stability_assessment,
        -- Overall effectiveness score (0-100)
        LEAST(100, GREATEST(0, 
            (em.actual_savings_percent * 0.4) + 
            (em.savings_consistency_percent * 0.3) + 
            (CASE WHEN em.variability_ratio <= 1.0 THEN 30 ELSE 30 - (em.variability_ratio - 1.0) * 20 END)
        )) as effectiveness_score
    FROM effectiveness_metrics em
)
SELECT 
    va.building_id,
    va.analysis_id,
    va.recommendations,
    va.implementation_date,
    va.expected_savings,
    va.actual_total_savings,
    va.actual_savings_percent,
    va.savings_achievement_percent,
    va.savings_consistency_percent,
    va.performance_validation,
    va.stability_assessment,
    va.effectiveness_score,
    -- Validation conclusions
    CASE 
        WHEN va.performance_validation = 'failed' THEN 'Implementation failed - investigate and remediate'
        WHEN va.performance_validation = 'poor' THEN 'Below expectations - require system adjustments'
        WHEN va.performance_validation = 'moderate' THEN 'Partially successful - fine-tune for better results'
        WHEN va.performance_validation = 'good' THEN 'Successful implementation - monitor for sustained performance'
        WHEN va.performance_validation = 'excellent' THEN 'Highly successful - model for future implementations'
        ELSE 'Insufficient data for validation'
    END as validation_conclusion,
    -- Corrective actions
    CASE 
        WHEN va.savings_consistency_percent < 50 THEN 'Inconsistent savings - check system operation and setpoints'
        WHEN va.variability_ratio > 1.5 THEN 'High variability - review control stability'
        WHEN va.actual_savings_percent < 30 THEN 'Low savings - verify implementation completeness'
        ELSE 'Continue monitoring'
    END as corrective_actions,
    -- Future recommendations
    CASE 
        WHEN va.effectiveness_score >= 80 THEN 'Scale similar measures to other buildings'
        WHEN va.effectiveness_score >= 60 THEN 'Continue current approach with minor improvements'
        WHEN va.effectiveness_score >= 40 THEN 'Review implementation approach'
        ELSE 'Reassess measure feasibility'
    END as future_recommendations
FROM validation_assessment va
ORDER BY va.effectiveness_score DESC;
```

### Continuous Learning and System Improvement

#### System Quality Assurance and Error Detection
```sql
-- Detect errors and quality issues across all agent operations
WITH agent_performance_metrics AS (
    SELECT 
        ea.building_id,
        ea.analysis_type,
        ea.model_id,
        ea.model_version,
        ea.model_accuracy,
        ea.confidence_score,
        ea.created_at,
        ea.status,
        -- Categorize analysis types by agent
        CASE 
            WHEN ea.analysis_type LIKE '%energy_data%' THEN 'energy_intelligence'
            WHEN ea.analysis_type LIKE '%weather%' THEN 'weather_intelligence'
            WHEN ea.analysis_type LIKE '%optimization%' THEN 'optimization_strategy'
            WHEN ea.analysis_type LIKE '%forecast%' THEN 'forecast_intelligence'
            WHEN ea.analysis_type LIKE '%control%' THEN 'system_control'
            WHEN ea.analysis_type LIKE '%validation%' THEN 'validator'
            ELSE 'unknown'
        END as agent_type
    FROM energy.energy_analytics ea
    WHERE ea.building_id = $1
        AND ea.created_at >= (CURRENT_TIMESTAMP - INTERVAL '30 days')
),
data_quality_assessment AS (
    SELECT 
        mr.building_id,
        mr.meter_type,
        COUNT(*) as total_readings,
        COUNT(CASE WHEN mr.quality = 'good' THEN 1 END) as good_quality_readings,
        COUNT(CASE WHEN mr.is_outlier = true THEN 1 END) as outlier_readings,
        AVG(mr.confidence_score) as avg_confidence_score,
        -- Missing data periods
        COUNT(CASE WHEN mr.value IS NULL THEN 1 END) as null_readings,
        -- Data consistency checks
        COUNT(CASE WHEN mr.value < 0 THEN 1 END) as negative_values,
        COUNT(CASE WHEN mr.value > 10000 THEN 1 END) as extreme_high_values
    FROM energy.meter_readings mr
    WHERE mr.building_id = $1
        AND mr.timestamp >= (CURRENT_TIMESTAMP - INTERVAL '7 days')
    GROUP BY mr.building_id, mr.meter_type
),
model_performance_analysis AS (
    SELECT 
        apm.agent_type,
        apm.model_id,
        COUNT(*) as analysis_count,
        AVG(apm.model_accuracy) as avg_model_accuracy,
        AVG(apm.confidence_score) as avg_confidence_score,
        COUNT(CASE WHEN apm.status = 'failed' THEN 1 END) as failed_analyses,
        COUNT(CASE WHEN apm.status = 'completed' THEN 1 END) as successful_analyses,
        -- Performance trends
        AVG(CASE WHEN apm.created_at >= (CURRENT_TIMESTAMP - INTERVAL '7 days') THEN apm.model_accuracy END) as recent_accuracy,
        AVG(CASE WHEN apm.created_at < (CURRENT_TIMESTAMP - INTERVAL '7 days') THEN apm.model_accuracy END) as historical_accuracy
    FROM agent_performance_metrics apm
    GROUP BY apm.agent_type, apm.model_id
),
error_detection AS (
    SELECT 
        dqa.building_id,
        dqa.meter_type,
        dqa.total_readings,
        dqa.good_quality_readings,
        dqa.outlier_readings,
        dqa.null_readings,
        dqa.negative_values,
        dqa.extreme_high_values,
        -- Calculate quality scores
        (dqa.good_quality_readings::float / NULLIF(dqa.total_readings, 0)) * 100 as data_quality_percentage,
        (dqa.outlier_readings::float / NULLIF(dqa.total_readings, 0)) * 100 as outlier_percentage,
        (dqa.null_readings::float / NULLIF(dqa.total_readings, 0)) * 100 as missing_data_percentage,
        -- Error flags
        CASE 
            WHEN (dqa.good_quality_readings::float / NULLIF(dqa.total_readings, 0)) < 0.8 THEN true
            ELSE false
        END as poor_data_quality_flag,
        CASE 
            WHEN (dqa.outlier_readings::float / NULLIF(dqa.total_readings, 0)) > 0.1 THEN true
            ELSE false
        END as excessive_outliers_flag,
        CASE 
            WHEN dqa.negative_values > 0 OR dqa.extreme_high_values > (dqa.total_readings * 0.01) THEN true
            ELSE false
        END as data_anomaly_flag
    FROM data_quality_assessment dqa
),
system_health_summary AS (
    SELECT 
        ed.building_id,
        -- Data quality summary
        AVG(ed.data_quality_percentage) as avg_data_quality,
        AVG(ed.outlier_percentage) as avg_outlier_rate,
        COUNT(CASE WHEN ed.poor_data_quality_flag = true THEN 1 END) as meters_with_quality_issues,
        COUNT(CASE WHEN ed.excessive_outliers_flag = true THEN 1 END) as meters_with_outlier_issues,
        COUNT(CASE WHEN ed.data_anomaly_flag = true THEN 1 END) as meters_with_anomalies,
        COUNT(*) as total_meters
    FROM error_detection ed
    GROUP BY ed.building_id
)
SELECT 
    shs.building_id,
    shs.avg_data_quality,
    shs.avg_outlier_rate,
    shs.meters_with_quality_issues,
    shs.meters_with_outlier_issues,
    shs.meters_with_anomalies,
    shs.total_meters,
    -- Model performance summary
    mpa.agent_type,
    mpa.avg_model_accuracy,
    mpa.avg_confidence_score,
    mpa.failed_analyses,
    mpa.successful_analyses,
    mpa.recent_accuracy - mpa.historical_accuracy as accuracy_trend,
    -- Overall system health score
    LEAST(100, GREATEST(0,
        (shs.avg_data_quality * 0.4) +
        ((100 - shs.avg_outlier_rate) * 0.2) +
        ((shs.total_meters - shs.meters_with_quality_issues)::float / NULLIF(shs.total_meters, 0) * 100 * 0.2) +
        (mpa.avg_model_accuracy * 100 * 0.2)
    )) as system_health_score,
    -- Issue priority classification
    CASE 
        WHEN shs.avg_data_quality < 70 OR mpa.avg_model_accuracy < 0.7 THEN 'critical'
        WHEN shs.meters_with_quality_issues > (shs.total_meters * 0.3) THEN 'high'
        WHEN shs.avg_outlier_rate > 10 OR mpa.failed_analyses > (mpa.analysis_count * 0.1) THEN 'medium'
        ELSE 'low'
    END as issue_priority,
    -- Specific error recommendations
    CASE 
        WHEN shs.avg_data_quality < 70 THEN 'URGENT: Data quality below acceptable threshold - calibrate meters'
        WHEN mpa.avg_model_accuracy < 0.7 THEN 'URGENT: Model accuracy degraded - retrain models'
        WHEN shs.meters_with_anomalies > 0 THEN 'WARNING: Data anomalies detected - investigate meter readings'
        WHEN shs.avg_outlier_rate > 10 THEN 'CAUTION: High outlier rate - review data validation rules'
        ELSE 'System operating within normal parameters'
    END as error_recommendations,
    -- System improvement suggestions
    CASE 
        WHEN mpa.accuracy_trend < -0.05 THEN 'Model performance declining - consider retraining'
        WHEN shs.meters_with_quality_issues = 0 AND mpa.avg_model_accuracy > 0.9 THEN 'System performing excellently - maintain current approach'
        WHEN shs.avg_data_quality > 90 AND mpa.avg_model_accuracy > 0.8 THEN 'Good performance - consider expanding to additional metrics'
        ELSE 'Continue standard monitoring and maintenance'
    END as improvement_suggestions
FROM system_health_summary shs
CROSS JOIN model_performance_analysis mpa
ORDER BY system_health_score ASC;
```

---

## Query Usage Guidelines

### Connection Information
All queries are designed for the TimescaleDB database:
- **Connection String**: `postgresql://eaio_user:password@localhost:5434/eaio_energy`
- **Schema**: `energy` (default)

### Parameter Conventions
- `$1` - Building ID (varchar)
- `$2` - Start timestamp (timestamptz)
- `$3` - End timestamp (timestamptz)
- Additional parameters as documented in each query

### Performance Optimization
1. All queries use appropriate indexes on hypertables
2. Time-range filters should always be included for hypertable queries
3. Use materialized views (`meter_readings_hourly`, `daily_building_consumption`) for performance
4. Consider query timeout limits for large date ranges

### Data Quality Considerations
1. Always filter by `quality = 'good'` for analysis queries
2. Handle NULL values appropriately in calculations
3. Use confidence scores for model reliability assessment
4. Validate outlier flags before including in critical calculations

---

*This query collection is optimized for the EAIO TimescaleDB schema and should be adapted for specific agent implementations and requirements.*