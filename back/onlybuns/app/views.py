from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from .models import VerifiedUser
from .serializers import RegistrationSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone

def index(request):
    html = render_to_string("index.js", {})
    return HttpResponse(html)

    
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Kreiramo korisnika pomoću serializer-a
            serializer.save()
            return Response({
                'message': 'The user is successfully registered. An activation link has been sent to your email.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny]) 
def activate_account(request, activation_token):
    try:
        # Validiramo aktivacioni token
        token = AccessToken(activation_token)
        
        # Provera isteka tokena
        try:
            token.verify()
        except TokenError:
            return HttpResponse(
                """
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Account activation</title>
                    </head>
                    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                        <h1>Account activation</h1>
                        <p>The activation link has expired! Please try to register again.</p>
                    </body>
                </html>
                """, content_type="text/html; charset=UTF-8"
            )

        user_id = token['user_id']
        user = get_user_model().objects.get(id=user_id)

        # Ako je korisnik već aktiviran, vraćamo odgovarajuću poruku
        if user.user_type == 'authenticated':
            return HttpResponse(
                """
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Account activation</title>
                    </head>
                    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                        <h1>Account activation</h1>
                        <p>Account already activated! You can sign up now.</p>
                    </body>
                </html>
                """, content_type="text/html; charset=UTF-8"
            )

        # Aktiviramo korisnika
        user.user_type = 'authenticated'
        user.is_active = True
        user.save()

        VerifiedUser.objects.create(user=user)

        return HttpResponse(
                """
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Account activation</title>
                    </head>
                    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                        <h1>Account activation</h1>
                        <p>Account successfully activated! You can sign up now.</p>
                    </body>
                </html>
                """, content_type="text/html; charset=UTF-8"
            )

    except Exception as e:
        # Ako token nije validan ili je istekao
        return HttpResponse(
                """
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Account activation</title>
                    </head>
                    <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                        <h1>Account activation</h1>
                        <p>The activation link has expired! Please try to register again.</p>
                    </body>
                </html>
                """, content_type="text/html; charset=UTF-8"
            )
    
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_model().objects.filter(email=email).first()
        
        if user is not None and user.is_active and user.check_password(password):
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Incorrect email or password.'}, status=status.HTTP_401_UNAUTHORIZED)