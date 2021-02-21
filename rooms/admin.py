from django.contrib import admin
from . import models as room_models
from photos import models as photo_models


@admin.register(
    room_models.RoomType,
    room_models.Facility,
    room_models.Amenity,
    room_models.HouseRule,
)
class ItemAdmin(admin.ModelAdmin):

    """ Item Admin """

    list_display = ("name", "used_by")

    def used_by(self, obj):
        return obj.rooms.count()


class PhotoInline(admin.StackedInline):
    model = photo_models.Photo


@admin.register(room_models.Room)
class RoomAdmin(admin.ModelAdmin):

    """ Room Admin Definition """

    inlines = [
        PhotoInline,
    ]

    def count_amenities(self, obj):
        return obj.amenities.count()

    count_amenities.short_description = "Amenity Count"

    def count_facilities(self, obj):
        return obj.facilities.count()

    count_facilities.short_description = "Facility Count"