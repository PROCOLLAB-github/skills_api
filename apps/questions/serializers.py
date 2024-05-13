from abc import ABC

from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from progress.models import TaskObjUserResult
from questions.models import InfoSlide
from questions.typing import (
    QuestionSerializerData,
    SingleAnswerData,
    QuestionWriteSerializerData,
    QuestionСonnectSerializerData,
)


class IsAnsweredSerializer(serializers.Serializer):
    is_answered = serializers.BooleanField(default=False)


class FileSerializer(serializers.ListSerializer, ABC):
    child = serializers.FileField()


class InfoSlideSerializer(serializers.Serializer):
    text = serializers.CharField()
    files = serializers.ListSerializer(child=serializers.CharField())
    is_done = serializers.BooleanField()

    class Meta:
        model = InfoSlide
        fields = ["text", "files", "is_done"]


class SingleAnswerSerializer(DataclassSerializer):
    class Meta:
        dataclass = SingleAnswerData


class SingleQuestionAnswerSerializer(DataclassSerializer):
    class Meta:
        dataclass = QuestionSerializerData


class SingleCorrectPostSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField(allow_null=False)
    correct_answer = serializers.IntegerField(required=False)


class StrSerializer(serializers.Serializer):
    string = serializers.CharField(required=False)


class ConnectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    answer_text = serializers.CharField()


class ConnectQuestionSerializer(DataclassSerializer):
    class Meta:
        dataclass = QuestionСonnectSerializerData


class ScoredConnectAnswerSerializer(serializers.Serializer):
    left_id = serializers.IntegerField()
    right_id = serializers.IntegerField()
    is_correct = serializers.BooleanField()


class ConnectQuestionPostResponseSerializer(serializers.ListSerializer):
    child = ScoredConnectAnswerSerializer()


class ConnectAnswerSerializer(serializers.Serializer):
    left_id = serializers.IntegerField()
    right_id = serializers.IntegerField()


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


class WriteQuestionSerializer(DataclassSerializer):
    class Meta:
        dataclass = QuestionWriteSerializerData


class WriteAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskObjUserResult
        fields = ["id", "text"]


class WriteAnswerTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskObjUserResult
        fields = [
            "text",
        ]


class QuestionTextSerializer(serializers.Serializer):
    answer_id = serializers.IntegerField()
