from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.common_serializers import *
from tests.models import User
from tests.utils import generate_otp, send_otp_email
from rest_framework_simplejwt.tokens import RefreshToken


    
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendOTPAPIView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            otp = generate_otp()
            user.otp = otp
            user.save()

            send_otp_email(email, otp)
            return Response({"message": "OTP sent successfully to your email."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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



            return Response({"message": "OTP verified successfully!","data":data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)