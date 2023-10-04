import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework.response import Response
from rest_framework import generics, status, views
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from.renderers import UserRenderer
from .serializers import (EmailVerificationSerializer, LoginSerializer, PasswordResetSerializer, 
                          RegisterSerializer, RequestPasswordResetSerializer)
from .utils import Util

User = get_user_model()

class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email=user_data["email"])
        token = RefreshToken.for_user(user=user).access_token

        domain = get_current_site(request).domain
        relative_path = reverse("email-verify")
        absolute_path = f"http://{domain}{relative_path}?token={str(token)}"

        data = {
            "sender": settings.EMAIL_HOST_USER,
            "recipient": user.email,
            "email_subject": Util.email_subject(),
            "email_body": Util.email_body(site_name=domain, recipient=user.username, confirmation_link=absolute_path)
        }
        Util.send_email(data)
        
        return Response(user_data, status=status.HTTP_201_CREATED)
    
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request): 
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
                    
class VerifyEmailAPIView(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description="Email verification token", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({"detail": "Account successfully activated"}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            # TODO: rember to handle sending new activation link logic in front end
            return Response({"error": "Activation link expired"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        

class RequestPasswordResetAPIView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        email = request.data["email"]
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            domain = get_current_site(request).domain
            relative_path = reverse("password-reset-confirm", kwargs={"uidb64": uidb64, "token": token})
            absolute_path = f"http://{domain}{relative_path}"

            data = {
                "sender": settings.EMAIL_HOST_USER,
                "recipient": user.email,
                "email_subject": Util.email_subject(type="password-reset-request"), 
                "email_body": Util.email_body(site_name=domain, 
                                                recipient=user.username, 
                                                confirmation_link=absolute_path, 
                                                type="password_reset")
            }
            Util.send_email(data)
        return Response({"message": "A link to reset your password was sent to your registered email account."},
                        status=status.HTTP_200_OK)
    

class PasswordResetAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)


class TokenVerifyAPIView(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user=user, token=token):
                return Response({"message": "Invalid token, please send a new token request"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"details": "success", "uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError:
            return Response({"message": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)
            pass
