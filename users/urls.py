from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import (LoginAPIView, PasswordResetAPIView,
                    RequestPasswordResetAPIView, RegisterAPIView, TokenVerifyAPIView, VerifyEmailAPIView)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("email/verify/", VerifyEmailAPIView.as_view(), name="email-verify"),
    path("password/reset/request/", RequestPasswordResetAPIView.as_view(), name="password-reset-request"),
    path("password/reset/<uidb64>/<token>/", TokenVerifyAPIView.as_view(), name="password-reset-confirm"),
    path("password/reset/", PasswordResetAPIView.as_view(), name="password-reset"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
]