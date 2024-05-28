from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from questions.models import InfoSlide
from questions import typing


class InfoSlideSerializer(serializers.Serializer):
    """GET: Инфо-слайд (response)."""
    text = serializers.CharField()
    files = serializers.ListSerializer(child=serializers.CharField())
    is_done = serializers.BooleanField()

    class Meta:
        model = InfoSlide
        fields = ["text", "files", "is_done"]


class SingleQuestionAnswerSerializer(DataclassSerializer):
    """GET: Вопрос с 1 правильным ответом/на исключение (response)."""
    class Meta:
        dataclass = typing.QuestionSerializerData


class WriteQuestionSerializer(DataclassSerializer):
    """GET: Вопрос на ввод ответа (response)."""
    class Meta:
        dataclass = typing.QuestionWriteSerializerData


class ConnectQuestionSerializer(DataclassSerializer):
    """GET: Вопрос на соотношение (response)."""
    class Meta:
        dataclass = typing.QuestionСonnectSerializerData

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Удаляет "лишние" null поля: если вопрос содержит картинку, но не содержит "text" поля, "text" убирается.
        data["connect_left"] = [{k: v for k, v in item.items() if v is not None} for item in data["connect_left"]]
        data["connect_right"] = [{k: v for k, v in item.items() if v is not None} for item in data["connect_right"]]
        return data


class QuestionTextSerializer(serializers.Serializer):
    """POST: Вопрос с 1 правильным ответом - ответ пользователя (request)."""
    answer_id = serializers.IntegerField()


class SingleCorrectPostSerializer(serializers.Serializer):
    """POST: Вопрос с 1 правильным ответом - ответ пользователя (response)."""
    is_correct = serializers.BooleanField(allow_null=False)
    correct_answer = serializers.IntegerField(required=False)


class SingleCorrectPostErrorResponseSerializer(DataclassSerializer):
    """POST: Вопрос с 1 правильным ответом если пользователь ошибся (response)."""
    class Meta:
        dataclass = typing.SingleCorrectPostErrorResponseSerializerData


class SingleCorrectPostSuccessResponseSerializer(DataclassSerializer):
    """POST: Вопрос с 1 правильным ответом если пользователь прав (response)."""
    class Meta:
        dataclass = typing.SingleCorrectPostSuccessResponseSerializerData


class ConnectAnswerSerializer(DataclassSerializer):
    """Вопрос на соотношение: 1 ответ пользователя."""
    class Meta:
        dataclass = typing.ConnectAnswerSerializerData


class ConnectQuestionPostRequestSerializer(serializers.ListSerializer):
    """POST: Вопрос на соотношение - список ответов пользователя (request)."""
    child = ConnectAnswerSerializer()


class ScoredConnectAnswerSerializer(DataclassSerializer):
    """Вопрос на соотношение: 1 ответ с результатом если пользователь ошибся."""
    class Meta:
        dataclass = typing.ScoredConnectAnswerSerializerData


class ConnectQuestionPostResponseSerializer(serializers.ListSerializer):
    """POST: Вопрос на соотношение - список из ответов с результатом если пользователь ошибся (response)."""
    child = ScoredConnectAnswerSerializer()


class WriteAnswerTextSerializer(DataclassSerializer):
    """POST: Вопрос на ввод ответа - ответ пользователя (request)."""
    class Meta:
        dataclass = typing.WriteAnswerTextSerializerData


class QuestionExcludePostResponseSerializer(DataclassSerializer):
    """POST: Вопрос на исключение - ответ если пользователь ошибся (response)."""
    class Meta:
        dataclass = typing.QuestionExcludePostResponseSerializer


class IntegerListSerializer(serializers.ListSerializer):
    """Список int чисел."""
    child = serializers.IntegerField()


class SimpleNumberListSerializer(serializers.Serializer):
    """Словарь 'numbers' со списком int чисел."""
    numbers = IntegerListSerializer(child=serializers.IntegerField(), allow_empty=False)


class CustomTextSucessSerializer(DataclassSerializer):
    """Словарь 'text' с str описанием."""
    class Meta:
        dataclass = typing.CustomTextSucessSerializerData


class CustomTextErrorSerializer(DataclassSerializer):
    """Словарь 'error' с str описанием."""
    class Meta:
        dataclass = typing.CustomTextErrorSerializerData
