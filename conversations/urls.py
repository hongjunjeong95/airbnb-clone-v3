from django.urls import path
from . import views


app_name = "conversations"

urlpatterns = [
    path(
        "<int:host_pk>/<int:guest_pk>/",
        views.createConversation,
        name="create-conversation",
    ),
]
