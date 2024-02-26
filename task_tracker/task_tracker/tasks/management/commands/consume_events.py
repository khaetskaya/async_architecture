from django.core.management import BaseCommand
from tasks.models import User
from tasks.kafka.kafka_consumer import consumer


class Command(BaseCommand):
    def handle(self, *args, **options):
        consumer.subscribe(topics=["accounts", "accounts-stream"])
        for message in consumer:
            value = message.value
            event_name = value["event_name"]
            data = value["data"]
            print("Received message: {}".format(value))
            if event_name == "AccountCreated":
                User.objects.create(**message.value["data"])

            elif event_name == "AccountRoleChanged":
                new_role = data["role"]
                public_id = data["public_id"]
                try:
                    user = User.objects.get(public_id=public_id)
                    user.role = new_role
                    user.save(update_fields=["role"])
                except User.DoesNotExist:
                    User.objects.create(**message.value["data"])

            elif event_name == "AccountChanged":
                public_id = data["public_id"]
                try:
                    user = User.objects.get(public_id=public_id)
                    user.first_name = data["first_name"]
                    user.last_name = data["last_name"]
                    user.save(update_fields=["role", "first_name", "last_name"])
                except User.DoesNotExist:
                    User.objects.create(**data)
