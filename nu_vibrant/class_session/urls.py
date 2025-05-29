from django.urls import path
from . import views

app_name = "class_session"

urlpatterns = [
    path("", views.ClassSessionListView.as_view(), name="list"),
    path("<int:pk>/book/", views.ClassBookingCreateView.as_view(), name="book"),
    path("bookings/", views.ClassBookingListView.as_view(), name="bookings"),
]