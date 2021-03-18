import json

from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404

from reviews import models as review_models
from reservations import models as reservation_models


@login_required
def createReview(request, reservation_pk):
    if request.method == "POST":
        reservation = reservation_models.Reservation.objects.get_or_none(
            pk=reservation_pk
        )
        if reservation is None:
            messages.error(request, "Reservation does not exist")
            return redirect(
                reverse("reservations:detail", kwargs={"pk": reservation_pk})
            )

        if reservation.guest.pk != request.user.pk:
            raise Http404("Page not found")

        review = request.POST.get("review")
        accuracy = int(request.POST.get("accuracy"))
        communication = int(request.POST.get("communication"))
        cleanliness = int(request.POST.get("cleanliness"))
        location = int(request.POST.get("location"))
        check_in = int(request.POST.get("check_in"))
        value = int(request.POST.get("value"))

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


@login_required
def updateReview(request, room_pk, review_pk):
    review = review_models.Review.objects.get_or_none(pk=review_pk)

    if review is None:
        messages.error(request, "Review doesn't exist")

    if review.user.pk != request.user.pk:
        raise Http404("Page not found")

    content = json.loads(request.body.decode("utf-8"))
    text = content["review"]
    review.review = text
    review.save()

    return HttpResponse(200)


@login_required
def deleteReview(request, room_pk, review_pk):
    review = review_models.Review.objects.get_or_none(pk=review_pk)

    if review is None:
        messages.error(request, "Review doesn't exist")

    if review.user.pk != request.user.pk:
        raise Http404("Page not found")

    review.delete()

    return HttpResponse(200)
