from rest_framework.pagination import PageNumberPagination


class BorrowingsPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 1000
