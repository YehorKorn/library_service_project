from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from books.models import Book, Author
from books.serializers import BookListSerializer, BookDetailSerializer

BOOK_URL = reverse("books:books-list")


def sample_author(**params):
    defaults = {
        "first_name": "Testname",
        "last_name": "Testsername",
    }
    defaults.update(params)

    return Author.objects.create(**defaults)


def sample_book(**params):
    defaults = {
        "title": "Title",
        "cover": "HARD",
        "inventory": 2,
        "daily_fee": 0.50,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def book_detail_url(book_id):
    return reverse("books:books-detail", args=[book_id])


class UnauthenticatedBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        sample_book()
        sample_book(title="Some_book")

        res = self.client.get(BOOK_URL)

        books = Book.objects.order_by("id")
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_books_by_authors(self):
        author1 = sample_author(first_name="Author1")
        author2 = sample_author(first_name="Author2")

        book1 = sample_book(title="Book 1")
        book2 = sample_book(title="Book 2")

        book1.authors.add(author1)
        book2.authors.add(author2)

        book3 = sample_book(title="Book without authors")

        res = self.client.get(BOOK_URL, {"authors": f"{author1.id},{author2.id}"})

        serializer1 = BookListSerializer(book1)
        serializer2 = BookListSerializer(book2)
        serializer3 = BookListSerializer(book3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_books_by_title(self):
        book1 = sample_book(title="Book")
        book2 = sample_book(title="Another Book")
        book3 = sample_book(title="No match")

        res = self.client.get(BOOK_URL, {"title": "book"})

        serializer1 = BookListSerializer(book1)
        serializer2 = BookListSerializer(book2)
        serializer3 = BookListSerializer(book3)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_retrieve_books_detail(self):
        book = sample_book()
        url = book_detail_url(book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_unauthorized(self):
        author = sample_author()

        payload = {
            "title": "Title",
            "cover": "HARD",
            "authors": author.id,
            "inventory": 2,
            "daily_fee": 0.50,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_create_book_forbidden(self):
        author = sample_author()

        payload = {
            "title": "Title",
            "cover": "HARD",
            "authors": author.id,
            "inventory": 2,
            "daily_fee": 0.50,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Title",
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": 0.50,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_create_book_with_authors(self):
        author1 = sample_author(first_name="Author1")
        author2 = sample_author(first_name="Author2")
        payload = {
            "title": "Title",
            "cover": "HARD",
            "authors": [author1.id, author2.id],
            "inventory": 2,
            "daily_fee": 0.50,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data["id"])
        authors = book.authors.all()
        self.assertEqual(authors.count(), 2)
        self.assertIn(author1, authors)
        self.assertIn(author2, authors)

    def test_raise_validation_error_when_created_book_with_inventory_less_than_zero(
        self,
    ):
        payload = {
            "title": "Title",
            "cover": "HARD",
            "inventory": -1,
            "daily_fee": 0.50,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_raise_validation_error_when_created_book_with_daily_fee_less_than_zero(
        self,
    ):
        payload = {
            "title": "Title",
            "cover": "HARD",
            "inventory": 2,
            "daily_fee": -0.50,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_book(self):
        payload = {
            "title": "TitleUpdated",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": 2.50,
        }

        book = sample_book()
        url = book_detail_url(book.id)

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_delete_book(self):
        book = sample_book()
        url = book_detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
