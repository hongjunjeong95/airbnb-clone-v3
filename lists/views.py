from django.shortcuts import redirect, reverse
from django.views.generic import ListView
from django.contrib import messages

from lists import models as list_models
from rooms import models as room_models
from users import mixins


def toggleList(request, room_pk):
    user = request.user
    if str(user) == "AnonymousUser":
        return redirect(reverse("users:login"))
    action = request.GET.get("action")
    room = room_models.Room.objects.get(pk=room_pk)
    if room is not None and action is not None:
        the_list, b = list_models.List.objects.get_or_create(
            user=request.user, name="My Favorite Houses"
        )
        if action == "add":
            the_list.rooms.add(room)
        elif action == "remove":
            the_list.rooms.remove(room)
    return redirect(reverse("core:home"))


class FavsList(mixins.LoggedInOnlyView, ListView):

    """ Fav List View Definition """

    template_name = "pages/lists/fav_list.html"
    context_object_name = "rooms"
    paginate_by = 12
    paginate_orphans = 6
    ordering = "created"

    def get_queryset(self):
        the_list = list_models.List.objects.get_or_none(user=self.request.user)
        if the_list is None:
            messages.error(self.request, "List does not exist")
            return redirect(reverse("core:home"))

        return the_list.rooms.all()

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
