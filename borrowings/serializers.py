from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookDetailSerializer, BookListSerializer
from borrowings.models import Borrowings


class BorrowingsSerializer(serializers.ModelSerializer):
    actual_return_date = serializers.DateField(required=False)

    def validate(self, attrs):
        data = super(BorrowingsSerializer, self).validate(attrs=attrs)
        Borrowings.validate_date(
            attrs["expected_return_date"],
            ValidationError,
            attrs.get("actual_return_date", None),
        )
        Borrowings.validate_book_inventory(
            attrs["book"].inventory,
            ValidationError,
        )
        return data

    class Meta:
        model = Borrowings
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )


class BorrowingsListSerializer(BorrowingsSerializer):
    book = BookListSerializer(many=False, read_only=True)


class BorrowingsDetailSerializer(BorrowingsSerializer):
    book = BookDetailSerializer(many=False, read_only=True)


class BorrowingsCreateSerializer(BorrowingsSerializer):
    class Meta:
        model = Borrowings
        fields = (
            "id",
            "expected_return_date",
            "book",
        )
