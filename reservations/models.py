import datetime
from django.db import models
from django.db.models import Q
from django.utils import timezone
from core import models as core_models


class BookedDay(core_models.TimeStampedModel):
    day = models.DateField()
    reservation = models.ForeignKey(
        "Reservation", related_name="bookedDays", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"

    def __str__(self):
        return str(self.day)


class Reservation(core_models.TimeStampedModel):

    """ Reservation Model Definition """

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )

    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    guest = models.ForeignKey(
        "users.User", related_name="reservations", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "rooms.Room", related_name="reservations", on_delete=models.CASCADE
    )
    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f"{self.room} - {self.check_in}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            start = self.check_in
            end = self.check_out
            difference = end - start

            # Check if reserved room exsists
            booked_room_existed = BookedDay.objects.filter(
                reservation__room=self.room
            ).exists()

            if booked_room_existed:

                # Check if the days are reserved with that room
                bookedDays = BookedDay.objects.filter(
                    Q(reservation__room=self.room) & Q(day__range=(start, end))
                ).exists()
                if not bookedDays:
                    super().save(*args, **kwargs)
                    for i in range(difference.days + 1):
                        day = start + datetime.timedelta(days=i)
                        BookedDay.objects.create(day=day, reservation=self)
                    return
            else:
                super().save(*args, **kwargs)
                for i in range(difference.days + 1):
                    day = start + datetime.timedelta(days=i)
                    BookedDay.objects.create(day=day, reservation=self)
                return
        return

    def in_progress(self):
        now = timezone.localtime().date()
        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True

    def is_finished(self):
        now = timezone.localtime().date()
        is_finished_var = now > self.check_out
        if is_finished_var:
            BookedDay.objects.filter(reservation=self).delete()
        return is_finished_var

    is_finished.boolean = True
