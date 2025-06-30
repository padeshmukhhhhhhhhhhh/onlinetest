
from rest_framework import serializers
from tests.models import User

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=User.Role.choices)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        data['user'] = user 
        return data
