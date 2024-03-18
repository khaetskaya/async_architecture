from analytics.models import UserTransaction, BillingCycle
from analytics.defs import BillingCycleStatus


def count_total_earned():
    billing_cycle = BillingCycle.objects.get(status=BillingCycleStatus.OPENED.value)
    daily_transactions_credits = UserTransaction.objects.filter(billing_cycle=billing_cycle).values_list('credit', flat=True)
    print(daily_transactions_credits)
    total_assigned_amount = total_closed_amount = 0
    for daily_transactions_credit in daily_transactions_credits:
        total_assigned_amount += daily_transactions_credit

    daily_transactions_debits = UserTransaction.objects.filter(billing_cycle=billing_cycle).values_list('debit', flat=True)
    for daily_transactions_debit in daily_transactions_debits:
        total_closed_amount += daily_transactions_debit

    return total_assigned_amount - total_closed_amount
