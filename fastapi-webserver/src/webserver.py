from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI
from resonate.context import Context
from resonate.resonate import Resonate

_resonate: Resonate | None = None


async def baz(_: Context) -> int:
    return 1


async def bar(ctx: Context) -> int:
    v = await ctx.run(baz)
    return v + 1


async def foo(ctx: Context) -> int:
    v = await ctx.run(bar)
    return v + 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _resonate
    _resonate = Resonate()
    _resonate.register(foo)
    _resonate.register(bar)
    _resonate.register(baz)
    yield
    if _resonate is not None:
        await _resonate.stop()
        _resonate = None


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root() -> dict[str, Any]:
    assert _resonate is not None
    handle = _resonate.run("fastapi_webserver_foo_promise_id", foo)
    value = await handle.result()
    return {"value": value}


def main() -> None:
    uvicorn.run(app)
