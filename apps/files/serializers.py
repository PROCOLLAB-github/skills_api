from rest_framework.serializers import ModelSerializer

from files.models import FileModel


class UserFileSerializer(ModelSerializer):
    class Meta:
        model = FileModel
        fields = [
            "name",
            "extension",
            "mime_type",
            "size",
            "link",
            "user",
            "datetime_uploaded",
        ]
