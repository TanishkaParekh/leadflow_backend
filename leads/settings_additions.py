"""
Paste these blocks into your existing settings.py.
They add JWT config, throttling, token blacklist, and logging.
"""

from datetime import timedelta

# ---------------------------------------------------------------------------
# INSTALLED_APPS — add these two entries
# ---------------------------------------------------------------------------
# 'rest_framework_simplejwt.token_blacklist',   # enables logout blacklisting
# Already present: 'rest_framework', 'corsheaders', 'leads'


# ---------------------------------------------------------------------------
# REPLACE your existing REST_FRAMEWORK block with this
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon':   '100/day',
        'user':   '1000/day',
        'login':  '5/min',     # 5 login attempts per minute per IP
        'signup': '10/hour',   # 10 signup attempts per hour per IP
    },
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}


# ---------------------------------------------------------------------------
# JWT settings
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    # Token lifetimes
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=30),   # short-lived
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    # Security
    'ROTATE_REFRESH_TOKENS':    True,   # issue new refresh token on every use
    'BLACKLIST_AFTER_ROTATION': True,   # blacklist old refresh token immediately
    'UPDATE_LAST_LOGIN':        False,  # we handle this manually in LoginSerializer

    # Algorithm
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,          # already defined above in your settings

    # Headers
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # Custom claims
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    # Token classes
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}


# ---------------------------------------------------------------------------
# CORS — tighten for production
# ---------------------------------------------------------------------------
# Development (already in your settings — keep as-is):
# CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Additional CORS settings to add:
CORS_ALLOW_CREDENTIALS = True          # required if frontend sends cookies/auth headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'x-csrftoken',
    'x-requested-with',
]


# ---------------------------------------------------------------------------
# Logging — structured logs for auth events
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',   # mkdir logs/ in project root
            'maxBytes': 1024 * 1024 * 5,   # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'leads': {                         # your app name
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}


# ---------------------------------------------------------------------------
# Security headers (add for production — guarded by DEBUG flag)
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER        = True
    SECURE_CONTENT_TYPE_NOSNIFF      = True
    X_FRAME_OPTIONS                  = 'DENY'
    SECURE_HSTS_SECONDS              = 31536000   # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
    SECURE_HSTS_PRELOAD              = True
    SECURE_SSL_REDIRECT              = True
    SESSION_COOKIE_SECURE            = True
    CSRF_COOKIE_SECURE               = True
