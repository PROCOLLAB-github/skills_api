# from django.http import JsonResponse
# from rest_framework import status
# from rest_framework_simplejwt.authentication import JWTAuthentication

#
# from progress.exceptions import UserDoesNotExistException
# from progress.models import CustomUser
#
# CustomUser
# import requests
# import json
# import jwt
# from django.conf import settings

# TODO заменить AuthCheck из Permissions на Middleware
# class AuthCheckMiddleware:
#    """
#    Проверка JWT юзера через основной Procollab
#    """
#
#    @staticmethod
#    def _check_exists_skills(request, view, email: str) -> bool:
#        if user := CustomUser.objects.filter(email=email).first():
#            view.user = user
#            return True
#        return False
#
#    @staticmethod
#    def _check_exists_procollab(request, view, email: str) -> bool:
#        user_procollab_response = requests.get("https://dev.procollab.ru/auth/users/clone-data", data={"email": email})
#        if user_procollab_response.status_code == status.HTTP_200_OK:
#            data = json.loads(user_procollab_response.content)[0]
#            user = CustomUser.objects.create(
#                email=data["email"],
#                is_superuser=data["is_superuser"],
#                first_name=data["first_name"],
#                last_name=data["last_name"],
#                password=data["password"],
#            )
#            view.user = user
#            return True
#        raise UserDoesNotExistException()
#
#    def __init__(self, get_response):
#        self.get_response = get_response
#
#    def __call__(self, request):
#        token = request.META.get("HTTP_AUTHORIZATION")
#        url = request.path
#
#        if "docs" in url or "admin" in url:
#            return None
#
#        raise ValueError(url, type(url), "docs" in url)
#
#        if token and token.startswith("Bearer "):
#            try:
#                view_class = request.resolver_match.func.cls
#                raise ValueError(view_class)
#                decoded_token = jwt.decode(token[7:], settings.SECRET_KEY, algorithms=["HS256"])
#                email = decoded_token.get("email")
#                if self._check_exists_skills(request, request, email) or self._check_exists_procollab(request,
#                request, email):
#                    response = self.get_response(request)
#                    return response
#                else:
#                    return JsonResponse({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
#            except jwt.ExpiredSignatureError:
#                return JsonResponse({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
#            except jwt.InvalidTokenError:
#                return JsonResponse({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
#        else:
#            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


# class CustomJWTAuthentication(JWTAuthentication):
#     def authenticate(self, request):
#         pass
