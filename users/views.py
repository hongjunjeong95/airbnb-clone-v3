from django.contrib.auth import authenticate, login, logout
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


class LoginView(FormView):

    """ Login View """

    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")
    template_name = "pages/users/login.html"

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is None:
            return redirect(reverse("users:login"))
        login(self.request, user)
        return super().form_valid(form)


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(reverse("core:home"))
    else:
        return redirect(reverse("users:login"))