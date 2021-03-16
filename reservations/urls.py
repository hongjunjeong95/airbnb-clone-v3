from django.urls import path
from reservations import views

app_name = "reservations"

urlpatterns = [
    path(
        "<int:room_pk>/create/<int:year>-<int:month>-<int:day>/",
        views.createReservation,
        name="create",
    ),
    path(
        "user/<int:user_pk>/",
        views.ReservationListView.as_view(),
        name="list",
    ),
    path(
        "<int:pk>/",
        views.ReservationDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:pk>/reservation/list/",
        views.reservationHostList,
        name="host-list",
    ),
]
