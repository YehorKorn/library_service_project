import datetime

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
        "book__authors",
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.STR,
                description=(
                    "Filter by bool value regardless of letter case, "
                    "active borrowing or not. (ex. ?is_active=true; ?is_active=false)"
                ),
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by user of borrowings. Can only be used by the admin (ex. ?user_id=1)",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=BorrowingsCreateSerializer,
        responses={status.HTTP_201_CREATED: BorrowingsCreateSerializer},
        description=(
            "Creation takes -1 away from the book inventory. "
            "Only an authorized user can create borrowings"
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class BorrowingsDetailView(generics.RetrieveAPIView):
    queryset = Borrowings.objects.prefetch_related(
        "book__authors",
        "user",
    )
    serializer_class = BorrowingsDetailSerializer
    permission_classes = (IsAdminOrIfIsAuthenticateCreateOrReadOnly,)


@transaction.atomic()
@api_view(["POST"])
def borrowings_return_view(request, pk):
    """
    Return adds +1 to the book inventory, and changes
    the actual_return_date to the current date.
    A second return is not possible. Only borrowings
    that belong to an authorized user can be returned.
    """
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
