
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..serializers.student_serializers import *
from django.utils import timezone
from tests.utils  import *
from datetime import timedelta
from tests.tasks import *


class StudentTestListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        validator = StudentTestListValidator(data={}, context={'request': request})
        if not validator.is_valid():
            return CustomResponse(
                2,
                "Validation failed.",
                errors=validator.errors,
                status_code=status.HTTP_403_FORBIDDEN
            )
        tests = Test.objects.all().order_by('-created_at')
        serializer = StudentTestListSerializer(tests,context={'request': request},many=True)
        
        
        return CustomResponse(
            1,
            "Student test list retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )




class StartTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
        data = {"test_id": test_id}
        serializer = StartTestSessionSerializer(data=data, context={'request': request})

        if not serializer.is_valid():
            return CustomResponse(
                2,
                "Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        test = serializer.validated_data['test']
        student = request.user

        session = StudentTestSession.objects.create(
            student=student,
            test=test,
            start_time=timezone.now()
        )

        end_time = session.start_time + timedelta(minutes=session.test.duration_minutes)
        auto_submit_test.apply_async((session.id,), eta=end_time)

        questions = Question.objects.filter(test=test)
        question_data = StudentQuestionSerializer(questions, many=True).data

        return CustomResponse(
            1,
            "Test session started successfully.",
            data={
                "student_session_id": session.id,
                "test_id": test.id,
                "test_title": test.title,
                "duration_minutes": test.duration_minutes,
                "total_marks": test.total_marks,
                "questions": question_data
            },
            status_code=status.HTTP_201_CREATED
        )


class SubmitAnswerView(APIView):
    def post(self, request):
        serializer = SubmitAnswerSerializer(data=request.data)

        if serializer.is_valid():
            session = serializer.validated_data["session"]
            question = serializer.validated_data["question"]
            selected_option = serializer.validated_data["selected_option"]

            is_correct = (selected_option == question.correct_answer)

            StudentAnswer.objects.update_or_create(
                session=session,
                question=question,
                defaults={
                    "selected_option": selected_option,
                    "is_correct": is_correct
                }
            )

            return CustomResponse(
                1,
                "Answer saved successfully.",
                status_code=status.HTTP_200_OK
            )

        return CustomResponse(
            2,
            "Validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class SubmitTestView(APIView):
    def post(self, request):
        serializer = SubmitTestSerializer(data=request.data)

        if serializer.is_valid():
            session = serializer.instance
            calculate_and_submit_test(session)

            return CustomResponse(
                1,
                "Test submitted successfully.",
                data={"score": session.score},
                status_code=status.HTTP_200_OK
            )

        return CustomResponse(
            2,
            "Validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
