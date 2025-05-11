from django.conf import settings
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from drf_yasg import openapi
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'username', 'first_name', 'last_name', 'type', 'industry'


class UserListSerializer(serializers.ModelSerializer):
    from src.product.serializers import IndustrySerializer
    industry = IndustrySerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'birthday',
            'type',
            'industry',
        )


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = 'id', 'username', 'first_name', 'last_name', 'avatar', 'birthday', 'type'


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserRegistrationSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    password = serializers.CharField(write_only=True, required=True, label="Пароль")
    password2 = serializers.CharField(write_only=True, required=True, label="Повторный пароль")

    class Meta:
        model = User
        fields = 'id', 'username', 'password', 'password2', 'type', 'first_name', 'last_name', 'avatar', 'birthday'

    def validate(self, data):
        password = data['password']
        password2 = data['password2']
        if password and password2 and password != password2:
            raise serializers.ValidationError("The two password fields didn’t match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = 'password',
