from django.urls import path

from borrowings.views import BorrowingsListCreateView, BorrowingsDetailView, borrowings_return_view

app_name = "borrowings"

urlpatterns = [
    path("", BorrowingsListCreateView.as_view(), name="borrowings-list"),
    path("<int:pk>/", BorrowingsDetailView.as_view(), name="borrowings-detail"),
    path("<int:pk>/return/", borrowings_return_view, name="borrowings-return"),
]
