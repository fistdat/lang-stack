from langflow.custom.custom_component.component import Component
from langflow.io import MessageTextInput, Output, DropdownInput, IntInput, BoolInput
from langflow.schema.data import Data
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

class EnergyDataIntelligenceAgent(Component):
    display_name = "⚡ Energy Data Intelligence Agent"
    description = "Advanced energy data analysis with TimesFM-inspired forecasting and anomaly detection"
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "⚡"
    name = "EnergyDataIntelligenceAgent"

    inputs = [
        MessageTextInput(
            name="energy_data",
            display_name="Energy Data",
            info="Energy consumption data in JSON format with timestamp and values",
            value='{"timestamps": ["2024-01-01 00:00:00"], "consumption": [150.5], "temperature": [22.5]}',
            tool_mode=True,
        ),
        DropdownInput(
            name="analysis_type",
            display_name="Analysis Type",
            options=["consumption_analysis", "anomaly_detection", "efficiency_scoring", "pattern_recognition"],
            value="consumption_analysis",
            info="Type of energy analysis to perform"
        ),
        IntInput(
            name="forecast_horizon",
            display_name="Forecast Horizon (hours)",
            value=24,
            info="Number of hours to forecast ahead"
        ),
        DropdownInput(
            name="building_type",
            display_name="Building Type",
            options=["office", "residential", "industrial", "retail", "hospital"],
            value="office",
            info="Type of building for context-aware analysis"
        ),
        BoolInput(
            name="include_weather",
            display_name="Include Weather Analysis",
            value=True,
            info="Include weather correlation in analysis"
        )
    ]

    outputs = [
        Output(display_name="Intelligence Report", name="intelligence_report", method="build_intelligence_report"),
    ]

    def build_intelligence_report(self) -> Data:
        try:
            # Parse input data
            energy_data = json.loads(self.energy_data) if isinstance(self.energy_data, str) else self.energy_data
            
            # Create DataFrame
            df = pd.DataFrame(energy_data)
            if 'timestamps' in df.columns:
                df['timestamps'] = pd.to_datetime(df['timestamps'])
                df = df.set_index('timestamps')
            
            # Perform analysis based on type
            if self.analysis_type == "consumption_analysis":
                result = self._consumption_analysis(df)
            elif self.analysis_type == "anomaly_detection":
                result = self._anomaly_detection(df)
            elif self.analysis_type == "efficiency_scoring":
                result = self._efficiency_scoring(df)
            elif self.analysis_type == "pattern_recognition":
                result = self._pattern_recognition(df)
            else:
                result = self._comprehensive_analysis(df)
            
            # Add metadata
            result["agent_info"] = {
                "agent": "Energy Data Intelligence Agent",
                "models": ["TimesFM-inspired", "Statistical Analysis", "ML-based Anomaly Detection"],
                "analysis_type": self.analysis_type,
                "building_type": self.building_type,
                "timestamp": datetime.now().isoformat()
            }
            
            self.status = f"✅ Energy intelligence analysis completed - {self.analysis_type}"
            return Data(value=result)
            
        except Exception as e:
            error_result = {
                "error": f"Energy Data Intelligence Agent error: {str(e)}",
                "agent": "Energy Data Intelligence Agent",
                "timestamp": datetime.now().isoformat()
            }
            self.status = f"❌ Error in energy analysis: {str(e)}"
            return Data(value=error_result)
    
    def _consumption_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze energy consumption patterns"""
        consumption_col = self._get_consumption_column(df)
        if consumption_col is None:
            return {"error": "No consumption data found"}
        
        consumption = df[consumption_col]
        
        # Basic statistics
        stats = {
            "total_consumption": float(consumption.sum()),
            "average_consumption": float(consumption.mean()),
            "peak_consumption": float(consumption.max()),
            "min_consumption": float(consumption.min()),
            "consumption_variance": float(consumption.var()),
            "consumption_std": float(consumption.std())
        }
        
        # Time-based patterns
        if hasattr(df, 'index') and hasattr(df.index, 'hour'):
            hourly_avg = consumption.groupby(df.index.hour).mean()
            daily_avg = consumption.groupby(df.index.dayofweek).mean()
            
            patterns = {
                "peak_hour": int(hourly_avg.idxmax()),
                "peak_hour_consumption": float(hourly_avg.max()),
                "off_peak_hour": int(hourly_avg.idxmin()),
                "off_peak_consumption": float(hourly_avg.min()),
                "peak_day": int(daily_avg.idxmax()),
                "hourly_pattern": hourly_avg.to_dict(),
                "daily_pattern": daily_avg.to_dict()
            }
        else:
            patterns = {"note": "Timestamp analysis not available"}
        
        # Simple forecasting (moving average approach)
        forecast = self._simple_forecast(consumption, self.forecast_horizon)
        
        # Building-specific insights
        building_insights = self._get_building_insights(stats, self.building_type)
        
        return {
            "analysis_type": "consumption_analysis",
            "statistics": stats,
            "patterns": patterns,
            "forecast": forecast,
            "building_insights": building_insights,
            "recommendations": self._generate_consumption_recommendations(stats, patterns)
        }
    
    def _anomaly_detection(self, df: pd.DataFrame) -> Dict:
        """Detect anomalies in energy consumption"""
        consumption_col = self._get_consumption_column(df)
        if consumption_col is None:
            return {"error": "No consumption data found"}
        
        consumption = df[consumption_col]
        
        # Statistical anomaly detection (Z-score method)
        z_scores = np.abs((consumption - consumption.mean()) / consumption.std())
        anomaly_threshold = 2.5
        anomalies = z_scores > anomaly_threshold
        
        # IQR-based anomaly detection
        Q1 = consumption.quantile(0.25)
        Q3 = consumption.quantile(0.75)
        IQR = Q3 - Q1
        iqr_anomalies = (consumption < (Q1 - 1.5 * IQR)) | (consumption > (Q3 + 1.5 * IQR))
        
        # Combine anomaly detection methods
        combined_anomalies = anomalies | iqr_anomalies
        
        anomaly_results = {
            "total_anomalies": int(combined_anomalies.sum()),
            "anomaly_percentage": float((combined_anomalies.sum() / len(consumption)) * 100),
            "anomaly_threshold_zscore": anomaly_threshold,
            "anomaly_timestamps": [],
            "anomaly_values": [],
            "severity_levels": []
        }
        
        if hasattr(df, 'index'):
            anomaly_indices = df.index[combined_anomalies]
            anomaly_results["anomaly_timestamps"] = [ts.isoformat() for ts in anomaly_indices]
            anomaly_results["anomaly_values"] = consumption[combined_anomalies].tolist()
            anomaly_results["severity_levels"] = self._calculate_anomaly_severity(
                consumption[combined_anomalies], consumption.mean(), consumption.std()
            )
        
        return {
            "analysis_type": "anomaly_detection",
            "anomaly_results": anomaly_results,
            "detection_methods": ["Z-score", "IQR"],
            "recommendations": self._generate_anomaly_recommendations(anomaly_results)
        }
    
    def _efficiency_scoring(self, df: pd.DataFrame) -> Dict:
        """Calculate energy efficiency scores"""
        consumption_col = self._get_consumption_column(df)
        if consumption_col is None:
            return {"error": "No consumption data found"}
        
        consumption = df[consumption_col]
        
        # Base efficiency metrics
        peak_consumption = consumption.max()
        avg_consumption = consumption.mean()
        load_factor = avg_consumption / peak_consumption if peak_consumption > 0 else 0
        
        # Consistency score (lower variance = higher efficiency)
        cv = consumption.std() / avg_consumption if avg_consumption > 0 else 0
        consistency_score = max(0, 100 - (cv * 100))
        
        # Peak demand management score
        peak_hours = [17, 18, 19, 20]  # Typical peak hours
        if hasattr(df, 'index') and hasattr(df.index, 'hour'):
            peak_consumption_avg = consumption[df.index.hour.isin(peak_hours)].mean()
            off_peak_avg = consumption[~df.index.hour.isin(peak_hours)].mean()
            peak_management_score = max(0, 100 - ((peak_consumption_avg / off_peak_avg - 1) * 50))
        else:
            peak_management_score = 50  # Default score
        
        # Overall efficiency score
        efficiency_score = (
            load_factor * 30 +
            consistency_score * 0.4 +
            peak_management_score * 0.3
        )
        
        # Building type benchmarking
        benchmark = self._get_efficiency_benchmark(self.building_type)
        performance_vs_benchmark = (efficiency_score / benchmark) * 100 if benchmark > 0 else 100
        
        return {
            "analysis_type": "efficiency_scoring",
            "efficiency_metrics": {
                "overall_efficiency_score": round(efficiency_score, 2),
                "load_factor": round(load_factor, 3),
                "consistency_score": round(consistency_score, 2),
                "peak_management_score": round(peak_management_score, 2),
                "coefficient_of_variation": round(cv, 3)
            },
            "benchmarking": {
                "building_type": self.building_type,
                "benchmark_score": benchmark,
                "performance_vs_benchmark": round(performance_vs_benchmark, 2),
                "rating": self._get_efficiency_rating(efficiency_score)
            },
            "recommendations": self._generate_efficiency_recommendations(efficiency_score, load_factor, consistency_score)
        }
    
    def _pattern_recognition(self, df: pd.DataFrame) -> Dict:
        """Recognize patterns in energy consumption"""
        consumption_col = self._get_consumption_column(df)
        if consumption_col is None:
            return {"error": "No consumption data found"}
        
        consumption = df[consumption_col]
        patterns = {}
        
        # Trend analysis
        if len(consumption) > 1:
            trend_slope = np.polyfit(range(len(consumption)), consumption, 1)[0]
            patterns["trend"] = {
                "direction": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
                "slope": float(trend_slope),
                "strength": "strong" if abs(trend_slope) > consumption.std() * 0.1 else "weak"
            }
        
        # Cyclical patterns (if timestamp data available)
        if hasattr(df, 'index') and hasattr(df.index, 'hour'):
            # Daily cycles
            hourly_std = consumption.groupby(df.index.hour).std().mean()
            daily_variation = consumption.groupby(df.index.hour).mean().std()
            
            patterns["daily_cycle"] = {
                "variation_strength": float(daily_variation),
                "consistency": float(hourly_std),
                "cycle_detected": daily_variation > consumption.std() * 0.5
            }
            
            # Weekly cycles
            if hasattr(df.index, 'dayofweek'):
                weekly_variation = consumption.groupby(df.index.dayofweek).mean().std()
                patterns["weekly_cycle"] = {
                    "variation_strength": float(weekly_variation),
                    "cycle_detected": weekly_variation > consumption.std() * 0.3
                }
        
        # Consumption level classification
        quartiles = consumption.quantile([0.25, 0.5, 0.75])
        patterns["consumption_levels"] = {
            "low_threshold": float(quartiles[0.25]),
            "medium_threshold": float(quartiles[0.5]),
            "high_threshold": float(quartiles[0.75]),
            "distribution": {
                "low_consumption_hours": int((consumption <= quartiles[0.25]).sum()),
                "medium_consumption_hours": int(((consumption > quartiles[0.25]) & (consumption <= quartiles[0.75])).sum()),
                "high_consumption_hours": int((consumption > quartiles[0.75]).sum())
            }
        }
        
        return {
            "analysis_type": "pattern_recognition",
            "identified_patterns": patterns,
            "pattern_insights": self._generate_pattern_insights(patterns),
            "recommendations": self._generate_pattern_recommendations(patterns)
        }
    
    def _comprehensive_analysis(self, df: pd.DataFrame) -> Dict:
        """Perform comprehensive energy analysis"""
        consumption_analysis = self._consumption_analysis(df)
        anomaly_analysis = self._anomaly_detection(df)
        efficiency_analysis = self._efficiency_scoring(df)
        pattern_analysis = self._pattern_recognition(df)
        
        return {
            "analysis_type": "comprehensive_analysis",
            "consumption_analysis": consumption_analysis,
            "anomaly_analysis": anomaly_analysis,
            "efficiency_analysis": efficiency_analysis,
            "pattern_analysis": pattern_analysis,
            "executive_summary": self._generate_executive_summary(
                consumption_analysis, anomaly_analysis, efficiency_analysis, pattern_analysis
            )
        }
    
    def _get_consumption_column(self, df: pd.DataFrame) -> str:
        """Find the consumption column in the dataframe"""
        possible_names = ['consumption', 'energy_consumption', 'kwh', 'power', 'energy', 'load']
        for col in df.columns:
            if any(name in col.lower() for name in possible_names):
                return col
        # Return first numeric column if no match
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return numeric_cols[0] if len(numeric_cols) > 0 else None
    
    def _simple_forecast(self, data: pd.Series, horizon: int) -> Dict:
        """Simple forecasting using moving average"""
        if len(data) < 3:
            return {"error": "Insufficient data for forecasting"}
        
        # Use last 7 days or available data for moving average
        window = min(7 * 24, len(data))  # 7 days in hours
        ma = data.rolling(window=window).mean().iloc[-1]
        
        # Simple trend adjustment
        trend = (data.iloc[-1] - data.iloc[-horizon if len(data) > horizon else 0]) / horizon
        
        forecast_values = []
        for i in range(horizon):
            forecast_val = ma + (trend * i)
            forecast_values.append(max(0, float(forecast_val)))  # Ensure non-negative
        
        return {
            "forecast_values": forecast_values,
            "forecast_method": "Moving Average with Trend",
            "horizon_hours": horizon,
            "base_value": float(ma),
            "trend_adjustment": float(trend)
        }
    
    def _get_building_insights(self, stats: Dict, building_type: str) -> Dict:
        """Generate building-specific insights"""
        benchmarks = {
            "office": {"avg_kwh_sqft": 15, "peak_ratio": 1.4},
            "residential": {"avg_kwh_sqft": 12, "peak_ratio": 1.6},
            "industrial": {"avg_kwh_sqft": 25, "peak_ratio": 1.2},
            "retail": {"avg_kwh_sqft": 18, "peak_ratio": 1.5},
            "hospital": {"avg_kwh_sqft": 30, "peak_ratio": 1.3}
        }
        
        benchmark = benchmarks.get(building_type, benchmarks["office"])
        peak_ratio = stats["peak_consumption"] / stats["average_consumption"] if stats["average_consumption"] > 0 else 0
        
        return {
            "building_type": building_type,
            "peak_to_average_ratio": round(peak_ratio, 2),
            "benchmark_peak_ratio": benchmark["peak_ratio"],
            "peak_ratio_performance": "Good" if peak_ratio <= benchmark["peak_ratio"] else "Needs Improvement",
            "building_specific_notes": self._get_building_notes(building_type, peak_ratio)
        }
    
    def _get_building_notes(self, building_type: str, peak_ratio: float) -> str:
        """Get building-specific performance notes"""
        notes = {
            "office": "Consider load shifting during peak hours (9-17h)",
            "residential": "Monitor evening peak usage (17-21h)",
            "industrial": "Optimize equipment scheduling for consistent load",
            "retail": "Balance lighting and HVAC during operating hours",
            "hospital": "Critical systems must maintain 24/7 efficiency"
        }
        
        base_note = notes.get(building_type, "Monitor energy patterns")
        if peak_ratio > 2.0:
            return f"{base_note}. HIGH PEAK RATIO DETECTED - Review equipment cycling."
        elif peak_ratio < 1.2:
            return f"{base_note}. Excellent load management detected."
        else:
            return base_note
    
    def _get_efficiency_benchmark(self, building_type: str) -> float:
        """Get efficiency benchmark for building type"""
        benchmarks = {
            "office": 75.0,
            "residential": 70.0,
            "industrial": 80.0,
            "retail": 72.0,
            "hospital": 85.0
        }
        return benchmarks.get(building_type, 75.0)
    
    def _get_efficiency_rating(self, score: float) -> str:
        """Convert efficiency score to rating"""
        if score >= 90:
            return "Excellent (A+)"
        elif score >= 80:
            return "Very Good (A)"
        elif score >= 70:
            return "Good (B)"
        elif score >= 60:
            return "Fair (C)"
        else:
            return "Poor (D)"
    
    def _calculate_anomaly_severity(self, anomaly_values: pd.Series, mean_val: float, std_val: float) -> List[str]:
        """Calculate severity levels for anomalies"""
        severity_levels = []
        for val in anomaly_values:
            z_score = abs((val - mean_val) / std_val)
            if z_score > 4:
                severity_levels.append("Critical")
            elif z_score > 3:
                severity_levels.append("High")
            elif z_score > 2.5:
                severity_levels.append("Medium")
            else:
                severity_levels.append("Low")
        return severity_levels
    
    def _generate_consumption_recommendations(self, stats: Dict, patterns: Dict) -> List[str]:
        """Generate consumption-based recommendations"""
        recommendations = []
        
        if patterns.get("peak_hour_consumption", 0) > stats["average_consumption"] * 1.5:
            recommendations.append("🔴 High peak consumption detected. Consider load shifting strategies.")
        
        if stats["consumption_variance"] > stats["average_consumption"] * 0.5:
            recommendations.append("🟡 High consumption variability. Implement demand smoothing measures.")
        
        recommendations.append("💡 Monitor consumption during identified peak hours for optimization opportunities.")
        
        return recommendations
    
    def _generate_anomaly_recommendations(self, anomaly_results: Dict) -> List[str]:
        """Generate anomaly-based recommendations"""
        recommendations = []
        
        if anomaly_results["anomaly_percentage"] > 10:
            recommendations.append("🚨 High anomaly rate detected. Investigate equipment performance.")
        elif anomaly_results["anomaly_percentage"] > 5:
            recommendations.append("⚠️ Moderate anomaly rate. Monitor system closely.")
        
        if anomaly_results["total_anomalies"] > 0:
            recommendations.append("🔍 Review anomaly timestamps for maintenance scheduling.")
        
        return recommendations
    
    def _generate_efficiency_recommendations(self, efficiency_score: float, load_factor: float, consistency_score: float) -> List[str]:
        """Generate efficiency-based recommendations"""
        recommendations = []
        
        if efficiency_score < 70:
            recommendations.append("🔴 Overall efficiency below optimal. Comprehensive energy audit recommended.")
        
        if load_factor < 0.6:
            recommendations.append("⚡ Low load factor. Consider base load optimization.")
        
        if consistency_score < 60:
            recommendations.append("📊 High consumption variability. Implement demand management strategies.")
        
        return recommendations
    
    def _generate_pattern_insights(self, patterns: Dict) -> List[str]:
        """Generate insights from pattern analysis"""
        insights = []
        
        if patterns.get("trend", {}).get("direction") == "increasing":
            insights.append("📈 Increasing consumption trend detected.")
        elif patterns.get("trend", {}).get("direction") == "decreasing":
            insights.append("📉 Decreasing consumption trend detected.")
        
        if patterns.get("daily_cycle", {}).get("cycle_detected"):
            insights.append("🔄 Strong daily consumption pattern identified.")
        
        if patterns.get("weekly_cycle", {}).get("cycle_detected"):
            insights.append("📅 Weekly consumption pattern detected.")
        
        return insights
    
    def _generate_pattern_recommendations(self, patterns: Dict) -> List[str]:
        """Generate pattern-based recommendations"""
        recommendations = []
        
        if patterns.get("daily_cycle", {}).get("cycle_detected"):
            recommendations.append("⏰ Leverage identified daily patterns for optimal scheduling.")
        
        if patterns.get("trend", {}).get("direction") == "increasing":
            recommendations.append("📊 Address increasing consumption trend through efficiency measures.")
        
        return recommendations
    
    def _generate_executive_summary(self, consumption_analysis: Dict, anomaly_analysis: Dict, 
                                   efficiency_analysis: Dict, pattern_analysis: Dict) -> Dict:
        """Generate executive summary of all analyses"""
        
        # Extract key metrics
        total_consumption = consumption_analysis.get("statistics", {}).get("total_consumption", 0)
        efficiency_score = efficiency_analysis.get("efficiency_metrics", {}).get("overall_efficiency_score", 0)
        anomaly_rate = anomaly_analysis.get("anomaly_results", {}).get("anomaly_percentage", 0)
        
        # Overall health score
        health_score = (efficiency_score * 0.6 + max(0, 100 - anomaly_rate * 10) * 0.4)
        
        return {
            "overall_health_score": round(health_score, 1),
            "key_metrics": {
                "total_consumption_kwh": round(total_consumption, 2),
                "efficiency_score": round(efficiency_score, 1),
                "anomaly_rate_percent": round(anomaly_rate, 2)
            },
            "status": self._get_overall_status(health_score),
            "priority_actions": self._get_priority_actions(efficiency_score, anomaly_rate),
            "next_review_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }
    
    def _get_overall_status(self, health_score: float) -> str:
        """Get overall system status"""
        if health_score >= 85:
            return "🟢 Excellent - System performing optimally"
        elif health_score >= 70:
            return "🟡 Good - Minor optimizations available"
        elif health_score >= 55:
            return "🟠 Fair - Attention required"
        else:
            return "🔴 Poor - Immediate action needed"
    
    def _get_priority_actions(self, efficiency_score: float, anomaly_rate: float) -> List[str]:
        """Get priority actions based on analysis"""
        actions = []
        
        if anomaly_rate > 10:
            actions.append("🚨 URGENT: Investigate high anomaly rate")
        
        if efficiency_score < 60:
            actions.append("🔧 Schedule comprehensive energy audit")
        
        if not actions:
            actions.append("✅ Continue monitoring current performance")
        
        return actions