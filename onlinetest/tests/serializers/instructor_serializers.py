from rest_framework import serializers
from tests.models import *

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'title', 'description', 'duration_minutes', 'total_marks', 'created_at']

    def validate(self, attrs):
        user = self.context['request'].user
        if user.role != 'instructor':
            raise serializers.ValidationError("Only instructors can create or update tests.")
        return attrs

    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user != instance.instructor:
            raise serializers.ValidationError("You can only update your own tests.")
        return super().update(instance, validated_data)

class TestDeleteValidator(serializers.Serializer):
    pk = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        try:
            test = Test.objects.get(pk=data['pk'])
        except Test.DoesNotExist:
            raise serializers.ValidationError("Test not found.")

        if test.instructor != user:
            raise serializers.ValidationError("You can only delete your own test.")

        self.test = test
        return data


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'test', 'text', 'options', 'correct_answer']

    def validate(self, data):
        user = self.context['request'].user

        if user.role != 'instructor':
            raise serializers.ValidationError("Only instructors can manage questions.")

        test = data.get('test') or getattr(self.instance, 'test', None)
        if test and test.instructor != user:
            raise serializers.ValidationError("You can only manage questions in your own tests.")

        return data



class QuestionAccessValidator(serializers.Serializer):
    pk = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        try:
            question = Question.objects.get(pk=data['pk'])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question not found.")

        if question.test.instructor != user:
            raise serializers.ValidationError("You can only access your own questions.")

        self.question = question
        return data