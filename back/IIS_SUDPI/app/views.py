from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from .serializers import RegistrationSerializer

def index(request):
    html = render_to_string("index.js", {})
    return HttpResponse(html)
    
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('mail_k')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_model().objects.filter(mail_k=email).first()
        
        if user is not None and user.is_active and user.check_password(password):
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_type': user.tip_k,
                'user_name': f"{user.ime_k} {user.prz_k}",
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Incorrect email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Korisnik je uspešno registrovan.',
            'user_type': user.tip_k,
            'user_name': f"{user.ime_k} {user.prz_k}",
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)