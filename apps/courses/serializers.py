from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from courses.mapping import SWAGGER_API_HINTS
from courses.models import Skill, Task
from courses.typing import TaskResultData


class StepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=SWAGGER_API_HINTS)
    is_done = serializers.BooleanField()
    ordinal_number = serializers.IntegerField()


class TaskSerializer(serializers.Serializer):
    skill_name = serializers.CharField()
    skill_preview = serializers.CharField()
    skill_point_logo = serializers.CharField()
    count = serializers.IntegerField(help_text="количество вопросов и информационных слайдов у задания")
    step_data = StepSerializer(many=True)


class TasksOfSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["skill"]


class SkillsBasicSerializer(serializers.ModelSerializer):
    file_link = serializers.URLField(source="file.link")  # Access the link field from the related FileModel

    class Meta:
        model = Skill
        fields = ("id", "name", "who_created", "file_link", "quantity_of_levels", "description")


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


IntegerListSerializer = serializers.ListSerializer(child=serializers.IntegerField(), allow_empty=False)
