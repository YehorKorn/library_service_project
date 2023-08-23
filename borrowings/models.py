import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from books.models import Book
from users.models import User


class Borrowings(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book: Book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user: User = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        is_active_str = (
            f"Expected return date: {self.expected_return_date}"
            if self.is_active
            else f"Return date: {self.actual_return_date}"
        )
        return (
            f"Book: {self.book.title}; Borrow date: {self.borrow_date};\n"
            f"Customer: {self.user.email}; Is active: {self.is_active};\n"
            + is_active_str
        )

    @property
    def is_active(self):
        return not bool(self.actual_return_date)

    @staticmethod
    def validate_date(expected_return_date, actual_return_date, error_to_raise):
        today = datetime.datetime.today().date()
        if not expected_return_date >= today:
            raise error_to_raise(
                {
                    expected_return_date: f"{expected_return_date} can't be any sooner than today."
                }
            )
        if actual_return_date and not actual_return_date == today:
            raise error_to_raise(
                {
                    actual_return_date: f"{actual_return_date} cannot be earlier or later than today."
                }
            )

    def clean(self):
        Borrowings.validate_date(
            self.expected_return_date,
            self.actual_return_date,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Borrowings, self).save(
            force_insert, force_update, using, update_fields
        )
