from django.urls import path
from rooms import views

app_name = "rooms"

urlpatterns = [
    path("<int:pk>/", views.RoomDetailView.as_view(), name="room-detail"),
    path("create/", views.CreateRoomView.as_view(), name="create-room"),
    path("<int:pk>/edit/", views.EditRoomView.as_view(), name="edit-room"),
    path("<int:pk>/delete/", views.deleteRoom, name="delete-room"),
    path("<int:pk>/photos/", views.PhotoListView.as_view(), name="photo-list"),
    path(
        "<int:pk>/photos/create/", views.CreatePhotoView.as_view(), name="create-photo"
    ),
    path(
        "<int:room_pk>/photos/<int:photo_pk>/edit/",
        views.EditPhotoView.as_view(),
        name="edit-photo",
    ),
]
