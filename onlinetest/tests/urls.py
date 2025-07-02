
from django.urls import path
from .views.common import *
from .views.instructor import *
from .views.student import *
urlpatterns = [
    path('register/',RegisterAPIView.as_view(), name='register'),
    path('send-login-otp/', SendOTPAPIView.as_view(), name='send-login-otp'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),


    path('tests/create/', TestAPIView.as_view(), name="tests-create"),
    path('tests/update/<int:pk>/', TestAPIView.as_view(), name="tests-update"),
    path('tests/view/<int:pk>/', TestAPIView.as_view(), name="tests-view"),
    path('tests/questions/view/<int:test_id>/', QuestionListByTestAPIView.as_view(), name="tests-questions-view"),
    path('tests/delete/<int:pk>/', TestAPIView.as_view(), name="tests-view"),


    path('questions/<int:test_id>/create/', QuestionAPIView.as_view(), name="tests-create"),
    path('questions/update/<int:pk>/', QuestionAPIView.as_view(), name="tests-update"),
    path('questions/view/<int:pk>/', QuestionAPIView.as_view(), name="tests-view"),
    path('questions/delete/<int:pk>/', QuestionAPIView.as_view(), name="tests-delete"),


    path('student/test/list/', StudentTestListAPIView.as_view(), name='student-test-list'),
    path('student/test/start/<int:test_id>/', StartTestAPIView.as_view(), name='start-test'),
    path('student/submit-answer/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('student/submit-test/', SubmitTestView.as_view(), name='submit-test'),

]
