import asyncio
import os
import threading

from django.http import JsonResponse
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


class ResonateBridge:
    """Drives the async Resonate SDK from Django's synchronous views.

    Django's development server serves requests on worker threads with no event
    loop, but the Resonate SDK is async and its client must live on one loop for
    its whole lifetime -- it starts a background network as it is constructed,
    so it cannot be built per request.

    So the client is created on a dedicated event loop running in a background
    thread, and views hand work to that loop and block for the result.
    """

    def __init__(self, url: str) -> None:
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, daemon=True).start()
        self._resonate = self._submit(self._create(url))

    async def _create(self, url: str) -> Resonate:
        resonate = Resonate(url=url)
        resonate.register(foo)
        return resonate

    def _submit(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def run(self, promise_id: str) -> int:
        async def invoke():
            return await self._resonate.run(promise_id, foo).result()

        return self._submit(invoke())


# There is no in-process store: a Resonate server must be reachable at
# RESONATE_URL.
bridge = ResonateBridge(os.environ.get("RESONATE_URL", "http://localhost:8001"))


def read_root(request):
    # The promise id is the idempotency key: the first request computes the
    # result, and later requests for the same id read back the value the
    # Resonate server already holds.
    return JsonResponse({"value": bridge.run("django_webserver_foo_promise_id")})
