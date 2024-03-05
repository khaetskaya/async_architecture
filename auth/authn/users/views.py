import ujson
from django.http import HttpResponse
from oauth2_provider.views.generic import ProtectedResourceView
from rest_framework import viewsets

from users.kafka_producer import producer, PRODUCER_AUTH_SERVICE

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer
from schema_validator import Validator
from datetime import datetime
import uuid


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        result = super().create(request, *args, **kwargs)
        data = result.data
        event = {
            "event_name": "UserCreated",
            "event_id": str(uuid.uuid4()),
            "event_version": 1,
            "event_time": str(datetime.now()),
            "producer": PRODUCER_AUTH_SERVICE,
            "data": {
                "public_id": data.get("public_id"),
                "email": data.get("email"),
                "role": data.get("role"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "username": data.get("username"),
            },
        }
        event_result, errors = Validator().validate_data(schema_name='users.created', version=1, data=event)
        if event_result:
            producer.send("users-stream", event)

        return result

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        new_role = request.data.get("role")
        old_role = user.role
        result = super().update(request, *args, **kwargs)
        data = result.data
        if new_role != old_role:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_version": 1,
                "event_time": str(datetime.now()),
                "producer": PRODUCER_AUTH_SERVICE,
                "event_name": "UserRoleChanged",
                "data": {
                    "public_id": str(user.public_id),
                    "role": new_role,
                },
            }
            result, errors = Validator().validate_data(
                schema_name='users.role_changed',
                version=1,
                data=event
            )
            if result:
                producer.send("users-role", event)

        event = {
            "event_name": "UserChanged",
            "event_id": str(uuid.uuid4()),
            "event_version": 1,
            "event_time": str(datetime.now()),
            "producer": PRODUCER_AUTH_SERVICE,
            "data": {
                "public_id": data.get("public_id") or str(user.public_id),
                "first_name": data.get("first_name") or user.first_name,
                "last_name": data.get("last_name") or user.last_name,
            },
        }
        event_result, errors = Validator().validate_data(schema_name='users.changed', version=1, data=event)
        if event_result:
            producer.send("users-stream", event)
        return result

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        result = super().destroy(request, *args, **kwargs)
        event = {
            "event_name": "UserDeactivated",
            "event_id": str(uuid.uuid4()),
            "event_version": 1,
            "event_time": str(datetime.now()),
            "producer": PRODUCER_AUTH_SERVICE,
            "data": {
                "public_id": user.public_id,
            },
        }
        event_result, errors = Validator().validate_data(schema_name='users.deactivated', version=1, data=event)
        if event_result:
            producer.send("users-stream", event)
        return result


class CurrentUserInfo(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_info = {
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "public_id": str(user.public_id),
            "is_active": user.is_active,
        }
        return HttpResponse(ujson.dumps(user_info))
