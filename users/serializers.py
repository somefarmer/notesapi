from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password",)

    def validate(self, attrs):
        username = attrs.get("username", "")
        email = attrs.get("email", "")

        if not username.isalnum():
            raise serializers.ValidationError("Username must only contain letters and digits")
        
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=64, min_length=8, write_only=True)
    username = serializers.CharField(max_length=15, min_length=2, read_only=True)
    tokens = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "username", "tokens",)

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Incorrect username or password")
        
        if not user.is_active:
            raise AuthenticationFailed("Account disabled. Email support team")
        
        if not user.is_verified:
            raise AuthenticationFailed("Please confirm your account before logging in")
        
        return {
            "email": user.email,
            "username": user.username,
            "tokens": user.tokens()
        }

    
class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=512)

    class Meta:
        model = User
        fields = ("token",)

class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ("email",)

class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=64, min_length=8, write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    class Meta:
        fields = ("password", "uidb64", "token",)

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            uidb64 = attrs.get("uidb64")
            token = attrs.get("token")
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed(detail="Invalid password reset link", code=401)
            user.set_password(password)
            user.save()
            return user
        except Exception:
            raise AuthenticationFailed(detail="Invalid password reset link", code=401)