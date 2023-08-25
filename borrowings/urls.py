from django.urls import path

from borrowings.views import BorrowingsListCreateView, BorrowingsDetailView

app_name = "borrowings"

urlpatterns = [
    path("", BorrowingsListCreateView.as_view(), name="borrowings-list"),
    path("<int:pk>/", BorrowingsDetailView.as_view(), name="borrowings-detail"),
]
