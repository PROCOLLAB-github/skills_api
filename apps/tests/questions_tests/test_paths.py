import pytest
from rest_framework.test import APIClient

from . import constants


class TestAllGetQUestionsPaths:
    """
    Тесты на отсутстивие доступа к получению задания (GET).
    Аноним, юзер без подписки, юзер с просроченной подпиской - не имеют доступа.
    К бесплтаным навыкам доступ отсуствует только у анонима.
    """

    @pytest.mark.parametrize("path", constants.ALL_GET_PATHS)
    def test_get_questions_path_by_anonymous(self, path: str, api_anonymous_client: APIClient):
        response = api_anonymous_client.get(path)
        response_data = response.json()

        assert response.status_code == 403, f"Аноним получил не тот статус код к: {path}"
        assert response_data["error"] == "User credentials are not given", "Неверный response для анона"

    @pytest.mark.parametrize("path", constants.ALL_GET_PATHS)
    def test_get_questions_path_wo_sub(self, path: str, api_auth_without_sub_client: APIClient):
        response = api_auth_without_sub_client.get(path)
        response_data = response.json()

        assert response.status_code == 404, f"Без подписки не тот статус код к: {path}"
        assert response_data["detail"] == "No TaskObject matches the given query.", "Неверный response без подписки"

    @pytest.mark.parametrize("path", constants.ALL_GET_PATHS)
    def test_get_questions_path_by_overdue_sub(self, path: str, api_auth_with_overdue_sub_client: APIClient):
        response = api_auth_with_overdue_sub_client.get(path)
        response_data = response.json()

        assert response.status_code == 404, "Просроченная подписка, не тот статус код"
        assert response_data["detail"] == "No TaskObject matches the given query.", (
            "Неверный response с просроченной подпиской"
        )


class TestAllPostQUestionsPaths:
    """
    Тесты на отсутстивие доступа к ответу на задание (POST).
    Аноним, юзер без подписки, юзер с просроченной подпиской - не имеют доступа.
    К бесплтаным навыкам доступ отсуствует только у анонима.
    """

    @pytest.mark.parametrize("path", constants.ALL_POST_PATHS)
    def test_post_questions_path_by_anonymous(self, path: str, api_anonymous_client: APIClient):
        response = api_anonymous_client.post(path)
        response_data = response.json()

        assert response.status_code == 403, "Аноним получил не тот статус код"
        assert response_data["error"] == "User credentials are not given", "Неверный response для анона"

    @pytest.mark.parametrize("path", constants.ALL_POST_PATHS)
    def test_post_questions_path_wo_sub(self, path: str, api_auth_without_sub_client: APIClient):
        response = api_auth_without_sub_client.get(path)
        response_data = response.json()

        assert response.status_code == 404, f"Без подписки не тот статус код к: {path}"
        assert response_data["detail"] == "No TaskObject matches the given query.", "Неверный response без подписки"

    @pytest.mark.parametrize("path", constants.ALL_POST_PATHS)
    def test_post_questions_path_by_overdue_sub(self, path: str, api_auth_with_overdue_sub_client: APIClient):
        response = api_auth_with_overdue_sub_client.get(path)
        response_data = response.json()

        assert response.status_code == 404, f"Просроченная подписка, не тот статус код к: {path}"
        assert response_data["detail"] == "No TaskObject matches the given query.", (
            "Неверный response с просроченной подпиской"
        )
