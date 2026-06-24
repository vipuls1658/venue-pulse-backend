import logging
import traceback

from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets

from api.transactions import api_methods
from api.transactions.serializers import TransactionCreateSerializer
from api.utilities.response import error_response, success_response
from api.transactions.api_methods import create_transaction

logger = logging.getLogger("api")


class TransactionViewSet(viewsets.ViewSet):
    """POS-facing transaction endpoints."""

    def create(self, request):
        """This API method receives and stores a transaction from a venue POS.

        Args:
            request (object): Request Object

        Returns:
            Response: Response object
        """
        try:
            serializer = TransactionCreateSerializer(data=request.data)
            if serializer.is_valid():
                txn = create_transaction(serializer.validated_data)
                if txn:
                    return success_response(
                        {}, message=_("transaction.created"), status_name="CREATED"
                    )
                return error_response(
                    _("transaction.create_failed"), status_name="BAD_REQUEST"
                )
            else:
                return error_response(
                    _("error.invalid_request_data"), errors=serializer.errors, status_name="BAD_REQUEST"
                )
        except Exception:
            logger.error(traceback.format_exc())
            return error_response(_("error.server_error"), status_name="SERVER_ERROR")
