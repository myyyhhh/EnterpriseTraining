from pydantic import BaseModel
from datetime import date
from typing import Optional, Literal

class UserAccountInfo(BaseModel):
    """用户账户信息模型"""
    username: Optional[str] = None
    password: Optional[str] = None

class UserBasedInfo(BaseModel):
    """用户基本信息模型"""
    real_name: Optional[str] = None
    gender: Optional[Literal[0, 1, 2]] = None  # 0=未知, 1=男, 2=女
    birthday: Optional[date] = None  # 格式：YYYY-MM-DD
    height: Optional[float] = None  # 单位：cm
    weight: Optional[float] = None  # 单位：kg

class UserHabitInfo(BaseModel):
    """用户习惯信息模型"""
    daily_water: Optional[float] = None  # 单位：L
    sleep_duration: Optional[float] = None  # 单位：小时
    exercise_amount: Optional[str] = None
    vegetable_fruit_intake: Optional[str] = None
    protein_intake: Optional[str] = None
    meat_vegetable_ratio: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    cooking_method: Optional[str] = None

class UserPsychology(BaseModel):
    """用户心理信息模型"""
    physical_reaction_index: Optional[str] = None  # 躯体反应
    sleep_cognition_bias: Optional[str] = None  # 睡眠认知偏差
    exercise_stress_value: Optional[str] = None  # 运动压力值
    emotion_stress_index: Optional[str] = None  # 情绪压力指标

class User(BaseModel):
    """用户总模型"""
    user_account_info: UserAccountInfo
    user_based_info: UserBasedInfo
    user_habit_info: UserHabitInfo
    user_psychology: UserPsychology