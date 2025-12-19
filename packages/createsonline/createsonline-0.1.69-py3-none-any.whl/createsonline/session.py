"""
Session Management for CREATESONLINE
Provides cookie-based session management with HMAC-signed cookies (no JWT dependency).
"""
import os
import secrets
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Iterable


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


class SessionManager:
    """
    Manages user sessions with HMAC-signed cookies (stateless, no JWT dependency).
    """
    
    def __init__(self, secret_key: Optional[str] = None, expiry_days: int = 30, backend: Optional[str] = None):
        """
        Initialize session manager
        
        Args:
            secret_key: Secret key for signing (auto-generated if None; use env for stability)
            expiry_days: Session expiration in days (default: 30)
            backend: kept for backward compatibility; ignored (always signed)
        """
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.expiry_days = expiry_days
        self.backend = "signed"
        self._secret_bytes = self.secret_key.encode("utf-8")
    
    def _build_payload(self, user_id: int, user_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        expiry = datetime.utcnow() + timedelta(days=self.expiry_days)
        payload = {
            'user_id': user_id,
            'exp': expiry,
            'iat': datetime.utcnow()
        }
        if user_data:
            payload.update(user_data)
        return payload
    
    def _encode_signed(self, payload: Dict[str, Any]) -> str:
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str).encode("utf-8")
        body_b64 = _b64url_encode(body)
        sig = hmac.new(self._secret_bytes, body_b64.encode("ascii"), hashlib.sha256).digest()
        sig_b64 = _b64url_encode(sig)
        return f"s1.{body_b64}.{sig_b64}"
    
    def _decode_signed(self, token: str) -> Optional[Dict[str, Any]]:
        if not token.startswith("s1."):
            return None
        parts = token.split(".")
        if len(parts) != 3:
            return None
        _, body_b64, sig_b64 = parts
        expected_sig = hmac.new(self._secret_bytes, body_b64.encode("ascii"), hashlib.sha256).digest()
        try:
            provided_sig = _b64url_decode(sig_b64)
        except Exception:
            return None
        if not hmac.compare_digest(expected_sig, provided_sig):
            return None
        try:
            body = _b64url_decode(body_b64)
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return None
        # Expiry check (payload exp stored as ISO or timestamp string)
        exp = payload.get("exp")
        if exp:
            try:
                # try numeric timestamp first
                exp_ts = float(exp) if isinstance(exp, (int, float, str)) else None
                if exp_ts is not None:
                    if datetime.utcfromtimestamp(exp_ts) < datetime.utcnow():
                        return None
                else:
                    # fallback ISO
                    exp_dt = datetime.fromisoformat(exp)
                    if exp_dt < datetime.utcnow():
                        return None
            except Exception:
                return None
        return payload
    
    def create_session(self, user_id: int, user_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session token (signed cookie)
        """
        payload = self._build_payload(user_id, user_data)
        # Store exp/iat as timestamps for compactness
        payload["exp"] = payload["exp"].timestamp() if hasattr(payload["exp"], "timestamp") else payload["exp"]
        payload["iat"] = payload["iat"].timestamp() if hasattr(payload["iat"], "timestamp") else payload["iat"]
        return self._encode_signed(payload)
    
    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate session token and return user data
        """
        if not token:
            return None
        return self._decode_signed(token)
    
    def get_user_id(self, token: str) -> Optional[int]:
        payload = self.validate_session(token)
        if payload:
            return payload.get('user_id')
        return None
    
    def refresh_session(self, token: str) -> Optional[str]:
        payload = self.validate_session(token)
        if not payload:
            return None
        payload.pop('exp', None)
        payload.pop('iat', None)
        user_id = payload.pop('user_id', None)
        if user_id is None:
            return None
        return self.create_session(user_id, payload)


class SessionMiddleware:
    """
    ASGI Middleware for session management
    
    Adds session data to request object from cookies
    """
    
    def __init__(self, app, session_manager: SessionManager, cookie_name: str = 'session'):
        """
        Initialize session middleware
        
        Args:
            app: ASGI application
            session_manager: SessionManager instance
            cookie_name: Name of session cookie (default: 'session')
        """
        self.app = app
        self.session_manager = session_manager
        self.cookie_name = cookie_name
    
    async def __call__(self, scope, receive, send):
        """Process ASGI request with session handling"""
        if scope['type'] == 'http':
            # Extract session from cookies
            headers = scope.get('headers', [])
            cookies = {}
            
            for name, value in headers:
                if name == b'cookie':
                    cookie_str = value.decode('utf-8')
                    for cookie in cookie_str.split(';'):
                        cookie = cookie.strip()
                        if '=' in cookie:
                            key, val = cookie.split('=', 1)
                            cookies[key] = val
            
            # Validate session token
            session_token = cookies.get(self.cookie_name)
            session_data = None
            
            if session_token:
                session_data = self.session_manager.validate_session(session_token)
            
            # Add session to scope
            scope['session'] = session_data or {}
            scope['session_manager'] = self.session_manager
            scope['session_cookie_name'] = self.cookie_name
        
        # Pass to next middleware/app
        await self.app(scope, receive, send)


def get_session(request) -> Dict[str, Any]:
    """
    Get session data from request
    
    Args:
        request: Starlette/ASGI request object
    
    Returns:
        Session data dictionary (empty if no session)
    """
    return getattr(request, 'scope', {}).get('session', {})


def get_user_id(request) -> Optional[int]:
    """
    Get logged-in user ID from request session
    
    Args:
        request: Request object
    
    Returns:
        User ID if logged in, None otherwise
    """
    session = get_session(request)
    return session.get('user_id')


def is_authenticated(request) -> bool:
    """
    Check if user is authenticated
    
    Args:
        request: Request object
    
    Returns:
        True if user is logged in, False otherwise
    """
    return get_user_id(request) is not None


def set_session_cookie(response, token: str, cookie_name: str = 'session', max_age: int = 2592000):
    """
    Set session cookie in response
    
    Args:
        response: Response object
        token: JWT session token
        cookie_name: Cookie name (default: 'session')
        max_age: Cookie max age in seconds (default: 30 days)
    """
    # Add Set-Cookie header
    cookie_value = f"{cookie_name}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"
    
    # Check if response has headers attribute
    if hasattr(response, 'headers'):
        response.headers['Set-Cookie'] = cookie_value
    elif hasattr(response, 'init_headers'):
        response.init_headers.append(('Set-Cookie', cookie_value.encode()))
    
    return response


def clear_session_cookie(response, cookie_name: str = 'session'):
    """
    Clear session cookie (logout)
    
    Args:
        response: Response object
        cookie_name: Cookie name (default: 'session')
    """
    cookie_value = f"{cookie_name}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
    
    if hasattr(response, 'headers'):
        response.headers['Set-Cookie'] = cookie_value
    elif hasattr(response, 'init_headers'):
        response.init_headers.append(('Set-Cookie', cookie_value.encode()))
    
    return response


# ---------------------------------------------------------------------------
# Helper utilities for projects to manage auth without re-implementing
# ---------------------------------------------------------------------------

def _infer_cookie_name(request, fallback: str = "session") -> str:
    if hasattr(request, "scope"):
        return request.scope.get("session_cookie_name", fallback)
    return fallback


def get_session_manager(request=None, secret_key: Optional[str] = None, expiry_days: int = 30, backend: Optional[str] = None) -> SessionManager:
    """
    Retrieve an existing session manager (from request.scope) or build one using project secrets.
    """
    if request is not None and hasattr(request, "scope"):
        mgr = request.scope.get("session_manager")
        if mgr:
            return mgr
        if backend is None:
            backend = request.scope.get("session_backend")

    secret = secret_key
    if secret is None:
        try:
            from user_config import SECRET_KEY as USER_SECRET
            secret = USER_SECRET or None
        except Exception:
            secret = None
    secret = secret or os.getenv("SECRET_KEY")
    backend = backend or os.getenv("SESSION_BACKEND")
    return SessionManager(secret_key=secret, expiry_days=expiry_days, backend=backend)


def login_user(request, response, user_id: int, user_data: Optional[Dict[str, Any]] = None, *, max_age: int = 2592000, cookie_name: Optional[str] = None, secret_key: Optional[str] = None):
    """
    Issue a JWT session token for the user and attach it as an httpOnly cookie.
    Returns (response, token).
    """
    manager = get_session_manager(request, secret_key=secret_key)
    token = manager.create_session(user_id=user_id, user_data=user_data)
    name = cookie_name or _infer_cookie_name(request)
    set_session_cookie(response, token, cookie_name=name, max_age=max_age)
    return response, token


def logout_user(request, response, *, cookie_name: Optional[str] = None):
    """
    Clear the user's session cookie and return the response.
    """
    name = cookie_name or _infer_cookie_name(request)
    clear_session_cookie(response, cookie_name=name)
    return response


def has_role(request, allowed_roles: Iterable[str]) -> bool:
    """
    Check whether the current session role is in the allowed list.
    """
    session = get_session(request) or {}
    role = session.get("role")
    if role is None:
        return False
    allowed = {r.value if hasattr(r, "value") else str(r) for r in allowed_roles}
    return role in allowed
