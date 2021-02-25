from random import randint
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from conversations import models as conversation_models
from users import models as user_models


NAME = "conversations"


class Command(BaseCommand):

    help = f"This command creates many {NAME}"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number", type=int, help=f"How many {NAME} do you want to create"
        )

    def handle(self, *args, **options):
        number = options.get("number", 1)
        users = user_models.User.objects.all()

        seeder = Seed.seeder()
        seeder.add_entity(
            conversation_models.Conversation,
            number,
        )
        created_conversations = seeder.execute()
        conversation_pks = flatten(created_conversations.values())

        for conversation_pk in conversation_pks:
            conversation_model = conversation_models.Conversation.objects.get(
                pk=conversation_pk
            )
            add_participants = users[randint(0, 5) : randint(5, 30)]
            conversation_model.participants.add(*add_participants)

        self.stdout.write(self.style.SUCCESS(f"Successfully create {number} {NAME}"))
