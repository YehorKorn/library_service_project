import datetime

from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from books.models import Book
from borrowings.models import Borrowing
from borrowings.paginations import BorrowingPagination
from borrowings.permissions import (
    IsAdminOrIfIsOwnerGetPost,
)
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingSerializer, BorrowingReturnSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.prefetch_related(
        "book__authors",
        "user",
    )
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfIsOwnerGetPost,)
    pagination_class = BorrowingPagination

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer

        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingDetailSerializer

        if self.action == "return_view":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=BorrowingCreateSerializer,
        responses={status.HTTP_201_CREATED: BorrowingCreateSerializer},
        description=(
            "Creation takes -1 away from the book inventory. "
            "Only an authorized user can create borrowings"
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic()
    @action(
        methods=["POST"],
        detail=True,
        url_path="return",
        permission_classes=[IsAdminOrIfIsOwnerGetPost],
    )
    def return_view(self, request, pk=None):
        """
        Return adds +1 to the book inventory, and changes the actual_return_date to the current date.
        A second return is not possible. Only borrowings that belong to an authorized user can be returned.
        """
        borrowing = self.get_object()
        if not borrowing.is_active:
            raise ValidationError(
                {
                    "actual_return_date": f"This borrowing is no longer active, re-closing is not possible"
                }
            )
        borrowing.actual_return_date = datetime.date.today()
        serializer = self.get_serializer(borrowing)
        book = Book.objects.get(pk=borrowing.book.id)
        book.inventory += 1
        book.save()
        borrowing.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
