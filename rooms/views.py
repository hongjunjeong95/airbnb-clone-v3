from django.views.generic import ListView, DetailView, FormView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.http import Http404

from django_countries import countries

from rooms import models as room_models
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


class CreateRoomView(mixins.LoggedInOnlyView, mixins.HostOnlyView, FormView):

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


class EditRoomView(mixins.LoggedInOnlyView, mixins.HostOnlyView, UpdateView):

    """ Edit Room View Definition """

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


def searchView(request):
    city = request.GET.get("city", "Anywhere")
    country = request.GET.get("country")
    price = int(request.GET.get("price", 0))
    guests = int(request.GET.get("guests", 0))
    bedrooms = int(request.GET.get("bedrooms", 0))
    beds = int(request.GET.get("beds", 0))
    bathrooms = int(request.GET.get("bathrooms", 0))
    room_type = int(request.GET.get("room_type", 0))
    s_amenities = request.GET.getlist("amenities")
    s_facilities = request.GET.getlist("facilities")
    s_house_rules = request.GET.getlist("house_rules")
    instant_book = bool(request.GET.get("instant_book"))

    room_types = room_models.RoomType.objects.all()
    amenities = room_models.Amenity.objects.all()
    facilities = room_models.Facility.objects.all()
    house_rules = room_models.HouseRule.objects.all()

    filter_args = {}

    form = {
        "city": city,
        "countries": countries,
        "price": price,
        "guests": guests,
        "bedrooms": bedrooms,
        "beds": beds,
        "bathrooms": bathrooms,
        "room_types": room_types,
        "amenities": amenities,
        "facilities": facilities,
        "house_rules": house_rules,
        "instant_book": instant_book,
    }

    choices = {
        "s_country": country,
        "s_room_type": room_type,
        "s_amenities": s_amenities,
        "s_facilities": s_facilities,
        "s_house_rules": s_house_rules,
    }

    if city != "Anywhere":
        filter_args["city__startswith"] = city

    filter_args["country"] = country

    if price != 0:
        filter_args["price__lte"] = price
    if guests != 0:
        filter_args["guests__gte"] = guests
    if bedrooms != 0:
        filter_args["bedrooms__gte"] = bedrooms
    if beds != 0:
        filter_args["beds__gte"] = beds
    if bathrooms != 0:
        filter_args["bathrooms__gte"] = bathrooms

    if room_type != 0:
        filter_args["room_type__pk"] = room_type

    if len(s_amenities) > 0:
        for s_amenity in s_amenities:
            filter_args["amenities__pk"] = int(s_amenity)

    if len(s_facilities) > 0:
        for s_facility in s_facilities:
            filter_args["facilities__pk"] = int(s_facility)

    if len(s_house_rules) > 0:
        for s_house_rule in s_house_rules:
            filter_args["house_rules__pk"] = int(s_house_rule)

    if instant_book:
        filter_args["instant_book"] = instant_book

    qs = room_models.Room.objects.filter(**filter_args).order_by("created")
    paginoatr = Paginator(qs, 12, orphans=6)
    page = int(request.GET.get("page", 1))
    page_sector = (page - 1) // 5
    page_sector = page_sector * 5
    rooms = paginoatr.get_page(page)

    return render(
        request,
        "pages/root/search.html",
        context={"rooms": rooms, "page_sector": page_sector, **form, **choices},
    )


@login_required
def photoList(request, pk):
    try:
        if not request.session.get("is_hosting"):
            raise HostOnly("Change host mode")

        page = request.GET.get("page", 1)

        if page == "":
            page = 1
        else:
            page = int(page)

        page_sector = ((page - 1) // 5) * 5

        room = room_models.Room.objects.get(pk=pk)
        if room is None:
            messages.error(request, "Room does not exsit")
            return redirect(reverse("rooms:room-detail", kwargs={"pk": room.pk}))

        qs = room.photos.all()
        paginator = Paginator(qs, 10, orphans=5)
        photos = paginator.get_page(page)

        if request.user.pk != room.host.pk:
            raise Http404("Page Not Found")

        return render(
            request,
            "pages/rooms/photos/photo_list.html",
            context={
                "photos": photos,
                "page_sector": page_sector,
                "room": room,
            },
        )
    except HostOnly as error:
        messages.error(request, error)
        return redirect(reverse("core:home"))


class PhotoListView(mixins.LoggedInOnlyView, mixins.HostOnlyView, DetailView):

    """ Photo List View Definition """

    model = room_models.Room
    template_name = "pages/rooms/photos/photo_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        page = int(self.request.GET.get("page", 1))
        page_sector = (page - 1) // 5
        page_sector = page_sector * 5
        context["page_sector"] = page_sector

        room = context["room"]
        qs = room.photos.all()
        paginator = Paginator(qs, 10, orphans=5)
        photos = paginator.get_page(page)
        context["photos"] = photos
        return context


class CreatePhotoView(mixins.LoggedInOnlyView, mixins.HostOnlyView, FormView):

    """ Create Photo View Definition """

    form_class = forms.CreatePhotoForm
    template_name = "pages/rooms/photos/create_photo.html"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        room = room_models.Room.objects.get(pk=pk)

        if self.request.user != room.host:
            raise Http404("Page not found")

        context = super().get_context_data(**kwargs)
        context["room"] = room
        return context

    def form_valid(self, form):
        pk = self.kwargs.get(self.pk_url_kwarg)
        room = room_models.Room.objects.get(pk=pk)
        photo = form.save()
        photo.room = room
        photo.save()
        return redirect(reverse("rooms:photo-list", kwargs={"pk": pk}))


class EditPhotoView(
    mixins.LoggedInOnlyView, mixins.HostOnlyView, SuccessMessageMixin, UpdateView
):

    """ Edit Photo View Definition """

    model = photo_models.Photo
    template_name = "pages/rooms/photos/edit_photo.html"
    fields = ("caption",)
    pk_url_kwarg = "photo_pk"
    success_message = "Photo Updated"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["caption"].widget.attrs = {"placeholder": "Caption"}
        return form

    def get_object(self, queryset=None):
        photo = super().get_object(queryset=queryset)
        if self.request.user.pk != photo.room.host.pk:
            raise Http404("Page not found")
        return photo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = context["photo"]
        context["room"] = photo.room
        return context

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photo-list", kwargs={"pk": room_pk})
