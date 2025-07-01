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