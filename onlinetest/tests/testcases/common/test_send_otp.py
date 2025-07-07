from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class TestSendOTPAPIView(APITestCase):
    def setUp(self):
        self.url = reverse('send-login-otp')  
        self.user = User.objects.create(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            role='student',
        )

    def test_send_otp_success(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['st'], 1)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.otp)

    def test_send_otp_invalid_email_format(self):
        data = {'email': 'invalid-email'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['st'], 2)
        self.assertIn('email', response.data['errors'])

    def test_send_otp_nonexistent_email(self):
        data = {'email': 'notfound@example.com'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['st'], 2)
        self.assertIn('email', response.data['errors'])
