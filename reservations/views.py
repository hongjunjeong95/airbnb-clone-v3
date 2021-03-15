import datetime
from django.shortcuts import redirect, reverse, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator

from reservations import models as reservation_models
from rooms import models as room_models


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
        reservation_models.Reservation.objects.create(
            status=reservation_models.Reservation.STATUS_PENDING,
            guest=request.user,
            room=room,
            check_in=date_obj,
            check_out=date_obj + datetime.timedelta(days=1),
        )

        messages.success(request, f"Reserve {room} successfully")
        return redirect(reverse("rooms:room-detail", kwargs={"pk": room_pk}))


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