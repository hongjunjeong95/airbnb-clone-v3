from django import forms
from . import models


class SignUpForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = {
            "first_name",
            "last_name",
            "email",
            "avatar",
            "bio",
            "gender",
            "language",
            "currency",
            "birthdate",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "First name", "required": True, "class": "w-full"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Last name", "required": True, "class": "w-full"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Email", "required": True, "class": "w-full"}
            ),
            "bio": forms.Textarea(attrs={"placeholder": "Bio", "class": "resize-none"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["avatar"].required = False
        self.fields["birthdate"].required = False

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
        label="Confirm Password",
    )

    def clean__email(self):
        email = self.cleaned_data.get("email")
        try:
            models.User.objects.get(email=email)
            raise forms.ValidationError("User already exists with that email")
        except models.User.DoesNotExist:
            return email

    def clean__password(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")

        if password != password1:
            raise forms.ValidationError("Password confirmation does not match")
        else:
            return password

    def save(self):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password)
        user.save()
