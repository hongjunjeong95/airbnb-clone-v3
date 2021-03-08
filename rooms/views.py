from django.views.generic import ListView, DetailView, FormView
from django.shortcuts import redirect, reverse
from django.contrib.messages.views import SuccessMessageMixin

from . import models as room_models
from photos import models as photo_models
from . import forms
from users import mixins


class HomeView(ListView):

    """ Home View Definition """

    model = room_models.Room
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

    """ Room Detail View Definition """

    model = room_models.Room
    template_name = "pages/rooms/room_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = context["room"]
        month = room.host.date_joined.strftime("%b")
        context["joined_month"] = month
        return context


class CreateRoomView(mixins.LoginOnlyView, SuccessMessageMixin, FormView):

    """ Create Room View Definition """

    form_class = forms.CreateRoomForm
    template_name = "pages/rooms/create_room.html"

    def form_valid(self, form):
        room = form.save()
        room.host = self.request.user
        room.save()
        form.save_m2m()
        caption = self.request.POST.get("caption")
        photo = self.request.FILES.get("photo")

        photo_models.Photo.objects.create(file=photo, caption=caption, room_id=room.pk)
        return redirect(reverse("rooms:room-detail", kwargs={"pk": room.pk}))
