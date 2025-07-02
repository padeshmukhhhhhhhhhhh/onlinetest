from rest_framework import serializers
from tests.models import *



class StudentTestListSerializer(serializers.ModelSerializer):
    total_questions = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['id', 'title', 'description', 'duration_minutes', 'total_marks', 'total_questions']

    def get_total_questions(self, obj):
        return obj.questions.count()




class StudentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'options']  



class StartTestSessionSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        try:
            test = Test.objects.get(pk=data['test_id'])
        except Test.DoesNotExist:
            raise serializers.ValidationError("Test not found.")

        if user.role != 'student':
            raise serializers.ValidationError("Only students can start tests.")

        if StudentTestSession.objects.filter(student=user, test=test, submitted=False).exists():
            raise serializers.ValidationError("You have already started this test.")

        self.test = test
        return data