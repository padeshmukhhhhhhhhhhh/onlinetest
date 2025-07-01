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
