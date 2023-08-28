from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookDetailSerializer, BookListSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(required=False)

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_date(
            attrs["expected_return_date"],
            ValidationError,
            attrs.get("actual_return_date", None),
        )
        Borrowing.validate_book_inventory(
            attrs["book"].inventory,
            ValidationError,
        )
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = BookListSerializer(many=False, read_only=True)


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookDetailSerializer(many=False, read_only=True)


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book",
        )
