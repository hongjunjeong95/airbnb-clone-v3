from django.shortcuts import redirect, reverse, render
from django.views.generic import DetailView
from django.core.paginator import Paginator

from conversations import models as conversation_models
from users import models as user_models
from users import mixins


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


class ConversationDetailView(mixins.LoggedInOnlyView, DetailView):

    """ Conversation Detail View Definition """

    model = conversation_models.Conversation
    template_name = "pages/conversations/conversation_detail.html"


def conversationList(request):
    qs = conversation_models.Conversation.objects.filter(participants=request.user)

    page = request.GET.get("page", 1)

    if page == "":
        page = 1
    else:
        page = int(page)

    page_sector = ((page - 1) // 5) * 5
    paginator = Paginator(qs, 12, orphans=6)
    conversations = paginator.get_page(page)

    return render(
        request,
        "pages/conversations/conversation_host_list.html",
        context={"conversations": conversations, "page_sector": page_sector},
    )
