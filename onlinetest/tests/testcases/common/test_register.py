from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class TestRegisterAPIView(APITestCase):
    def setUp(self):
        self.url = reverse('register')  

    def test_successful_registration(self):
        data = {
            "first_name": "Priya",
            "last_name": "Kadam",
            "email": "priya@example.com",
            "role": "instructor"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['st'], 1)
        self.assertTrue(User.objects.filter(email='priya@example.com').exists())

    def test_missing_email(self):
        data = {
            "first_name": "Priya",
            "last_name": "Kadam",
            "email": "",
            "role": "student"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['st'], 2)
        self.assertIn('email', response.data['errors'])

    def test_duplicate_email(self):
        User.objects.create(
            first_name="Priya",
            last_name="Kadam",
            email="priya@example.com",
            role="student"  
        )
        data = {
            "first_name": "Another",
            "last_name": "User",
            "email": "priya@example.com",  
            "role": "student"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])
