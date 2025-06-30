
from django.urls import path
from .views.common import *
urlpatterns = [
    path('register/',RegisterAPIView.as_view(), name='register'),
    path('send-login-otp/', SendOTPAPIView.as_view(), name='send-login-otp'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
]
