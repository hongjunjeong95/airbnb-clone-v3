from django.urls import path
from conversations import views


app_name = "conversations"

urlpatterns = [
    path(
        "<int:host_pk>/<int:guest_pk>/<int:room_pk>/",
        views.createConversation,
        name="create-conversation",
    ),
    path(
        "<int:pk>/conversation-detail/",
        views.ConversationDetailView.as_view(),
        name="conversation-detail",
    ),
]
