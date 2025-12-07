from rest_framework import serializers
from django.contrib.auth.models import User


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_user_type(self, value):
        allowed_types = ["customer", "seller"]
        if value.lower() not in allowed_types:
            raise serializers.ValidationError(
                "Invalid user_type. Allowed values are 'customer' or 'seller'."
            )
        return value.lower()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            username=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False)  

class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class LoginResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserResponseSerializer()

class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserResponseSerializer()

class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class RefreshTokenResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class ProfileResponseSerializer(serializers.Serializer):
    user = UserResponseSerializer()

