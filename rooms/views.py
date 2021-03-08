from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django_countries import countries

from . import models as room_models
from photos import models as photo_models
from . import forms
from users import mixins
from users.exception import HostOnly, VerifyUser


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


@login_required
def editRoom(request, pk):
    if request.method == "GET":
        try:
            if not request.session.get("is_hosting"):
                raise HostOnly("Page Not Found")

            room = room_models.Room.objects.get(pk=pk)

            if room is None:
                messages.error(request, "Room does not exsit")
                return redirect(reverse("core:home"))

            if request.user.pk != room.host.pk:
                raise VerifyUser("Page Not Found")

            amenities = room_models.Amenity.objects.all()
            facilities = room_models.Facility.objects.all()
            house_rules = room_models.HouseRule.objects.all()
            room_types = room_models.RoomType.objects.all()

            s_amenities = room.amenities.all()
            s_facilities = room.facilities.all()
            s_house_rules = room.house_rules.all()

            form = {
                "countries": countries,
                "room_types": room_types,
                "amenities": amenities,
                "facilities": facilities,
                "house_rules": house_rules,
            }

            choices = {
                "s_amenities": s_amenities,
                "s_facilities": s_facilities,
                "s_house_rules": s_house_rules,
            }

            return render(
                request, "pages/rooms/edit_room.html", {"room": room, **form, **choices}
            )
        except (HostOnly, VerifyUser) as error:
            messages.error(request, error)
            return redirect(reverse("core:home"))
    elif request.method == "POST":
        try:
            if not request.session.get("is_hosting"):
                raise HostOnly("Page Not Found")

            room = room_models.Room.objects.get(pk=pk)

            if room is None:
                messages.error(request, "Room does not exsit")
                return redirect(reverse("core:home"))

            if request.user.pk != room.host.pk:
                raise VerifyUser("Page Not Found")

            name = request.POST.get("name")
            city = request.POST.get("city")
            address = request.POST.get("address")
            country_code = request.POST.get("country")
            price = int(request.POST.get("price", 0))
            guests = int(request.POST.get("guests", 0))
            bedrooms = int(request.POST.get("bedrooms", 0))
            beds = int(request.POST.get("beds", 0))
            bathrooms = int(request.POST.get("bathrooms", 0))
            room_type = int(request.POST.get("room_type", 0))
            description = request.POST.get("description")
            amenities = request.POST.getlist("amenities")
            facilities = request.POST.getlist("facilities")
            house_rules = request.POST.getlist("house_rules")
            instant_book = bool(request.POST.get("instant_book"))

            s_room_type = room_models.RoomType.objects.get(pk=room_type)

            room.name = name
            room.city = city
            room.address = address
            room.price = price
            room.guests = guests
            room.bedrooms = bedrooms
            room.beds = beds
            room.bathrooms = bathrooms
            room.room_type = s_room_type
            room.description = description
            room.instant_book = instant_book

            room.country = country_code
            room.save()

            room.amenities.set(amenities)
            room.facilities.set(facilities)
            room.house_rules.set(house_rules)

            messages.success(request, f"Edit {room.name} successfully")
            return redirect(reverse("rooms:room-detail", kwargs={"pk": room.pk}))
        except (HostOnly, VerifyUser) as error:
            messages.error(request, error)
            return redirect(reverse("core:home"))
