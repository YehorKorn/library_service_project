# Generated by Django 4.2.4 on 2023-08-21 11:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.ManyToManyField(
                blank=True, related_name="books", to="books.author"
            ),
        ),
    ]
