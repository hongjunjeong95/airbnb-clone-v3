from django.views.generic import ListView
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from . import models


class HomeView(ListView):
    model = models.Room
    template_name = "pages/root/home.html"
    context_object_name = "rooms"
    paginate_by = 12
    paginate_orphans = 6
    ordering = "created"

    def get_context_data(self):
        page = int(self.request.GET.get("page", 1))
        page_sector = (page - 1) // 5
        page_sector = page_sector * 5
        context = super().get_context_data()
        context["page_sector"] = page_sector
        return context


def roomDetail(request, pk):
    room = models.Room.objects.get(pk=pk)
    if room is None:
        messages.error(request, "Room does not exsit")
        return redirect(reverse("core:home"))
    month = room.host.date_joined.strftime("%b")

    return render(
        request,
        "pages/rooms/room_detail.html",
        context={"room": room, "joined_month": month},
    )
