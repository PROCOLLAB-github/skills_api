from abc import ABC, abstractmethod

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from requests import Response

from files.constants import SUPPORTED_IMAGES_TYPES
from files.exceptions import SelectelUploadError
from files.helpers import convert_image_to_webp
from files.typings import FileInfo
from procollab_skills.settings import SELECTEL_UPLOAD_URL

User = get_user_model()


class File:
    def __init__(self, file: TemporaryUploadedFile | InMemoryUploadedFile, quality: int = 70):
        self.size = file.size
        self.name = File._get_name(file)
        self.extension = File._get_extension(file)
        self.buffer = file.open(mode="rb")
        self.content_type = file.content_type

        # we can compress given type of image
        if self.content_type in SUPPORTED_IMAGES_TYPES:
            webp_image = convert_image_to_webp(file, quality)
            self.buffer = webp_image.buffer()
            self.size = webp_image.size
            self.content_type = "image/webp"
            self.extension = "webp"

    @staticmethod
    def _get_name(file) -> str:
        name_parts = file.name.split(".")
        if len(name_parts) == 1:
            return name_parts[0]
        return ".".join(name_parts[:-1])

    @staticmethod
    def _get_extension(file) -> str:
        if len(file.name.split(".")) > 1:
            return file.name.split(".")[-1]
        return ""


class Storage(ABC):
    @abstractmethod
    def delete(self, url: str) -> Response:
        pass

    @abstractmethod
    def upload(self, file: File, user: User) -> FileInfo:
        pass


class SelectelSwiftStorage(Storage):
    def delete(self, url: str) -> Response:
        token = self._get_auth_token()
        return requests.delete(url, headers={"X-Auth-Token": token})

    def upload(self, file: File, user: User) -> FileInfo:
        url = self._upload(file)
        return FileInfo(
            url=url,
            name=file.name,
            extension=file.extension,
            mime_type=file.content_type,
            size=file.size,
        )

    def _upload(self, file: File) -> str:
        token = self._get_auth_token()
        url = self._generate_url(file)

        requests.put(
            url,
            headers={
                "X-Auth-Token": token,
                "Content-Type": file.content_type,
            },
            data=file.buffer,
        )
        return f"{settings.SELECTEL_READ_FILES_DOMAIN}{file.name}.{file.extension}"  # show file

    def _generate_url(self, file: File) -> str:
        """
        Generates url for selcdn
        Returns:
            url: str looks like /hashedEmail/hashedFilename_hashedTime.extension
        """
        # return (
        #     f"{SELECTEL_SWIFT_URL}"
        #     f"{abs(hash(user.email))}"
        #     f"/{abs(hash(file.name))}"
        #     f"_{abs(hash(time.time()))}"
        #     f".{file.extension}"
        # )
        return f"{SELECTEL_UPLOAD_URL}" f"{file.name}" f".{file.extension}"

    @staticmethod
    def _get_auth_token():
        data = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": settings.SELECTEL_SERVICE_USERNAME,
                            "domain": {"name": settings.SELECTEL_ACCOUNT_ID},
                            "password": settings.SELECTEL_SERVICE_PASSWORD,
                        }
                    },
                },
                "scope": {
                    "project": {
                        "name": settings.SELECTEL_PROJECT_NAME,
                        "domain": {"name": settings.SELECTEL_ACCOUNT_ID},
                    }
                },
            }
        }

        response = requests.post(
            settings.SELECTEL_NEW_AUTH_TOKEN, headers={"Content-Type": "application/json"}, json=data
        )
        if response.status_code not in [200, 201]:
            raise SelectelUploadError("Couldn't generate a token for Selectel Swift API (selcdn)")
        return response.headers["X-Subject-Token"]


class CDN:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def delete(self, url: str) -> Response:
        return self.storage.delete(url)

    def upload(
        self,
        file: TemporaryUploadedFile | InMemoryUploadedFile,
        user: User,
        quality: int = 70,
    ) -> FileInfo:
        return self.storage.upload(File(file, quality), user)
