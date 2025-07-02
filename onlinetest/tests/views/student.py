
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..serializers.student_serializers import *
from django.utils import timezone
from tests.utils  import calculate_and_submit_test



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

            return Response({"message": "Answer saved."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class SubmitTestView(APIView):
    def post(self, request):
        serializer = SubmitTestSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.instance
            calculate_and_submit_test(session)

            return Response({
                "message": "Test submitted successfully.",
                "score": session.score
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)