from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Validate email + password and produce an access / refresh token pair."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # Look the user up by email, then authenticate with their username so we
        # go through Django's normal password hashing/backends.
        user = User.objects.filter(email__iexact=attrs["email"]).first()
        if user is not None:
            user = authenticate(username=user.get_username(), password=attrs["password"])
        if user is None:
            raise serializers.ValidationError(_("auth.invalid_credentials"))

        refresh = RefreshToken.for_user(user)
        attrs["access_token"] = str(refresh.access_token)
        attrs["refresh_token"] = str(refresh)
        return attrs


class RefreshSerializer(serializers.Serializer):
    """Validate a refresh token and produce a fresh access token."""

    refresh_token = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refresh_token"])
        except TokenError:
            raise serializers.ValidationError(_("auth.invalid_refresh_token")) from None
        attrs["access_token"] = str(refresh.access_token)
        return attrs
