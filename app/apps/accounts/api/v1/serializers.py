from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)

from decouple import config
from jwt import decode
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from rest_framework import status
from rest_framework.response import Response

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=50, write_only=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        max_length=50, write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["email", "password", "confirm_password"]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"detail": "Passwords do not match."}
            )

        try:
            validate_password(password=password)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        self.instance = user
        return user


class AccountVerifyResendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "User with this email address does not exist."}
            )
        if user.is_active:
            raise serializers.ValidationError(
                {"detail": "Account has already been verified."}
            )
        attrs["user"] = user
        return attrs


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs.update({"user_id": self.user.pk, "email": self.user.email})
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=50, write_only=True, style={"input_type": "password"}
    )
    new_password1 = serializers.CharField(
        max_length=50, write_only=True, style={"input_type": "password"}
    )
    new_password2 = serializers.CharField(
        max_length=50, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        new_password = attrs.get("new_password1")
        confirm_new_password = attrs.get("new_password2")

        if new_password != confirm_new_password:
            raise serializers.ValidationError(
                {"detail": "Passwords do not match."}
            )

        try:
            validate_password(password=new_password)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password1": list(e.messages)}
            )

        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "User with this email address does not exist."}
            )
        attrs["user"] = user
        return attrs


class PasswordResetCompleteSerializer(serializers.Serializer):
    token = serializers.CharField()
    password1 = serializers.CharField(
        max_length=50, write_only=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        max_length=50, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        token = attrs.get("token")
        password1 = attrs.get("password1")
        password2 = attrs.get("password2")

        try:
            decoded = decode(token, config("SECRET_KEY"), algorithms=["HS256"])
        except ExpiredSignatureError:
            return Response(
                {"detail": "Signature has been expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"detail": "Token is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password1 != password2:
            raise serializers.ValidationError(
                {"detail": "Passwords do not match."}
            )

        try:
            validate_password(password=password1)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        attrs["user_id"] = decoded.get("user_id")

        return attrs
