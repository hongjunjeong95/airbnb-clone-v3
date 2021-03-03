from django.contrib.auth.models import AbstractUser
from django.db import models
from . import managers


class User(AbstractUser):

    """ Custom User model """

    GENDER_MALE = "Male"
    GENDER_FEMALE = "Female"
    GENDER_OTHER = "Other"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    )

    LANGUAGE_KOREAN = "KR"
    LANGUAGE_ENGLISH = "EN"
    LANGUAGE_CHOICES = (
        (LANGUAGE_KOREAN, "Korean"),
        (LANGUAGE_ENGLISH, "English"),
    )

    CURRENCY_KRW = "KRW"
    CURRENCY_USD = "USD"
    CURRENCY_CHOICES = ((CURRENCY_KRW, "KRW"), (CURRENCY_USD, "USD"))

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGIN_KAKAO = "kakao"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "Github"),
        (LOGIN_KAKAO, "Kakao"),
    )

    objects = managers.CustomUserModelManager()

    avatar = models.ImageField(upload_to="avatars", blank=True)
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, null=True)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, null=True)
    birthdate = models.DateField(null=True)
    superhost = models.BooleanField(default=False)
    login_method = models.CharField(
        max_length=6, choices=LOGIN_CHOICES, default=LOGIN_EMAIL
    )