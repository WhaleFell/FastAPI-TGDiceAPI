#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TGDiceNode main Crud Require:
"""
实现以下 TGDice 的 Crud

用户充提:
时间,uid,用户名,流水(余额),充值,提现

用户输赢:
时间,uid,用户名,下注内容,期数,开奖数字,开奖结果,下注金额

"""

from fastapi import APIRouter, Depends
from app.schemas.Base import BaseResp, RechargeWithdrawal, UserWinLose
from app.database.connect import get_session, AsyncSession
from typing import List
from typing_extensions import Annotated
from sqlalchemy import text
from datetime import datetime
from app.utils import logger

router = APIRouter()

SQL = {
    "get_pay_withdrawal": """
SELECT w.telegramid, w.name, w.way, w.amount, w.applytime
FROM withdrawal w
WHERE w.telegramid = '{telegramid}'
UNION
SELECT p.telegramid, p.name, p.way, p.amount, p.applytime
FROM pay p
WHERE p.telegramid = '{telegramid}';
""",
    "get_balance": """
SELECT COALESCE(p.amount_sum, 0) - COALESCE(b.amount_sum, 0) - COALESCE(w.amount_sum, 0) AS balance
FROM (
  SELECT SUM(amount) AS amount_sum
  FROM pay
  WHERE telegramid = '{telegramid}'
		AND changetime <= '{deadline}'
) p
LEFT JOIN (
  SELECT SUM(amount - amountreturn - result) AS amount_sum
  FROM bet
  WHERE telegramid = '{telegramid}'
    AND time <= '{deadline}'
) b ON 1=1
LEFT JOIN (
  SELECT SUM(amount) AS amount_sum
  FROM withdrawal
  WHERE telegramid = '{telegramid}'
	AND changetime <= '{deadline}'
) w ON 1=1;
""",
    "get_bet": """
SELECT b.time, b.telegramid, u.name, b.guess, b.resultid,
       CONCAT(r.one, ',', r.two, ',', r.three) AS winning_numbers,
       CONCAT(
           CASE WHEN r.big = 1 THEN '大 ' ELSE '' END,
           CASE WHEN r.small = 1 THEN '小 ' ELSE '' END,
           CASE WHEN r.odd = 1 THEN '单 ' ELSE '' END,
           CASE WHEN r.even = 1 THEN '双 ' ELSE '' END,
           CASE WHEN r.baozi = 1 THEN '豹子 ' ELSE '' END,
           CASE WHEN r.shunzi = 1 THEN '顺子 ' ELSE '' END,
           CASE WHEN r.duizi = 1 THEN '对子 ' ELSE '' END
       ) AS result,
       b.amount
FROM bet b
JOIN result r ON b.resultid = r.id
JOIN users u ON b.telegramid = u.telegramid
WHERE b.telegramid = '{telegramid}';
""",
}


@router.get("/get_recharge_withdrawal/{tgid}")
async def get_recharge_withdrawal(
    tgid: str, db: Annotated[AsyncSession, Depends(get_session)]
) -> BaseResp[List[RechargeWithdrawal]]:
    result = await db.execute(
        text(SQL["get_pay_withdrawal"].format(telegramid=tgid))
    )

    datas = result.fetchall()
    lst: List[RechargeWithdrawal] = []
    for telegramid, name, way, amount, time in datas:
        recharge = 0
        withdrawal = 0
        time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        if "上分" in way:
            recharge = amount
        elif "下分" in way:
            withdrawal = amount
        res = await db.execute(
            text(SQL["get_balance"].format(telegramid=tgid, deadline=time))
        )
        balance = res.fetchall()[0][0]
        lst.append(
            RechargeWithdrawal(
                time=time,
                tgid=tgid,
                tgname=name,
                balance=balance + recharge - withdrawal,
                recharge=recharge,
                withdrawal=withdrawal,
            )
        )

    return BaseResp(msg="获取成功!", content=lst)


@router.get("/get_win_lose/{tgid}")
async def get_win_lose(
    tgid: str, db: Annotated[AsyncSession, Depends(get_session)]
) -> BaseResp[List[UserWinLose]]:
    result = await db.execute(text(SQL["get_bet"].format(telegramid=tgid)))
    datas = result.fetchall()

    lst: List[UserWinLose] = []
    for time, telegramid, tgname, guess, order, number, res, amount in datas:
        lst.append(
            UserWinLose(
                time=datetime.strptime(time, "%Y-%m-%d %H:%M:%S"),
                tgid=telegramid,
                tgname=tgname,
                guess=guess,
                order=order,
                number=number,
                result=res,
                amount=amount,
            )
        )

    return BaseResp(msg="获取成功!", content=lst)
