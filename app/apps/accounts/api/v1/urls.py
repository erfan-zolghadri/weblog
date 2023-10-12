from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

app_name = "accounts_api_1.0"

urlpatterns = [
    path("signup/", views.SignUpAPIView.as_view(), name="signup"),
    path(
        "verify/resend/",
        views.AccountVerifyResendAPIView.as_view(),
        name="account-verify-resend",
    ),
    path(
        "verify/<str:token>/",
        views.AccountVerifyAPIView.as_view(),
        name="account-verify",
    ),
    path(
        "jwt/create/", views.TokenObtainPairView.as_view(), name="jwt-create"
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    path(
        "password/change/",
        views.PasswordChangeAPIView.as_view(),
        name="password-change",
    ),
    path(
        "password/reset/",
        views.PasswordResetAPIView.as_view(),
        name="password-reset",
    ),
    path(
        "password/reset/confirm/<str:token>/",
        views.PasswordResetConfirmAPIView.as_view(),
        name="password-reset",
    ),
    path(
        "password/reset/complete/",
        views.PasswordResetCompleteAPIView.as_view(),
        name="password-reset-complete",
    ),
]
