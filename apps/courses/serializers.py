from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from courses.mapping import SWAGGER_API_HINTS
from courses.models import Skill, Task
from courses.typing import TaskResultData, TaskResponseSerializerData, PopupSerializerData


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


class TasksOfSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["skill"]


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


class SkillSerializer(serializers.Serializer):
    skill_name = serializers.CharField()
    file = serializers.URLField()
    skill_preview = serializers.URLField()
    skill_point_logo = serializers.URLField()
    description = serializers.CharField()
    level = serializers.IntegerField()
    progress = serializers.IntegerField()


class TaskResult(DataclassSerializer):

    class Meta:
        dataclass = TaskResultData


class PopupSerializer(DataclassSerializer):

    class Meta:
        dataclass = PopupSerializerData


IntegerListSerializer = serializers.ListSerializer(child=serializers.IntegerField(), allow_empty=False)
