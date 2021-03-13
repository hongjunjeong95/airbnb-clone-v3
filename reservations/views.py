import datetime
from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
