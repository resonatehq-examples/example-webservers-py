from __future__ import annotations

import asyncio

from django.http import JsonResponse
from resonate.resonate import Resonate
from resonate.context import Context


async def baz(_: Context) -> int:
    return 1


async def bar(ctx: Context) -> int:
    v = await ctx.run(baz)
    return v + 1


async def foo(ctx: Context) -> int:
    v = await ctx.run(bar)
    return v + 1


async def _run() -> int:
    r = Resonate()
    r.register(foo)
    r.register(bar)
    r.register(baz)
    handle = r.run("django_webserver_foo_promise_id", foo)
    result = await handle.result()
    await r.stop()
    return result


def read_root(request):
    v = asyncio.run(_run())
    return JsonResponse({"value": v})
