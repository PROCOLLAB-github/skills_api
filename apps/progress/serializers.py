from datetime import datetime

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from progress.models import CustomUser, UserProfile


class UserDataSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    specialization = serializers.CharField(max_length=100)
    geo_position = serializers.CharField(max_length=100)
    points = serializers.IntegerField()


class SkillSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField()
    skill_name = serializers.CharField()
    skill_level = serializers.IntegerField()
    skill_progress = serializers.IntegerField()


class MonthSerializer(serializers.Serializer):
    month = serializers.CharField()
    year = serializers.IntegerField()
    successfully_done = serializers.BooleanField()


class ProfileResponseSerializer(serializers.Serializer):
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

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    age = serializers.SerializerMethodField()
    specialization = serializers.CharField(source="user.specialization", read_only=True)
    geo_position = serializers.CharField(source="user.geo_position", read_only=True)
    score_count = serializers.IntegerField(read_only=True)
    file = serializers.CharField(source="file.link", read_only=True, default=None)

    class Meta:
        model = UserProfile
        fields = ["user_name", "age", "specialization", "geo_position", "score_count", "file"]

    def get_age(self, obj) -> int:
        if not obj.user.age:
            return 0
        current_date = datetime.now().date()
        time_difference = current_date - obj.user.age
        years_passed = time_difference.days // 365
        return years_passed


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


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class CustomObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class SubProclong(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["is_autopay_allowed"]


class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "city",
            "organization",
            "age",
            "specialization",
            "datetime_updated",
            "datetime_created",
            "avatar",
        ]

    def get_avatar(self, obj: CustomUser) -> str | None:
        if file := obj.profiles.file:
            return file.link
