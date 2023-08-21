from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=65,)
    last_name = models.CharField(max_length=65,)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
