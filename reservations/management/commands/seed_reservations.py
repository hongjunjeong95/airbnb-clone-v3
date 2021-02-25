import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_seed import Seed
from reservations import models as reservation_models
from users import models as user_models
from rooms import models as room_models


class Command(BaseCommand):

    help = "This command creates many reservations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, help="How many reservations do you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number", 1)
        users = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()
        seeder = Seed.seeder()
        seeder.add_entity(
            reservation_models.Reservation,
            number,
            {
                "guest": lambda x: random.choice(users),
                "room": lambda x: random.choice(rooms),
                "check_in": lambda x: timezone.localtime(),
                "check_out": lambda x: timezone.localtime()
                + timezone.timedelta(days=random.randint(1, 30)),
            },
        )
        seeder.execute()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully create {number} reservations")
        )
