from django.shortcuts import render, redirect, reverse
from django.views.generic import DetailView

from conversations import models as conversation_models
from users import models as user_models


def createConversation(request, host_pk, guest_pk, room_pk):
    try:
        host = user_models.User.objects.get(pk=host_pk)
        if host_pk == guest_pk:
            return redirect(reverse("rooms:room-detail", kwargs={"pk": room_pk}))
        guest = user_models.User.objects.get(pk=guest_pk)
        conversation = conversation_models.Conversation.objects.filter(
            participants=guest
        ).get(participants=host)

        return redirect(
            reverse("conversations:conversation-detail", kwargs={"pk": conversation.pk})
        )
    except conversation_models.Conversation.DoesNotExist:
        conversation = conversation_models.Conversation.objects.create()
        conversation.participants.add(host, guest)
        return redirect(
            reverse("conversations:conversation-detail", kwargs={"pk": conversation.pk})
        )


def conversationDetail(request, pk):
    conversation = conversation_models.Conversation.objects.get(pk=pk)

    return render(
        request,
        "pages/conversations/conversation_detail.html",
        context={"conversation": conversation},
    )


class ConversationDetailView(DetailView):

    """ Conversation Detail View Definition """

    model = conversation_models.Conversation
    template_name = "pages/conversations/conversation_detail.html"
