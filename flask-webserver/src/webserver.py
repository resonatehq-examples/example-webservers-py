from __future__ import annotations

import asyncio

from flask import Flask, jsonify
from resonate.context import Context
from resonate.resonate import Resonate

app = Flask("flask-webserver")


async def baz(_: Context) -> str:
    print("running baz")
    return "hello world!"


async def bar(ctx: Context) -> str:
    print("running bar")
    result = await ctx.run(baz)
    return result


async def foo(ctx: Context) -> str:
    print("running foo")
    result = await ctx.run(bar)
    return result


async def _run() -> str:
    r = Resonate()
    r.register(foo)
    r.register(bar)
    r.register(baz)
    handle = r.run("flask_webserver_foo_promise_id", foo)
    result = await handle.result()
    await r.stop()
    return result


@app.route("/")
def read_root():
    value = asyncio.run(_run())
    return jsonify({"value": value})


def main() -> None:
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
