from django import forms
from . import models as room_models
from photos import models as photo_models


class CreateRoomForm(forms.ModelForm):

    """ Create Room Form Definition """

    class Meta:
        model = room_models.Room
        fields = (
            "name",
            "country",
            "city",
            "address",
            "price",
            "guests",
            "bedrooms",
            "beds",
            "bathrooms",
            "description",
            "room_type",
            "amenities",
            "facilities",
            "house_rules",
            "instant_book",
        )

    def save(self, *args, **kwargs):
        room = super().save(commit=False)
        return room


class CreatePhotoForm(forms.ModelForm):

    """ Create Photo Form Definition """

    class Meta:
        model = photo_models.Photo
        fields = (
            "caption",
            "file",
        )
        widgets = {
            "caption": forms.TextInput(attrs={"placeholder": "Caption"}),
            "file": forms.FileInput(attrs={"class": "p-1 w-full"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = True

    def save(self, *args, **kwargs):
        photo = super().save(commit=False)
        return photo
