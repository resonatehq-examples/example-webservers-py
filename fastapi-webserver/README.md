# FastAPI webserver | Resonate example application

This example application has been tested with Resonate Python SDK v0.7.4.

The SDK has no in-process store, so this example needs a running Resonate server.

Install dependencies:

```
uv sync
```

Start a Resonate server:

```
resonate dev
```

The webserver connects to `http://localhost:8001` by default. Set `RESONATE_URL`
to point it somewhere else.

Run the webserver:

```
uv run webserver
```

Send a request:

```
curl -X GET http://127.0.0.1:8000
```
