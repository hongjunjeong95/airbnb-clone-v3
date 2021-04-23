from django.shortcuts import redirect, reverse
from django.views.generic import DetailView, ListView
from django.contrib import messages

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


class ConversationList(mixins.LoggedInOnlyView, ListView):

    """ Conversation List View Definition """

    template_name = "pages/conversations/conversation_host_list.html"
    context_object_name = "conversations"
    paginate_by = 12
    paginate_orphans = 6
    ordering = "created"

    def get_queryset(self):
        return conversation_models.Conversation.objects.filter(
            participants=self.request.user
        )

    def get_context_data(self, **kwargs):
        page = int(self.request.GET.get("page", 1))
        if page == "":
            page = 1
        else:
            page = int(page)
        page_sector = (page - 1) // 5
        page_sector = page_sector * 5
        context = super().get_context_data()
        context["page_sector"] = page_sector
        return context


def createMessage(request, conversation_pk):
    message = request.POST.get("message")
    try:
        conversation = conversation_models.Conversation.objects.get(pk=conversation_pk)
        pk = []
        for participant in conversation.participants.all():
            pk.append(participant.pk)
        if message is not None:
            conversation_models.Message.objects.create(
                message=message, user=request.user, conversation=conversation
            )
    except conversation_models.Conversation.DoesNotExist:
        messages.error(request, "Conversation does not exist")
    return redirect(
        reverse("conversations:conversation-detail", kwargs={"pk": conversation.pk})
    )
