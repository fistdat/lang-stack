# Reports Module Analysis & Improvement Plan

**Date**: 2025-12-12
**Module**: Energy Consumption Reports
**Status**: ❌ **CRITICAL - 100% MOCK DATA**
**Priority**: HIGH

---

## Executive Summary

### 🔴 Critical Finding
The Reports module (`http://localhost:3002/reports`) is currently **100% non-functional** in terms of real data. All displayed data is generated client-side using mock/fake data generators.

### Impact
- ❌ **No real consumption data** displayed
- ❌ **No backend integration** - zero API calls
- ❌ **Misleading to users** - appears functional but shows fake numbers
- ❌ **No value for decision-making** - all insights are fabricated

### Severity
**CRITICAL** - Same severity as Forecasting module before fix. Reports are core functionality for energy management systems.

---

## Current State Analysis

### Frontend Implementation

**File**: `/frontend/src/pages/Reports.tsx` (782 lines)

**Architecture**:
```
Reports.tsx (All-in-One Component)
├── State Management (Line 44-50)
├── Buildings API Call (Line 53-83) ✅ Real
├── generateReport() (Line 93-237) ❌ Mock
│   ├── Date Range Calculation (Line 100-120) ✅ Real
│   ├── Mock Data Generation (Line 127-229) ❌ Fake
│   └── No Backend API Calls ❌ Missing
├── Mock Data Generators (Line 240-295)
├── UI Rendering (Line 394-780)
│   ├── Report Configuration (Line 413-479)
│   ├── Performance Cards (Line 534-574)
│   ├── Consumption Charts (Line 577-638)
│   ├── Recommendations Table (Line 641-693)
│   ├── Anomalies Table (Line 696-744)
│   └── Summary Section (Line 747-776)
```

### Mock Data Generation (Lines 122-229)

**Explicit Mock Data Warning**:
```tsx
// Line 123-124
console.log('Using mock data for reports as the backend API endpoint is not yet implemented');
setError('Report functionality is under development. Using mock data for visualization.');
```

**Mock Components**:

1. **Mock Consumption Data** (Line 127-129):
```tsx
const mockElectricityData = generateMockConsumptionData(startDate, endDate, 'electricity');
const mockWaterData = generateMockConsumptionData(startDate, endDate, 'water');
const mockGasData = generateMockConsumptionData(startDate, endDate, 'gas');
```

2. **Mock Analysis** (Line 131-152):
```tsx
const mockAnalysisData = {
  building_id: selectedBuilding.id,
  metric: "electricity",
  period: { start: startDate, end: endDate },
  patterns: {
    daily: {
      peak_hours: ["09:00", "18:00"],  // Fake
      off_peak_hours: ["01:00", "04:00"],  // Fake
      average_daily_profile: [100, 110, 105, 110, 115]  // Fake
    },
    weekly: {
      highest_day: "Monday",  // Fake
      lowest_day: "Sunday",  // Fake
      weekday_weekend_ratio: 1.4  // Fake
    },
    seasonal: {
      summer_average: 120,  // Fake
      winter_average: 140,  // Fake
      seasonal_variation: 16.7  // Fake
    }
  }
};
```

3. **Mock Recommendations** (Line 154-173):
```tsx
const mockRecommendations = [
  {
    id: "rec-001",
    title: "Optimize HVAC Schedule",  // Fake
    description: "Adjust HVAC schedules to match occupancy patterns",  // Fake
    potential_savings: 1200,  // Fake number
    implementation_cost: "Low",  // Fake
    priority: "High"  // Fake
  },
  {
    id: "rec-002",
    title: "Lighting Upgrades",  // Fake
    potential_savings: 800,  // Fake
  }
];
```

4. **Mock Anomalies** (Line 175-186):
```tsx
const mockAnomalies = [
  {
    id: "anom-001",
    timestamp: new Date(startDate).toISOString(),  // Fake
    expected_value: 120,  // Fake
    actual_value: 175,  // Fake
    deviation_percentage: 45.8,  // Fake
    severity: "High"  // Fake
  }
];
```

### Mock Data Generator Function (Line 240-270)

```tsx
const generateMockConsumptionData = (startDate: string, endDate: string, metric: string) => {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const days = Math.round((end.getTime() - start.getTime()) / (24 * 60 * 60 * 1000)) + 1;

  const result = [];
  let date = new Date(start);

  for (let i = 0; i < days; i++) {
    // Base value depends on metric
    let baseValue = metric === 'electricity' ? 120 : metric === 'water' ? 50 : 30;

    // Add weekly pattern - higher on weekdays
    const dayOfWeek = date.getDay();
    const weekdayFactor = dayOfWeek === 0 || dayOfWeek === 6 ? 0.7 : 1.0 + (dayOfWeek / 10);

    // Add some randomness
    const randomFactor = 0.8 + Math.random() * 0.4;

    const value = Math.round(baseValue * weekdayFactor * randomFactor);

    result.push({
      timestamp: new Date(date).toISOString(),
      value  // COMPLETELY FAKE
    });

    date.setDate(date.getDate() + 1);
  }

  return result;
};
```

**Algorithm**: Simple random number generator with weekday pattern. No relation to real building data.

---

## Backend Status

### Missing Endpoints

**Current Status**: ❌ **NO REPORT ENDPOINTS EXIST**

**Evidence**:
```bash
# Checked all route files in /backend/api/routes/
$ ls backend/api/routes/*.py
adapter_routes.py
analysis_routes.py
building_routes.py
chat.py
commander_routes.py
evaluator_routes.py
forecasting_routes.py
memory_routes.py
recommendation_routes.py
weather_routes.py

# No report_routes.py found

# Searched for "report" in all routes
$ grep -r "report" backend/api/routes/
# No results
```

**Conclusion**: Backend has **ZERO** report functionality implemented.

---

## Database Capability

### Available Data (TimescaleDB)

**Container**: `7de4b223ee21` (eaio_timescaledb_new)
**Database**: `eaio_energy`
**Schema**: `energy`

**Tables**:
```sql
-- energy.meter_readings (PRIMARY DATA SOURCE)
SELECT
    COUNT(*) as total_records,
    MIN(timestamp) as earliest,
    MAX(timestamp) as latest,
    COUNT(DISTINCT building_id) as buildings,
    COUNT(DISTINCT meter_type) as meter_types
FROM energy.meter_readings;

-- Results:
-- total_records: 40,508,810
-- earliest: 2016-01-01 00:00:00+00
-- latest: 2017-12-31 23:00:00+00
-- buildings: 1,636
-- meter_types: 8 (electricity, gas, water, steam, hotwater, chilledwater, irrigation, solar)
```

**Data Quality**: ✅ **EXCELLENT**
- 2 years of hourly data (2016-2017)
- 40.5 million records
- All requested meter types available
- All buildings have consumption history

**Potential Reports**:
1. ✅ **Monthly/Quarterly/Annual Consumption** - Aggregate by period
2. ✅ **Consumption Trends** - Daily/weekly/monthly patterns
3. ✅ **Peak Analysis** - Identify high consumption periods
4. ✅ **Comparisons** - Building-to-building, period-to-period
5. ✅ **Anomaly Detection** - Statistical outliers
6. ✅ **Performance Scoring** - Energy Use Intensity (EUI)

---

## Comparison with Working Modules

### Forecasting Module (After Fix) ✅

**Data Flow**:
```
Frontend → API Call → Backend → TimescaleDB Query → Real Data → Chart
```

**Example**:
```tsx
// Frontend: ForecastContainer.tsx
const forecastData = await forecastApi.getTimeSeriesForecast(
  buildingId, metric, startDate, horizon
);
// Returns: Real forecast based on 40.5M historical records
```

**Backend**:
```python
# forecasting_routes.py:66-127
def get_building_data(building_id, metric, start_date, end_date):
    query = """
        SELECT timestamp, value as consumption
        FROM energy.meter_readings
        WHERE building_id = :building_id AND meter_type = :metric
    """
    df = pd.read_sql_query(text(query), engine, params=params)
    # Returns: Real DataFrame with actual consumption
```

### Reports Module (Current) ❌

**Data Flow**:
```
Frontend → generateMockData() → Random Numbers → Fake Chart
          ↑
          No backend call!
```

**Example**:
```tsx
// Reports.tsx:127-129
const mockElectricityData = generateMockConsumptionData(startDate, endDate, 'electricity');
// Returns: Array of random numbers with no relation to building
```

**Backend**:
```
❌ DOES NOT EXIST
```

---

## Required Implementation

### Phase 1: Backend API Development

**New File**: `/backend/api/routes/report_routes.py`

**Required Endpoints**:

#### 1. Generate Report Endpoint
```python
@router.post("/reports/generate")
async def generate_report(
    building_id: str,
    report_type: str,  # "monthly", "quarterly", "annual"
    start_date: str,
    end_date: str
):
    """
    Generate comprehensive energy consumption report

    Returns:
        - consumption_summary: Total consumption by meter type
        - daily_trends: Day-by-day consumption data
        - patterns: Peak hours, weekday vs weekend, seasonal
        - performance_score: Energy Use Intensity (EUI) based score
        - anomalies: Statistical outliers in consumption
        - period_comparison: Comparison with previous period
    """
```

**SQL Queries Needed**:

```sql
-- 1. Consumption Summary
SELECT
    meter_type,
    SUM(value) as total,
    AVG(value) as average,
    MIN(value) as minimum,
    MAX(value) as maximum,
    COUNT(*) as data_points
FROM energy.meter_readings
WHERE building_id = :building_id
  AND timestamp >= :start_date
  AND timestamp <= :end_date
GROUP BY meter_type;

-- 2. Daily Consumption Trends
SELECT
    DATE(timestamp) as date,
    meter_type,
    SUM(value) as daily_total
FROM energy.meter_readings
WHERE building_id = :building_id
  AND meter_type = :meter_type
  AND timestamp >= :start_date
  AND timestamp <= :end_date
GROUP BY DATE(timestamp), meter_type
ORDER BY date ASC;

-- 3. Peak Hours Analysis
SELECT
    EXTRACT(HOUR FROM timestamp) as hour,
    AVG(value) as avg_consumption
FROM energy.meter_readings
WHERE building_id = :building_id
  AND meter_type = 'electricity'
  AND timestamp >= :start_date
  AND timestamp <= :end_date
GROUP BY EXTRACT(HOUR FROM timestamp)
ORDER BY avg_consumption DESC;

-- 4. Weekday vs Weekend Pattern
SELECT
    CASE
        WHEN EXTRACT(DOW FROM timestamp) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type,
    AVG(value) as avg_consumption,
    SUM(value) as total_consumption
FROM energy.meter_readings
WHERE building_id = :building_id
  AND meter_type = :meter_type
  AND timestamp >= :start_date
  AND timestamp <= :end_date
GROUP BY day_type;

-- 5. Anomaly Detection (Simple Statistical Method)
WITH stats AS (
    SELECT
        AVG(value) as mean,
        STDDEV(value) as stddev
    FROM energy.meter_readings
    WHERE building_id = :building_id
      AND meter_type = :meter_type
      AND timestamp >= :start_date
      AND timestamp <= :end_date
)
SELECT
    timestamp,
    value as actual_value,
    (SELECT mean FROM stats) as expected_value,
    ((value - (SELECT mean FROM stats)) / (SELECT stddev FROM stats)) as z_score
FROM energy.meter_readings, stats
WHERE building_id = :building_id
  AND meter_type = :meter_type
  AND timestamp >= :start_date
  AND timestamp <= :end_date
  AND ABS((value - stats.mean) / stats.stddev) > 2.5  -- Outliers beyond 2.5 std dev
ORDER BY ABS((value - stats.mean) / stats.stddev) DESC
LIMIT 10;
```

#### 2. Period Comparison Endpoint
```python
@router.post("/reports/compare-periods")
async def compare_periods(
    building_id: str,
    period1_start: str,
    period1_end: str,
    period2_start: str,
    period2_end: str,
    meter_type: str = "electricity"
):
    """
    Compare consumption between two time periods

    Returns:
        - period1_total, period2_total
        - percentage_change
        - daily_comparison_chart_data
    """
```

#### 3. Performance Score Endpoint
```python
@router.get("/reports/performance-score/{building_id}")
async def get_performance_score(
    building_id: str,
    start_date: str,
    end_date: str
):
    """
    Calculate building energy performance score (0-100)

    Based on:
        - Energy Use Intensity (EUI) = kWh / m²
        - Comparison with building type benchmarks
        - Anomaly frequency
        - Trend analysis (improving vs declining)
    """
```

---

### Phase 2: Frontend Integration

**File**: `/frontend/src/pages/Reports.tsx`

**Changes Required**:

#### 1. Create API Service (NEW FILE)

**File**: `/frontend/src/services/api/reportApi.ts`

```typescript
import { apiClient } from './client';

export interface ReportRequest {
  building_id: string;
  report_type: 'monthly' | 'quarterly' | 'annual';
  start_date: string;
  end_date: string;
}

export interface ReportData {
  period: {
    type: string;
    start: string;
    end: string;
  };
  building: {
    id: string;
    name: string;
    type: string;
    size: number;
  };
  consumption: {
    electricity: { total: number; unit: string; data: ConsumptionDataPoint[] };
    water: { total: number; unit: string; data: ConsumptionDataPoint[] };
    gas: { total: number; unit: string; data: ConsumptionDataPoint[] };
  };
  patterns: {
    daily: {
      peak_hours: string[];
      off_peak_hours: string[];
      hourly_averages: number[];
    };
    weekly: {
      highest_day: string;
      lowest_day: string;
      weekday_weekend_ratio: number;
    };
  };
  performance_score: number;
  anomalies: Anomaly[];
}

export const reportApi = {
  generateReport: async (request: ReportRequest): Promise<ReportData> => {
    const response = await apiClient.post('/reports/generate', request);
    return response.data;
  },

  comparePeroids: async (
    building_id: string,
    period1_start: string,
    period1_end: string,
    period2_start: string,
    period2_end: string
  ) => {
    const response = await apiClient.post('/reports/compare-periods', {
      building_id,
      period1_start,
      period1_end,
      period2_start,
      period2_end
    });
    return response.data;
  },

  getPerformanceScore: async (
    building_id: string,
    start_date: string,
    end_date: string
  ) => {
    const response = await apiClient.get(
      `/reports/performance-score/${building_id}`,
      { params: { start_date, end_date } }
    );
    return response.data;
  }
};
```

#### 2. Replace Mock Data Generation

**REMOVE** (Lines 122-229):
```tsx
// DELETE ALL MOCK DATA GENERATION
console.log('Using mock data...');  // DELETE
const mockElectricityData = ...;  // DELETE
const mockAnalysisData = ...;  // DELETE
const mockRecommendations = ...;  // DELETE
const mockAnomalies = ...;  // DELETE
```

**ADD**:
```tsx
import { reportApi } from '../services/api/reportApi';

const generateReport = async () => {
  if (!selectedBuilding) return;

  setLoading(true);
  setError(null);

  try {
    // Calculate date range (keep existing logic)
    let startDate: string, endDate: string;
    // ... existing date calculation code ...

    // CALL REAL API INSTEAD OF MOCK
    const reportData = await reportApi.generateReport({
      building_id: selectedBuilding.id,
      report_type: reportType,
      start_date: startDate,
      end_date: endDate
    });

    setReportData(reportData);
  } catch (err: any) {
    setError(err.message || 'Error generating report');
    console.error('Error generating report:', err);
  } finally {
    setLoading(false);
  }
};
```

#### 3. Remove Mock Data Generator Functions

**DELETE** (Lines 240-295):
```tsx
// DELETE ENTIRE FUNCTION
const generateMockConsumptionData = (startDate, endDate, metric) => {
  // ... 30 lines of fake data generation ...
};

// DELETE THESE TOO
const calculateEstimatedSavings = ...;
const calculatePerformanceScore = ...;
```

**REASON**: All calculations should be done on backend with real data.

---

### Phase 3: Recommendations Integration

**Current Issue**: Recommendations are hardcoded fakes

**Solution**: Integrate with existing `recommendation_routes.py`

**File**: `/backend/api/routes/recommendation_routes.py`

**Check if endpoint exists**:
```python
@router.get("/recommendations/building/{building_id}")
async def get_recommendations_for_building(building_id: str):
    # Check if this exists
```

**If exists**: ✅ Use it in reports
**If not**: ❌ Create it (likely already exists from earlier modules)

---

### Phase 4: Anomaly Detection Integration

**Current Issue**: Anomalies are hardcoded fakes

**Options**:

**Option 1**: Extend `analysis_routes.py`
```python
# /backend/api/routes/analysis_routes.py
@router.get("/analysis/anomalies/{building_id}")
async def detect_anomalies(
    building_id: str,
    metric: str = "electricity",
    start_date: str = Query(...),
    end_date: str = Query(...),
    sensitivity: float = 2.5  # Z-score threshold
):
    # Statistical anomaly detection on real data
```

**Option 2**: Create in `report_routes.py`
```python
# /backend/api/routes/report_routes.py (NEW)
# Include anomaly detection as part of report generation
```

**Recommendation**: Check if anomaly endpoint exists in `analysis_routes.py`, if yes use it, if no add to `report_routes.py`.

---

## Implementation Plan

### Priority Order

#### 🔴 Phase 1: Backend Foundation (2-3 hours)
1. ✅ Create `/backend/api/routes/report_routes.py`
2. ✅ Implement `generate_report` endpoint with TimescaleDB queries
3. ✅ Add to `backend/api/main.py` router includes
4. ✅ Test with Postman/curl

#### 🟡 Phase 2: Frontend Integration (1-2 hours)
1. ✅ Create `/frontend/src/services/api/reportApi.ts`
2. ✅ Replace mock data in `Reports.tsx` with API calls
3. ✅ Remove all mock generation functions
4. ✅ Test UI with real data

#### 🟢 Phase 3: Enhanced Features (1-2 hours)
1. ✅ Add period comparison functionality
2. ✅ Integrate recommendations (check existing endpoint)
3. ✅ Add anomaly detection
4. ✅ Improve performance scoring algorithm

#### 🔵 Phase 4: Polish & Testing (1 hour)
1. ✅ Add loading states and error handling
2. ✅ UI/UX improvements (similar to Forecasting fixes)
3. ✅ Export to PDF functionality (optional)
4. ✅ Comprehensive testing

---

## Expected Outcomes

### Before (Current State) ❌

```
User selects: Bear_assembly_Genia, Monthly, Dec 2024
↓
Frontend generates: Random numbers (100-150 kWh)
↓
Displays: Completely fake charts and recommendations
↓
Value: ZERO (misleading fake data)
```

### After (Proposed Solution) ✅

```
User selects: Bear_assembly_Genia, Monthly, Dec 2016
↓
Frontend calls: POST /api/reports/generate
↓
Backend queries: energy.meter_readings (real 2016 data)
↓
Returns:
  - Total: 87,450 kWh (real)
  - Peak hours: 14:00-18:00 (real pattern)
  - Anomalies: 3 detected (real outliers)
  - Score: 72/100 (real EUI calculation)
↓
Displays: Accurate charts based on 40.5M real records
↓
Value: HIGH (actionable insights for energy management)
```

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Database query performance (40M records) | Medium | High | Add indexes, use time-bucket aggregation |
| Frontend state management complexity | Low | Medium | Keep existing structure, just swap data source |
| Date range calculation bugs | Medium | Low | Extensive testing, reuse existing logic |
| Missing building metadata | Low | Medium | Join with energy.buildings table |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Users expect current 2025 data | High | High | Clear messaging: "Historical 2016-2017 data" |
| Report generation timeout | Low | Medium | Async processing, caching |
| Unexpected data quality issues | Medium | Medium | Data validation, graceful error handling |

---

## Success Metrics

### Functional Requirements ✅
- [ ] Reports display real consumption data from TimescaleDB
- [ ] Monthly/Quarterly/Annual periods work correctly
- [ ] Charts reflect actual building consumption patterns
- [ ] Performance score based on real EUI calculations
- [ ] Anomalies detected using statistical methods on real data
- [ ] No mock data generators remain in codebase

### Performance Requirements ✅
- [ ] Report generation < 5 seconds
- [ ] Database queries optimized with indexes
- [ ] Frontend renders smoothly without lag
- [ ] Memory usage < 500MB during report generation

### Quality Requirements ✅
- [ ] Code follows existing patterns (similar to Forecasting fix)
- [ ] Comprehensive error handling
- [ ] Loading states during data fetch
- [ ] User-friendly error messages
- [ ] Documentation updated

---

## Similar to Forecasting Module

### Parallels with Forecasting Fix

| Aspect | Forecasting (Before) | Reports (Current) | Both Need |
|--------|---------------------|-------------------|-----------|
| Data Source | CSV files (missing) | Mock generators | TimescaleDB |
| Backend | CSV reading | No endpoints | SQL queries |
| Frontend | Fallback to mock | Only mock | API integration |
| Impact | No real forecasts | No real reports | Full rewrite |
| Priority | CRITICAL | CRITICAL | Immediate fix |

### Lessons Learned from Forecasting

1. ✅ **Network Configuration**: Already connected backend to TimescaleDB network
2. ✅ **Database Connection**: `POSTGRES_URL` environment variable works
3. ✅ **SQL Queries**: Use `energy.meter_readings` table with proper schema
4. ✅ **Code Pattern**: Similar `get_building_data()` function can be reused
5. ✅ **Testing**: Same curl/Postman testing approach
6. ✅ **Frontend**: Replace mock with `await api.call()` pattern

### Reusable Code from Forecasting Fix

```python
# FROM: /backend/api/routes/forecasting_routes.py:66-127
# CAN REUSE for Reports:

def get_building_consumption(
    building_id: str,
    metric: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """Get real consumption data from TimescaleDB - WORKING CODE"""
    from sqlalchemy import create_engine, text
    import os

    db_host = os.getenv('POSTGRES_HOST', 'eaio_timescaledb_new')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_name = os.getenv('POSTGRES_DB', 'eaio_energy')
    db_user = os.getenv('POSTGRES_USER', 'eaio_user')
    db_pass = os.getenv('POSTGRES_PASSWORD', 'eaio_password')

    engine = create_engine(
        f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    )

    query = """
        SELECT timestamp, value as consumption, meter_type
        FROM energy.meter_readings
        WHERE building_id = :building_id
          AND meter_type = :meter_type
          AND timestamp >= :start_date
          AND timestamp <= :end_date
        ORDER BY timestamp ASC
    """

    df = pd.read_sql_query(
        text(query),
        engine,
        params={
            'building_id': building_id,
            'meter_type': metric,
            'start_date': start_date,
            'end_date': end_date
        }
    )

    return df
```

**Status**: ✅ **PROVEN TO WORK** - Retrieved 17,490 records successfully for forecasting

**Adaptation for Reports**: Change aggregation level (hourly → daily/monthly)

---

## Appendix

### A. Current File Structure

```
EAIO-DL/
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── Reports.tsx ❌ (100% mock data)
│       └── services/
│           └── api/
│               ├── exports.ts
│               └── reportApi.ts ⚠️ (DOES NOT EXIST - NEED TO CREATE)
├── backend/
│   └── api/
│       └── routes/
│           ├── analysis_routes.py ✅ (exists, check for anomalies)
│           ├── recommendation_routes.py ✅ (exists, check for recs)
│           └── report_routes.py ❌ (DOES NOT EXIST - NEED TO CREATE)
└── claudedocs/
    ├── FORECASTING_MODULE_DEVELOPMENT_2025-12-12.md ✅
    └── REPORTS_MODULE_ANALYSIS_2025-12-12.md ✅ (this file)
```

### B. Database Schema Reference

```sql
-- TABLE: energy.meter_readings
CREATE TABLE energy.meter_readings (
    id BIGINT PRIMARY KEY,
    meter_id VARCHAR,
    building_id VARCHAR,           -- "Bear_assembly_Genia"
    meter_type VARCHAR,             -- "electricity", "gas", "water", etc.
    timestamp TIMESTAMPTZ,          -- 2016-01-01 to 2017-12-31
    value NUMERIC,                  -- Consumption value
    unit VARCHAR,                   -- "kWh", "gal", "m³"
    quality VARCHAR,
    is_outlier BOOLEAN,
    confidence_score NUMERIC,
    source VARCHAR,
    batch_id VARCHAR,
    import_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ
);

-- Recommended Index (if not exists)
CREATE INDEX IF NOT EXISTS idx_meter_readings_reports
ON energy.meter_readings(building_id, meter_type, timestamp);
```

### C. API Endpoint Specifications

**Base URL**: `http://localhost:8001/api`

**Endpoint 1**: `POST /reports/generate`

**Request**:
```json
{
  "building_id": "Bear_assembly_Genia",
  "report_type": "monthly",
  "start_date": "2016-12-01",
  "end_date": "2016-12-31"
}
```

**Response**:
```json
{
  "status": "success",
  "report": {
    "period": {
      "type": "monthly",
      "start": "2016-12-01",
      "end": "2016-12-31"
    },
    "building": {
      "id": "Bear_assembly_Genia",
      "name": "Genia Assembly Building",
      "type": "Assembly",
      "size": 12500
    },
    "consumption": {
      "electricity": {
        "total": 87450,
        "unit": "kWh",
        "daily_data": [
          {"date": "2016-12-01", "value": 2850},
          {"date": "2016-12-02", "value": 2920},
          ...
        ]
      },
      "water": { ... },
      "gas": { ... }
    },
    "patterns": {
      "daily": {
        "peak_hours": ["14:00", "15:00", "16:00"],
        "off_peak_hours": ["02:00", "03:00", "04:00"],
        "hourly_averages": [120, 115, 110, ...]
      },
      "weekly": {
        "highest_day": "Wednesday",
        "lowest_day": "Sunday",
        "weekday_weekend_ratio": 1.35
      }
    },
    "performance_score": 72,
    "anomalies": [
      {
        "timestamp": "2016-12-15T14:00:00Z",
        "expected_value": 120,
        "actual_value": 185,
        "deviation_percentage": 54.2,
        "severity": "High"
      }
    ]
  }
}
```

---

## Next Steps

1. **Immediate**: Create `report_routes.py` backend file
2. **Immediate**: Implement basic `/reports/generate` endpoint
3. **Immediate**: Create `reportApi.ts` frontend service
4. **Immediate**: Replace mock data in `Reports.tsx`
5. **Follow-up**: Add enhanced features (comparison, detailed anomalies)
6. **Follow-up**: UI/UX improvements similar to Forecasting module

---

**Document Version**: 1.0
**Status**: Analysis Complete, Ready for Implementation
**Next Action**: Begin Phase 1 - Backend Foundation

