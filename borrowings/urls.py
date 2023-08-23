from django.urls import path

from borrowings.views import BorrowingsListView, BorrowingsDetailView

app_name = "borrowings"

urlpatterns = [
    path("", BorrowingsListView.as_view(), name="borrowings-list"),
]
