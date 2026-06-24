import logging
import traceback

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from api.auth.serializers import LoginSerializer, RefreshSerializer
from api.utilities.response import error_response, success_response

logger = logging.getLogger("api")


class AuthViewSet(viewsets.ViewSet):
    """Login and token-refresh endpoints. Open to anonymous callers."""

    permission_classes = [AllowAny]

    def login(self, request):
        """This API method authenticates a user by email and returns a JWT pair.

        Args:
            request (object): Request Object

        Returns:
            Response: Response object
        """
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                data = {
                    "access_token": serializer.validated_data["access_token"],
                    "refresh_token": serializer.validated_data["refresh_token"],
                }
                return success_response(data, message=_("auth.login_successful"))
            else:
                return error_response(
                    _("auth.login_failed"), errors=serializer.errors, status_name="BAD_REQUEST"
                )
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")

    def refresh(self, request):
        """This API method returns a fresh access token from a refresh token.

        Args:
            request (object): Request Object

        Returns:
            Response: Response object
        """
        try:
            serializer = RefreshSerializer(data=request.data)
            if serializer.is_valid():
                data = {"access_token": serializer.validated_data["access_token"]}
                return success_response(data, message=_("auth.token_refreshed"))
            else:
                return error_response(
                    _("auth.token_refresh_failed"), errors=serializer.errors, status_name="BAD_REQUEST"
                )
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")
