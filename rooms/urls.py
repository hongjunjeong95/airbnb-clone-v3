from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [path("<int:pk>/", views.RoomDetailView.as_view(), name="room-detail")]
