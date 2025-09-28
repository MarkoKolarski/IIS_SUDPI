from django.urls import path
from .views import LoginView, RegistrationView, activate_account, index

urlpatterns = [
    path('', index, name='index'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('activate/<str:activation_token>/', activate_account, name='activate-account'),
    path('login/', LoginView.as_view(), name='login'),
]
