import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from resonate.context import Context
from resonate.resonate import Resonate


async def baz(ctx: Context) -> int:
    return 1


async def bar(ctx: Context) -> int:
    v = await ctx.run(baz)
    return v + 1


async def foo(ctx: Context) -> int:
    v = await ctx.run(bar)
    return v + 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Resonate must be constructed on a running event loop -- it starts its
    # network in the background as it is created. Building it at import time
    # raises "RuntimeError: no running event loop", so it belongs in the
    # lifespan startup rather than at module scope.
    #
    # There is also no in-process store: a Resonate server must be reachable
    # at RESONATE_URL.
    resonate = Resonate(url=os.environ.get("RESONATE_URL", "http://localhost:8001"))
    resonate.register(foo)
    app.state.resonate = resonate
    try:
        yield
    finally:
        await resonate.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    # The promise id is the idempotency key: the first request computes the
    # result, and later requests for the same id read back the value the
    # Resonate server already holds.
    handle = app.state.resonate.run("fastapi_webserver_foo_promise_id", foo)
    return {"value": await handle.result()}


def main() -> None:
    uvicorn.run(app)


if __name__ == "__main__":
    main()
