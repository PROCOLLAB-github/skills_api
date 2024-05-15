from django.db import IntegrityError
from rest_framework.exceptions import PermissionDenied

PermissionDenied


class UserAlreadyAnsweredException(IntegrityError):
    message = "User has already done this slide!"

    def __str__(self):
        return f"{self.message}"


class WrongEndpointUsedException(PermissionDenied):
    @classmethod
    def __str__(self, expected_model_name: str, gotten_obj_model_name: str) -> str:
        return f"""You tried to summon taskobject with a wrong endpoint. 
            Instead of using '{expected_model_name}' endpoint, 
            try using '{gotten_obj_model_name}' endpoint."""
