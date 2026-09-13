"""Pagination configuration for the public offer list."""

from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Paginate offers and allow the documented page_size parameter."""

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
