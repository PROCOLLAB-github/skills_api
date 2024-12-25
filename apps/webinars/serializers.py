from rest_framework import serializers

from webinars.models import Webinar, Speaker, WebinarRegistration


class SpeakerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Speaker
        fields = [
            "full_name",
            "photo",
            "position",
        ]


class AbstractWebinarFields(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    speaker = SpeakerSerializer()

    def get_duration(self, obj: Webinar) -> int:
        """Длительность вебинара в минутах."""
        return int((obj.datetime_end - obj.datetime_start).total_seconds() // 60)


class WebinarActualSerializer(AbstractWebinarFields, serializers.ModelSerializer):
    is_registrated = serializers.SerializerMethodField()

    class Meta:
        model = Webinar
        fields = [
            "id",
            "title",
            "description",
            "datetime_start",
            "duration",
            "is_registrated",
            "speaker",
        ]

    def get_is_registrated(self, obj: Webinar) -> bool | None:
        """Зарегистрирован ли пользователь на вебинар."""
        request_user = self.context["request"].user
        if not request_user:
            return None
        return WebinarRegistration.objects.filter(user=request_user, webinar=obj).exists()


class WebinarRecordsSerializer(AbstractWebinarFields, serializers.ModelSerializer):
    recording_link = serializers.SerializerMethodField()

    class Meta:
        model = Webinar
        fields = [
            "id",
            "title",
            "description",
            "datetime_start",
            "recording_link",
            "duration",
            "speaker",
        ]

    def get_recording_link(self, obj: Webinar) -> bool:
        """Булевый параметр наличия ссылки, получить ссылку можно на отдельном эндпоинте"""
        return bool(obj.recording_link)


class WebinarRecordsLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webinar
        fields = ["recording_link"]
