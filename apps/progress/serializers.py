from rest_framework import serializers

from progress.models import CustomUser


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


class UserScoreSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    specialization = serializers.CharField(max_length=100)
    geo_position = serializers.CharField(max_length=100)
    score_count = serializers.IntegerField()


class IntegerListSerializer(serializers.ListSerializer):
    child = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        return user

    class Meta:
        model = CustomUser
        fields = ("id", "email", "password", "first_name", "last_name")
