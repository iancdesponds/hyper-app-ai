from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class PhysicalProfile(BaseModel):
    age: int
    gender: str
    weight: float
    height: float
    experience_level: str
    injuries: Optional[str]

class Logistics(BaseModel):
    days_per_week: int
    time_per_workout: str

class Objectives(BaseModel):
    primary_goal: str
    prioritized_muscle_groups: List[str]

class Adaptation(BaseModel):
    progress_history: Optional[Dict[str, List[Any]]]
    pre_workout_feedback: Optional[str]
    post_workout_feedback: Optional[str]

class AIRequest(BaseModel):
    physical_profile: PhysicalProfile
    logistics: Logistics
    objectives: Objectives
    adaptation: Adaptation