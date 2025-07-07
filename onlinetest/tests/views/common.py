from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.common_serializers import *
from tests.models import User
from tests.utils import *
from rest_framework_simplejwt.tokens import RefreshToken



class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return CustomResponse(1, "User registered successfully", status_code=status.HTTP_201_CREATED)
        return CustomResponse(2, "Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class SendOTPAPIView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            otp = generate_otp()
            user.otp = otp
            user.save()

            send_otp_email(email, otp,user)
            return CustomResponse(1, "OTP sent successfully to your email.", status_code=status.HTTP_200_OK)
        
        return CustomResponse(2, "Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        

class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']  
    
            user.otp = ''
            user.save()
            refresh = RefreshToken.for_user(user)

            data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "access": str(refresh.access_token),
            }

            return CustomResponse(1, "OTP verified successfully!", data=data, status_code=status.HTTP_200_OK)

        return CustomResponse(2, "Validation failed", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)