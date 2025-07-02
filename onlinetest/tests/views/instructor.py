from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..serializers.instructor_serializers import *



class TestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            test = serializer.save()
            return Response(TestSerializer(test).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk):
        test = get_object_or_404(Test, pk=pk)

        serializer = TestSerializer(test, data=request.data, context={'request': request})
        if serializer.is_valid():
            test = serializer.save()
            return Response(TestSerializer(test).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        test = get_object_or_404(Test, pk=pk)
        return Response(TestSerializer(test).data)

    def delete(self, request, pk):
        serializer = TestDeleteValidator(data={'pk': pk}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        test = serializer.test
        test.delete()
        return Response({"detail": "Test deleted successfully."}, status=204)




class QuestionListByTestAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        test = get_object_or_404(Test, pk=test_id)

        questions = Question.objects.filter(test=test)
        serializer = QuestionSerializer(questions, many=True, context={'request': request})

        return Response({
            "question_count": questions.count(),
            "questions": serializer.data
        }, status=status.HTTP_200_OK)

class QuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
    
        data = request.data.copy()
        data['test'] = test_id  

        serializer = QuestionSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        return Response(QuestionSerializer(question).data, status=201)

    def put(self, request, pk):
        
        question = get_object_or_404(Question, pk=pk)

        print(question)

        serializer = QuestionSerializer(question, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_question = serializer.save()

        return Response(QuestionSerializer(updated_question).data, status=200)


    def get(self, request, pk):

        validator = QuestionAccessValidator(data={'pk': pk}, context={'request': request})
        validator.is_valid(raise_exception=True)
        question = validator.question

        return Response(QuestionSerializer(question).data, status=200)

    def delete(self, request, pk):
    
        validator = QuestionAccessValidator(data={'pk': pk}, context={'request': request})
        validator.is_valid(raise_exception=True)
        question = validator.question

        question.delete()
        return Response({"detail": "Question deleted."}, status=204)