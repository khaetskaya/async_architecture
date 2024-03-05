from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('role', 'public_id', 'first_name', 'last_name', 'id', 'username', 'email')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('role', 'first_name', 'last_name')
