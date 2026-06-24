import logging
import traceback

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.dashboard.api_methods import (
    alerts,
    hourly_sales,
    top_items,
    venue_detail,
    venue_sales,
)
from api.dashboard.serializers import VenueDetailSerializer
from api.utilities.pagination import CustomPagination
from api.utilities.response import error_response, success_response

logger = logging.getLogger("api")


class DashboardViewSet(viewsets.GenericViewSet):
    """This DashboardViewSet class stores the APIs method to be used for the dashboard

    Args:
        viewsets (class): GenericViewSet Class
    """

    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @action(detail=False, methods=["get"])
    def venue_sales(self, request):
        """This method is for getting today's sales ranking by venue

        Args:
            request (object): request object

        Returns:
            Json: Json Response
        """
        try:
            page = self.paginate_queryset(venue_sales())
            return success_response(page, meta=self.paginator.get_pagination_meta())
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")

    @action(detail=False, methods=["get"])
    def top_items(self, request):
        """This method is for getting the top selling items across all venues

        Args:
            request (object): request object

        Returns:
            Json: Json Response
        """
        try:
            page = self.paginate_queryset(top_items(limit=None))
            return success_response(page, meta=self.paginator.get_pagination_meta())
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")

    @action(detail=False, methods=["get"])
    def alerts(self, request):
        """This method is for getting all the active alerts

        Args:
            request (object): request object

        Returns:
            Json: Json Response
        """
        try:
            return success_response(alerts())
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")

    @action(detail=False, methods=["get"])
    def hourly_sales(self, request):
        """This method is for getting the hourly sales trend for all venues

        Args:
            request (object): request object

        Returns:
            Json: Json Response
        """
        try:
            return success_response(hourly_sales())
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")

    @action(detail=False, methods=["get"])
    def venue_detail(self, request):
        """This method is for getting detailed information for one venue

        Args:
            request (object): request object

        Returns:
            Json: Json Response
        """
        try:
            request_data = request.query_params
            serializer = VenueDetailSerializer(data=request_data)
            if serializer.is_valid():
                venue_id = serializer.validated_data.get("venue_id")
                data = venue_detail(venue_id)
                if data:
                    page = self.paginate_queryset([data])
                    return success_response(page, meta=self.paginator.get_pagination_meta())
                return error_response(_("error.venue_not_found"), status_name="NOT_FOUND")
            else:
                return error_response(
                    _("error.invalid_request_data"), errors=serializer.errors, status_name="BAD_REQUEST"
                )
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")
