#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   Base.py
@Time    :   2023/10/12 10:40:43
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   schemas/Base.py  API 基模型
"""


# schemas/base.py
# API 基模型

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from pydantic import ConfigDict
from datetime import datetime

# Pydantic Generic Type 泛型
# reference:
# 1. https://blog.csdn.net/qq_45668004/article/details/113730684
# 2. https://docs.pydantic.dev/2.4/concepts/models/#generic-models
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseResp(BaseModel, Generic[T]):
    code: int = Field(default=200, description="响应状态码")
    msg: Optional[str] = Field(default=None, description="响应信息")

    # Pydantic V2 changes
    # https://docs.pydantic.dev/latest/migration/#changes-to-config
    # class Config:
    # no only trying to get the id value from a dict
    # also try to get it from an attribute,
    # id = data["id"] 或者 id = data.id

    # class Config:
    #     orm_mode = True

    content: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)


class RechargeWithdrawal(BaseModel):
    """充值提现信息"""

    time: datetime = Field(description="充提时间")
    tgid: str = Field(description="TG ID")
    tgname: str = Field(description="TG用户名", default="None")
    balance: float = Field(description="余额")
    recharge: float = Field(description="充值", default=0)
    withdrawal: float = Field(description="提现", default=0)

    @field_validator("recharge", "withdrawal", "balance", mode="after")
    @classmethod
    def double(cls, v: float) -> float:
        return round(v, 2)


class UserWinLose(BaseModel):
    """用户输赢"""

    time: datetime = Field(description="下注时间")
    tgid: str = Field(description="TG ID")
    tgname: str = Field(description="TG用户名", default="None")
    guess: str = Field(description="下注内容")
    order: str = Field(description="开奖期数")
    number: str = Field(description="开奖结果")
    result: str = Field(description="开奖结果")
    amount: float = Field(description="下注金额")
    win_amount: float = Field(description="输赢")

    @field_validator("amount", "win_amount", mode="after")
    @classmethod
    def double(cls, v: float) -> float:
        return round(v, 2)
