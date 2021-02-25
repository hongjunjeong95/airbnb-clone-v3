from random import choice, randint

from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten

from django_seed import Seed

from lists import models as list_models
from users import models as user_models
from rooms import models as room_models

NAME = "lists"


class Command(BaseCommand):

    help = f"This command creates many {NAME}"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, help=f"How many {NAME} do you want to create"
        )

    def get_user(self, users):
        for user in users:
            try:
                pass
            except Exception:
                return user

    def handle(self, *args, **options):
        number = options.get("number", 1)
        users = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()

        seeder = Seed.seeder()
        seeder.add_entity(
            list_models.List,
            number,
            {
                "name": lambda x: seeder.faker.sentence(),
                "user": lambda x: self.get_user(users),
            },
        )
        created_lists = seeder.execute()
        list_pks = flatten(created_lists.values())
        for list_pk in list_pks:
            list_model = list_models.List.objects.get(pk=list_pk)
            add_rooms = rooms[randint(0, 5) : randint(5, 30)]
            list_model.rooms.add(*add_rooms)

        self.stdout.write(self.style.SUCCESS(f"Successfully create {number} {NAME}"))
