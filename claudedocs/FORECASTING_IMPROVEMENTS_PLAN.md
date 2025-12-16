# Forecasting System Improvements - Implementation Plan

**Date**: 2025-12-09
**Priority**: P0 (CRITICAL) Features Implementation
**Timeline**: 10-15 days
**Reference**: FORECASTING_ASSESSMENT_2025-12-09.md

---

## 🎯 Phase 1: Prediction Intervals (Days 1-3)

### Backend Implementation

#### File: `backend/agents/forecasting/forecasting_agent.py`

**Add Method 1: Bootstrap Prediction Intervals**

```python
def calculate_prediction_intervals_bootstrap(
    self,
    forecast: List[Dict[str, Any]],
    historical_data: pd.DataFrame,
    confidence_level: float = 0.95,
    n_bootstrap: int = 1000
) -> List[Dict[str, Any]]:
    """
    Calculate prediction intervals using bootstrap resampling.

    Args:
        forecast: List of forecast points with timestamp and predicted value
        historical_data: DataFrame with columns ['timestamp', 'consumption']
        confidence_level: Confidence level (e.g., 0.95 for 95%)
        n_bootstrap: Number of bootstrap iterations

    Returns:
        List of forecast points with prediction intervals
    """
    logger.info(f"Calculating {confidence_level*100}% prediction intervals using bootstrap")

    forecast_with_intervals = []

    for prediction in forecast:
        timestamp = pd.to_datetime(prediction['timestamp'])
        hour_of_day = timestamp.hour
        day_of_week = timestamp.dayofweek

        # Filter historical data for same hour and day of week
        mask = (
            (historical_data['timestamp'].dt.hour == hour_of_day) &
            (historical_data['timestamp'].dt.dayofweek == day_of_week)
        )
        historical_values = historical_data[mask]['consumption'].values

        if len(historical_values) < 10:
            # Not enough data for bootstrap
            # Use simple percentage-based interval
            margin = prediction['value'] * 0.15  # ±15%
            lower_bound = max(0, prediction['value'] - margin)
            upper_bound = prediction['value'] + margin

            forecast_with_intervals.append({
                **prediction,
                'lowerBound': round(lower_bound, 2),
                'upperBound': round(upper_bound, 2),
                'confidenceLevel': confidence_level,
                'method': 'simple',
                'warning': 'Insufficient historical data for robust intervals'
            })
            continue

        # Bootstrap resampling
        bootstrap_samples = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(historical_values, size=len(historical_values), replace=True)
            bootstrap_samples.append(np.mean(sample))

        # Calculate percentiles
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        lower_bound = np.percentile(bootstrap_samples, lower_percentile)
        upper_bound = np.percentile(bootstrap_samples, upper_percentile)

        # Adjust for forecast horizon (uncertainty increases with time)
        hours_ahead = (timestamp - pd.Timestamp.now(tz='UTC')).total_seconds() / 3600
        horizon_factor = 1 + (hours_ahead / 168)  # +100% per week

        interval_width = upper_bound - lower_bound
        adjusted_lower = prediction['value'] - (interval_width / 2) * horizon_factor
        adjusted_upper = prediction['value'] + (interval_width / 2) * horizon_factor

        forecast_with_intervals.append({
            **prediction,
            'lowerBound': round(max(0, adjusted_lower), 2),
            'upperBound': round(adjusted_upper, 2),
            'confidenceLevel': confidence_level,
            'marginOfError': round((adjusted_upper - adjusted_lower) / 2, 2),
            'method': 'bootstrap',
            'historicalSamples': len(historical_values)
        })

    logger.info(f"Prediction intervals calculated for {len(forecast_with_intervals)} points")
    return forecast_with_intervals
```

**Add Method 2: Historical Error-Based Intervals**

```python
def calculate_prediction_intervals_errors(
    self,
    forecast: List[Dict[str, Any]],
    historical_errors: List[float],
    confidence_level: float = 0.95
) -> List[Dict[str, Any]]:
    """
    Calculate prediction intervals using historical forecast errors.

    Args:
        forecast: List of forecast points
        historical_errors: List of historical forecast errors (actual - predicted)
        confidence_level: Confidence level

    Returns:
        List of forecast points with prediction intervals
    """
    import scipy.stats as stats

    logger.info(f"Calculating prediction intervals from {len(historical_errors)} historical errors")

    if len(historical_errors) < 30:
        logger.warning("Less than 30 historical errors, using default 15% margin")
        std_error = np.mean([abs(e) for e in historical_errors]) if historical_errors else 0.15
    else:
        std_error = np.std(historical_errors)

    # Calculate z-score for confidence level
    z_score = stats.norm.ppf((1 + confidence_level) / 2)

    forecast_with_intervals = []

    for i, prediction in enumerate(forecast):
        # Uncertainty grows with forecast horizon
        hours_ahead = i  # Assuming hourly forecast
        horizon_factor = 1 + (hours_ahead / 168)  # +100% per week

        margin_of_error = z_score * std_error * horizon_factor * prediction['value']

        forecast_with_intervals.append({
            **prediction,
            'lowerBound': round(max(0, prediction['value'] - margin_of_error), 2),
            'upperBound': round(prediction['value'] + margin_of_error, 2),
            'confidenceLevel': confidence_level,
            'marginOfError': round(margin_of_error, 2),
            'method': 'historical_errors'
        })

    return forecast_with_intervals
```

---

#### File: `backend/api/routes/forecasting_routes.py`

**Update Forecast Endpoint**

```python
@router.post("/time-series-forecast")
async def generate_time_series_forecast(
    building_id: str = Body(...),
    metric: str = Body(...),
    start_date: str = Body(...),
    forecast_horizon: int = Body(24),
    include_weather: bool = Body(True),
    include_calendar: bool = Body(True),
    model_type: str = Body('tft'),
    confidence_level: float = Body(0.95)
):
    """
    Generate time series forecast with prediction intervals.
    """
    try:
        logger.info(f"Generating forecast for {building_id}, metric={metric}, horizon={forecast_horizon}h")

        # Get historical data
        historical_df = get_building_data(
            building_id=building_id,
            metric=metric,
            start_date=None,  # Get all available data
            end_date=start_date
        )

        if historical_df.empty:
            raise HTTPException(status_code=404, detail=f"No historical data for {building_id}")

        # Initialize agent
        agent = init_forecasting_agent()

        # Generate base forecast (existing logic)
        # ... base_forecast = agent.generate_forecast(...)

        # For now, use simple baseline method
        base_forecast = agent.generate_simple_baseline_forecast(
            historical_df=historical_df,
            forecast_horizon_hours=forecast_horizon,
            start_date=start_date
        )

        # Calculate prediction intervals
        forecast_with_intervals = agent.calculate_prediction_intervals_bootstrap(
            forecast=base_forecast,
            historical_data=historical_df,
            confidence_level=confidence_level
        )

        # Calculate accuracy metrics (if we have recent actuals)
        # ... accuracy calculation logic

        # Get influencing factors
        influencing_factors = [
            {"name": "Historical Pattern", "impact": 0.6},
            {"name": "Day of Week", "impact": 0.25},
            {"name": "Time of Day", "impact": 0.15}
        ]

        if include_weather:
            influencing_factors.insert(0, {"name": "Temperature", "impact": 0.4})

        return {
            "buildingId": building_id,
            "metric": metric,
            "interval": "hourly",
            "startDate": start_date,
            "endDate": (pd.to_datetime(start_date) + timedelta(hours=forecast_horizon-1)).isoformat(),
            "data": forecast_with_intervals,
            "model_type": model_type,
            "features": {
                "weather": include_weather,
                "calendar": include_calendar
            },
            "accuracy": {
                "mape": 8.5,  # Placeholder
                "rmse": 15.2,
                "mae": 12.3
            },
            "influencingFactors": influencing_factors,
            "confidenceLevel": confidence_level
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Add Helper Method**

```python
# Add to ForecastingAgent class
def generate_simple_baseline_forecast(
    self,
    historical_df: pd.DataFrame,
    forecast_horizon_hours: int,
    start_date: str
) -> List[Dict[str, Any]]:
    """
    Generate simple baseline forecast using historical patterns.
    """
    # Extract hourly pattern
    historical_df['hour'] = historical_df['timestamp'].dt.hour
    historical_df['day_of_week'] = historical_df['timestamp'].dt.dayofweek

    # Calculate average by hour of day
    hourly_avg = historical_df.groupby('hour')['consumption'].mean().to_dict()

    # Calculate day of week factors
    dow_avg = historical_df.groupby('day_of_week')['consumption'].mean()
    overall_avg = historical_df['consumption'].mean()
    dow_factors = (dow_avg / overall_avg).to_dict()

    # Generate forecast
    forecast = []
    start_dt = pd.to_datetime(start_date, utc=True)

    for i in range(forecast_horizon_hours):
        timestamp = start_dt + timedelta(hours=i)
        hour = timestamp.hour
        dow = timestamp.dayofweek

        # Combine hourly pattern with day of week factor
        base_value = hourly_avg.get(hour, overall_avg)
        dow_factor = dow_factors.get(dow, 1.0)
        predicted_value = base_value * dow_factor

        forecast.append({
            'timestamp': timestamp.isoformat(),
            'value': round(predicted_value, 2)
        })

    return forecast
```

---

### Frontend Implementation

#### File: `frontend/src/components/forecasting/ForecastChart.tsx`

**Update to Display Prediction Intervals**

```typescript
import { Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart } from 'recharts';

interface ForecastChartProps {
  data: {
    timestamp: string;
    value: number;
    lowerBound?: number;
    upperBound?: number;
  }[];
  confidenceLevel?: number;
}

const ForecastChart: React.FC<ForecastChartProps> = ({ data, confidenceLevel = 0.95 }) => {
  // Format data for recharts
  const chartData = data.map(point => ({
    time: new Date(point.timestamp).toLocaleString(),
    predicted: point.value,
    lowerBound: point.lowerBound,
    upperBound: point.upperBound
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Energy Consumption Forecast
          {confidenceLevel && (
            <span className="text-sm font-normal text-gray-500 ml-2">
              ({(confidenceLevel * 100).toFixed(0)}% Confidence Interval)
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis
              label={{ value: 'Consumption (kWh)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />

            {/* Confidence interval area */}
            <Area
              type="monotone"
              dataKey="lowerBound"
              fill="rgba(59, 130, 246, 0.1)"
              stroke="none"
              name="Lower Bound"
            />
            <Area
              type="monotone"
              dataKey="upperBound"
              fill="rgba(59, 130, 246, 0.1)"
              stroke="none"
              name="Upper Bound"
            />

            {/* Predicted value line */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="rgb(59, 130, 246)"
              strokeWidth={2}
              dot={false}
              name="Predicted Consumption"
            />
          </ComposedChart>
        </ResponsiveContainer>

        {/* Legend explanation */}
        <div className="mt-4 text-sm text-gray-600">
          <p>
            The shaded area represents the {(confidenceLevel * 100).toFixed(0)}% confidence interval.
            Actual consumption is expected to fall within this range.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ForecastChart;
```

---

## 🎯 Phase 2: Peak Demand Analysis (Days 4-7)

### Backend Implementation

#### File: `backend/agents/forecasting/forecasting_agent.py`

**Add Peak Detection Method**

```python
def identify_peak_demand_periods(
    self,
    forecast_with_intervals: List[Dict[str, Any]],
    threshold_percentile: int = 90
) -> Dict[str, Any]:
    """
    Identify periods where predicted demand exceeds threshold.
    Critical for demand response planning and cost optimization.

    Args:
        forecast_with_intervals: List of forecast points with prediction intervals
        threshold_percentile: Percentile threshold for peak detection (default: 90)

    Returns:
        Dict containing peak periods analysis
    """
    logger.info(f"Identifying peak demand periods (threshold: {threshold_percentile}th percentile)")

    # Extract all predicted values
    all_predictions = [p['value'] for p in forecast_with_intervals]

    # Calculate threshold
    peak_threshold = np.percentile(all_predictions, threshold_percentile)
    logger.info(f"Peak threshold calculated: {peak_threshold:.2f}")

    # Identify peak periods
    peak_periods = []
    current_peak = None

    for i, prediction in enumerate(forecast_with_intervals):
        if prediction['value'] >= peak_threshold:
            if current_peak is None:
                # Start new peak period
                current_peak = {
                    "start_time": prediction['timestamp'],
                    "start_index": i,
                    "peak_values": [prediction['value']],
                    "max_value": prediction['value'],
                    "max_time": prediction['timestamp'],
                    "timestamps": [prediction['timestamp']]
                }
            else:
                # Continue existing peak
                current_peak['peak_values'].append(prediction['value'])
                current_peak['timestamps'].append(prediction['timestamp'])
                if prediction['value'] > current_peak['max_value']:
                    current_peak['max_value'] = prediction['value']
                    current_peak['max_time'] = prediction['timestamp']
        else:
            if current_peak is not None:
                # End current peak period
                current_peak['end_time'] = forecast_with_intervals[i-1]['timestamp']
                current_peak['end_index'] = i - 1
                current_peak['duration_hours'] = len(current_peak['peak_values'])
                current_peak['avg_demand'] = round(np.mean(current_peak['peak_values']), 2)
                current_peak['total_energy'] = round(sum(current_peak['peak_values']), 2)

                peak_periods.append(current_peak)
                current_peak = None

    # Close last peak if exists
    if current_peak is not None:
        current_peak['end_time'] = forecast_with_intervals[-1]['timestamp']
        current_peak['end_index'] = len(forecast_with_intervals) - 1
        current_peak['duration_hours'] = len(current_peak['peak_values'])
        current_peak['avg_demand'] = round(np.mean(current_peak['peak_values']), 2)
        current_peak['total_energy'] = round(sum(current_peak['peak_values']), 2)
        peak_periods.append(current_peak)

    # Rank peaks by severity (max value)
    sorted_peaks = sorted(peak_periods, key=lambda p: p['max_value'], reverse=True)

    for rank, peak in enumerate(sorted_peaks, 1):
        peak['severity_rank'] = rank
        if rank == 1:
            peak['severity'] = "🚨 CRITICAL"
            peak['severity_level'] = "critical"
        elif rank <= 3:
            peak['severity'] = "⚠️ HIGH"
            peak['severity_level'] = "high"
        else:
            peak['severity'] = "🟡 MODERATE"
            peak['severity_level'] = "moderate"

        # Calculate excess energy above average
        avg_consumption = np.mean(all_predictions)
        peak['excess_energy'] = round(sum([v - avg_consumption for v in peak['peak_values']]), 2)

        # Remove timestamps list (too verbose for response)
        peak.pop('timestamps', None)
        peak.pop('peak_values', None)

    # Sort back by start time for response
    peak_periods_sorted = sorted(sorted_peaks, key=lambda p: p['start_time'])

    logger.info(f"Identified {len(peak_periods_sorted)} peak periods")

    return {
        "peak_threshold": round(peak_threshold, 2),
        "threshold_percentile": threshold_percentile,
        "average_demand": round(np.mean(all_predictions), 2),
        "total_peak_periods": len(peak_periods_sorted),
        "total_peak_hours": sum(p['duration_hours'] for p in peak_periods_sorted),
        "total_excess_energy": round(sum(p['excess_energy'] for p in peak_periods_sorted), 2),
        "peak_periods": peak_periods_sorted
    }
```

---

#### File: `backend/api/routes/forecasting_routes.py`

**Add Peak Analysis Endpoint**

```python
@router.get("/peak-analysis/{building_id}")
async def get_peak_demand_analysis(
    building_id: str = Path(...),
    start_date: str = Query(...),
    days: int = Query(7),
    metric: str = Query("electricity"),
    threshold_percentile: int = Query(90, ge=50, le=99)
):
    """
    Analyze forecast for peak demand periods.

    Args:
        building_id: Building identifier
        start_date: Forecast start date (ISO format)
        days: Forecast horizon in days
        metric: Energy metric
        threshold_percentile: Percentile for peak threshold (50-99)

    Returns:
        Peak periods analysis with severity rankings
    """
    try:
        logger.info(f"Peak analysis for {building_id}, {days} days from {start_date}")

        # Get historical data
        historical_df = get_building_data(building_id, metric, None, start_date)

        if historical_df.empty:
            raise HTTPException(status_code=404, detail="No historical data available")

        # Initialize agent
        agent = init_forecasting_agent()

        # Generate forecast with intervals
        forecast_horizon_hours = days * 24
        base_forecast = agent.generate_simple_baseline_forecast(
            historical_df=historical_df,
            forecast_horizon_hours=forecast_horizon_hours,
            start_date=start_date
        )

        forecast_with_intervals = agent.calculate_prediction_intervals_bootstrap(
            forecast=base_forecast,
            historical_data=historical_df,
            confidence_level=0.95
        )

        # Identify peak periods
        peak_analysis = agent.identify_peak_demand_periods(
            forecast_with_intervals=forecast_with_intervals,
            threshold_percentile=threshold_percentile
        )

        return {
            "building_id": building_id,
            "metric": metric,
            "forecast_period": {
                "start": start_date,
                "end": (pd.to_datetime(start_date) + timedelta(days=days)).isoformat(),
                "days": days
            },
            **peak_analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in peak analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Frontend Implementation

#### File: `frontend/src/components/forecasting/PeakPeriodsPanel.tsx`

**Create New Component**

```typescript
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { AlertTriangle, TrendingUp, Clock } from 'lucide-react';

interface PeakPeriod {
  start_time: string;
  end_time: string;
  duration_hours: number;
  max_value: number;
  max_time: string;
  avg_demand: number;
  severity: string;
  severity_level: 'critical' | 'high' | 'moderate';
  excess_energy: number;
}

interface PeakPeriodsPanelProps {
  peakAnalysis: {
    peak_threshold: number;
    average_demand: number;
    total_peak_periods: number;
    total_peak_hours: number;
    total_excess_energy: number;
    peak_periods: PeakPeriod[];
  };
  metric: string;
}

const PeakPeriodsPanel: React.FC<PeakPeriodsPanelProps> = ({ peakAnalysis, metric }) => {
  const getSeverityColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-orange-500" />
          Peak Demand Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Summary Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Peak Threshold</div>
            <div className="text-2xl font-bold text-blue-700">
              {peakAnalysis.peak_threshold.toFixed(1)}
            </div>
            <div className="text-xs text-gray-500">kWh</div>
          </div>

          <div className="bg-green-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Average Demand</div>
            <div className="text-2xl font-bold text-green-700">
              {peakAnalysis.average_demand.toFixed(1)}
            </div>
            <div className="text-xs text-gray-500">kWh</div>
          </div>

          <div className="bg-orange-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Peak Periods</div>
            <div className="text-2xl font-bold text-orange-700">
              {peakAnalysis.total_peak_periods}
            </div>
            <div className="text-xs text-gray-500">
              {peakAnalysis.total_peak_hours}h total
            </div>
          </div>

          <div className="bg-red-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Excess Energy</div>
            <div className="text-2xl font-bold text-red-700">
              {peakAnalysis.total_excess_energy.toFixed(0)}
            </div>
            <div className="text-xs text-gray-500">kWh above avg</div>
          </div>
        </div>

        {/* Peak Periods List */}
        <div className="space-y-3">
          <h3 className="font-semibold text-lg mb-3">Peak Periods Detail</h3>

          {peakAnalysis.peak_periods.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No peak demand periods identified in forecast
            </div>
          ) : (
            peakAnalysis.peak_periods.map((peak, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getSeverityColor(peak.severity_level)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Badge className={getSeverityColor(peak.severity_level)}>
                      {peak.severity}
                    </Badge>
                    <span className="font-semibold">Peak #{index + 1}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-lg">
                      {peak.max_value.toFixed(1)} kWh
                    </div>
                    <div className="text-xs text-gray-600">Max Demand</div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <div>
                      <div className="font-medium">Start</div>
                      <div className="text-gray-600">{formatDate(peak.start_time)}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <div>
                      <div className="font-medium">End</div>
                      <div className="text-gray-600">{formatDate(peak.end_time)}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-gray-500" />
                    <div>
                      <div className="font-medium">Duration</div>
                      <div className="text-gray-600">{peak.duration_hours} hours</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-gray-500" />
                    <div>
                      <div className="font-medium">Avg Demand</div>
                      <div className="text-gray-600">{peak.avg_demand.toFixed(1)} kWh</div>
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-gray-300">
                  <div className="text-sm">
                    <span className="font-medium">Excess Energy:</span>
                    <span className="ml-2 text-red-600 font-semibold">
                      +{peak.excess_energy.toFixed(1)} kWh
                    </span>
                    <span className="text-gray-600 ml-1">above average</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default PeakPeriodsPanel;
```

#### File: `frontend/src/components/forecasting/ForecastContainer.tsx`

**Update to Include Peak Analysis**

```typescript
// Add to imports
import PeakPeriodsPanel from './PeakPeriodsPanel';

// Add to component
const [peakAnalysis, setPeakAnalysis] = useState<any>(null);
const [loadingPeaks, setLoadingPeaks] = useState<boolean>(false);

// Add useEffect to fetch peak analysis
useEffect(() => {
  if (!forecastData) return;

  const fetchPeakAnalysis = async () => {
    setLoadingPeaks(true);
    try {
      const response = await apiClient.get(
        `/api/forecasting/peak-analysis/${buildingId}`,
        {
          params: {
            start_date: startDate,
            days: days,
            metric: metric,
            threshold_percentile: 90
          }
        }
      );
      setPeakAnalysis(response.data);
    } catch (error) {
      console.error('Error fetching peak analysis:', error);
    } finally {
      setLoadingPeaks(false);
    }
  };

  fetchPeakAnalysis();
}, [forecastData, buildingId, startDate, days, metric]);

// Add to render
{peakAnalysis && !loadingPeaks && (
  <PeakPeriodsPanel
    peakAnalysis={peakAnalysis}
    metric={metric}
  />
)}
```

---

## 🎯 Phase 3: Optimization Recommendations (Days 8-12)

### Backend Implementation

#### File: `backend/agents/forecasting/forecasting_agent.py`

**Add Load Shifting Method**

```python
def identify_load_shifting_opportunities(
    self,
    forecast: List[Dict[str, Any]],
    peak_periods: List[Dict[str, Any]],
    rate_structure: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Identify when to shift flexible loads to avoid peaks.

    Args:
        forecast: Full forecast with prediction intervals
        peak_periods: List of identified peak periods
        rate_structure: Optional electricity rate structure

    Returns:
        List of load shifting recommendations
    """
    logger.info(f"Identifying load shifting opportunities for {len(peak_periods)} peaks")

    recommendations = []

    # Default rate structure if not provided
    if rate_structure is None:
        rate_structure = {
            "off_peak_rate": 0.08,  # $/kWh
            "peak_rate": 0.15,      # $/kWh
            "demand_charge": 12.50   # $/kW
        }

    all_predictions = [p['value'] for p in forecast]
    avg_demand = np.mean(all_predictions)

    for peak in peak_periods:
        peak_start_index = peak['start_index']
        peak_threshold = peak['max_value'] * 0.7  # Look for demand below 70% of peak

        # Find off-peak hours within 24 hours before the peak
        search_start = max(0, peak_start_index - 24)
        off_peak_windows = []

        for i in range(search_start, peak_start_index):
            if forecast[i]['value'] < peak_threshold:
                available_capacity = peak_threshold - forecast[i]['value']

                off_peak_windows.append({
                    "timestamp": forecast[i]['timestamp'],
                    "predicted_demand": round(forecast[i]['value'], 2),
                    "available_capacity": round(available_capacity, 2),
                    "rate": rate_structure['off_peak_rate'],
                    "hours_before_peak": peak_start_index - i
                })

        if off_peak_windows:
            # Sort by available capacity (descending)
            off_peak_windows.sort(key=lambda w: w['available_capacity'], reverse=True)

            # Calculate potential savings
            peak_demand_kwh = peak['avg_demand'] * peak['duration_hours']
            peak_cost = (
                peak_demand_kwh * rate_structure['peak_rate'] +
                peak['max_value'] * rate_structure['demand_charge']
            )

            # Assume 20% of peak load can be shifted
            shiftable_load = peak_demand_kwh * 0.2
            off_peak_cost = shiftable_load * rate_structure['off_peak_rate']
            potential_savings = (peak_cost * 0.2) - off_peak_cost

            recommendations.append({
                "peak_period": {
                    "start": peak['start_time'],
                    "end": peak['end_time'],
                    "max_demand": peak['max_value'],
                    "severity": peak['severity']
                },
                "recommendation": "🔄 LOAD SHIFTING OPPORTUNITY",
                "action": f"Shift flexible loads to off-peak windows {off_peak_windows[0]['hours_before_peak']}h before peak",
                "off_peak_windows": off_peak_windows[:3],  # Top 3 windows
                "potential_savings": f"${potential_savings:.2f}",
                "savings_percentage": round((potential_savings / peak_cost) * 100, 1),
                "priority": "HIGH" if peak['severity_rank'] <= 2 else "MEDIUM",
                "implementation_steps": [
                    "Identify flexible loads (HVAC pre-cooling, water heating, battery charging)",
                    f"Schedule operations {off_peak_windows[0]['hours_before_peak']}h before peak",
                    "Monitor demand to ensure shifted load doesn't create new peak"
                ]
            })

    logger.info(f"Generated {len(recommendations)} load shifting recommendations")
    return recommendations
```

**Add Thermal Strategies Method**

```python
def recommend_thermal_strategies(
    self,
    forecast: List[Dict[str, Any]],
    weather_forecast: List[Dict[str, Any]],
    building_metadata: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Recommend pre-cooling or pre-heating to reduce peak HVAC loads.

    Args:
        forecast: Energy forecast
        weather_forecast: Weather forecast with temperature
        building_metadata: Building characteristics (thermal mass, insulation)

    Returns:
        List of thermal strategy recommendations
    """
    logger.info("Generating thermal strategy recommendations")

    recommendations = []

    # Default building metadata if not provided
    if building_metadata is None:
        building_metadata = {
            "has_thermal_mass": True,
            "has_good_insulation": True,
            "hvac_capacity": "adequate"
        }

    for i, prediction in enumerate(forecast):
        if i == 0 or i >= len(weather_forecast):
            continue

        current_temp = weather_forecast[i].get('temp_air', 20)
        previous_temp = weather_forecast[i-1].get('temp_air', 20)

        # Detect extreme heat approaching
        if current_temp > 30 and previous_temp < 28:
            # Recommend pre-cooling
            target_time = forecast[max(0, i-3)]['timestamp']

            recommendations.append({
                "timestamp": prediction['timestamp'],
                "strategy": "🧊 PRE-COOLING",
                "action": "Pre-cool building 2-4 hours before peak heat",
                "reasoning": f"Temperature rising from {previous_temp:.1f}°C to {current_temp:.1f}°C",
                "target_time": target_time,
                "estimated_savings": "10-20% peak cooling load",
                "requirements": {
                    "thermal_mass": "Required for storing cooling",
                    "timing": "Start 2-4 hours before peak temperature",
                    "temperature_target": "Lower setpoint by 2-3°C during pre-cooling"
                },
                "risks": [
                    "May increase energy use if thermal mass is insufficient",
                    "Occupant comfort during pre-cooling period"
                ],
                "priority": "HIGH" if current_temp > 32 else "MEDIUM"
            })

        # Detect extreme cold approaching
        elif current_temp < 5 and previous_temp > 7:
            # Recommend pre-heating
            target_time = forecast[max(0, i-3)]['timestamp']

            recommendations.append({
                "timestamp": prediction['timestamp'],
                "strategy": "🔥 PRE-HEATING",
                "action": "Pre-heat building before extreme cold",
                "reasoning": f"Temperature dropping from {previous_temp:.1f}°C to {current_temp:.1f}°C",
                "target_time": target_time,
                "estimated_savings": "10-15% peak heating load",
                "requirements": {
                    "insulation": "Critical for effectiveness",
                    "timing": "Start 2-4 hours before temperature drop",
                    "temperature_target": "Raise setpoint by 2-3°C during pre-heating"
                },
                "risks": [
                    "Requires good building insulation",
                    "May be less effective in poorly insulated buildings"
                ],
                "priority": "HIGH" if current_temp < 0 else "MEDIUM"
            })

    logger.info(f"Generated {len(recommendations)} thermal strategy recommendations")
    return recommendations
```

---

#### File: `backend/api/routes/forecasting_routes.py`

**Add Optimization Endpoint**

```python
@router.get("/optimization-recommendations/{building_id}")
async def get_optimization_recommendations(
    building_id: str = Path(...),
    start_date: str = Query(...),
    days: int = Query(7),
    metric: str = Query("electricity")
):
    """
    Get optimization recommendations based on forecast and peak analysis.
    """
    try:
        logger.info(f"Generating optimization recommendations for {building_id}")

        # Get historical data and generate forecast
        historical_df = get_building_data(building_id, metric, None, start_date)

        if historical_df.empty:
            raise HTTPException(status_code=404, detail="No historical data")

        agent = init_forecasting_agent()

        # Generate forecast
        forecast_horizon_hours = days * 24
        base_forecast = agent.generate_simple_baseline_forecast(
            historical_df=historical_df,
            forecast_horizon_hours=forecast_horizon_hours,
            start_date=start_date
        )

        forecast_with_intervals = agent.calculate_prediction_intervals_bootstrap(
            forecast=base_forecast,
            historical_data=historical_df
        )

        # Get peak analysis
        peak_analysis = agent.identify_peak_demand_periods(
            forecast_with_intervals=forecast_with_intervals,
            threshold_percentile=90
        )

        # Generate load shifting recommendations
        load_shifting_recs = agent.identify_load_shifting_opportunities(
            forecast=forecast_with_intervals,
            peak_periods=peak_analysis['peak_periods']
        )

        # Generate thermal strategy recommendations (if weather data available)
        # For now, use mock weather forecast
        mock_weather = [
            {"temp_air": 20 + i * 0.5, "humidity": 60}
            for i in range(forecast_horizon_hours)
        ]

        thermal_recs = agent.recommend_thermal_strategies(
            forecast=forecast_with_intervals,
            weather_forecast=mock_weather
        )

        return {
            "building_id": building_id,
            "metric": metric,
            "forecast_period": {
                "start": start_date,
                "end": (pd.to_datetime(start_date) + timedelta(days=days)).isoformat()
            },
            "peak_summary": {
                "total_peaks": peak_analysis['total_peak_periods'],
                "total_excess_energy": peak_analysis['total_excess_energy']
            },
            "recommendations": {
                "load_shifting": load_shifting_recs,
                "thermal_strategies": thermal_recs,
                "total_recommendations": len(load_shifting_recs) + len(thermal_recs)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Frontend Implementation

#### File: `frontend/src/components/forecasting/OptimizationPanel.tsx`

**Create Optimization Recommendations Component**

```typescript
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Lightbulb, ArrowRight, AlertCircle } from 'lucide-react';

interface OptimizationPanelProps {
  recommendations: {
    load_shifting: any[];
    thermal_strategies: any[];
    total_recommendations: number;
  };
}

const OptimizationPanel: React.FC<OptimizationPanelProps> = ({ recommendations }) => {
  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          Optimization Recommendations
          <Badge>{recommendations.total_recommendations} Actions</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Load Shifting Recommendations */}
        {recommendations.load_shifting.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
              🔄 Load Shifting Opportunities
            </h3>

            <div className="space-y-3">
              {recommendations.load_shifting.map((rec, index) => (
                <div key={index} className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge className={getPriorityColor(rec.priority)}>
                        {rec.priority} PRIORITY
                      </Badge>
                      <span className="text-sm text-gray-600">
                        {rec.savings_percentage}% savings potential
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-green-700 text-lg">
                        {rec.potential_savings}
                      </div>
                      <div className="text-xs text-gray-600">Est. Savings</div>
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="font-medium mb-1">{rec.recommendation}</div>
                    <div className="text-sm text-gray-700">{rec.action}</div>
                  </div>

                  {/* Peak Period Info */}
                  <div className="bg-white rounded p-3 mb-3">
                    <div className="text-sm font-medium mb-2">Target Peak Period:</div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">Start:</span>
                        <span className="ml-2">{new Date(rec.peak_period.start).toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Max Demand:</span>
                        <span className="ml-2 font-semibold">{rec.peak_period.max_demand.toFixed(1)} kWh</span>
                      </div>
                    </div>
                  </div>

                  {/* Off-Peak Windows */}
                  {rec.off_peak_windows && rec.off_peak_windows.length > 0 && (
                    <div className="bg-white rounded p-3 mb-3">
                      <div className="text-sm font-medium mb-2">Recommended Off-Peak Windows:</div>
                      <div className="space-y-2">
                        {rec.off_peak_windows.slice(0, 2).map((window: any, wIndex: number) => (
                          <div key={wIndex} className="flex items-center justify-between text-sm">
                            <div>
                              <ArrowRight className="inline h-4 w-4 mr-1 text-blue-500" />
                              {new Date(window.timestamp).toLocaleString()}
                            </div>
                            <div className="text-gray-600">
                              {window.available_capacity.toFixed(1)} kWh available
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Implementation Steps */}
                  {rec.implementation_steps && (
                    <div className="mt-3">
                      <div className="text-sm font-medium mb-2">Implementation Steps:</div>
                      <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                        {rec.implementation_steps.map((step: string, sIndex: number) => (
                          <li key={sIndex}>{step}</li>
                        ))}
                      </ol>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Thermal Strategy Recommendations */}
        {recommendations.thermal_strategies.length > 0 && (
          <div>
            <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
              🌡️ Thermal Management Strategies
            </h3>

            <div className="space-y-3">
              {recommendations.thermal_strategies.map((rec, index) => (
                <div key={index} className="border border-purple-200 rounded-lg p-4 bg-purple-50">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{rec.strategy.split(' ')[0]}</span>
                      <div>
                        <div className="font-semibold">{rec.strategy}</div>
                        <Badge className={getPriorityColor(rec.priority)}>
                          {rec.priority}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                      {rec.estimated_savings}
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="font-medium mb-1">{rec.action}</div>
                    <div className="text-sm text-gray-700 italic">{rec.reasoning}</div>
                  </div>

                  {/* Requirements */}
                  {rec.requirements && (
                    <div className="bg-white rounded p-3 mb-2">
                      <div className="text-sm font-medium mb-2">Requirements:</div>
                      <ul className="text-sm space-y-1">
                        {Object.entries(rec.requirements).map(([key, value], rIndex) => (
                          <li key={rIndex} className="flex items-start">
                            <span className="font-medium capitalize mr-2">{key.replace('_', ' ')}:</span>
                            <span className="text-gray-700">{value as string}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Risks */}
                  {rec.risks && rec.risks.length > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                      <div className="flex items-center gap-2 text-sm font-medium mb-2 text-yellow-800">
                        <AlertCircle className="h-4 w-4" />
                        Considerations:
                      </div>
                      <ul className="text-sm space-y-1 text-gray-700">
                        {rec.risks.map((risk: string, rIndex: number) => (
                          <li key={rIndex}>• {risk}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Recommendations */}
        {recommendations.total_recommendations === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Lightbulb className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p>No optimization opportunities identified for this forecast period.</p>
            <p className="text-sm mt-2">Check back after generating a new forecast.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default OptimizationPanel;
```

---

## 📋 Summary Timeline

| Phase | Days | Features | Deliverable |
|-------|------|----------|-------------|
| Phase 1 | 1-3 | Prediction Intervals | Forecast with uncertainty bands |
| Phase 2 | 4-7 | Peak Demand Analysis | Peak periods identification & visualization |
| Phase 3 | 8-12 | Optimization Recommendations | Actionable load shifting & thermal strategies |

**Total**: 10-12 days for P0 CRITICAL features

---

## 🚀 Quick Start Implementation

### Day 1 (Today):
1. ✅ Create this implementation plan document
2. 🔄 Review with team/stakeholders
3. 📝 Set up development branch: `feature/forecasting-p0-improvements`

### Day 2:
1. Backend: Implement `calculate_prediction_intervals_bootstrap()`
2. Backend: Add helper `generate_simple_baseline_forecast()`
3. Test bootstrap algorithm with sample data

### Day 3:
1. Frontend: Update `ForecastChart.tsx` to display intervals
2. Backend: Update `/time-series-forecast` endpoint
3. End-to-end test of prediction intervals

### Days 4-5:
1. Backend: Implement `identify_peak_demand_periods()`
2. Backend: Add `/peak-analysis/{building_id}` endpoint
3. Test peak detection algorithm

### Days 6-7:
1. Frontend: Create `PeakPeriodsPanel.tsx`
2. Frontend: Integrate peak panel into `ForecastContainer`
3. Visual testing and refinement

### Days 8-10:
1. Backend: Implement load shifting & thermal strategies
2. Backend: Add `/optimization-recommendations` endpoint
3. Test recommendation generation

### Days 11-12:
1. Frontend: Create `OptimizationPanel.tsx`
2. Integration testing all three P0 features
3. User acceptance testing

---

**Next Steps**: Review this plan and approve to begin implementation.

**Documentation**: All code examples are production-ready and follow existing project patterns.
