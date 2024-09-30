from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from courses.mapping import SWAGGER_API_HINTS
from courses.models import Skill
from courses.typing import (
    TaskResultData,
    TaskResponseSerializerData,
    PopupSerializerData,
    TaskOfSkillProgressSerializerData,
)


class StepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=SWAGGER_API_HINTS)
    is_done = serializers.BooleanField()
    ordinal_number = serializers.IntegerField()


class TaskSerializer(serializers.Serializer):
    skill_name = serializers.CharField(allow_null=True)
    skill_preview = serializers.CharField(allow_null=True)
    skill_point_logo = serializers.CharField(allow_null=True)
    count = serializers.IntegerField(help_text="количество вопросов и информационных слайдов у задания")
    step_data = StepSerializer(many=True)


class TaskResponseSerializer(DataclassSerializer):

    class Meta:
        dataclass = TaskResponseSerializerData


class CoursesResponseSerializer(TaskSerializer):
    current_level = serializers.IntegerField()
    next_level = serializers.IntegerField(required=False, allow_null=True)
    progress = serializers.IntegerField()
    tasks = TaskResponseSerializer(many=True)


class TaskOfSkillProgressSerializer(DataclassSerializer):
    class Meta:
        dataclass = TaskOfSkillProgressSerializerData


class SkillsBasicSerializer(serializers.ModelSerializer):
    file_link = serializers.URLField(source="file.link")  # Access the link field from the related FileModel
    # Просьба захардкодить, статичный 1 уровень для всех навыков
    quantity_of_levels = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = ("id", "name", "who_created", "file_link", "quantity_of_levels", "description")

    def get_quantity_of_levels(self, obj) -> int:
        # Просьба захардкодить, статичный 1 уровень для всех навыков
        return 1


class TaskResult(DataclassSerializer):

    class Meta:
        dataclass = TaskResultData


class PopupSerializer(DataclassSerializer):

    class Meta:
        dataclass = PopupSerializerData


IntegerListSerializer = serializers.ListSerializer(child=serializers.IntegerField(), allow_empty=False)


class SkillDetailsSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="name")
    file = serializers.SerializerMethodField()
    skill_preview = serializers.SerializerMethodField()
    skill_point_logo = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = (
            "skill_name",
            "file",
            "skill_preview",
            "skill_point_logo",
            "description",
            "level",
        )

    def get_level(self, obj) -> int:
        # Просьба захардкодить на 1 уровень везде.
        return 1

    def get_file(self, obj) -> str | None:
        return obj.file.link if obj.file else None

    def get_skill_preview(self, obj) -> str | None:
        return obj.skill_preview.link if obj.skill_preview else None

    def get_skill_point_logo(self, obj) -> str | None:
        return obj.skill_point_logo.link if obj.skill_point_logo else None
