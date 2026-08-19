import asyncio
import os
import threading

from flask import Flask, jsonify
from resonate.context import Context
from resonate.resonate import Resonate

app = Flask("flask-webserver")


async def baz(ctx: Context) -> str:
    print("running baz")
    return "hello world!"


async def bar(ctx: Context) -> str:
    print("running bar")
    return await ctx.run(baz)


async def foo(ctx: Context) -> str:
    print("running foo")
    return await ctx.run(bar)


class ResonateBridge:
    """Drives the async Resonate SDK from Flask's synchronous request handlers.

    Flask (WSGI) serves each request on a worker thread with no event loop, but
    the Resonate SDK is async and its client must live on one loop for its whole
    lifetime -- it starts a background network as it is constructed, so it
    cannot be built at import time or per request.

    So the client is created on a dedicated event loop running in a background
    thread, and request handlers hand work to that loop and block for the
    result.
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

    def run(self, promise_id: str) -> str:
        async def invoke():
            return await self._resonate.run(promise_id, foo).result()

        return self._submit(invoke())


bridge = ResonateBridge(os.environ.get("RESONATE_URL", "http://localhost:8001"))


@app.route("/")
def read_root():
    # The promise id is the idempotency key: the first request computes the
    # result, and later requests for the same id read back the value the
    # Resonate server already holds.
    return jsonify({"value": bridge.run("flask_webserver_foo_promise_id")})


def main() -> None:
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
