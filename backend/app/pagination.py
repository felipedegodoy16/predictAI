from rest_framework.pagination import PageNumberPagination

class DynamicPageSizePagination(PageNumberPagination):
    page_size_query_param = 'size'
    page_size = 10  # Default value fallback
    max_page_size = 50 # Prevents frontend from requesting 1000 items and crashing server
