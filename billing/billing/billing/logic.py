from billing.models import UserTransaction, BillingCycle
from billing.defs import BillingCycleStatus
import uuid
from datetime import datetime, timedelta
from billing.kafka.kafka_producer import PRODUCER_BILLING_SERVICE, producer
from schema_validator import Validator


def create_user_transaction(debit, credit, user, reason, description, task_public_id=None):
    billing_cycle, _ = BillingCycle.objects.get_or_create(
        status=BillingCycleStatus.OPENED.value,
        defaults={
            "status": BillingCycleStatus.OPENED.value,
            "start_date": datetime.now(),
            "end_date": datetime.now() + timedelta(days=1)
        }
    )
    user_transaction = UserTransaction.objects.create(
        user=user,
        debit=debit,
        credit=credit,
        description=description,
        reason=reason,
        billing_cycle=billing_cycle
    )
    event = {
        "event_id": str(uuid.uuid4()),
        "event_name": "UserTransactionCreated",
        "event_version": 1,
        "event_time": str(datetime.now()),
        "producer": PRODUCER_BILLING_SERVICE,
        "data": {
            "public_id": str(user_transaction.public_id),
            "user_public_id": str(user.public_id),
            "task_public_id": str(task_public_id),
            "billing_cycle_public_id": str(billing_cycle.public_id),
            "debit": debit,
            "credit": credit,
            "reason": reason
        },
    }

    result, errors = Validator().validate_data(schema_name='user_transactions.created', version=1, data=event)
    if result:
        producer.send("billing-stream", event)


def count_total_earned(billing_cycle):
    daily_transactions_credits = UserTransaction.objects.filter(billing_cycle=billing_cycle).values_list('credit', flat=True)
    total_assigned_amount = total_closed_amount = 0
    for daily_transactions_credit in daily_transactions_credits:
        total_assigned_amount += daily_transactions_credit

    daily_transactions_debits = UserTransaction.objects.filter(billing_cycle=billing_cycle).values_list('debit', flat=True)
    for daily_transactions_debit in daily_transactions_debits:
        total_closed_amount += daily_transactions_debit

    return total_assigned_amount - total_closed_amount


def send_event_user_balance_changed(user):
    event = {
        "event_id": str(uuid.uuid4()),
        "event_name": "UserBalanceChanged",
        "event_version": 1,
        "event_time": str(datetime.now()),
        "producer": PRODUCER_BILLING_SERVICE,
        "data": {
            "public_id": str(user.public_id),
            "balance": user.balance
        },
    }
    result, errors = Validator().validate_data(schema_name='users.balance_changed', version=1, data=event)
    if result:
        producer.send("users-balance", event)
