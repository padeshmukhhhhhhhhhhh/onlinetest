
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..serializers.student_serializers import *
from django.utils import timezone




class StudentTestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tests = Test.objects.all().order_by('-created_at')
        serializer = StudentTestListSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class StartTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):

        data = {"test_id": test_id}
        serializer = StartTestSessionSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        test = serializer.test
        student = request.user

        session = StudentTestSession.objects.create(
            student=student,
            test=test,
            start_time=timezone.now()
        )

      
        questions = Question.objects.filter(test=test)
        question_data = StudentQuestionSerializer(questions, many=True).data

        return Response({
            "student_session_id": session.id,
            "test_id": test.id,
            "test_title": test.title,
            "duration_minutes": test.duration_minutes,
            "total_marks": test.total_marks,
            "questions": question_data
        }, status=status.HTTP_201_CREATED)