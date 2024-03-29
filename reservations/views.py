import datetime
from django.shortcuts import redirect, reverse, render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator

from reservations import models as reservation_models
from rooms import models as room_models
from users import mixins


class CreateError(Exception):
    pass


@login_required
def createReservation(request, room_pk, year, month, day):
    try:
        room = room_models.Room.objects.get(pk=room_pk)
        date_obj = datetime.datetime(year, month, day)
        reservation_models.BookedDay.objects.get(day=date_obj, reservation__room=room)
        raise CreateError()
    except (room_models.Room.DoesNotExist, CreateError):
        messages.error(request, "Can't reserve that room")
        return redirect(reverse("core:home"))
    except reservation_models.BookedDay.DoesNotExist:
        reservation = reservation_models.Reservation.objects.create(
            status=reservation_models.Reservation.STATUS_PENDING,
            guest=request.user,
            room=room,
            check_in=date_obj,
            check_out=date_obj + datetime.timedelta(days=1),
        )

        messages.success(request, f"Reserve {room} successfully")
        return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


@login_required
def reservationList(request, user_pk):
    qs = reservation_models.Reservation.objects.filter(guest_id=user_pk)

    if not qs:
        # if 'qs' Queryset is empty, execute this code.
        return render(
            request,
            "pages/reservations/reservation_list.html",
            context={"reservations": qs},
        )

    for reservation in qs:
        # Route Protection
        if reservation.guest != request.user:
            raise Http404()

    page = request.GET.get("page", 1)
    if page == "":
        page = 1
    else:
        page = int(page)
    page_sector = (page - 1) // 5
    page_sector = page_sector * 5
    paginator = Paginator(qs, 8, orphans=4)
    reservations = paginator.get_page(page)
    return render(
        request,
        "pages/reservations/reservation_list.html",
        context={"reservations": reservations, "page_sector": page_sector},
    )


class ReservationListView(mixins.LoggedInOnlyView, ListView):

    """ Reservation List View Definition """

    template_name = "pages/reservations/reservation_list.html"
    context_object_name = "reservations"
    paginate_by = 12
    paginate_orphans = 6
    ordering = "created"

    def get_queryset(self):
        user_pk = self.kwargs.get("user_pk")

        if user_pk != self.request.user.pk:
            return redirect(reverse("core:home"))

        return reservation_models.Reservation.objects.filter(guest_id=user_pk)

    def get_context_data(self, **kwargs):
        page = int(self.request.GET.get("page", 1))
        page_sector = (page - 1) // 5
        page_sector = page_sector * 5
        context = super().get_context_data()
        context["page_sector"] = page_sector
        return context


class ReservationDetailView(mixins.LoggedInOnlyView, DetailView):

    """ Reservation Detail View Definition """

    model = reservation_models.Reservation
    template_name = "pages/reservations/reservation_detail.html"

    def get_context_data(self, **kwargs):
        # Get room
        context = super().get_context_data(**kwargs)
        reservation = context["reservation"]
        room = reservation.room
        context["room"] = room

        if reservation.guest.pk != self.request.user.pk:
            return redirect(reverse("core:home"))

        # Get days
        bookedDays = reservation.bookedDays.all()
        days = []
        for day in bookedDays:
            day = str(day)
            day = int(day.split("-")[2])
            days.append(day)

        context["days"] = days
        return context


@login_required
def reservationHostList(request, pk):
    reservations = reservation_models.Reservation.objects.filter(room__host_id=pk)

    qs = []
    for reservation in reservations:
        # Route Protection
        if reservation.room.host != request.user:
            raise Http404()
        if reservation.room not in qs:
            qs.append(reservation.room)
    page = request.GET.get("page", 1)
    if page == "":
        page = 1
    else:
        page = int(page)
    page_sector = (page - 1) // 5
    page_sector = page_sector * 5
    paginator = Paginator(qs, 8, orphans=4)
    rooms = paginator.get_page(page)
    return render(
        request,
        "pages/reservations/reservation_room_list_onHost.html",
        context={"rooms": rooms, "page_sector": page_sector},
    )


class ReservationListOnRoomView(mixins.LoggedInOnlyView, ListView):

    """ Reservation List on Room View Definition """

    template_name = "pages/reservations/reservation_list_onRoom.html"
    context_object_name = "reservations"
    paginate_by = 12
    paginate_orphans = 6
    ordering = "created"

    def get_queryset(self):
        user_pk = self.kwargs.get("user_pk")
        room_pk = self.kwargs.get("room_pk")
        reservations = reservation_models.Reservation.objects.filter(
            room__host_id=user_pk, room_id=room_pk
        )

        if user_pk != self.request.user.pk:
            return redirect(reverse("core:home"))

        return reservations

    def get_context_data(self, **kwargs):
        user_pk = self.kwargs.get("user_pk")
        room_pk = self.kwargs.get("room_pk")
        reservations = reservation_models.Reservation.objects.filter(
            room__host_id=user_pk, room_id=room_pk
        )
        room_name = reservations[0].room.name
        context = super().get_context_data()
        context["room_name"] = room_name
        return context


@login_required
def confirmReservation(request, pk):
    reservation = reservation_models.Reservation.objects.get_or_none(pk=pk)
    if reservation is None:
        messages.error(request, "Rservation does not exist")
        return redirect(reverse("core:home"))
    # Route Protection
    if reservation.room.host != request.user:
        raise Http404()
    reservation.status = reservation_models.Reservation.STATUS_CONFIRMED
    reservation.save()

    room = reservation.room

    user_pk = request.user.pk
    room_pk = room.pk

    return redirect(
        reverse(
            "reservations:host-room-list",
            kwargs={
                "user_pk": user_pk,
                "room_pk": room_pk,
            },
        )
    )


@login_required
def cancelReservation(request, pk):
    reservation = reservation_models.Reservation.objects.get_or_none(pk=pk)
    if reservation is None:
        messages.error(request, "Rservation does not exist")
        return redirect(reverse("core:home"))
    if request.user != reservation.guest and request.user != reservation.room.host:
        raise Http404()
    room = reservation.room
    reservation.delete()
    return redirect(reverse("rooms:room-detail", kwargs={"pk": room.pk}))
