from django.core.management import BaseCommand
from billing.models import User, Task
from billing.kafka.kafka_consumer import consumer
import random
from billing.logic import create_user_transaction
from billing.defs import UserTransactionReason
from django.db import transaction
from billing.logic import send_event_user_balance_changed
import uuid
from datetime import datetime
from billing.kafka.kafka_producer import PRODUCER_BILLING_SERVICE, producer
from schema_validator import Validator
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        consumer.subscribe(topics=["users-role", "users-stream", "tasks-history", "tasks-stream"])
        for message in consumer:
            value = message.value
            event_name = value["event_name"]
            data = value["data"]
            print("Received message: {}".format(value))
            if event_name == "UserCreated":
                User.objects.create(**message.value["data"])

            elif event_name == "UserRoleChanged":
                new_role = data["role"]
                public_id = data["public_id"]
                try:
                    user = User.objects.get(public_id=public_id)
                    user.role = new_role
                    user.save(update_fields=["role"])
                except User.DoesNotExist:
                    User.objects.create(**message.value["data"])

            elif event_name == "UserChanged":
                public_id = data["public_id"]
                try:
                    user = User.objects.get(public_id=public_id)
                    user.first_name = data["first_name"]
                    user.last_name = data["last_name"]
                    user.save(update_fields=["role", "first_name", "last_name"])
                except User.DoesNotExist:
                    User.objects.create(**data)

            elif event_name == "TaskCreated":
                jira_id = message.value["data"].get("jira_id")
                if "[" or "]" in jira_id:
                    logger.error("Invalid jira_id")

                task_assign_price = random.randint(10, 20)
                task_closure_price = random.randint(20, 40)
                assignee = User.objects.get(public_id=message.value["data"].get("assignee_public_id"))
                task, _ = Task.objects.get_or_create(
                    public_id=message.value["data"].get("public_id"),
                    defaults={
                        "status": message.value["data"].get("status"),
                        "description":  message.value["data"].get("description"),
                        "assignee_id": assignee.id,
                        "assign_price": task_assign_price,
                        "closure_price": task_closure_price
                }
                )
                event = {
                    "event_id": str(uuid.uuid4()),
                    "event_name": "TaskCostsSet",
                    "event_version": 1,
                    "event_time": str(datetime.now()),
                    "producer": PRODUCER_BILLING_SERVICE,
                    "data": {
                        "public_id": str(task.public_id),
                        "assign_price": task.assign_price,
                        "closure_price": task.closure_price
                    },
                }
                result, errors = Validator().validate_data(schema_name='tasks.costs_set', version=1, data=event)
                if result:
                    producer.send("tasks-history", event)

            elif event_name == "TaskAssigned":
                assignee = User.objects.get(public_id=message.value["data"].get("assignee_public_id"))
                task, _ = Task.objects.get_or_create(
                    public_id=message.value["data"].get("public_id"),
                    defaults={
                        "assign_price": random.randint(10, 20),
                        "closure_price": random.randint(20, 40),
                        "assignee_id": assignee.id
                    }
                )
                task.assignee = assignee
                task.save(update_fields=["assignee"])
                with transaction.atomic():
                    create_user_transaction(
                        debit=0,
                        credit=task.assign_price,
                        user=task.assignee,
                        reason=UserTransactionReason.ASSIGN.value,
                        description='Withdrawn for task assign',
                        task_public_id=str(task.public_id)
                    )
                    task.assignee.balance -= task.assign_price
                    task.assignee.save(update_fields=["balance"])
                    send_event_user_balance_changed(task.assignee)

            elif event_name == "TaskClosed":
                task = Task.objects.get(public_id=message.value["data"]["public_id"])
                task_assignee = task.assignee
                with transaction.atomic():
                    create_user_transaction(
                        debit=task.task_closure_price,
                        credit=0,
                        user=task_assignee,
                        reason=UserTransactionReason.CLOSURE.value,
                        description='Money for task closure',
                        task_public_id=str(task.public_id)
                    )
                    task_assignee.balance += task.closure_price
                    task_assignee.save(update_fields=["balance"])
                    send_event_user_balance_changed(task_assignee)