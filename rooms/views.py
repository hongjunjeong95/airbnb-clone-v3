from django.views.generic import ListView, DetailView
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


class RoomDetailView(DetailView):
    model = models.Room
    template_name = "pages/rooms/room_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = context["room"]
        month = room.host.date_joined.strftime("%b")
        context["joined_month"] = month
        return context
