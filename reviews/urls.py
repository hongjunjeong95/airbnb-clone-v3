from django.urls import path
from reviews import views

app_name = "reviews"

urlpatterns = [path("<int:reservation_pk>/create/", views.createReview, name="create")]
