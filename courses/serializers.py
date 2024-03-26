from rest_framework import serializers

from courses.mapping import SWAGGER_API_HINTS
from courses.models import Skill


class StepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=SWAGGER_API_HINTS)
    is_done = serializers.BooleanField()


class TaskSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text="количество вопросов и информационных слайдов у задания"
    )
    step_data = StepSerializer(many=True)


class FileSerializer(serializers.ListSerializer):
    child = serializers.FileField(required=False)


class InfoSlideSerializer(serializers.Serializer):
    text = serializers.CharField()
    files = FileSerializer(required=False)


class SingleAnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    answer_text = serializers.CharField()


class SingleQuestionAnswerSerializer(serializers.Serializer):
    question_text = serializers.CharField()
    description = serializers.CharField(required=False)
    files = FileSerializer(required=False)
    answers = SingleAnswerSerializer(many=True)


class SingleCorrectPostSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField(allow_null=False)
    correct_answer = serializers.IntegerField(required=False)


class StrSerializer(serializers.Serializer):
    string = serializers.CharField(required=False)


class ConnectQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question_text = serializers.CharField(required=False)
    connect_left = SingleAnswerSerializer(many=True)
    connect_right = StrSerializer(many=True)

class ScoredConnectAnswerSerializer(serializers.Serializer):
    left_id = serializers.IntegerField()
    right_text = serializers.CharField(max_length=255)
    is_correct = serializers.BooleanField()

class ConnectQuestionPostResponseSerializer(serializers.ListSerializer):
    child = ScoredConnectAnswerSerializer()


class ConnectAnswerSerializer(serializers.Serializer):
    left_id = serializers.IntegerField()
    right_text = serializers.CharField()


class ConnectQuestionPostRequestSerializer(serializers.Serializer):
    answer = ConnectAnswerSerializer(many=True)


class IntegerListSerializer(serializers.ListSerializer):
    child = serializers.IntegerField()


class SimpleNumberListSerializer(serializers.Serializer):
    numbers = IntegerListSerializer(child=serializers.IntegerField(), allow_empty=False)

class SkillsBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class CustomTextSerializer(serializers.Serializer):
    text = serializers.CharField(default="need more...")

class CustomTextSucessSerializer(serializers.Serializer):
    text = serializers.CharField(default="success")