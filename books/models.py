from django.core.validators import MinValueValidator
from django.db import models


class Author(models.Model):
    first_name = models.CharField(
        max_length=65,
    )
    last_name = models.CharField(
        max_length=65,
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(
        max_length=155,
    )
    author = models.ManyToManyField(Author, blank=True, related_name="books")
    cover = models.CharField(max_length=10, choices=CoverChoices.choices)
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    daily_fee = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self) -> str:
        return self.title

    def decrease_inventory_by_1(self):
        self.inventory -= 1

    def add_1_to_inventory(self):
        self.inventory += 1
