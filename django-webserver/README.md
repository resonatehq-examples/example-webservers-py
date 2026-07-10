# Django webserver | Resonate example application

This application has been tested with Resonate Python SDK v0.7.1.

Install dependencies:

```
uv sync
```

Run the webserver:

```
uv run django-webserver runserver
```

Send a request:

```
curl -X GET http://127.0.0.1:8000
```
