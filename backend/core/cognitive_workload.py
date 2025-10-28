"""
Cognitive Workload Management System
Optimal human-AI collaboration through cognitive science
Revolutionary human-AI interaction for today's big update
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import math
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class CognitiveLoadType(Enum):
    """Types of cognitive load"""
    INTRINSIC = "intrinsic"          # Task complexity
    EXTRINSIC = "extrinsic"          # Interface complexity
    GERMANE = "germane"              # Learning effort
    EMOTIONAL = "emotional"          # Stress and anxiety
    PHYSICAL = "physical"            # Fatigue and health

class WorkloadLevel(Enum):
    """Cognitive workload levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    OVERLOAD = "overload"

class AdaptationStrategy(Enum):
    """Cognitive workload adaptation strategies"""
    TASK_DECOMPOSITION = "task_decomposition"
    INTERFACE_SIMPLIFICATION = "interface_simplification"
    AUTOMATION_INCREASE = "automation_increase"
    BREAK_SUGGESTION = "break_suggestion"
    ASSISTANCE_ESCALATION = "assistance_escalation"
    CONTEXT_SWITCHING = "context_switching"

@dataclass
class CognitiveState:
    """Current cognitive state of a user"""
    user_id: str
    workload_level: WorkloadLevel
    load_components: Dict[CognitiveLoadType, float]
    attention_level: float
    stress_level: float
    fatigue_level: float
    confidence_level: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_duration: float = 0.0
    task_switches: int = 0
    error_rate: float = 0.0

@dataclass
class WorkloadProfile:
    """User's cognitive workload profile"""
    user_id: str
    baseline_capacity: float
    peak_capacity: float
    recovery_rate: float
    stress_sensitivity: float
    task_preferences: Dict[str, float]
    optimal_workload_range: Tuple[float, float]
    adaptation_preferences: List[AdaptationStrategy]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CognitiveTask:
    """Cognitive task representation"""
    id: str
    name: str
    complexity_score: float
    cognitive_requirements: Dict[CognitiveLoadType, float]
    estimated_duration: float
    priority: int
    dependencies: List[str] = field(default_factory=list)
    cognitive_benefits: List[str] = field(default_factory=list)

@dataclass
class AdaptationRecommendation:
    """Cognitive workload adaptation recommendation"""
    id: str
    user_id: str
    strategy: AdaptationStrategy
    confidence: float
    expected_benefit: float
    implementation_effort: float
    parameters: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

class CognitiveWorkloadManager:
    """Cognitive workload management system"""
    
    def __init__(self):
        self.user_states: Dict[str, CognitiveState] = {}
        self.user_profiles: Dict[str, WorkloadProfile] = {}
        self.cognitive_tasks: Dict[str, CognitiveTask] = {}
        self.adaptation_history: Dict[str, List[AdaptationRecommendation]] = defaultdict(list)
        
        # Cognitive load thresholds
        self.load_thresholds = {
            WorkloadLevel.VERY_LOW: 0.2,
            WorkloadLevel.LOW: 0.4,
            WorkloadLevel.MODERATE: 0.6,
            WorkloadLevel.HIGH: 0.8,
            WorkloadLevel.VERY_HIGH: 0.9,
            WorkloadLevel.OVERLOAD: 1.0
        }
        
        # Performance tracking
        self.total_adaptations = 0
        self.successful_adaptations = 0
        self.workload_reductions = 0
        
    async def assess_cognitive_state(self, user_id: str, context: Dict[str, Any]) -> CognitiveState:
        """Assess current cognitive state of a user"""
        try:
            # Get or create user profile
            if user_id not in self.user_profiles:
                await self._create_default_profile(user_id)
            
            profile = self.user_profiles[user_id]
            
            # Calculate cognitive load components
            load_components = await self._calculate_load_components(user_id, context)
            
            # Calculate overall workload level
            total_load = sum(load_components.values()) / len(load_components)
            workload_level = self._determine_workload_level(total_load)
            
            # Calculate other cognitive metrics
            attention_level = await self._calculate_attention_level(user_id, context)
            stress_level = await self._calculate_stress_level(user_id, context)
            fatigue_level = await self._calculate_fatigue_level(user_id, context)
            confidence_level = await self._calculate_confidence_level(user_id, context)
            
            # Create cognitive state
            state = CognitiveState(
                user_id=user_id,
                workload_level=workload_level,
                load_components=load_components,
                attention_level=attention_level,
                stress_level=stress_level,
                fatigue_level=fatigue_level,
                confidence_level=confidence_level,
                session_duration=context.get('session_duration', 0.0),
                task_switches=context.get('task_switches', 0),
                error_rate=context.get('error_rate', 0.0)
            )
            
            self.user_states[user_id] = state
            
            # Trigger adaptations if needed
            if total_load > profile.optimal_workload_range[1]:
                await self._trigger_adaptations(user_id, state)
            
            logger.debug(f"Cognitive state assessed for user {user_id}: {workload_level.value}")
            return state
            
        except Exception as e:
            logger.error(f"Cognitive state assessment failed: {str(e)}")
            raise
    
    async def _calculate_load_components(self, user_id: str, context: Dict[str, Any]) -> Dict[CognitiveLoadType, float]:
        """Calculate individual cognitive load components"""
        components = {}
        
        # Intrinsic load (task complexity)
        task_complexity = context.get('task_complexity', 0.5)
        components[CognitiveLoadType.INTRINSIC] = min(1.0, task_complexity)
        
        # Extrinsic load (interface complexity)
        interface_complexity = context.get('interface_complexity', 0.3)
        components[CognitiveLoadType.EXTRINSIC] = min(1.0, interface_complexity)
        
        # Germane load (learning effort)
        learning_effort = context.get('learning_effort', 0.4)
        components[CognitiveLoadType.GERMANE] = min(1.0, learning_effort)
        
        # Emotional load (stress and anxiety)
        emotional_stress = context.get('emotional_stress', 0.2)
        components[CognitiveLoadType.EMOTIONAL] = min(1.0, emotional_stress)
        
        # Physical load (fatigue)
        physical_fatigue = context.get('physical_fatigue', 0.1)
        components[CognitiveLoadType.PHYSICAL] = min(1.0, physical_fatigue)
        
        return components
    
    def _determine_workload_level(self, total_load: float) -> WorkloadLevel:
        """Determine workload level from total load"""
        if total_load <= self.load_thresholds[WorkloadLevel.VERY_LOW]:
            return WorkloadLevel.VERY_LOW
        elif total_load <= self.load_thresholds[WorkloadLevel.LOW]:
            return WorkloadLevel.LOW
        elif total_load <= self.load_thresholds[WorkloadLevel.MODERATE]:
            return WorkloadLevel.MODERATE
        elif total_load <= self.load_thresholds[WorkloadLevel.HIGH]:
            return WorkloadLevel.HIGH
        elif total_load <= self.load_thresholds[WorkloadLevel.VERY_HIGH]:
            return WorkloadLevel.VERY_HIGH
        else:
            return WorkloadLevel.OVERLOAD
    
    async def _calculate_attention_level(self, user_id: str, context: Dict[str, Any]) -> float:
        """Calculate user's attention level"""
        # Base attention from session duration
        session_duration = context.get('session_duration', 0.0)
        attention_decay = max(0.0, 1.0 - (session_duration / 3600))  # Decay over 1 hour
        
        # Task switches reduce attention
        task_switches = context.get('task_switches', 0)
        switch_penalty = min(0.3, task_switches * 0.05)
        
        # Error rate indicates attention issues
        error_rate = context.get('error_rate', 0.0)
        error_penalty = min(0.2, error_rate * 0.1)
        
        attention = max(0.0, attention_decay - switch_penalty - error_penalty)
        return min(1.0, attention)
    
    async def _calculate_stress_level(self, user_id: str, context: Dict[str, Any]) -> float:
        """Calculate user's stress level"""
        # Base stress from workload
        workload_stress = context.get('workload_stress', 0.3)
        
        # Time pressure increases stress
        time_pressure = context.get('time_pressure', 0.2)
        
        # Error rate increases stress
        error_rate = context.get('error_rate', 0.0)
        error_stress = min(0.3, error_rate * 0.2)
        
        stress = workload_stress + time_pressure + error_stress
        return min(1.0, stress)
    
    async def _calculate_fatigue_level(self, user_id: str, context: Dict[str, Any]) -> float:
        """Calculate user's fatigue level"""
        # Session duration increases fatigue
        session_duration = context.get('session_duration', 0.0)
        duration_fatigue = min(0.6, session_duration / 7200)  # Max fatigue after 2 hours
        
        # Task complexity increases fatigue
        task_complexity = context.get('task_complexity', 0.5)
        complexity_fatigue = task_complexity * 0.3
        
        # Physical fatigue from context
        physical_fatigue = context.get('physical_fatigue', 0.1)
        
        fatigue = duration_fatigue + complexity_fatigue + physical_fatigue
        return min(1.0, fatigue)
    
    async def _calculate_confidence_level(self, user_id: str, context: Dict[str, Any]) -> float:
        """Calculate user's confidence level"""
        # Base confidence
        base_confidence = 0.7
        
        # Error rate reduces confidence
        error_rate = context.get('error_rate', 0.0)
        error_penalty = min(0.4, error_rate * 0.3)
        
        # Success rate increases confidence
        success_rate = context.get('success_rate', 0.8)
        success_boost = success_rate * 0.2
        
        # Experience level affects confidence
        experience_level = context.get('experience_level', 0.5)
        experience_boost = experience_level * 0.1
        
        confidence = base_confidence - error_penalty + success_boost + experience_boost
        return max(0.0, min(1.0, confidence))
    
    async def _trigger_adaptations(self, user_id: str, state: CognitiveState):
        """Trigger cognitive workload adaptations"""
        try:
            profile = self.user_profiles[user_id]
            
            # Generate adaptation recommendations
            recommendations = await self._generate_adaptations(user_id, state, profile)
            
            # Apply adaptations
            for recommendation in recommendations:
                await self._apply_adaptation(recommendation)
                self.adaptation_history[user_id].append(recommendation)
            
            self.total_adaptations += len(recommendations)
            
        except Exception as e:
            logger.error(f"Adaptation triggering failed: {str(e)}")
    
    async def _generate_adaptations(self, user_id: str, state: CognitiveState, profile: WorkloadProfile) -> List[AdaptationRecommendation]:
        """Generate cognitive workload adaptation recommendations"""
        recommendations = []
        
        # Task decomposition for high intrinsic load
        if state.load_components[CognitiveLoadType.INTRINSIC] > 0.7:
            recommendation = AdaptationRecommendation(
                id=f"task_decomp_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                strategy=AdaptationStrategy.TASK_DECOMPOSITION,
                confidence=0.8,
                expected_benefit=0.3,
                implementation_effort=0.4,
                parameters={
                    'decomposition_level': 'high',
                    'max_subtasks': 5,
                    'complexity_reduction': 0.4
                }
            )
            recommendations.append(recommendation)
        
        # Interface simplification for high extrinsic load
        if state.load_components[CognitiveLoadType.EXTRINSIC] > 0.6:
            recommendation = AdaptationRecommendation(
                id=f"interface_simp_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                strategy=AdaptationStrategy.INTERFACE_SIMPLIFICATION,
                confidence=0.7,
                expected_benefit=0.2,
                implementation_effort=0.3,
                parameters={
                    'simplification_level': 'moderate',
                    'hide_advanced_features': True,
                    'reduce_visual_clutter': True
                }
            )
            recommendations.append(recommendation)
        
        # Automation increase for high overall load
        if state.workload_level in [WorkloadLevel.HIGH, WorkloadLevel.VERY_HIGH, WorkloadLevel.OVERLOAD]:
            recommendation = AdaptationRecommendation(
                id=f"automation_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                strategy=AdaptationStrategy.AUTOMATION_INCREASE,
                confidence=0.9,
                expected_benefit=0.4,
                implementation_effort=0.6,
                parameters={
                    'automation_level': 'high',
                    'auto_suggestions': True,
                    'auto_completion': True,
                    'auto_validation': True
                }
            )
            recommendations.append(recommendation)
        
        # Break suggestion for high fatigue
        if state.fatigue_level > 0.7 or state.session_duration > 7200:  # 2 hours
            recommendation = AdaptationRecommendation(
                id=f"break_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                strategy=AdaptationStrategy.BREAK_SUGGESTION,
                confidence=0.8,
                expected_benefit=0.5,
                implementation_effort=0.1,
                parameters={
                    'break_duration': 15,
                    'break_type': 'cognitive_rest',
                    'suggested_activities': ['walk', 'meditation', 'light_exercise']
                }
            )
            recommendations.append(recommendation)
        
        # Assistance escalation for overload
        if state.workload_level == WorkloadLevel.OVERLOAD:
            recommendation = AdaptationRecommendation(
                id=f"assistance_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                strategy=AdaptationStrategy.ASSISTANCE_ESCALATION,
                confidence=0.9,
                expected_benefit=0.6,
                implementation_effort=0.2,
                parameters={
                    'assistance_level': 'high',
                    'proactive_help': True,
                    'expert_recommendation': True,
                    'priority_support': True
                }
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _apply_adaptation(self, recommendation: AdaptationRecommendation):
        """Apply a cognitive workload adaptation"""
        try:
            # Log adaptation
            logger.info(f"Applying adaptation {recommendation.strategy.value} for user {recommendation.user_id}")
            
            # Simulate adaptation application
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Track success
            if recommendation.confidence > 0.5:
                self.successful_adaptations += 1
                self.workload_reductions += 1
            
        except Exception as e:
            logger.error(f"Adaptation application failed: {str(e)}")
    
    async def _create_default_profile(self, user_id: str):
        """Create default cognitive workload profile for a user"""
        profile = WorkloadProfile(
            user_id=user_id,
            baseline_capacity=0.6,
            peak_capacity=0.9,
            recovery_rate=0.1,
            stress_sensitivity=0.5,
            task_preferences={
                'complexity': 0.5,
                'automation': 0.6,
                'guidance': 0.7
            },
            optimal_workload_range=(0.3, 0.7),
            adaptation_preferences=[
                AdaptationStrategy.TASK_DECOMPOSITION,
                AdaptationStrategy.INTERFACE_SIMPLIFICATION,
                AdaptationStrategy.AUTOMATION_INCREASE
            ]
        )
        
        self.user_profiles[user_id] = profile
    
    async def optimize_task_sequence(self, user_id: str, tasks: List[CognitiveTask]) -> List[CognitiveTask]:
        """Optimize task sequence for cognitive workload"""
        try:
            if user_id not in self.user_profiles:
                await self._create_default_profile(user_id)
            
            profile = self.user_profiles[user_id]
            
            # Sort tasks by cognitive load and user preferences
            def task_score(task: CognitiveTask) -> float:
                # Lower cognitive load is better
                cognitive_score = 1.0 - sum(task.cognitive_requirements.values()) / len(task.cognitive_requirements)
                
                # Higher priority is better
                priority_score = task.priority / 10.0
                
                # User preferences
                preference_score = 0.5  # Default preference
                if task.name in profile.task_preferences:
                    preference_score = profile.task_preferences[task.name]
                
                return cognitive_score * 0.4 + priority_score * 0.3 + preference_score * 0.3
            
            # Sort tasks by score (higher is better)
            optimized_tasks = sorted(tasks, key=task_score, reverse=True)
            
            return optimized_tasks
            
        except Exception as e:
            logger.error(f"Task sequence optimization failed: {str(e)}")
            return tasks
    
    async def get_cognitive_insights(self, user_id: str) -> Dict[str, Any]:
        """Get cognitive workload insights for a user"""
        try:
            if user_id not in self.user_states:
                return {"error": "No cognitive state data available"}
            
            state = self.user_states[user_id]
            profile = self.user_profiles.get(user_id)
            
            insights = {
                'current_state': {
                    'workload_level': state.workload_level.value,
                    'attention_level': state.attention_level,
                    'stress_level': state.stress_level,
                    'fatigue_level': state.fatigue_level,
                    'confidence_level': state.confidence_level
                },
                'load_breakdown': {
                    load_type.value: load_value
                    for load_type, load_value in state.load_components.items()
                },
                'session_metrics': {
                    'duration': state.session_duration,
                    'task_switches': state.task_switches,
                    'error_rate': state.error_rate
                },
                'recommendations': []
            }
            
            # Generate insights based on current state
            if state.workload_level in [WorkloadLevel.HIGH, WorkloadLevel.VERY_HIGH, WorkloadLevel.OVERLOAD]:
                insights['recommendations'].append("Consider taking a break to reduce cognitive load")
            
            if state.fatigue_level > 0.7:
                insights['recommendations'].append("High fatigue detected - consider task simplification")
            
            if state.confidence_level < 0.4:
                insights['recommendations'].append("Low confidence detected - consider additional guidance")
            
            if state.attention_level < 0.5:
                insights['recommendations'].append("Attention level low - consider reducing distractions")
            
            return insights
            
        except Exception as e:
            logger.error(f"Cognitive insights generation failed: {str(e)}")
            return {"error": str(e)}
    
    async def get_workload_statistics(self) -> Dict[str, Any]:
        """Get cognitive workload management statistics"""
        total_users = len(self.user_states)
        total_adaptations = self.total_adaptations
        success_rate = (self.successful_adaptations / max(total_adaptations, 1)) * 100
        
        # Workload level distribution
        workload_distribution = {}
        for state in self.user_states.values():
            level = state.workload_level.value
            workload_distribution[level] = workload_distribution.get(level, 0) + 1
        
        return {
            'total_users': total_users,
            'total_adaptations': total_adaptations,
            'successful_adaptations': self.successful_adaptations,
            'success_rate': success_rate,
            'workload_reductions': self.workload_reductions,
            'workload_distribution': workload_distribution,
            'average_attention_level': np.mean([s.attention_level for s in self.user_states.values()]) if self.user_states else 0.0,
            'average_stress_level': np.mean([s.stress_level for s in self.user_states.values()]) if self.user_states else 0.0,
            'average_fatigue_level': np.mean([s.fatigue_level for s in self.user_states.values()]) if self.user_states else 0.0
        }
    
    async def cleanup(self):
        """Cleanup cognitive workload management resources"""
        self.user_states.clear()
        self.user_profiles.clear()
        self.cognitive_tasks.clear()
        self.adaptation_history.clear()
        logger.info("Cognitive Workload Manager cleanup completed")

# Global cognitive workload manager instance
cognitive_workload_manager = CognitiveWorkloadManager()

