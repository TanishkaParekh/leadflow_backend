import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .serializers import LoginSerializer, LogoutSerializer, SignupSerializer

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom throttle classes
# ---------------------------------------------------------------------------

class LoginRateThrottle(AnonRateThrottle):
    """Strict rate limit for login attempts — brute-force protection."""
    scope = 'login'       # set in settings: REST_FRAMEWORK THROTTLE_RATES {'login': '5/min'}


class SignupRateThrottle(AnonRateThrottle):
    """Moderate rate limit for signups."""
    scope = 'signup'      # e.g. '10/hour'


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([SignupRateThrottle])
def signup(request):
    """
    POST /api/auth/signup/

    Body:
        {
            "first_name": "Alex",
            "last_name":  "Smith",
            "email":      "alex@company.com",
            "password":   "Secure@123",
            "phone":      "+91 98765 43210",   // optional
            "role_name":  "Sales Rep" | "Sales Manager"
        }

    Returns 201 with user object + JWT tokens on success.
    """
    serializer = SignupSerializer(data=request.data)

    if not serializer.is_valid():
        logger.warning("Signup validation failed | errors=%s", serializer.errors)
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        result = serializer.create(serializer.validated_data)
        logger.info("New user signed up | email=%s role=%s",
                    result['user']['email'], result['user']['role'])
        return Response(
            {"success": True, "message": "Account created successfully.", **result},
            status=status.HTTP_201_CREATED,
        )
    except Exception:
        logger.exception("Unexpected error during signup")
        return Response(
            {"success": False, "errors": {"non_field_errors": ["An unexpected error occurred. Please try again."]}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login(request):
    """
    POST /api/auth/login/

    Body:
        {
            "email":     "alex@company.com",
            "password":  "Secure@123",
            "role_name": "Sales Rep" | "Sales Manager"
        }

    Returns 200 with user object + JWT tokens on success.
    Role mismatch (e.g. rep trying manager portal) returns 403.
    """
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        errors = serializer.errors
        # Distinguish role mismatch (403) from bad credentials (401)
        if 'role_name' in errors:
            return Response(
                {"success": False, "errors": errors},
                status=status.HTTP_403_FORBIDDEN,
            )
        logger.warning("Login failed | ip=%s errors=%s",
                       _get_client_ip(request), errors)
        return Response(
            {"success": False, "errors": errors},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    result = serializer.to_representation(serializer.validated_data)
    logger.info("User logged in | email=%s role=%s",
                result['user']['email'], result['user']['role'])
    return Response(
        {"success": True, "message": "Login successful.", **result},
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def logout(request):
    """
    POST /api/auth/logout/

    Headers:
        Authorization: Bearer <access_token>

    Body:
        { "refresh": "<refresh_token>" }

    Blacklists the refresh token so it can no longer be used.
    Requires rest_framework_simplejwt.token_blacklist in INSTALLED_APPS.
    """
    serializer = LogoutSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        serializer.save()
        logger.info("User logged out | user_id=%s",
                    getattr(request.user, 'id', 'unknown'))
        return Response(
            {"success": True, "message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )
    except Exception:
        logger.exception("Logout failed — token blacklist error")
        return Response(
            {"success": False, "errors": {"non_field_errors": ["Logout failed. Token may already be invalid."]}},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _get_client_ip(request) -> str:
    """Extract real client IP, respecting X-Forwarded-For in production."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')
