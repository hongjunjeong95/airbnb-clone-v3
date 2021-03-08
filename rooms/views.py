from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django_countries import countries
from . import models as room_models
from photos import models as photo_models


class HomeView(ListView):
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
    model = room_models.Room
    template_name = "pages/rooms/room_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = context["room"]
        month = room.host.date_joined.strftime("%b")
        context["joined_month"] = month
        return context


@login_required
def creatRoom(request):
    if request.method == "GET":
        if not request.session.get("is_hosting"):
            raise Http404("Page Not Found")

        room_types = room_models.RoomType.objects.all()
        amenities = room_models.Amenity.objects.all()
        facilities = room_models.Facility.objects.all()
        house_rules = room_models.HouseRule.objects.all()

        form = {
            "countries": countries,
            "room_types": room_types,
            "amenities": amenities,
            "facilities": facilities,
            "house_rules": house_rules,
        }

        return render(request, "pages/rooms/create_room.html", {**form})
    elif request.method == "POST":
        if not request.session.get("is_hosting"):
            raise Http404("Page Not Found")

        host = request.user
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
        caption = request.POST.get("caption")
        photo = request.FILES.get("photo")
        instant_book = bool(request.POST.get("instant_book"))

        room = room_models.Room.objects.create(
            name=name,
            city=city,
            address=address,
            price=price,
            guests=guests,
            bedrooms=bedrooms,
            beds=beds,
            bathrooms=bathrooms,
            description=description,
            host=host,
            room_type_id=room_type,
            instant_book=instant_book,
        )

        room.country = country_code

        room.amenities.set(amenities)
        room.facilities.set(facilities)
        room.house_rules.set(house_rules)
        room.save()

        photo = photo_models.Photo.objects.create(
            file=photo, caption=caption, room_id=room.pk
        )

        messages.success(request, f"Create {room.name} successfully")
        return redirect(reverse("rooms:room-detail", kwargs={"pk": room.pk}))
