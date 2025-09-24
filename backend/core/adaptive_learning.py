"""
Adaptive Learning System - Learning from interactions and optimizing performance
Intelligent adaptation and personalization for today's update
"""

import logging
import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import pickle

logger = logging.getLogger(__name__)

class LearningSignal(Enum):
    """Types of learning signals from user interactions"""
    POSITIVE_FEEDBACK = "positive_feedback"
    NEGATIVE_FEEDBACK = "negative_feedback"
    TASK_COMPLETION = "task_completion"
    TASK_ABANDONMENT = "task_abandonment"
    ERROR_CORRECTION = "error_correction"
    PREFERENCE_INDICATION = "preference_indication"
    USAGE_PATTERN = "usage_pattern"
    PERFORMANCE_METRIC = "performance_metric"

class AdaptationType(Enum):
    """Types of adaptations the system can make"""
    AGENT_SELECTION = "agent_selection"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    WORKFLOW_SUGGESTION = "workflow_suggestion"
    UI_PERSONALIZATION = "ui_personalization"
    RESPONSE_TUNING = "response_tuning"
    PROACTIVE_ASSISTANCE = "proactive_assistance"

@dataclass
class LearningEvent:
    """Individual learning event from user interaction"""
    id: str
    user_id: str
    signal_type: LearningSignal
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserProfile:
    """Adaptive user profile with learning history"""
    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    behavior_patterns: Dict[str, Any] = field(default_factory=dict)
    skill_level: Dict[str, float] = field(default_factory=dict)
    interaction_history: List[str] = field(default_factory=list)
    adaptation_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AdaptationRule:
    """Rule for system adaptation based on learning"""
    id: str
    name: str
    adaptation_type: AdaptationType
    trigger_conditions: Dict[str, Any]
    action_parameters: Dict[str, Any]
    confidence_threshold: float = 0.7
    priority: int = 1
    active: bool = True
    success_rate: float = 0.0
    usage_count: int = 0

class PatternRecognizer:
    """Recognizes patterns in user behavior and interactions"""
    
    def __init__(self):
        self.sequence_patterns = defaultdict(list)
        self.temporal_patterns = defaultdict(list)
        self.context_patterns = defaultdict(dict)
    
    async def analyze_interaction_sequence(self, user_id: str, events: List[LearningEvent]) -> Dict[str, Any]:
        """Analyze sequence of user interactions for patterns"""
        if len(events) < 2:
            return {}
        
        patterns = {
            "sequential_preferences": {},
            "common_workflows": [],
            "error_patterns": [],
            "efficiency_trends": {}
        }
        
        # Analyze sequential preferences
        for i in range(len(events) - 1):
            current = events[i]
            next_event = events[i + 1]
            
            sequence_key = f"{current.signal_type.value} -> {next_event.signal_type.value}"
            if sequence_key not in patterns["sequential_preferences"]:
                patterns["sequential_preferences"][sequence_key] = 0
            patterns["sequential_preferences"][sequence_key] += 1
        
        # Identify common workflows
        workflow_sequences = []
        current_workflow = []
        
        for event in events:
            if event.signal_type == LearningSignal.TASK_COMPLETION:
                if current_workflow:
                    workflow_sequences.append(current_workflow.copy())
                current_workflow = []
            else:
                current_workflow.append(event.context.get("action_type", "unknown"))
        
        # Find most common workflows
        workflow_counts = defaultdict(int)
        for workflow in workflow_sequences:
            workflow_key = " -> ".join(workflow)
            workflow_counts[workflow_key] += 1
        
        patterns["common_workflows"] = [
            {"workflow": workflow, "frequency": count}
            for workflow, count in sorted(workflow_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Analyze error patterns
        error_events = [e for e in events if e.signal_type in [LearningSignal.NEGATIVE_FEEDBACK, LearningSignal.ERROR_CORRECTION]]
        error_contexts = [e.context for e in error_events]
        
        if error_contexts:
            error_types = defaultdict(int)
            for context in error_contexts:
                error_type = context.get("error_type", "unknown")
                error_types[error_type] += 1
            
            patterns["error_patterns"] = [
                {"error_type": error_type, "frequency": count}
                for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)
            ]
        
        return patterns
    
    async def analyze_temporal_patterns(self, user_id: str, events: List[LearningEvent]) -> Dict[str, Any]:
        """Analyze temporal patterns in user behavior"""
        if not events:
            return {}
        
        patterns = {
            "active_hours": defaultdict(int),
            "session_durations": [],
            "productivity_trends": {},
            "seasonal_patterns": {}
        }
        
        # Analyze active hours
        for event in events:
            hour = event.timestamp.hour
            patterns["active_hours"][hour] += 1
        
        # Analyze session patterns
        sessions = self._group_events_into_sessions(events)
        
        for session in sessions:
            duration = (session[-1].timestamp - session[0].timestamp).total_seconds() / 60  # minutes
            patterns["session_durations"].append(duration)
        
        # Calculate productivity trends
        completion_events = [e for e in events if e.signal_type == LearningSignal.TASK_COMPLETION]
        if completion_events:
            # Group by day and calculate completion rate
            daily_completions = defaultdict(int)
            for event in completion_events:
                day_key = event.timestamp.date().isoformat()
                daily_completions[day_key] += 1
            
            patterns["productivity_trends"] = dict(daily_completions)
        
        return patterns
    
    def _group_events_into_sessions(self, events: List[LearningEvent], gap_threshold: int = 30) -> List[List[LearningEvent]]:
        """Group events into sessions based on time gaps"""
        if not events:
            return []
        
        sessions = []
        current_session = [events[0]]
        
        for i in range(1, len(events)):
            time_gap = (events[i].timestamp - events[i-1].timestamp).total_seconds() / 60  # minutes
            
            if time_gap <= gap_threshold:
                current_session.append(events[i])
            else:
                sessions.append(current_session)
                current_session = [events[i]]
        
        if current_session:
            sessions.append(current_session)
        
        return sessions

class PersonalizationEngine:
    """Engine for personalizing user experience based on learning"""
    
    def __init__(self):
        self.personalization_models = {}
        self.feature_weights = defaultdict(lambda: defaultdict(float))
    
    async def generate_agent_recommendations(self, user_profile: UserProfile, task_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized agent recommendations"""
        recommendations = []
        
        # Analyze user's historical agent preferences
        agent_preferences = user_profile.preferences.get("agent_preferences", {})
        
        # Consider task context
        task_type = task_context.get("type", "general")
        task_complexity = task_context.get("complexity", "medium")
        
        # Default agent scores
        agent_scores = {
            "document_agent": 0.5,
            "code_agent": 0.5,
            "web_agent": 0.5,
            "chat_agent": 0.5
        }
        
        # Adjust scores based on user preferences
        for agent, preference_score in agent_preferences.items():
            if agent in agent_scores:
                agent_scores[agent] = (agent_scores[agent] + preference_score) / 2
        
        # Adjust based on task type
        task_agent_affinity = {
            "analysis": {"document_agent": 0.8, "chat_agent": 0.6},
            "coding": {"code_agent": 0.9, "chat_agent": 0.4},
            "research": {"web_agent": 0.8, "document_agent": 0.6},
            "conversation": {"chat_agent": 0.9}
        }
        
        if task_type in task_agent_affinity:
            for agent, bonus in task_agent_affinity[task_type].items():
                if agent in agent_scores:
                    agent_scores[agent] += bonus * 0.3
        
        # Generate recommendations
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        
        for agent, score in sorted_agents:
            recommendations.append({
                "agent_id": agent,
                "agent_name": agent.replace("_", " ").title(),
                "recommendation_score": min(score, 1.0),
                "reasoning": f"Based on your preferences and task type: {task_type}"
            })
        
        return recommendations
    
    async def generate_workflow_suggestions(self, user_profile: UserProfile, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized workflow suggestions"""
        suggestions = []
        
        # Analyze user's common workflows
        common_workflows = user_profile.behavior_patterns.get("common_workflows", [])
        
        # Current task context
        current_task = current_context.get("task_type", "")
        
        # Generate suggestions based on patterns
        for workflow in common_workflows[:3]:  # Top 3 workflows
            workflow_steps = workflow.get("workflow", "").split(" -> ")
            frequency = workflow.get("frequency", 0)
            
            if len(workflow_steps) > 1:
                suggestions.append({
                    "workflow_name": f"Your Common {workflow_steps[0]} Workflow",
                    "steps": workflow_steps,
                    "confidence": min(frequency / 10.0, 1.0),  # Normalize frequency
                    "description": f"You've used this workflow {frequency} times",
                    "estimated_time": len(workflow_steps) * 2  # Rough estimate
                })
        
        # Add template suggestions based on task type
        template_suggestions = {
            "analysis": {
                "name": "Document Analysis Pipeline",
                "steps": ["Upload Document", "Extract Content", "Analyze", "Generate Summary"],
                "confidence": 0.8
            },
            "research": {
                "name": "Research Workflow",
                "steps": ["Web Search", "Document Search", "Synthesize Results", "Generate Report"],
                "confidence": 0.7
            }
        }
        
        if current_task in template_suggestions:
            template = template_suggestions[current_task]
            suggestions.append({
                "workflow_name": template["name"],
                "steps": template["steps"],
                "confidence": template["confidence"],
                "description": "Recommended template for this task type",
                "estimated_time": len(template["steps"]) * 3
            })
        
        return suggestions
    
    async def customize_ui_preferences(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Generate UI customization recommendations"""
        preferences = {
            "default_tab": "chat",
            "notification_frequency": "normal",
            "auto_save_interval": 30,
            "theme_preference": "light",
            "layout_density": "comfortable"
        }
        
        # Analyze user behavior patterns
        behavior = user_profile.behavior_patterns
        
        # Determine preferred starting tab
        tab_usage = behavior.get("tab_usage", {})
        if tab_usage:
            most_used_tab = max(tab_usage.items(), key=lambda x: x[1])[0]
            preferences["default_tab"] = most_used_tab
        
        # Adjust notification frequency based on activity level
        session_count = len(behavior.get("session_durations", []))
        if session_count > 20:  # Very active user
            preferences["notification_frequency"] = "minimal"
        elif session_count < 5:  # Less active user
            preferences["notification_frequency"] = "high"
        
        # Adjust auto-save based on session patterns
        avg_session_duration = np.mean(behavior.get("session_durations", [30]))
        if avg_session_duration > 60:  # Long sessions
            preferences["auto_save_interval"] = 60
        elif avg_session_duration < 15:  # Short sessions
            preferences["auto_save_interval"] = 15
        
        return preferences

class AdaptiveLearningSystem:
    """Main adaptive learning system"""
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.learning_events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.adaptation_rules: Dict[str, AdaptationRule] = {}
        self.pattern_recognizer = PatternRecognizer()
        self.personalization_engine = PersonalizationEngine()
        
        # Performance tracking
        self.total_adaptations = 0
        self.successful_adaptations = 0
        self.last_learning_update = datetime.utcnow()
        
        # Initialize default adaptation rules
        self._initialize_default_rules()
    
    async def record_learning_event(self, event: LearningEvent):
        """Record a learning event for analysis"""
        self.learning_events[event.user_id].append(event)
        
        # Update user profile
        if event.user_id not in self.user_profiles:
            self.user_profiles[event.user_id] = UserProfile(user_id=event.user_id)
        
        profile = self.user_profiles[event.user_id]
        profile.interaction_history.append(event.id)
        profile.updated_at = datetime.utcnow()
        
        # Trigger learning analysis
        await self._analyze_and_adapt(event.user_id, event)
        
        logger.debug(f"Recorded learning event: {event.signal_type.value} for user {event.user_id}")
    
    async def get_user_recommendations(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get personalized recommendations for a user"""
        if user_id not in self.user_profiles:
            return self._get_default_recommendations(context)
        
        profile = self.user_profiles[user_id]
        
        recommendations = {
            "agents": await self.personalization_engine.generate_agent_recommendations(profile, context),
            "workflows": await self.personalization_engine.generate_workflow_suggestions(profile, context),
            "ui_preferences": await self.personalization_engine.customize_ui_preferences(profile),
            "proactive_suggestions": await self._generate_proactive_suggestions(profile, context)
        }
        
        return recommendations
    
    async def adapt_agent_selection(self, user_id: str, task_context: Dict[str, Any]) -> Optional[str]:
        """Adaptively select the best agent for a user's task"""
        if user_id not in self.user_profiles:
            return None
        
        recommendations = await self.get_user_recommendations(user_id, task_context)
        agent_recommendations = recommendations.get("agents", [])
        
        if agent_recommendations:
            best_agent = agent_recommendations[0]
            if best_agent["recommendation_score"] > 0.7:
                return best_agent["agent_id"]
        
        return None
    
    async def learn_from_feedback(self, user_id: str, feedback_type: str, context: Dict[str, Any]):
        """Learn from explicit user feedback"""
        signal_type = LearningSignal.POSITIVE_FEEDBACK if feedback_type == "positive" else LearningSignal.NEGATIVE_FEEDBACK
        
        event = LearningEvent(
            id=f"feedback_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            signal_type=signal_type,
            context=context,
            outcome={"feedback_type": feedback_type}
        )
        
        await self.record_learning_event(event)
    
    async def _analyze_and_adapt(self, user_id: str, latest_event: LearningEvent):
        """Analyze user patterns and trigger adaptations"""
        events = list(self.learning_events[user_id])
        
        if len(events) < 5:  # Need minimum events for analysis
            return
        
        # Analyze patterns
        sequence_patterns = await self.pattern_recognizer.analyze_interaction_sequence(user_id, events)
        temporal_patterns = await self.pattern_recognizer.analyze_temporal_patterns(user_id, events)
        
        # Update user profile with patterns
        profile = self.user_profiles[user_id]
        profile.behavior_patterns.update({
            "sequence_patterns": sequence_patterns,
            "temporal_patterns": temporal_patterns
        })
        
        # Update preferences based on feedback
        if latest_event.signal_type in [LearningSignal.POSITIVE_FEEDBACK, LearningSignal.NEGATIVE_FEEDBACK]:
            await self._update_preferences(profile, latest_event)
        
        # Trigger adaptation rules
        await self._apply_adaptation_rules(user_id, latest_event)
        
        self.last_learning_update = datetime.utcnow()
    
    async def _update_preferences(self, profile: UserProfile, event: LearningEvent):
        """Update user preferences based on feedback"""
        context = event.context
        is_positive = event.signal_type == LearningSignal.POSITIVE_FEEDBACK
        
        # Update agent preferences
        if "agent_id" in context:
            agent_id = context["agent_id"]
            if "agent_preferences" not in profile.preferences:
                profile.preferences["agent_preferences"] = {}
            
            current_pref = profile.preferences["agent_preferences"].get(agent_id, 0.5)
            adjustment = 0.1 if is_positive else -0.1
            new_pref = max(0.0, min(1.0, current_pref + adjustment))
            profile.preferences["agent_preferences"][agent_id] = new_pref
        
        # Update task type preferences
        if "task_type" in context:
            task_type = context["task_type"]
            if "task_preferences" not in profile.preferences:
                profile.preferences["task_preferences"] = {}
            
            current_pref = profile.preferences["task_preferences"].get(task_type, 0.5)
            adjustment = 0.05 if is_positive else -0.05
            new_pref = max(0.0, min(1.0, current_pref + adjustment))
            profile.preferences["task_preferences"][task_type] = new_pref
    
    async def _apply_adaptation_rules(self, user_id: str, event: LearningEvent):
        """Apply adaptation rules based on events"""
        for rule in self.adaptation_rules.values():
            if not rule.active:
                continue
            
            # Check if rule conditions are met
            if await self._check_rule_conditions(rule, user_id, event):
                await self._execute_adaptation(rule, user_id, event)
                rule.usage_count += 1
    
    async def _check_rule_conditions(self, rule: AdaptationRule, user_id: str, event: LearningEvent) -> bool:
        """Check if adaptation rule conditions are met"""
        conditions = rule.trigger_conditions
        
        # Check event type condition
        if "event_types" in conditions:
            if event.signal_type.value not in conditions["event_types"]:
                return False
        
        # Check frequency condition
        if "min_frequency" in conditions:
            event_count = len([e for e in self.learning_events[user_id] 
                             if e.signal_type == event.signal_type])
            if event_count < conditions["min_frequency"]:
                return False
        
        # Check context conditions
        if "context_requirements" in conditions:
            for key, value in conditions["context_requirements"].items():
                if event.context.get(key) != value:
                    return False
        
        return True
    
    async def _execute_adaptation(self, rule: AdaptationRule, user_id: str, event: LearningEvent):
        """Execute an adaptation based on a rule"""
        try:
            if rule.adaptation_type == AdaptationType.AGENT_SELECTION:
                # Adaptive agent selection logic
                pass
            elif rule.adaptation_type == AdaptationType.WORKFLOW_SUGGESTION:
                # Workflow suggestion logic
                pass
            elif rule.adaptation_type == AdaptationType.UI_PERSONALIZATION:
                # UI personalization logic
                pass
            
            self.total_adaptations += 1
            self.successful_adaptations += 1
            rule.success_rate = self.successful_adaptations / self.total_adaptations
            
        except Exception as e:
            logger.error(f"Failed to execute adaptation: {str(e)}")
            self.total_adaptations += 1
    
    async def _generate_proactive_suggestions(self, profile: UserProfile, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate proactive suggestions based on user patterns"""
        suggestions = []
        
        # Analyze time patterns for suggestions
        temporal_patterns = profile.behavior_patterns.get("temporal_patterns", {})
        current_hour = datetime.utcnow().hour
        
        # Check if user is typically active at this time
        active_hours = temporal_patterns.get("active_hours", {})
        if str(current_hour) in active_hours and active_hours[str(current_hour)] > 3:
            suggestions.append({
                "type": "time_based",
                "title": "You're usually productive now",
                "description": "Based on your patterns, this is a good time for focused work",
                "confidence": 0.7
            })
        
        # Suggest based on incomplete workflows
        common_workflows = profile.behavior_patterns.get("common_workflows", [])
        if common_workflows:
            suggestions.append({
                "type": "workflow_completion",
                "title": "Continue your common workflow",
                "description": f"You often follow this pattern: {common_workflows[0].get('workflow', '')}",
                "confidence": 0.6
            })
        
        return suggestions
    
    def _initialize_default_rules(self):
        """Initialize default adaptation rules"""
        # Rule for frequent negative feedback
        self.adaptation_rules["reduce_agent_recommendation"] = AdaptationRule(
            id="reduce_agent_recommendation",
            name="Reduce Agent Recommendation on Negative Feedback",
            adaptation_type=AdaptationType.AGENT_SELECTION,
            trigger_conditions={
                "event_types": ["negative_feedback"],
                "min_frequency": 3,
                "context_requirements": {}
            },
            action_parameters={"adjustment": -0.2},
            confidence_threshold=0.6
        )
        
        # Rule for successful task completion patterns
        self.adaptation_rules["boost_successful_workflow"] = AdaptationRule(
            id="boost_successful_workflow",
            name="Boost Successful Workflow Patterns",
            adaptation_type=AdaptationType.WORKFLOW_SUGGESTION,
            trigger_conditions={
                "event_types": ["task_completion"],
                "min_frequency": 2
            },
            action_parameters={"boost_factor": 0.2},
            confidence_threshold=0.7
        )
    
    def _get_default_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get default recommendations for new users"""
        return {
            "agents": [
                {"agent_id": "chat_agent", "agent_name": "Chat Agent", "recommendation_score": 0.8, "reasoning": "Good for general interactions"},
                {"agent_id": "document_agent", "agent_name": "Document Agent", "recommendation_score": 0.7, "reasoning": "Useful for document tasks"},
            ],
            "workflows": [
                {"workflow_name": "Quick Start", "steps": ["Upload", "Process", "Review"], "confidence": 0.5, "description": "Basic workflow template"}
            ],
            "ui_preferences": {
                "default_tab": "chat",
                "notification_frequency": "normal",
                "auto_save_interval": 30
            },
            "proactive_suggestions": []
        }
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        total_users = len(self.user_profiles)
        total_events = sum(len(events) for events in self.learning_events.values())
        
        return {
            "total_users": total_users,
            "total_learning_events": total_events,
            "total_adaptations": self.total_adaptations,
            "successful_adaptations": self.successful_adaptations,
            "adaptation_success_rate": (self.successful_adaptations / max(self.total_adaptations, 1)) * 100,
            "active_adaptation_rules": len([r for r in self.adaptation_rules.values() if r.active]),
            "last_learning_update": self.last_learning_update.isoformat(),
            "events_by_type": {
                signal_type.value: sum(
                    1 for events in self.learning_events.values() 
                    for event in events 
                    if event.signal_type == signal_type
                )
                for signal_type in LearningSignal
            }
        }
    
    async def export_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Export user profile for analysis"""
        if user_id not in self.user_profiles:
            return None
        
        profile = self.user_profiles[user_id]
        events = list(self.learning_events[user_id])
        
        return {
            "user_id": profile.user_id,
            "preferences": profile.preferences,
            "behavior_patterns": profile.behavior_patterns,
            "skill_level": profile.skill_level,
            "total_interactions": len(events),
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
            "recent_events": [
                {
                    "signal_type": event.signal_type.value,
                    "timestamp": event.timestamp.isoformat(),
                    "context": event.context
                }
                for event in events[-10:]  # Last 10 events
            ]
        }
    
    async def cleanup(self):
        """Cleanup adaptive learning resources"""
        logger.info("Adaptive Learning System cleanup completed")

# Global adaptive learning system instance
adaptive_learning = AdaptiveLearningSystem() 