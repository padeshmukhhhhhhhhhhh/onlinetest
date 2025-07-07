from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse 
from tests.models import Test  
from django.contrib.auth import get_user_model

User = get_user_model()
class TestAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        self.url = reverse('tests-create')  

    def test_create_test_success(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Python Basics",
            "description": "Test on Python.",
            "duration_minutes": 30,
            "total_marks": 100
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['st'], 1)
        self.assertTrue(Test.objects.filter(title='Python Basics').exists())

    def test_create_test_validation_error(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "",
            "description": ""
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['st'], 2)
        self.assertIn('duration_minutes', response.data['errors'])
        self.assertIn('total_marks', response.data['errors'])

    def test_create_test_unauthenticated(self):
        data = {
            "title": "Unauthorized",
            "description": "No login",
            "duration_minutes": 20,
            "total_marks": 50
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
