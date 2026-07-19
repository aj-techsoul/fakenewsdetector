import re
import bcrypt
from flask import request, session, abort, render_template
from functools import wraps
from datetime import datetime, timedelta

def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password, hashed):
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def sanitize_input_text(text):
    """Remove HTML tags and potential XSS script injections from text inputs."""
    if not text:
        return ""
    # Strip script tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE)
    # Strip all other HTML tags
    text = re.sub(r'<.*?>', '', text)
    return text.strip()


# Simple memory/session based rate limiter for login protection
RATE_LIMIT_CACHE = {}

def rate_limit(limit=5, period_seconds=60):
    """Decorator to limit request rate by client IP."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr
            now = datetime.utcnow()
            
            # Clean expired records
            for key in list(RATE_LIMIT_CACHE.keys()):
                active_timestamps = [t for t in RATE_LIMIT_CACHE[key] if t > now - timedelta(seconds=period_seconds)]
                if not active_timestamps:
                    del RATE_LIMIT_CACHE[key]
                else:
                    RATE_LIMIT_CACHE[key] = active_timestamps
            
            # Count requests for this IP
            ip_requests = [t for t in RATE_LIMIT_CACHE.get(ip, []) if t > now - timedelta(seconds=period_seconds)]
            
            if len(ip_requests) >= limit:
                # Return custom rate limit template/response
                return render_template('error.html', 
                                       title="Too Many Requests", 
                                       message=f"Rate limit exceeded. Please wait {period_seconds} seconds and try again."), 429
            
            # Register current request
            ip_requests.append(now)
            RATE_LIMIT_CACHE[ip] = ip_requests
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
