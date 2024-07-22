from datetime import datetime
from rest_framework import serializers

from progress.models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from progress.models import CustomUser


class UserDataSerializer(serializers.Serializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    specialization = serializers.CharField(read_only=True)
    geo_position = serializers.CharField(read_only=True)
    file_link = serializers.CharField(read_only=True)


class UserSkillProgressSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField(read_only=True)
    skill_name = serializers.CharField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    progress = serializers.IntegerField(read_only=True)


class MonthSerializerResponseSerializer(serializers.Serializer):
    month = serializers.CharField(read_only=True)
    is_passed = serializers.BooleanField(read_only=True)


class UserProfileResponseSerializer(serializers.Serializer):
    user_data = UserDataSerializer(read_only=True)
    skills = UserSkillProgressSerializer(many=True, read_only=True)
    months = MonthSerializerResponseSerializer(many=True, read_only=True)


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
