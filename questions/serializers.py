from abc import ABC

from rest_framework import serializers

from questions.models import InfoSlide


class IsAnsweredSerializer(serializers.Serializer):
    is_answered = serializers.BooleanField(default=False)


class FileSerializer(serializers.ListSerializer, ABC):
    child = serializers.FileField(required=False)


class InfoSlideSerializer(serializers.Serializer):
    text = serializers.CharField()
    files = FileSerializer()

    class Meta:
        model = InfoSlide
        fields = ["text", "files"]


class SingleAnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    answer_text = serializers.CharField()


class SingleQuestionAnswerSerializer(IsAnsweredSerializer):
    question_text = serializers.CharField()
    description = serializers.CharField(required=False)
    files = FileSerializer(required=False)
    answers = SingleAnswerSerializer(many=True)


class SingleCorrectPostSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField(allow_null=False)
    correct_answer = serializers.IntegerField(required=False)


class StrSerializer(serializers.Serializer):
    string = serializers.CharField(required=False)


class ConnectQuestionSerializer(IsAnsweredSerializer):
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


class CustomTextSerializer(serializers.Serializer):
    text = serializers.CharField(default="need more...")


class CustomTextSucessSerializer(serializers.Serializer):
    text = serializers.CharField(default="success")
