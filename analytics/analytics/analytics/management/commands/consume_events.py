from django.core.management import BaseCommand
from analytics.models import User, Task, UserTransaction, BillingCycle
from analytics.kafka.kafka_consumer import consumer
from analytics.defs import TaskStatus, BillingCycleStatus
import random


class Command(BaseCommand):
    def handle(self, *args, **options):
        consumer.subscribe(
            topics=["users-role", "users-stream", "users-balance", "tasks-stream", "tasks-history", "billing-stream"]
        )
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
                task_assign_price = random.randint(10, 20)
                task_closure_price = random.randint(20, 40)
                assignee = User.objects.get(public_id=message.value["data"].get("assignee_public_id"))
                Task.objects.get_or_create(
                    public_id=message.value["data"].get("public_id"),
                    defaults={
                        "status": message.value["data"].get("status"),
                        "description":  message.value["data"].get("description"),
                        "assign_price": task_assign_price,
                        "closure_price": task_closure_price,
                        "assignee_id": assignee.id,
                        "jira_id": message.value["data"].get("jira_id")
                    }
                )

            elif event_name == "TaskCostsSet":
                task = Task.objects.get(public_id=message.value["data"]["public_id"])
                task.assign_price = data["assign_price"]
                task.closure_price = data["closure_price"]
                task.save(update_fields=["assign_price", "closure_price"])

            elif event_name == "TaskClosed":
                task = Task.objects.get(public_id=message.value["data"]["public_id"])
                task.status = TaskStatus.CLOSED
                task.save(update_fields=["status"])

            elif event_name == "UserTransactionCreated":
                user = User.objects.get(public_id=message.value["data"]["user_public_id"])
                task = Task.objects.get(public_id=message.value["data"]["task_public_id"])
                billing_cycle = BillingCycle.objects.get(public_id=message.value["data"]["billing_cycle_public_id"])
                UserTransaction.objects.create(
                    user=user,
                    debit=data.get("debit", 0),
                    credit=data.get("credit", 0),
                    reason=data.get("reason"),
                    task=task,
                    public_id=data["public_id"],
                    billing_cycle=billing_cycle
                )

            elif event_name == "UserBalanceChanged":
                user = User.objects.get(public_id=message.value["data"]["public_id"])
                user.balance = data["balance"]
                user.save(update_fields=["balance"])

            elif event_name == "BillingCycleCreated":
                BillingCycle.objects.create(
                    status=BillingCycleStatus.OPENED.value,
                    start_date=data.get("start_date"),
                    end_date=data.get("end_date"),
                    public_id=data.get("public_id")
                )
