from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme

from procollab_skills.auth import CustomAuth


class SimpleJWTTokenUserScheme(SimpleJWTScheme):
    target_class = CustomAuth
