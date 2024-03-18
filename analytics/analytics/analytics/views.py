from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import AdminPermission
from analytics.models import User, Task
from analytics.logic import count_total_earned
from analytics.defs import TaskStatus
from django.utils.dateparse import parse_datetime


class DailyStatsView(views.APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def get(self, request):
        total_earned_today = count_total_earned()
        poor_popugs_count = User.objects.filter(balance__lt=0).count()
        data = {
            "management earned today": total_earned_today,
            "poor_popugs_count": poor_popugs_count,
        }
        query_params = request.query_params
        time_period_start = parse_datetime(query_params.get("start_date"))
        time_period_end = parse_datetime(query_params.get("end_date"))
        most_expensive_task = Task.objects.filter(
            status=TaskStatus.CLOSED,
            modified_at__range=(time_period_start, time_period_end),
        ).order_by("-closure_price").first()
        data[f"most_expensive_task_in a period from {time_period_start} to {time_period_end}"] = most_expensive_task
        return Response(status=200, data=data)
