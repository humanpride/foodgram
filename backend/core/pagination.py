from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Пагинация в стиле `?page=<n>&limit=<m>`.

    Возвращает: {count, next, previous, results}
    """

    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = 6
    max_page_size = 100
