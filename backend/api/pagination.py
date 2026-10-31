from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Pagination using `?page=<n>&limit=<m>`.

    Returns: {count, next, previous, results}
    """

    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = 6
    max_page_size = 100
