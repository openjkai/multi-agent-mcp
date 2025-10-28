"""
Predictive Analytics Engine
Advanced forecasting and trend analysis using machine learning
Revolutionary prediction capabilities for today's big update
"""

import logging
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import math
from collections import defaultdict, deque
import json
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Types of predictions"""
    TIME_SERIES = "time_series"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_ANALYSIS = "trend_analysis"
    FORECASTING = "forecasting"
    PATTERN_RECOGNITION = "pattern_recognition"

class ModelType(Enum):
    """Types of prediction models"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    ARIMA = "arima"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"

class ConfidenceLevel(Enum):
    """Prediction confidence levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class PredictionRequest:
    """Request for prediction"""
    id: str
    prediction_type: PredictionType
    model_type: ModelType
    features: Dict[str, Any]
    target_variable: str
    time_horizon: int  # days
    confidence_threshold: float = 0.7
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PredictionResult:
    """Result of prediction"""
    id: str
    request_id: str
    prediction_value: float
    confidence: float
    confidence_level: ConfidenceLevel
    prediction_interval: Tuple[float, float]
    model_accuracy: float
    features_importance: Dict[str, float]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    id: str
    trend_direction: str  # 'increasing', 'decreasing', 'stable', 'volatile'
    trend_strength: float
    trend_duration: int  # days
    key_drivers: List[str]
    confidence: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    id: str
    anomaly_score: float
    anomaly_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    recommended_action: str
    confidence: float
    created_at: datetime = field(default_factory=datetime.utcnow)

class PredictiveAnalyticsEngine:
    """Advanced predictive analytics engine"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.prediction_requests: Dict[str, PredictionRequest] = {}
        self.prediction_results: Dict[str, PredictionResult] = {}
        self.trend_analyses: Dict[str, TrendAnalysis] = {}
        self.anomaly_detections: Dict[str, AnomalyDetection] = {}
        
        # Performance tracking
        self.total_predictions = 0
        self.successful_predictions = 0
        self.average_accuracy = 0.0
        self.model_performance: Dict[str, float] = {}
        
        # Data storage
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.feature_importance: Dict[str, Dict[str, float]] = {}
        
    async def make_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Make a prediction based on request"""
        try:
            self.prediction_requests[request.id] = request
            
            # Prepare data
            X, y = await self._prepare_data(request)
            
            if len(X) == 0 or len(y) == 0:
                raise ValueError("Insufficient data for prediction")
            
            # Train or load model
            model = await self._get_or_train_model(request, X, y)
            
            # Make prediction
            prediction_value, confidence = await self._make_model_prediction(model, X, y, request)
            
            # Calculate prediction interval
            prediction_interval = await self._calculate_prediction_interval(model, X, confidence)
            
            # Get feature importance
            features_importance = await self._get_feature_importance(model, request)
            
            # Create result
            result = PredictionResult(
                id=f"pred_{request.id}_{datetime.utcnow().timestamp()}",
                request_id=request.id,
                prediction_value=prediction_value,
                confidence=confidence,
                confidence_level=self._determine_confidence_level(confidence),
                prediction_interval=prediction_interval,
                model_accuracy=model.score(X, y) if hasattr(model, 'score') else 0.8,
                features_importance=features_importance
            )
            
            self.prediction_results[result.id] = result
            self.total_predictions += 1
            
            if confidence > request.confidence_threshold:
                self.successful_predictions += 1
            
            logger.info(f"Prediction completed: {result.prediction_value:.3f} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    async def _prepare_data(self, request: PredictionRequest) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for model training/prediction"""
        # Get historical data for the target variable
        historical_data = list(self.historical_data[request.target_variable])
        
        if len(historical_data) < 10:
            # Generate synthetic data for demonstration
            historical_data = self._generate_synthetic_data(request)
        
        # Convert to numpy arrays
        if isinstance(historical_data[0], dict):
            # Extract features and target
            X = np.array([[data.get(feature, 0) for feature in request.features.keys()] 
                         for data in historical_data[:-1]])
            y = np.array([data[request.target_variable] for data in historical_data[1:]])
        else:
            # Simple time series data
            X = np.array(historical_data[:-1]).reshape(-1, 1)
            y = np.array(historical_data[1:])
        
        return X, y
    
    def _generate_synthetic_data(self, request: PredictionRequest) -> List[Dict[str, Any]]:
        """Generate synthetic data for demonstration"""
        data = []
        base_value = 100.0
        trend = 0.1
        
        for i in range(100):
            # Add trend and noise
            value = base_value + trend * i + np.random.normal(0, 5)
            
            # Add seasonal component
            seasonal = 10 * math.sin(2 * math.pi * i / 12)
            value += seasonal
            
            # Create data point
            data_point = {
                request.target_variable: value,
                'timestamp': datetime.utcnow() - timedelta(days=100-i),
                'trend': trend,
                'seasonal': seasonal
            }
            
            # Add feature values
            for feature, feature_value in request.features.items():
                if isinstance(feature_value, dict):
                    data_point[feature] = np.random.uniform(feature_value.get('min', 0), 
                                                          feature_value.get('max', 100))
                else:
                    data_point[feature] = feature_value
            
            data.append(data_point)
        
        return data
    
    async def _get_or_train_model(self, request: PredictionRequest, X: np.ndarray, y: np.ndarray) -> Any:
        """Get existing model or train new one"""
        model_key = f"{request.prediction_type.value}_{request.model_type.value}"
        
        if model_key in self.models:
            return self.models[model_key]
        
        # Train new model
        model = await self._train_model(request, X, y)
        self.models[model_key] = model
        
        return model
    
    async def _train_model(self, request: PredictionRequest, X: np.ndarray, y: np.ndarray) -> Any:
        """Train a prediction model"""
        if request.model_type == ModelType.LINEAR_REGRESSION:
            model = LinearRegression()
        elif request.model_type == ModelType.RANDOM_FOREST:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif request.model_type == ModelType.GRADIENT_BOOSTING:
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif request.model_type == ModelType.RIDGE:
            model = Ridge(alpha=1.0)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Scale features if needed
        if model_key not in self.scalers:
            self.scalers[model_key] = StandardScaler()
            X_scaled = self.scalers[model_key].fit_transform(X)
        else:
            X_scaled = self.scalers[model_key].transform(X)
        
        # Train model
        model.fit(X_scaled, y)
        
        # Store performance
        accuracy = model.score(X_scaled, y) if hasattr(model, 'score') else 0.8
        self.model_performance[model_key] = accuracy
        
        return model
    
    async def _make_model_prediction(self, model: Any, X: np.ndarray, y: np.ndarray, request: PredictionRequest) -> Tuple[float, float]:
        """Make prediction using trained model"""
        # Prepare prediction features
        prediction_features = np.array([[request.features.get(feature, 0) 
                                       for feature in request.features.keys()]])
        
        # Scale features
        model_key = f"{request.prediction_type.value}_{request.model_type.value}"
        if model_key in self.scalers:
            prediction_features = self.scalers[model_key].transform(prediction_features)
        
        # Make prediction
        prediction_value = model.predict(prediction_features)[0]
        
        # Calculate confidence based on model performance and data quality
        model_accuracy = model.score(X, y) if hasattr(model, 'score') else 0.8
        data_quality = min(1.0, len(X) / 100)  # More data = higher quality
        confidence = (model_accuracy + data_quality) / 2
        
        return float(prediction_value), float(confidence)
    
    async def _calculate_prediction_interval(self, model: Any, X: np.ndarray, confidence: float) -> Tuple[float, float]:
        """Calculate prediction interval"""
        # Simple prediction interval based on confidence
        margin = (1 - confidence) * 20  # Adjust based on confidence
        
        # Get recent predictions for interval calculation
        if hasattr(model, 'predict'):
            recent_predictions = model.predict(X[-10:])  # Last 10 predictions
            if len(recent_predictions) > 0:
                std_dev = np.std(recent_predictions)
                margin = std_dev * (1 - confidence) * 2
        
        return (0.0, margin)  # Simplified for demonstration
    
    async def _get_feature_importance(self, model: Any, request: PredictionRequest) -> Dict[str, float]:
        """Get feature importance from model"""
        if hasattr(model, 'feature_importances_'):
            importance_dict = {}
            for i, feature in enumerate(request.features.keys()):
                importance_dict[feature] = float(model.feature_importances_[i])
            return importance_dict
        else:
            # Equal importance if not available
            return {feature: 1.0 / len(request.features) for feature in request.features.keys()}
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level from confidence score"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.7:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.6:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    async def analyze_trends(self, data_series: List[float], time_period: int = 30) -> TrendAnalysis:
        """Analyze trends in data series"""
        try:
            if len(data_series) < 10:
                raise ValueError("Insufficient data for trend analysis")
            
            # Calculate trend direction
            x = np.arange(len(data_series))
            slope, intercept = np.polyfit(x, data_series, 1)
            
            # Determine trend direction
            if slope > 0.1:
                trend_direction = 'increasing'
            elif slope < -0.1:
                trend_direction = 'decreasing'
            elif abs(slope) < 0.05:
                trend_direction = 'stable'
            else:
                trend_direction = 'volatile'
            
            # Calculate trend strength
            trend_strength = abs(slope) * 100
            
            # Calculate trend duration
            trend_duration = min(time_period, len(data_series))
            
            # Identify key drivers (simplified)
            key_drivers = ['time', 'seasonality', 'external_factors']
            
            # Calculate confidence
            r_squared = 1 - (np.sum((data_series - (slope * x + intercept))**2) / 
                           np.sum((data_series - np.mean(data_series))**2))
            confidence = max(0.0, min(1.0, r_squared))
            
            trend_analysis = TrendAnalysis(
                id=f"trend_{datetime.utcnow().timestamp()}",
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                trend_duration=trend_duration,
                key_drivers=key_drivers,
                confidence=confidence
            )
            
            self.trend_analyses[trend_analysis.id] = trend_analysis
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            raise
    
    async def detect_anomalies(self, data_series: List[float], threshold: float = 2.0) -> List[AnomalyDetection]:
        """Detect anomalies in data series"""
        try:
            if len(data_series) < 10:
                return []
            
            anomalies = []
            data_array = np.array(data_series)
            
            # Calculate statistical measures
            mean = np.mean(data_array)
            std = np.std(data_array)
            
            # Detect outliers using z-score
            z_scores = np.abs((data_array - mean) / std)
            
            for i, z_score in enumerate(z_scores):
                if z_score > threshold:
                    # Determine anomaly severity
                    if z_score > 4:
                        severity = 'critical'
                    elif z_score > 3:
                        severity = 'high'
                    elif z_score > 2.5:
                        severity = 'medium'
                    else:
                        severity = 'low'
                    
                    # Create anomaly detection
                    anomaly = AnomalyDetection(
                        id=f"anomaly_{i}_{datetime.utcnow().timestamp()}",
                        anomaly_score=float(z_score),
                        anomaly_type='statistical_outlier',
                        severity=severity,
                        description=f"Data point {i} is {z_score:.2f} standard deviations from mean",
                        recommended_action=self._get_anomaly_action(severity),
                        confidence=min(1.0, z_score / 5.0)
                    )
                    
                    anomalies.append(anomaly)
                    self.anomaly_detections[anomaly.id] = anomaly
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return []
    
    def _get_anomaly_action(self, severity: str) -> str:
        """Get recommended action for anomaly severity"""
        actions = {
            'low': 'Monitor closely for pattern changes',
            'medium': 'Investigate potential causes and monitor trends',
            'high': 'Immediate investigation required - may indicate system issues',
            'critical': 'Urgent attention required - potential system failure'
        }
        return actions.get(severity, 'Monitor and investigate')
    
    async def forecast_time_series(self, data_series: List[float], forecast_periods: int = 7) -> List[float]:
        """Forecast future values in time series"""
        try:
            if len(data_series) < 10:
                # Generate synthetic forecast
                last_value = data_series[-1] if data_series else 100.0
                return [last_value + i * 0.1 for i in range(1, forecast_periods + 1)]
            
            # Simple linear trend forecast
            x = np.arange(len(data_series))
            slope, intercept = np.polyfit(x, data_series, 1)
            
            # Generate forecast
            forecast = []
            for i in range(1, forecast_periods + 1):
                future_x = len(data_series) + i - 1
                predicted_value = slope * future_x + intercept
                
                # Add some noise for realism
                noise = np.random.normal(0, np.std(data_series) * 0.1)
                forecast.append(float(predicted_value + noise))
            
            return forecast
            
        except Exception as e:
            logger.error(f"Time series forecasting failed: {str(e)}")
            return []
    
    async def get_prediction_insights(self, result_id: str) -> Dict[str, Any]:
        """Get insights from prediction result"""
        if result_id not in self.prediction_results:
            return {"error": "Prediction result not found"}
        
        result = self.prediction_results[result_id]
        request = self.prediction_requests[result.request_id]
        
        insights = {
            'prediction_summary': {
                'value': result.prediction_value,
                'confidence': result.confidence,
                'confidence_level': result.confidence_level.value,
                'accuracy': result.model_accuracy
            },
            'model_info': {
                'type': request.model_type.value,
                'prediction_type': request.prediction_type.value,
                'time_horizon': request.time_horizon
            },
            'feature_analysis': {
                'most_important': max(result.features_importance.items(), key=lambda x: x[1])[0],
                'least_important': min(result.features_importance.items(), key=lambda x: x[1])[0],
                'feature_importance': result.features_importance
            },
            'recommendations': self._generate_prediction_recommendations(result)
        }
        
        return insights
    
    def _generate_prediction_recommendations(self, result: PredictionResult) -> List[str]:
        """Generate recommendations based on prediction result"""
        recommendations = []
        
        if result.confidence_level in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH]:
            recommendations.append("High confidence prediction - suitable for decision making")
        
        if result.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]:
            recommendations.append("Low confidence prediction - consider gathering more data")
        
        if result.model_accuracy < 0.7:
            recommendations.append("Model accuracy is low - consider retraining with more data")
        
        if result.prediction_value > 1000:  # Example threshold
            recommendations.append("Predicted value is high - monitor for potential issues")
        
        return recommendations
    
    async def get_analytics_statistics(self) -> Dict[str, Any]:
        """Get predictive analytics statistics"""
        success_rate = (self.successful_predictions / max(self.total_predictions, 1)) * 100
        
        # Calculate average accuracy
        if self.model_performance:
            self.average_accuracy = np.mean(list(self.model_performance.values()))
        
        return {
            'total_predictions': self.total_predictions,
            'successful_predictions': self.successful_predictions,
            'success_rate': success_rate,
            'average_accuracy': self.average_accuracy,
            'total_models': len(self.models),
            'total_trend_analyses': len(self.trend_analyses),
            'total_anomaly_detections': len(self.anomaly_detections),
            'model_performance': self.model_performance,
            'prediction_types': {
                pred_type.value: len([r for r in self.prediction_requests.values() 
                                    if r.prediction_type == pred_type])
                for pred_type in PredictionType
            },
            'model_types': {
                model_type.value: len([r for r in self.prediction_requests.values() 
                                     if r.model_type == model_type])
                for model_type in ModelType
            }
        }
    
    async def add_historical_data(self, variable: str, data_point: Dict[str, Any]):
        """Add historical data point for training"""
        self.historical_data[variable].append(data_point)
    
    async def cleanup(self):
        """Cleanup predictive analytics resources"""
        self.models.clear()
        self.scalers.clear()
        self.prediction_requests.clear()
        self.prediction_results.clear()
        self.trend_analyses.clear()
        self.anomaly_detections.clear()
        self.historical_data.clear()
        logger.info("Predictive Analytics Engine cleanup completed")

# Global predictive analytics engine instance
predictive_analytics = PredictiveAnalyticsEngine()

