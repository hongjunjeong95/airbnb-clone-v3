from django.core.management.base import BaseCommand
from rooms.models import RoomType

NAME = "room types"


class Command(BaseCommand):

    help = f"This command creates some {NAME}"

    def handle(self, *args, **options):
        room_types = ["Hotel Room", "Entire Place", "Shared Room", "Private Room"]
        for room_type in room_types:
            RoomType.objects.create(name=room_type)

        self.stdout.write(self.style.SUCCESS(f"Create {NAME}"))
