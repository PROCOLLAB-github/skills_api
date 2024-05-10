from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from progress.models import UserProfile


class UserDataSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    specialization = serializers.CharField(max_length=100)
    geo_position = serializers.CharField(max_length=100)


class SkillSerializer(serializers.Serializer):
    skill_name = serializers.CharField(max_length=100)
    level = serializers.IntegerField(help_text="""Выводится как 'количество пройденный уровней' + 1'""")
    progress = serializers.FloatField(required=False, help_text="""Выводится только выбран юзером""")


class MonthSerializer(serializers.Serializer):
    month = serializers.CharField(max_length=100)
    is_passed = serializers.BooleanField()


class ResponseSerializer(serializers.Serializer):
    user_data = UserDataSerializer()
    skills = SkillSerializer(many=True)
    months = MonthSerializer(many=True)


class HollowSerializer(serializers.Serializer):
    pass


class SkillScoreSerializer(serializers.Serializer):
    skill_name = serializers.CharField(max_length=100)
    score_count = serializers.IntegerField()


class UserScoreSerializer(serializers.ModelSerializer):
    """Сериалайзер пользователя для рейтинга."""

    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    age = serializers.IntegerField(source='user.age', read_only=True)
    specialization = serializers.CharField(source='user.specialization', read_only=True)
    geo_position = serializers.CharField(source='user.geo_position', read_only=True)
    score_count = serializers.IntegerField(read_only=True)
    file = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["user_name", "age", "specialization", "geo_position", "score_count", "file"]

    @extend_schema_field(serializers.CharField())
    def get_file(self, obj):
        # У профиля нет файлов пока что.
        # return obj.file.link if obj.file else None
        return None


class IntegerListSerializer(serializers.ListSerializer):
    child = serializers.IntegerField()
