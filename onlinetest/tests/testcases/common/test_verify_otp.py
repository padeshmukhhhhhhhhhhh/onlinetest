from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class TestVerifyOTPAPIView(APITestCase):
    def setUp(self):
        self.url = reverse('verify-otp')  
        self.user = User.objects.create(
            first_name="Priya",
            last_name="Kadam",
            email="priya@example.com",
            role="student",
            otp="123456"
        )

    def test_verify_otp_success(self):
        data = {
            "email": "priya@example.com",
            "otp": "123456"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['st'], 1)
        self.assertIn('access', response.data['data'])

        self.user.refresh_from_db()
        self.assertEqual(self.user.otp, '')  
    def test_verify_otp_invalid_code(self):
        data = {
            "email": "priya@example.com",
            "otp": "000000"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['st'], 2)
        self.assertIn('Invalid OTP.', response.data['errors']['non_field_errors'])
