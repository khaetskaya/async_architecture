import random

from rest_framework import generics, serializers, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import ReassignTasksPermission
from tasks.defs import Role, TaskStatus
from tasks.models import Task, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.CharField(required=False)

    class Meta:
        model = Task
        fields = ("description", "status", "assignee")


class UserList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateTaskView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        assignee_queryset = User.objects.exclude(
            role__in=[Role.ADMIN.value, Role.MANAGER.value]
        )
        if assignee_queryset.exists():
            total_assignees = assignee_queryset.count()
            random_index = random.randint(0, total_assignees - 1)
            assignee = assignee_queryset[random_index]
            serializer.validated_data["assignee"] = assignee

        serializer.save()


class ReassignTasksView(views.APIView):
    permission_classes = [IsAuthenticated, ReassignTasksPermission]

    def get(self, request):
        opened_tasks = Task.objects.filter(status=TaskStatus.OPENED.value)
        for task in opened_tasks:
            assignee_queryset = User.objects.exclude(
                role__in=[Role.ADMIN.value, Role.MANAGER.value]
            )

            if assignee_queryset.exists():
                total_assignees = assignee_queryset.count()
                random_index = random.randint(0, total_assignees - 1)
                assignee = assignee_queryset[random_index]
                task.assignee = assignee
                task.save()

        serializer = TaskSerializer(opened_tasks, many=True)
        return Response(serializer.data)


class CloseTaskView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get("task_id")
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response("task does not exist")

        if task.assignee != request.user:
            return Response("It's not your task to close")

        task.status = TaskStatus.CLOSED.value
        task.save(update_fields=["status"])
        return Response(status=200, data="ok")


class MyTasksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assignee=user)
