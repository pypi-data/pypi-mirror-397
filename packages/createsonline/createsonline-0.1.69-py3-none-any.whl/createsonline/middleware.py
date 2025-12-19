# createsonline/middleware.py
"""
CREATESONLINE Middleware System

Base classes and standard middleware implementations.
"""
from typing import Any, Optional, Callable, Awaitable, Iterable
import importlib
import inspect

def _import_from_string(path: str):
    module_path, _, attr = path.rpartition(".")
    if not module_path or not attr:
        raise ImportError(f"Invalid import path: {path}")
    module = importlib.import_module(module_path)
    return getattr(module, attr)

class BaseMiddleware:
    """Base class for all middleware"""
    
    async def before_request(self, request: Any) -> Optional[Any]:
        """
        Called before the request is handled by the route.
        Return a response object to intercept the request, or None to continue.
        """
        return None
        
    async def after_request(self, request: Any, response: Any) -> Any:
        """
        Called after the request is handled.
        Must return the response object (modified or original).
        """
        return response

class CORSMiddleware(BaseMiddleware):
    """Cross-Origin Resource Sharing (CORS) Middleware"""

    def __init__(self, allow_origins: list = None, allow_methods: list = None, allow_headers: list = None, **kwargs):
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        
    async def before_request(self, request):
        if request.method == "OPTIONS":
            # Handle preflight request
            from .server import InternalResponse
            headers = self._get_cors_headers()
            return InternalResponse(content="", status_code=204, headers=headers)
        return None
        
    async def after_request(self, request, response):
        # Add CORS headers to response
        cors_headers = self._get_cors_headers()
        
        # Handle dict response
        if isinstance(response, dict):
            # Can't easily add headers to dict response without wrapping it
            # Ideally, app.py should handle this, but for now we can't modify dict easily
            pass 
        # Handle InternalResponse
        elif hasattr(response, 'headers'):
            for k, v in cors_headers.items():
                response.headers[k] = v
                
        return response

    def _get_cors_headers(self):
        return {
            "Access-Control-Allow-Origin": ", ".join(self.allow_origins),
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
        }


def load_configured_middleware(app, middleware_list: Optional[Iterable] = None):
    """
    Dynamically attach middleware to the app.

    Accepts:
    - Dotted import strings: 'module.path.MiddlewareClass'
    - Tuples with kwargs: ('module.path.MiddlewareClass', {'param': 'value'})
    - Callables

    If a middleware inherits BaseMiddleware, its before_request/after_request
    will be invoked via app.middleware("http").
    """
    if middleware_list is None:
        try:
            from user_config import MIDDLEWARE
            middleware_list = MIDDLEWARE
        except Exception:
            middleware_list = []

    for entry in middleware_list:
        try:
            # Handle tuple format: ('path.to.Middleware', {'kwarg': 'value'})
            if isinstance(entry, tuple) and len(entry) == 2:
                middleware_path, kwargs = entry
                middleware_cls = _import_from_string(middleware_path)
                if inspect.isclass(middleware_cls) and issubclass(middleware_cls, BaseMiddleware):
                    instance = middleware_cls(**kwargs)
                else:
                    continue
            # Handle string format: 'path.to.Middleware'
            elif isinstance(entry, str):
                middleware_cls = _import_from_string(entry)
                if inspect.isclass(middleware_cls) and issubclass(middleware_cls, BaseMiddleware):
                    instance = middleware_cls()
                else:
                    middleware = middleware_cls
                    app.middleware("http")(middleware)
                    continue
            # Handle callable/class instances
            else:
                middleware = entry
                if isinstance(middleware, BaseMiddleware):
                    instance = middleware
                elif inspect.isclass(middleware) and issubclass(middleware, BaseMiddleware):
                    instance = middleware()
                else:
                    app.middleware("http")(middleware)
                    continue

            # Register the BaseMiddleware instance
            @app.middleware("http")
            async def _mw(request, _instance=instance):
                result = await _instance.before_request(request)
                if result is not None:
                    return result
                # after_request hook will be handled by the framework response pipeline if available
                return None

        except Exception:
            continue

