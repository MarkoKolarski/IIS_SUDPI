from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from IIS_SUDPI import settings
import re

# class RegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     email = serializers.EmailField(required=True)
    
#     class Meta:
#         model = get_user_model()
#         fields = ['email', 'username', 'password', 'confirm_password', 'first_name', 'last_name', 'location']

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
        
#         if get_user_model().objects.filter(email=data['email']).exists():
#             raise serializers.ValidationError({"email": "Email already exists."})
        
#         if get_user_model().objects.filter(username=data['username']).exists():
#             raise serializers.ValidationError({"username": "Username already exists."})
        
#         if len(data['password']) < 8:
#             raise serializers.ValidationError({"password": "Password must contain at least 8 characters."})
#         if data['password'].isdigit():
#             raise serializers.ValidationError({"password": "Password cannot be numeric only."})

#         name_regex = re.compile(r'\d')  # Regex koji traži brojeve
#         if name_regex.search(data['first_name']):
#             raise serializers.ValidationError({"first_name": "First Name cannot contain numbers."})
#         if name_regex.search(data['last_name']):
#             raise serializers.ValidationError({"last_name": "Last Name cannot contain numbers."})
#         if name_regex.search(data['location']):
#             raise serializers.ValidationError({"location": "Location cannot contain numbers."})

#         return data

#     def create(self, validated_data):
#         user = get_user_model().objects.create_user(
#             email=validated_data['email'],
#             username=validated_data['username'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name'],
#             password=validated_data['password'],
#             location=validated_data['location'],
#             is_active=False
#         )

#         activation_token = self.generate_activation_token(user)

#         self.send_activation_email(user, activation_token)
#         return user

#     def generate_activation_token(self, user):
#         token = RefreshToken.for_user(user)
#         access_token = token.access_token
#         access_token.set_exp(lifetime=timedelta(minutes=10))
#         return str(access_token)

#     def send_activation_email(self, user, activation_token):
#         activation_link = f"{settings.BACKEND_URL}/activate/{activation_token}/"
#         subject = "Account activation"
#         message = f"Click the following link to activate your account: {activation_link}"
#         send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])