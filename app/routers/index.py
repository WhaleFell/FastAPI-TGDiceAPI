#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# index router 示例路由

from fastapi import APIRouter
from app.schemas import BaseResp

router = APIRouter()


@router.get("/", tags=["index"])
async def root() -> BaseResp[None]:
    return BaseResp(code=200, msg="TGDiceSQL Project base FastAPI")
