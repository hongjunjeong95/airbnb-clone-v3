from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate
from . import forms


def signUp(request):
    if request.method == "GET":
        form = forms.SignUpForm
        return render(request, "pages/users/signup.html", {"form": form})
    elif request.method == "POST":
        form = forms.SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            user.avatar = request.FILES.get("avatar")
            user.save()
            return redirect(reverse("core:home"))
        else:
            print(form.errors)
            return redirect(reverse("users:signup"))
