from django.urls import path
from lists import views

app_name = "lists"

urlpatterns = [
    path("<int:room_pk>/toggle-list/", views.toggleList, name="toggle-list"),
    path("favs/", views.FavsList.as_view(), name="favs"),
]
