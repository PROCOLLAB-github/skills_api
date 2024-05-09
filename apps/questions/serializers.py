from abc import ABC

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from questions.models import InfoSlide
from questions.typing import QuestionExcludeSerializerData, SingleAnswerData


class IsAnsweredSerializer(serializers.Serializer):
    is_answered = serializers.BooleanField(default=False)


class FileSerializer(serializers.ListSerializer, ABC):
    child = serializers.FileField()


class InfoSlideSerializer(serializers.Serializer):
    text = serializers.CharField()
    files = serializers.ListSerializer(child=serializers.CharField())

    class Meta:
        model = InfoSlide
        fields = ["text", "files"]


class SingleAnswerSerializer(DataclassSerializer):
    class Meta:
        dataclass = SingleAnswerData


class SingleQuestionAnswerSerializer(DataclassSerializer):
    class Meta:
        dataclass = QuestionExcludeSerializerData


class SingleCorrectPostSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField(allow_null=False)
    correct_answer = serializers.IntegerField(required=False)


class StrSerializer(serializers.Serializer):
    string = serializers.CharField(required=False)


class ConnectQuestionSerializer(IsAnsweredSerializer):
    id = serializers.IntegerField()
    question_text = serializers.CharField(required=False)
    description = serializers.CharField()
    files = serializers.ListSerializer(child=serializers.CharField())
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


class CustomTextSerializer(serializers.Serializer):
    text = serializers.CharField(default="need more...")


class CustomTextSucessSerializer(serializers.Serializer):
    text = serializers.CharField(default="success")
