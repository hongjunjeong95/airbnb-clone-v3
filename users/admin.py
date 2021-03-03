from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):

    """ Custom User Admin """

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "gender",
        "language",
        "currency",
        "birthdate",
        "superhost",
        "login_method",
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
    )

    list_filter = UserAdmin.list_filter + (
        "gender",
        "language",
        "currency",
        "superhost",
        "login_method",
        "email_verified",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Custom Profile",
            {
                "fields": (
                    "avatar",
                    "bio",
                    "gender",
                    "language",
                    "currency",
                    "birthdate",
                    "superhost",
                    "login_method",
                    "email_verified",
                    "email_secret",
                )
            },
        ),
    )
