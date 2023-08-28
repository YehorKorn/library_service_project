from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from books.models import Book
from books.paginations import BookPagination
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer, BookListSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = BookPagination
    permission_classes = (IsAdminOrReadOnly,)

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
            queryset = queryset.filter(authors__id__in=authors_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer

        if self.action == "retrieve":
            return BookDetailSerializer

        return BookSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "authors",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by authors id (ex. ?authors=2,5)",
            ),
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by book title (ex. ?title=Some_book)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
