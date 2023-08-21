from rest_framework.pagination import PageNumberPagination


class BookPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 1000
