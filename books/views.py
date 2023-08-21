from rest_framework import viewsets

from books.models import Book
from books.paginations import BookPagination
from books.serializers import BookSerializer, BookListSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the books with filters"""
        title = self.request.query_params.get("title")
        authors = self.request.query_params.get("authors")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if authors:
            authors_ids = self._params_to_ints(authors)
            queryset = queryset.filter(author__id__in=authors_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        if self.action == "retrieve":
            return BookDetailSerializer

        return BookSerializer
