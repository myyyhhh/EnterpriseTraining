from pydantic import BaseModel
from datetime import date
from typing import Optional, Literal

class UserAccountInfo(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

class UserBasedInfo(BaseModel):
    real_name: Optional[str] = None
    gender: Optional[Literal[0, 1, 2]] = 0  # 0=未知,1=男,2=女
    birthday: Optional[date] = None
    height: Optional[float] = None  # cm
    weight: Optional[float] = None  # kg

class UserHabitInfo(BaseModel):
    daily_water: Optional[float] = None  # L
    sleep_duration: Optional[float] = None  # 小时
    exercise_amount: Optional[str] = None
    vegetable_fruit_intake: Optional[str] = None
    protein_intake: Optional[str] = None
    meat_vegetable_ratio: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    cooking_method: Optional[str] = None

class UserPsychology(BaseModel):
    physical_reaction_index: Optional[str] = None
    sleep_cognition_bias: Optional[str] = None
    exercise_stress_value: Optional[str] = None
    emotion_stress_index: Optional[str] = None

class User(BaseModel):
    user_account_info: UserAccountInfo
    user_based_info: UserBasedInfo
    user_habit_info: UserHabitInfo
    user_psychology: UserPsychology