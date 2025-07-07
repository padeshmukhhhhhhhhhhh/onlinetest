from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..serializers.instructor_serializers import *
from tests.utils import *


class TestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            test = serializer.save()
            return CustomResponse(
                1,
                "Test created successfully.",
                data=TestSerializer(test).data,
                status_code=status.HTTP_201_CREATED
            )
        return CustomResponse(
            2,
            "Validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk):
        test = get_object_or_404(Test, pk=pk)
        serializer = TestSerializer(test, data=request.data, context={'request': request})
        if serializer.is_valid():
            test = serializer.save()
            return CustomResponse(
                1,
                "Test updated successfully.",
                data=TestSerializer(test).data,
                status_code=status.HTTP_200_OK
            )
        return CustomResponse(
            2,
            "Validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, pk):
        test = get_object_or_404(Test, pk=pk)
        return CustomResponse(
            1,
            "Test retrieved successfully.",
            data=TestSerializer(test).data,
            status_code=status.HTTP_200_OK
        )

    def delete(self, request, pk):
        serializer = TestDeleteValidator(data={'pk': pk}, context={'request': request})
        if serializer.is_valid():
            test = serializer.validated_data['test']
            test.delete()
            return CustomResponse(
                1,
                "Test deleted successfully.",
                status_code=status.HTTP_204_NO_CONTENT
            )
        return CustomResponse(
            2,
            "Validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )



class QuestionListByTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        test = get_object_or_404(Test, pk=test_id)

        questions = Question.objects.filter(test=test)
        serializer = QuestionSerializer(questions, many=True, context={'request': request})

        return CustomResponse(
            1,
            "Questions retrieved successfully.",
            data={
                "question_count": questions.count(),
                "questions": serializer.data
            },
            status_code=status.HTTP_200_OK
        )



class QuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
        data = request.data.copy()
        data['test'] = test_id

        serializer = QuestionSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            question = serializer.save()
            return CustomResponse(
                1,
                "Question created successfully.",
                data=QuestionSerializer(question).data,
                status_code=status.HTTP_201_CREATED
            )
        return CustomResponse(
            2,
            "Validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, pk):
        question = get_object_or_404(Question, pk=pk)

        serializer = QuestionSerializer(question, data=request.data, context={'request': request})
        if serializer.is_valid():
            updated_question = serializer.save()
            return CustomResponse(
                1,
                "Question updated successfully.",
                data=QuestionSerializer(updated_question).data,
                status_code=status.HTTP_200_OK
            )
        return CustomResponse(
            2,
            "Validation failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, pk):
        validator = QuestionAccessValidator(data={'pk': pk}, context={'request': request})
        if validator.is_valid():
            question = validator.validated_data['question']
            
            return CustomResponse(
                1,
                "Question retrieved successfully.",
                data=QuestionSerializer(question).data,
                status_code=status.HTTP_200_OK
            )
        return CustomResponse(
            2,
            "Validation failed.",
            errors=validator.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        validator = QuestionAccessValidator(data={'pk': pk}, context={'request': request})
        if validator.is_valid():
            question = validator.validated_data['question']
            question.delete()
            return CustomResponse(
                1,
                "Question deleted successfully.",
                status_code=status.HTTP_204_NO_CONTENT
            )
        return CustomResponse(
            2,
            "Validation failed.",
            errors=validator.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class GenerateAIQuestionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIQuestionGenerationSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return CustomResponse(
                2,
                "Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        test = serializer.validated_data['test']
        num_questions = serializer.validated_data['number_of_questions']

        ai_response = generate_questions_via_ai(test.title, num_questions)
        print(ai_response)

        if isinstance(ai_response, dict) and ai_response.get("error"):
            return CustomResponse(
                2,
                "AI generation failed.",
                errors={"error": ai_response["error"]},
                status_code=status.HTTP_502_BAD_GATEWAY
            )

        try:
            questions_data = json.loads(ai_response)
        except json.JSONDecodeError:
            return CustomResponse(
                2,
                "Failed to parse AI response.",
                errors={"error": "Invalid JSON from AI."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        created_count = 0

        for q in questions_data:
            try:
                Question.objects.create(
                    test=test,
                    text=q['text'],
                    options=q['options'],
                    correct_answer=q['correct_answer']
                )
                created_count += 1
            except Exception:
                continue

        return CustomResponse(
            1,
            f"{created_count} questions generated and saved.",
            status_code=status.HTTP_201_CREATED
        )



class TestResultsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        serializer = TestResultsRequestSerializer(data={'test_id': test_id}, context={'request': request})
        
        if not serializer.is_valid():
            return CustomResponse(
                2,
                "Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        test = serializer.context['test']
        sessions = StudentTestSession.objects.filter(test=test)
        results_serializer = StudentTestResultSerializer(sessions, many=True)

        return CustomResponse(
            1,
            "Test results retrieved successfully.",
            data=results_serializer.data,
            status_code=status.HTTP_200_OK
        )
