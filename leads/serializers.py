import re
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Role


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALLOWED_ROLES = ['Sales Rep', 'Sales Manager']

PASSWORD_MIN_LENGTH = 8
PASSWORD_REGEX = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-#])[A-Za-z\d@$!%*?&_\-#]{8,}$'
)


def _get_tokens(user: User) -> dict:
    """Return a fresh JWT access/refresh pair for the given user."""
    refresh = RefreshToken().for_user(user)
    refresh['user_id'] = user.id
    refresh['email'] = user.email
    refresh['role'] = user.role.name if user.role else None
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ---------------------------------------------------------------------------
# Sign-up serializer
# ---------------------------------------------------------------------------

class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, trim_whitespace=True)
    last_name  = serializers.CharField(max_length=100, trim_whitespace=True)
    email      = serializers.EmailField()
    phone      = serializers.CharField(max_length=15, required=False, allow_blank=True, default='')
    password   = serializers.CharField(write_only=True, min_length=PASSWORD_MIN_LENGTH)
    role_name  = serializers.ChoiceField(choices=ALLOWED_ROLES)

    # ── field-level validation ──────────────────────────────────────────────

    def validate_email(self, value: str) -> str:
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_password(self, value: str) -> str:
        if not PASSWORD_REGEX.match(value):
            raise serializers.ValidationError(
                "Password must be at least 8 characters and contain an uppercase letter, "
                "a lowercase letter, a digit, and a special character (@$!%*?&_-#)."
            )
        return value

    def validate_first_name(self, value: str) -> str:
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("First name must contain only letters.")
        return value.strip().title()

    def validate_last_name(self, value: str) -> str:
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("Last name must contain only letters.")
        return value.strip().title()

    # ── create ──────────────────────────────────────────────────────────────

    def create(self, validated_data: dict) -> dict:
        role_name = validated_data.pop('role_name')
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={'description': f'Default {role_name} role'},
        )

        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone=validated_data.get('phone', ''),
            role=role,
            is_active=True,
        )

        user.set_password(validated_data['password'])
        user.save()

        tokens = _get_tokens(user)
        return {
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': role_name,
            },
            **tokens,
        }


# ---------------------------------------------------------------------------
# Login serializer
# ---------------------------------------------------------------------------

class LoginSerializer(serializers.Serializer):
    email     = serializers.EmailField()
    password  = serializers.CharField(write_only=True)
    role_name = serializers.ChoiceField(choices=ALLOWED_ROLES)

    # ── object-level validation (all fields available) ──────────────────────

    def validate(self, attrs: dict) -> dict:
        email     = attrs['email'].lower().strip()
        password  = attrs['password']
        role_name = attrs['role_name']

        # 1. User existence — use a generic message to avoid user enumeration
        try:
            user = User.objects.select_related('role').get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials."]}
            )

        # 2. Active check
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["This account has been deactivated."]}
            )

        # 3. Password check
        if not check_password(password, user.password):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials."]}
            )

        # 4. Role enforcement — prevents cross-portal login
        user_role = user.role.name if user.role else ''
        if user_role != role_name:
            raise serializers.ValidationError(
                {"role_name": [f"This account does not have the '{role_name}' role."]}
            )

        # 5. Stamp last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        attrs['user'] = user
        return attrs

    def to_representation(self, validated_data: dict) -> dict:
        user = validated_data['user']
        tokens = _get_tokens(user)
        return {
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role.name if user.role else None,
                'profile_picture': (
                    user.profile_picture.url if user.profile_picture else None
                ),
            },
            **tokens,
        }


# ---------------------------------------------------------------------------
# Logout serializer
# ---------------------------------------------------------------------------

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value: str) -> str:
        try:
            RefreshToken(value)
        except Exception:
            raise serializers.ValidationError("Invalid or expired refresh token.")
        return value

    def save(self) -> None:
        token = RefreshToken(self.validated_data['refresh'])
        token.blacklist()
