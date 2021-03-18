import json

from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.http import HttpResponse

from reviews import models as review_models
from reservations import models as reservation_models


def createReview(request, reservation_pk):
    if request.method == "POST":
        review = request.POST.get("review")
        accuracy = int(request.POST.get("accuracy"))
        communication = int(request.POST.get("communication"))
        cleanliness = int(request.POST.get("cleanliness"))
        location = int(request.POST.get("location"))
        check_in = int(request.POST.get("check_in"))
        value = int(request.POST.get("value"))

        reservation = reservation_models.Reservation.objects.get_or_none(
            pk=reservation_pk
        )
        if reservation is None:
            messages.error(request, "Reservation does not exist")
            return redirect(
                reverse("reservations:detail", kwargs={"pk": reservation_pk})
            )
        room = reservation.room

        review = review_models.Review.objects.create(
            review=review,
            accuracy=accuracy,
            communication=communication,
            cleanliness=cleanliness,
            location=location,
            check_in=check_in,
            value=value,
            user=request.user,
            room=room,
        )
        return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


def updateReview(request, room_pk, review_pk):
    review = review_models.Review.objects.get_or_none(pk=review_pk)
    if review is None:
        messages.error(request, "Review doesn't exist")

    content = json.loads(request.body.decode("utf-8"))
    text = content["review"]
    review.review = text
    review.save()

    return HttpResponse(200)
