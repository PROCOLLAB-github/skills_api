from rest_framework import serializers

from courses.mapping import SWAGGER_API_HINTS
from courses.models import Skill, Task
from files.models import FileModel


class StepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=SWAGGER_API_HINTS)
    is_done = serializers.BooleanField()
    ordinal_number = serializers.IntegerField()


class TaskSerializer(serializers.Serializer):
    count = serializers.IntegerField(help_text="количество вопросов и информационных слайдов у задания")
    step_data = StepSerializer(many=True)


class FileSerializer(serializers.ListSerializer):
    child = serializers.FileField(required=False)


class StrSerializer(serializers.Serializer):
    string = serializers.CharField(required=False)


class TasksOfSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["skill"]


class FileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = ("link",)


class SkillsBasicSerializer(serializers.ModelSerializer):
    file_link = serializers.URLField(source="file.link")  # Access the link field from the related FileModel

    class Meta:
        model = Skill
        fields = ("id", "name", "who_created", "file_link", "quantity_of_levels")


class SkillSerializer(serializers.Serializer):
    skill_name = serializers.CharField()
    file = serializers.URLField()
    skill_preview = serializers.URLField()
    skill_point_logo = serializers.URLField()
    description = serializers.CharField()
    level = serializers.IntegerField()
    progress = serializers.IntegerField()


class TaskOnSkillResponseSerializer(SkillSerializer):
    count = serializers.IntegerField()
    step_data = StepSerializer(many=True)


IntegerListSerializer = serializers.ListSerializer(child=serializers.IntegerField(), allow_empty=False)
