from rest_framework.exceptions import PermissionDenied


class UserDoesNotExistException(PermissionDenied):
    default_detail = {"error": "Such user does not exist. Try to register"}
