from django.contrib.auth import authenticate, login
from django.views.generic import FormView
from django.db.utils import IntegrityError
from django.shortcuts import redirect, reverse, render
from django.urls import reverse_lazy
from . import forms


class SignUpView(FormView):

    """ Sign Up View """

    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    template_name = "pages/users/signup.html"

    def form_valid(self, form):
        try:
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            authenticate(self.request, username=email, password=password)
            return super().form_valid(form)
        except IntegrityError as error:
            print(error)
            return redirect(reverse("users:signup"))


def loginView(request):
    if request.method == "GET":
        form = forms.LoginForm
    elif request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(request, username=email, password=password)
            if user is None:
                return redirect(reverse("users:login"))
            login(request, user)
            return redirect(reverse("core:home"))
    return render(request, "pages/users/login.html", {"form": form})
