from django.urls import path

from borrowings.views import (
    BorrowingListCreateView,
    BorrowingDetailView,
    borrowing_return_view,
)

app_name = "borrowings"

urlpatterns = [
    path("", BorrowingListCreateView.as_view(), name="borrowings-list"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowings-detail"),
    path("<int:pk>/return/", borrowing_return_view, name="borrowings-return"),
]
