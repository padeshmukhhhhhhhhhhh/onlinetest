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


class SubmitAnswerSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    selected_option = serializers.CharField(max_length=1)

    def validate(self, data):
       
        try:
            session = StudentTestSession.objects.get(id=data["session_id"])
        except StudentTestSession.DoesNotExist:
            raise serializers.ValidationError("Invalid session ID.")

        try:
            question = Question.objects.get(id=data["question_id"])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Invalid question ID.")


        if question.test_id != session.test_id:
            raise serializers.ValidationError("This question does not belong to the test in this session.")

       
        valid_options = question.options.keys()  
        if data["selected_option"] not in valid_options:
            raise serializers.ValidationError("Selected option is not valid for this question.")

       
        data["session"] = session
        data["question"] = question

        return data



class SubmitTestSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()

    def validate_session_id(self, value):
        try:
            session = StudentTestSession.objects.get(id=value)
        except StudentTestSession.DoesNotExist:
            raise serializers.ValidationError("Invalid session_id. Test session does not exist.")
        
        if session.submitted:
            raise serializers.ValidationError("Test is already submitted.")

        self.instance = session  
        return value


