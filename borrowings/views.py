import datetime

from django.db import transaction
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from books.models import Book
from borrowings.models import Borrowings
from borrowings.paginations import BorrowingsPagination
from borrowings.permissions import (
    IsAdminOrIfIsAuthenticateCreateOrReadOnly,
)
from borrowings.serializers import (
    BorrowingsListSerializer,
    BorrowingsDetailSerializer,
    BorrowingsCreateSerializer,
    BorrowingsSerializer,
)


class BorrowingsListCreateView(generics.ListCreateAPIView):
    queryset = Borrowings.objects.prefetch_related(
        "book__author",
        "user",
    )
    serializer_class = BorrowingsListSerializer
    permission_classes = (IsAdminOrIfIsAuthenticateCreateOrReadOnly,)
    pagination_class = BorrowingsPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingsCreateSerializer
        if self.request.method == "GET":
            return BorrowingsListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        book = Book.objects.get(pk=serializer.data["book"])
        book.inventory -= 1
        book.save()

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset
        if is_active:
            is_active = is_active.lower()
            if is_active == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active == "false":
                queryset = queryset.exclude(actual_return_date__isnull=True)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        queryset = queryset.distinct()

        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user.id)
        return queryset


class BorrowingsDetailView(generics.RetrieveAPIView):
    queryset = Borrowings.objects.prefetch_related(
        "book__author",
        "user",
    )
    serializer_class = BorrowingsDetailSerializer
    permission_classes = (IsAdminOrIfIsAuthenticateCreateOrReadOnly,)


@transaction.atomic()
@api_view(["POST"])
def borrowings_return_view(request, pk):
    borrowing = get_object_or_404(Borrowings, pk=pk)
    if request.user != borrowing.user and not request.user.is_staff:
        raise NotAuthenticated
    if not borrowing.is_active:
        raise ValidationError(
            {
                "actual_return_date": f"This borrowing is no longer active, re-closing is not possible"
            }
        )
    borrowing.actual_return_date = datetime.date.today()
    serializer = BorrowingsSerializer(borrowing)
    book = Book.objects.get(pk=serializer.data["book"])
    book.inventory += 1
    book.save()
    borrowing.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
