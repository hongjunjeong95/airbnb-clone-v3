from django.contrib.auth import authenticate
from django.views.generic import FormView
from django.db.utils import IntegrityError
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from . import forms


class SignUpView(FormView):
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
