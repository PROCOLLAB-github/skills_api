from rest_framework import serializers

from courses.mapping import SWAGGER_API_HINTS
from courses.models import Skill, Task
from files.models import FileModel


class StepSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=SWAGGER_API_HINTS)
    is_done = serializers.BooleanField()


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
        fields = ("name", "file")


class SkillsBasicSerializer(serializers.ModelSerializer):
    file = FileModelSerializer()

    class Meta:
        model = Skill
        fields = ("id", "name", "who_created", "file", "quantity_of_levels")
