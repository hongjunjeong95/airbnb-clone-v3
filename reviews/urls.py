from django.urls import path
from reviews import views

app_name = "reviews"

urlpatterns = [
    path("<int:reservation_pk>/create/", views.createReview, name="create"),
    path("<int:room_pk>/<int:review_pk>/update/", views.updateReview, name="update"),
]
