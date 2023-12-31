#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   main.py
@Time    :   2023/10/12 10:36:56
@Author  :   WhaleFall
@License :   (C)Copyright 2020-2023, WhaleFall
@Desc    :   fastapi main
"""


import uvicorn
from fastapi import FastAPI
import asyncio
from app.utils import logger
from contextlib import asynccontextmanager

from app.config import settings
from app.registers import (
    register_cors,
    register_exception,
    register_middleware,
    register_router,
)
import app.database


# Optimize Python Aysncio
# to fix: ValueError: too many file descriptors in select()
# reference: https://blog.csdn.net/qq_36759224/article/details/123084133
import selectors
import asyncio
import sys
from uvicorn import Config, Server

# Windows asynchronous optimize
# https://www.v2ex.com/t/653100
# https://stackoverflow.com/questions/47675410/python-asyncio-aiohttp-valueerror-too-many-file-descriptors-in-select-on-win
# https://github.com/tiangolo/fastapi/discussions/7651#discussioncomment-5143056
if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
else:
    selector = selectors.PollSelector()
    loop = asyncio.SelectorEventLoop(selector)
    asyncio.set_event_loop(loop)


# I.ni.tia.lize /[ɪˈnɪʃ(ə)lˌaɪz/ database 初始化数据库
# fastapi lifespan 生命周期 https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    # before app start 应用开始前执行
    logger.success("Before app start")
    yield
    # after app stop 应用结束后执行
    logger.success("After app stop")


app = FastAPI(
    description=settings.PROJECT_DESC,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

# register
register_cors(app)  # 注册跨域请求
register_exception(app)  # 注册异常捕获
register_middleware(app)  # 注册请求响应拦截
register_router(app)


logger.info("The FastAPI Start Success!")


if __name__ == "__main__":
    if sys.platform == "win32":
        from asyncio import (
            ProactorEventLoop,
            set_event_loop,
            get_event_loop,
        )
        from uvicorn import Config, Server

        set_event_loop(ProactorEventLoop())
        server = Server(
            config=Config(app=app, host="127.0.0.1", port=8000, workers=16)
        )
        get_event_loop().run_until_complete(server.serve())
