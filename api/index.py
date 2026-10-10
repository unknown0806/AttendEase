import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app
from urllib.parse import urlparse

_app = create_app()


def _rewrite_path(environ):
    original_uri = environ.get("HTTP_X_VERCEL_ORIGINAL_URL")
    if not original_uri:
        raw = environ.get("REQUEST_URI", "")
        if raw:
            original_uri = raw

    if original_uri:
        parsed = urlparse(original_uri)
        environ["PATH_INFO"] = parsed.path or "/"
        environ["SCRIPT_NAME"] = ""
        if parsed.query:
            environ["QUERY_STRING"] = parsed.query
    else:
        path = environ.get("PATH_INFO", "/")
        if path.startswith("/api/"):
            environ["PATH_INFO"] = "/"


class _PathRewriteMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        _rewrite_path(environ)
        return self.app(environ, start_response)


app = _PathRewriteMiddleware(_app)
handler = app
