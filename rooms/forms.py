from django import forms
from . import models


class CreateRoomForm(forms.ModelForm):

    """ Create Room Form Definition """

    class Meta:
        model = models.Room
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
