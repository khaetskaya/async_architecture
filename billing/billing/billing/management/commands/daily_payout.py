from django.core.management import BaseCommand
from billing.models import User, DailyRevenue, BillingCycle
from billing.logic import create_user_transaction, count_total_earned
from billing.defs import UserTransactionReason, BillingCycleStatus
from billing.email import send_email
from django.db import transaction
from billing.logic import send_event_user_balance_changed
from billing.kafka.kafka_producer import PRODUCER_BILLING_SERVICE, producer
from schema_validator import Validator
import uuid
from datetime import datetime, timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            daily_balance = user.balance
            if daily_balance <= 0:
                continue
            with transaction.atomic():
                create_user_transaction(
                    debit=daily_balance,
                    credit=0,
                    user=user,
                    reason=UserTransactionReason.DAILY_PAYOUT.value,
                    description='Daily payout'
                )
                user.balance = 0
                user.save(update_fields=['balance'])
            send_event_user_balance_changed(user)
            send_email(email=user.email, balance=daily_balance)

        billing_cycle = BillingCycle.objects.get(status=BillingCycleStatus.OPENED.value)
        total_earned = count_total_earned(billing_cycle)
        DailyRevenue.objects.create(amount=total_earned)
        billing_cycle.status = BillingCycleStatus.CLOSED.value
        billing_cycle.save(update_fields=['status'])
        event = {
            "event_id": str(uuid.uuid4()),
            "event_name": "BillingCycleClosed",
            "event_version": 1,
            "event_time": str(datetime.now()),
            "producer": PRODUCER_BILLING_SERVICE,
            "data": {
                "public_id": str(billing_cycle.public_id)
            },
        }

        result, errors = Validator().validate_data(schema_name='billing_cycle.closed', version=1, data=event)
        if result:
            producer.send("billing-stream", event)

        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=1)
        new_billing_cycle = BillingCycle.objects.create(
            status=BillingCycleStatus.OPENED.value,
            start_date=start_date,
            end_date=end_date
        )
        event = {
            "event_id": str(uuid.uuid4()),
            "event_name": "BillingCycleCreated",
            "event_version": 1,
            "event_time": str(datetime.now()),
            "producer": PRODUCER_BILLING_SERVICE,
            "data": {
                "public_id": str(new_billing_cycle.public_id),
                "start_date": str(start_date),
                "end_date": str(end_date)
            },
        }

        result, errors = Validator().validate_data(schema_name='billing_cycle.created', version=1, data=event)
        if result:
            producer.send("billing-stream", event)
