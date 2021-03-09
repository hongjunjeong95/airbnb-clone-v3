from django.views.generic import ListView, DetailView, FormView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import Http404

from . import models as room_models
from photos import models as photo_models
from . import forms
from users import mixins
from users.exception import HostOnly


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


class CreateRoomView(mixins.LoggedInOnlyView, SuccessMessageMixin, FormView):

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


class EditRoomView(mixins.LoggedInOnlyView, UpdateView):

    model = room_models.Room
    template_name = "pages/rooms/edit_room.html"
    fields = (
        "name",
        "country",
        "city",
        "address",
        "price",
        "guests",
        "bedrooms",
        "beds",
        "bathrooms",
        "description",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
        "instant_book",
    )

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["name"].widget.attrs = {"class": "w-full", "placeholder": "Name"}
        form.fields["city"].widget.attrs = {"class": "w-full", "placeholder": "City"}
        form.fields["address"].widget.attrs = {
            "class": "w-full",
            "placeholder": "Address",
        }
        form.fields["price"].widget.attrs = {"class": "w-full", "placeholder": "Price"}
        form.fields["guests"].widget.attrs = {
            "class": "w-full",
            "placeholder": "Guests",
        }
        form.fields["bedrooms"].widget.attrs = {
            "class": "w-full",
            "placeholder": "Bedrooms",
        }
        form.fields["beds"].widget.attrs = {"class": "w-full", "placeholder": "Beds"}
        form.fields["bathrooms"].widget.attrs = {
            "class": "w-full",
            "placeholder": "Bathrooms",
        }
        form.fields["description"].widget.attrs = {
            "class": "h-40",
            "placeholder": "Description",
        }
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = context["room"]

        s_amenities = room.amenities.all()
        s_facilities = room.facilities.all()
        s_house_rules = room.house_rules.all()

        context["s_amenities"] = s_amenities
        context["s_facilities"] = s_facilities
        context["s_house_rules"] = s_house_rules
        return context


@login_required
def deleteRoom(request, pk):
    try:
        if not request.session.get("is_hosting"):
            raise HostOnly("Change ot host mode")

        room = room_models.Room.objects.get_or_none(pk=pk)
        if request.user.pk != room.host.pk:
            raise Http404("Page Not Found")

        if room is None:
            messages.error(request, "Room does not exsit")
            return redirect(reverse("core:home"))
        room.delete()

        messages.success(request, f"Delete {room.name} successfully")

        return redirect(reverse("users:profile", kwargs={"pk": request.user.pk}))
    except HostOnly as error:
        messages.error(request, error)
        return redirect(reverse("core:home"))