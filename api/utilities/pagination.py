"""Custom page-number pagination.

Returns the standard response envelope with pagination meta under
``meta.pagination``. ``pageSize`` is a query param so callers can ask for a
different page size, capped by ``max_page_size``.
"""

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """This is the custom pagination class for the API. It exposes the pagination
    meta data so the common ``success_response`` can carry it.

    Args:
        PageNumberPagination (class): A simple page number based style that
            supports page numbers as query parameters.
    """

    page_size = 10
    page_size_query_param = "pageSize"
    max_page_size = 100

    def get_pagination_meta(self):
        """Return the pagination meta for the current page.

        Returns:
            dict: ``{"pagination": {page, pageSize, pageCount, total}}``
        """
        return {
            "pagination": {
                "page": self.page.number,
                "pageSize": self.page.paginator.per_page,
                "pageCount": self.page.paginator.num_pages,
                "total": self.page.paginator.count,
            }
        }
