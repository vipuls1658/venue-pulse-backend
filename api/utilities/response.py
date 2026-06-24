"""Standard API response helpers.

Every view returns one of these so the body shape stays consistent:

    success:    {"success": True,  "message": str, "data": ...}
    paginated:  {"success": True,  "message": str, "data": [...], "meta": {...}}
    error:      {"success": False, "message": str, "errors": ...}

The paginated shape is built by ``CustomPagination`` (api/utilities/pagination.py).
Views build the ``Response`` with ``StatusCodes.get(...)`` for the HTTP code.
"""

from rest_framework.response import Response

from api.constants import StatusCodes


def success_response(data=None, message="", meta=None, status_name="OK"):
    """Build a success body: ``{"success": True, "message": ..., "data": ...}``.

    ``meta`` (e.g. pagination info) is only included when supplied.
    """
    body = {"success": True, "message": message, "data": data}
    if meta is not None:
        body["meta"] = meta
    return Response(body, status=StatusCodes.get(status_name))


def error_response(message, errors=None, status_name="BAD_REQUEST"):
    """Build an error body: ``{"success": False, "message": ..., "errors": ...}``."""
    return Response(
        {"success": False, "message": message, "errors": errors},
        status=StatusCodes.get(status_name),
    )
