from django.shortcuts import render, redirect, reverse
from django.core.exceptions import ValidationError
from . import models


def signUp(request):
    if request.method == "GET":
        genders = models.User.GENDER_CHOICES
        languages = models.User.LANGUAGE_CHOICES
        currencies = models.User.CURRENCY_CHOICES

        choices = {
            "genders": genders,
            "languages": languages,
            "currencies": currencies,
        }

        return render(request, "pages/users/signup.html", context={**choices})
    elif request.method == "POST":
        email = request.POST.get("email")
        if email is None:
            return redirect(reverse("users:signup"))

        try:
            # If a registered user with the email exists, raise error
            models.User.objects.get(email=email)
            raise ValidationError("User already exists")
        except models.User.DoesNotExist:
            password = request.POST.get("password")
            if password is None:
                return redirect(reverse("users:signup"))

            password1 = request.POST.get("password1")
            if password1 is None:
                return redirect(reverse("users:signup"))

            # If password doesn't match, raise error
            if password != password1:
                raise ValidationError("Password confirmation does not match")
            user = models.User.objects.create_user(
                username=email, email=email, password=password1
            )

            avatar = request.FILES.get("avatar")
            if avatar is not None and avatar != "":
                user.avatar = avatar

            first_name = request.POST.get("first_name")
            if first_name is not None:
                user.first_name = first_name

            last_name = request.POST.get("last_name")
            if last_name is not None:
                user.last_name = last_name

            gender = request.POST.get("gender")
            if gender is not None:
                user.gender = gender

            language = request.POST.get("language")
            if language is not None:
                user.language = language

            currency = request.POST.get("currency")
            if currency is not None:
                user.currency = currency

            birthdate = request.POST.get("birthdate")
            if birthdate is not None:
                user.birthdate = birthdate

            superhost = bool(request.POST.get("superhost"))
            if superhost is not None:
                user.superhost = superhost

            bio = request.POST.get("bio")
            if bio is not None:
                user.bio = bio

            user.save()
            return redirect(reverse("core:home"))
        except ValidationError as error:
            print(error)
            return redirect("core:home")