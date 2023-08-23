from rest_framework import generics

from borrowings.models import Borrowings
from borrowings.serializers import BorrowingsListSerializer, BorrowingsDetailSerializer


class BorrowingsListView(generics.ListAPIView):
    queryset = Borrowings.objects.prefetch_related(
        "book__author",
        "user",
    )
    serializer_class = BorrowingsListSerializer

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

        return queryset.distinct()


class BorrowingsDetailView(generics.RetrieveAPIView):
    queryset = Borrowings.objects.prefetch_related(
        "book__author",
        "user",
    )
    serializer_class = BorrowingsDetailSerializer
