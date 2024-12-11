from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from courses.serializers import PopupSerializer
from questions import typing


class AbstractPopupField(DataclassSerializer):
    """Абстрактный класс под поле popups"""
    popups = PopupSerializer(many=True, read_only=True, required=False, allow_null=True)

    class Meta:
        abstract = True


class InfoSlideSerializer(AbstractPopupField):
    """GET: инфо-слайд (response)."""
    description = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        dataclass = typing.InfoSlideSerializerData


class SingleQuestionAnswerSerializer(AbstractPopupField):
    """GET: Вопрос с 1 правильным ответом/на исключение (response)."""

    class Meta:
        dataclass = typing.QuestionSerializerData


class WriteQuestionSerializer(AbstractPopupField):
    """GET: Вопрос на ввод ответа (response)."""

    class Meta:
        dataclass = typing.QuestionWriteSerializerData


class ConnectQuestionSerializer(AbstractPopupField):
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


class ConnectAnswerSerializer(DataclassSerializer):
    """Вопрос на соотношение: 1 ответ пользователя."""

    class Meta:
        dataclass = typing.ConnectAnswerSerializerData


class ConnectQuestionPostRequestSerializer(serializers.ListSerializer):
    """POST: Вопрос на соотношение - список ответов пользователя (request)."""

    child = ConnectAnswerSerializer()


class WriteAnswerTextSerializer(DataclassSerializer):
    """POST: Вопрос на ввод ответа - ответ пользователя (request)."""

    class Meta:
        dataclass = typing.WriteAnswerTextSerializerData


class CustomTextErrorSerializer(DataclassSerializer):
    """Словарь 'error' с str описанием."""

    class Meta:
        dataclass = typing.CustomTextErrorSerializerData


class CorrectAnswerResponse(serializers.Serializer):
    is_correct = serializers.BooleanField(default=True)


class IncorrectAnswerResponse(serializers.Serializer):
    is_correct = serializers.BooleanField(default=False)


class EmptySerializer(serializers.Serializer):
    pass
