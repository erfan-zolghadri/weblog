from decouple import config
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from jwt import decode
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from mail_templated import EmailMessage
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)

from .serializers import (
    AccountVerifyResendSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetCompleteSerializer,
    TokenObtainPairSerializer,
    UserSerializer,
)
from ..utilities import EmailThread

User = get_user_model()


class SignUpAPIView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        email = serializer.validated_data.get("email")
        data = {"email": email}
        headers = self.get_success_headers(serializer.data)

        # Send account verification email
        user = get_object_or_404(User, email=email)
        token = self.get_tokens_for_user(user)
        message = EmailMessage(
            template_name="email/account_verification_email.tpl",
            context={
                "subject": "Account Verification",
                "token": token,
                "domain": get_current_site(request),
            },
            from_email="admin@example.com",
            to=[email],
        )
        EmailThread(message).start()

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class AccountVerifyAPIView(APIView):
    def get(self, request, token, *args, **kwargs):
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
        user_id = decoded.get("user_id")
        user = get_object_or_404(User, pk=user_id)
        if user.is_active:
            return Response({"detail": "Account has already been verified."})
        user.is_active = True
        user.save()
        return Response({"detail": "Account has been successfully verified."})


class AccountVerifyResendAPIView(GenericAPIView):
    serializer_class = AccountVerifyResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user")
        token = self.get_tokens_for_user(user)
        message = EmailMessage(
            template_name="email/account_verification_email.tpl",
            context={
                "subject": "Account Verification",
                "token": token,
                "domain": get_current_site(request),
            },
            from_email="admin@example.com",
            to=[user.email],
        )
        EmailThread(message).start()
        return Response(
            {"detail": "Account verification email was sent to your email."}
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class PasswordChangeAPIView(UpdateAPIView):
    http_method_names = ["head", "options", "patch"]
    serializer_class = PasswordChangeSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate old_password
        old_password = serializer.validated_data.get("old_password")
        if not user.check_password(old_password):
            return Response(
                {"old_password": "Password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = serializer.validated_data.get("new_password1")
        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password was successfully changed"},
            status=status.HTTP_200_OK,
        )


class PasswordResetAPIView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user")
        token = self.get_tokens_for_user(user)
        message = EmailMessage(
            template_name="email/password_reset_email.tpl",
            context={
                "subject": "Password Reset",
                "domain": get_current_site(request),
                "token": token,
            },
            from_email="admin@example.com",
            to=[user.email],
        )
        EmailThread(message).start()
        return Response(
            {"detail": "Password reset link was sent to your email."}
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class PasswordResetConfirmAPIView(GenericAPIView):
    def get(self, request, token, *args, **kwargs):
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
        return Response({"token": token})


class PasswordResetCompleteAPIView(GenericAPIView):
    serializer_class = PasswordResetCompleteSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data.get("password1")
        user_id = serializer.validated_data.get("user_id")
        user = get_object_or_404(User, pk=user_id)
        user.set_password(password)
        user.save()
        return Response(
            {"detail": "Your password has been successfully reset."}
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
