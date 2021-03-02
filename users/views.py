from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import FormView
from django.db.utils import IntegrityError
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from . import forms, mixins


class SignUpView(mixins.LoggedOutOnlyView, FormView):

    """ Sign Up View """

    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    template_name = "pages/users/signup.html"

    def form_valid(self, form):
        try:
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(self.request, username=email, password=password)
            messages.success(self.request, f"{user.first_name} signed up")
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, "User already exists")
            return redirect(reverse("users:signup"))


class LoginView(mixins.LoggedOutOnlyView, FormView):

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
        messages.success(self.request, f"{user.first_name} logged in")
        login(self.request, user)
        return super().form_valid(form)


@login_required
def log_out(request):
    messages.info(request, f"See you later {request.user.first_name}")
    logout(request)
    return redirect(reverse("core:home"))
