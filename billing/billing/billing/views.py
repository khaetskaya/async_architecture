from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import StatsPermission
from billing.models import UserTransaction, DailyRevenue, BillingCycle
from billing.logic import count_total_earned
from billing.defs import BillingCycleStatus


class UserInfoView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        transactions = UserTransaction.objects.filter(user=user).order_by('created_at')
        data = {
            "user_balance": user.balance,
            "user_transactions": transactions
        }
        return Response(status=200, data=data)


class DailyStatsView(views.APIView):
    permission_classes = [IsAuthenticated, StatsPermission]

    def get(self, request):
        billing_cycle = BillingCycle.objects.get(status=BillingCycleStatus.OPENED.value)
        total_earned_today = count_total_earned(billing_cycle)
        data = {"today": total_earned_today}
        past_revenues = DailyRevenue.objects.all()

        for past_revenue in past_revenues:
            data[past_revenue.created_at__date] = past_revenue.amount
        return Response(status=200, data=data)
