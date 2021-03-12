import os
import requests

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.views.generic import FormView, DetailView, UpdateView
from django.db.utils import IntegrityError
from django.shortcuts import redirect, reverse, render
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404
from . import forms, mixins, models
from .exception import (
    LoggedOutOnlyFunctionView,
    GithubException,
    KakaoException,
    ChangePasswordException,
)
from config import settings


class SignUpView(mixins.LoggedOutOnlyView, FormView):

    """ Sign Up View """

    form_class = forms.SignUpForm
    success_url = reverse_lazy("users:check-email")
    template_name = "pages/users/signup.html"

    def form_valid(self, form):
        try:
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(self.request, username=email, password=password)
            user.verify_email()
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
        if user is not None and user.email_verified is True:
            messages.success(self.request, f"{user.first_name} logged in")
            login(self.request, user)
        else:
            return redirect(reverse("users:login"))
        return super().form_valid(form)


def github_login(request):
    try:
        if request.user.is_authenticated:
            raise LoggedOutOnlyFunctionView("User already logged in")
        client_id = os.environ.get("GH_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/github/callback/"
        scope = "read:user"
        return redirect(
            f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
        )
    except LoggedOutOnlyFunctionView as error:
        messages.error(request, error)
        return redirect("core:home")


def github_login_callback(request):
    try:
        if request.user.is_authenticated:
            raise LoggedOutOnlyFunctionView("User already logged in")
        code = request.GET.get("code", None)
        if code is None:
            raise GithubException("Can't get code")

        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")

        token_request = requests.post(
            f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
            headers={"Accept": "application/json"},
        )
        token_json = token_request.json()
        error = token_json.get("error", None)

        if error is not None:
            print(error)
            raise GithubException("Can't get access token")

        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json",
            },
        )
        profile_json = profile_request.json()
        username = profile_json.get("login", None)

        if username is None:
            raise GithubException("Can't get username from profile_request")

        avatar_url = profile_json.get("avatar_url", None)
        if avatar_url is None:
            raise GithubException("Can't get avatar_url from profile_request")

        name = profile_json.get("name", None)
        if name is None:
            raise GithubException("Can't get name from profile_request")

        email = profile_json.get("email", None)
        if email is None:
            raise GithubException("Can't get email from profile_request")

        bio = profile_json.get("bio", None)
        if bio is None:
            raise GithubException("Can't get bio from profile_request")

        user = models.User.objects.get_or_none(email=email)
        if user is not None:
            if user.login_method != models.User.LOGIN_GITHUB:
                raise GithubException(f"Please login with {user.login_method}")
        else:
            user = models.User.objects.create(
                username=email,
                first_name=name,
                email=email,
                bio=bio,
                login_method=models.User.LOGIN_GITHUB,
                email_verified=True,
            )
            photo_request = requests.get(avatar_url)

            user.avatar.save(f"{name}-avatar", ContentFile(photo_request.content))
            user.set_unusable_password()
            user.save()
        messages.success(request, f"{user.email} logged in with Github")
        login(request, user)
        return redirect(reverse("core:home"))
    except GithubException as error:
        messages.error(request, error)
        return redirect(reverse("core:home"))
    except LoggedOutOnlyFunctionView as error:
        messages.error(request, error)
        return redirect(reverse("core:home"))


def kakao_login(request):
    try:
        if request.user.is_authenticated:
            raise LoggedOutOnlyFunctionView("User already logged in")
        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback/"

        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        )
    except KakaoException as error:
        messages.error(request, error)
        return redirect("core:home")
    except LoggedOutOnlyFunctionView as error:
        messages.error(request, error)
        return redirect("core:home")


def kakao_login_callback(request):
    try:
        if request.user.is_authenticated:
            raise LoggedOutOnlyFunctionView("User already logged in")
        code = request.GET.get("code", None)
        if code is None:
            KakaoException("Can't get code")
        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback/"
        client_secret = os.environ.get("KAKAO_SECRET")
        request_access_token = requests.post(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}&client_secret={client_secret}",
            headers={"Accept": "application/json"},
        )
        access_token_json = request_access_token.json()
        error = access_token_json.get("error", None)
        if error is not None:
            print(error)
            KakaoException("Can't get access token")
        access_token = access_token_json.get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers=headers,
        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get("kakao_account")
        profile = kakao_account.get("profile")

        nickname = profile.get("nickname", None)
        avatar_url = profile.get("profile_image_url", None)
        email = kakao_account.get("email", None)
        gender = kakao_account.get("gender", None)

        user = models.User.objects.get_or_none(email=email)
        if user is not None:
            if user.login_method != models.User.LOGIN_KAKAO:
                raise GithubException(f"Please login with {user.login_method}")
        else:
            user = models.User.objects.create_user(
                email=email,
                username=email,
                first_name=nickname,
                gender=gender,
                login_method=models.User.LOGIN_KAKAO,
            )

            if avatar_url is not None:
                avatar_request = requests.get(avatar_url)
                user.avatar.save(
                    f"{nickname}-avatar", ContentFile(avatar_request.content)
                )
            user.set_unusable_password()
            user.save()
        messages.success(request, f"{user.email} signed up and logged in with Kakao")
        login(request, user)
        return redirect(reverse("core:home"))
    except KakaoException as error:
        messages.error(request, error)
        return redirect(reverse("core:home"))
    except LoggedOutOnlyFunctionView as error:
        messages.error(request, error)
        return redirect(reverse("core:home"))


@login_required
def log_out(request):
    messages.info(request, f"See you later {request.user.first_name}")
    logout(request)
    return redirect(reverse("core:home"))


def check_email(request):
    return render(request, "email/check_email.html")


def complete_verification(request, key):
    try:
        if request.user.is_authenticated:
            raise LoggedOutOnlyFunctionView("Please verify email first")
        user = models.User.objects.get_or_none(email_secret=key)
        if user is None:
            messages.error(request, "User does not exist")
            return redirect(reverse("core:home"))
        user.email_verified = True
        user.email_secret = ""
        user.save()
        login(request, user)
        messages.success(request, f"{user.email} verification is completed")
        return redirect(reverse("core:home"))
    except LoggedOutOnlyFunctionView as error:
        messages.error(request, error)
        return redirect("core:home")


@login_required
def userDetail(request, pk):
    user_obj = models.User.objects.get_or_none(pk=pk)
    if user_obj is None:
        messages.error(request, "User does not exist")
        return redirect(reverse("core:home"))

    page = int(request.GET.get("page", 1))
    page_sector = ((page - 1) // 5) * 5

    qs = user_obj.rooms.all()
    paginator = Paginator(qs, 12, orphans=6)
    rooms = paginator.get_page(page)

    return render(
        request,
        "pages/users/userDetail.html",
        {"user_obj": user_obj, "page_sector": page_sector, "rooms": rooms},
    )


class UserProfileView(mixins.LoggedInOnlyView, DetailView):

    """ User Profile View """

    model = models.User
    context_object_name = "user_obj"
    template_name = "pages/users/userDetail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        page = int(self.request.GET.get("page", 1))
        page_sector = ((page - 1) // 5) * 5

        user_obj = context["user_obj"]
        qs = user_obj.rooms.all()
        paginator = Paginator(qs, 12, orphans=6)
        rooms = paginator.get_page(page)

        context["page_sector"] = page_sector
        context["rooms"] = rooms
        return context


class UpdateProfileView(mixins.LoggedInOnlyView, UpdateView):
    model = models.User
    fields = {
        "avatar",
        "first_name",
        "last_name",
        "email",
        "gender",
        "language",
        "currency",
        "birthdate",
        "superhost",
        "bio",
    }
    template_name = "pages/users/update_profile.html"
    success_message = "Profile Updated"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["email"].widget.attrs = {"placeholder": "Email"}
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last name"}
        form.fields["bio"].widget.attrs = {"placeholder": "Bio"}
        return form


class EmailLoggedInOnly(Exception):
    pass


@login_required
def change_password(request, pk):
    if request.method == "GET":
        try:
            if request.user.login_method != "email":
                raise EmailLoggedInOnly("Page not found 404")
            if request.user.pk != pk:
                raise Http404("Page Not found 404")
            user = models.User.objects.get_or_none(pk=pk)
            if user is None:
                messages.error(request, "User does not exist")
                return redirect(reverse("core:home"))
            return render(
                request,
                "pages/users/change_password.html",
                context={"user": user},
            )
        except EmailLoggedInOnly as error:
            messages.error(request, error)
            return redirect("core:home")
    elif request.method == "POST":
        try:
            if request.user.login_method != "email":
                raise EmailLoggedInOnly("Page not found 404")
            if request.user.pk != pk:
                raise Http404("Page Not found 404")
            user = models.User.objects.get_or_none(pk=pk)
            if user is None:
                messages.error(request, "User does not exist")
                return redirect(reverse("core:home"))
            old_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            new_password1 = request.POST.get("verify_password")
            user = authenticate(request, username=user.email, password=old_password)
            if user is None:
                raise ChangePasswordException("Current password is wrong!")

            if new_password != new_password1:
                raise ChangePasswordException("New password doesn't match")
            user.set_password(new_password)
            user.save()
            messages.success(request, f"{user.email}'password changed successfully")
            login(request, user)
            return redirect(reverse("users:profile", kwargs={"pk": pk}))
        except ChangePasswordException as error:
            messages.error(request, error)
            return redirect(reverse("core:home"))
        except EmailLoggedInOnly as error:
            messages.error(request, error)
            return redirect("core:home")


class ChangePasswordView(
    mixins.LoggedInOnlyView,
    mixins.EmailLoginOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):
    template_name = "pages/users/change_password.html"
    success_message = "Password changed"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Old password"}
        form.error_messages["password_mismatch"] = "The two password didn't match"
        form.fields["new_password1"].widget.attrs = {"placeholder": "New password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Verify your new password"
        }
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()


@login_required
def switch_hosting(request):
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse("core:home"))


def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        response = HttpResponse(200)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
    return response
