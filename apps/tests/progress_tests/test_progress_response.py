import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from . import constants


class TestRegistrationResponse:
    """
    Тесты пути: `/progress/registration/`
    """

    def test_registration_with_correct_data(self, api_anonymous_client: APIClient):
        response = api_anonymous_client.post(
            path=constants.REGISTRATION_PATH,
            data=constants.CORRECT_REGISTRATION_DATA,
        )
        response_dct = response.json()

        assert response_dct == constants.REGISTRATION_RESPONSE_DATA, "Respose после регистрации не соотв."

    def test_registration_with_incorrect_data(self, api_anonymous_client: APIClient):
        response = api_anonymous_client.post(
            path=constants.REGISTRATION_PATH,
            data=constants.INCORRECT_REGISTRATION_DATA,
        )
        response_dct = response.json()

        assert response.status_code == 400, "Регистрация с некорректными данными"
        assert "email" in response_dct, "Не ругнулось на email"
        assert "password" in response_dct, "Не ругнулось на password"
        assert "first_name" in response_dct, "Не ругнулось на имя"
        assert "last_name" in response_dct, "Не ругнулось на фамилию"

    @pytest.mark.usefixtures("user")
    def test_registration_with_existing_email(self, api_anonymous_client: APIClient):
        response = api_anonymous_client.post(
            path=constants.REGISTRATION_PATH,
            data=constants.CORRECT_REGISTRATION_DATA,
        )
        response_dct = response.json()

        assert "email" in response_dct, "Не ругнулось на существующий email"


class TestProgressProfileResponse:
    """
    Тесты пути: `/progress/profile/`
    После выбора навыков, скорее всего надо будет вноситьправки в тесты.
    """

    POINTS_IN_PROFILE: int = 5
    SKILL_PERCENT_DONE: int = 13

    def test_progress_profile_new_sub_full_data(self, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.USER_PROFILE_PATH)
        response_dct = response.json()

        assert response_dct == constants.PROGRESS_USER_PROFILE_RESPONSE

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_progress_profile_new_sub_after_answer(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.USER_PROFILE_PATH)
        response_dct = response.json()

        assert response_dct["user_data"]["points"] == self.POINTS_IN_PROFILE, "После ответа не дали поинтов в профиль"
        assert len(response_dct["skills"]) == 1, "После ответа скилл не перешел в профиль"
        assert response_dct["skills"][0]["skill_progress"] == self.SKILL_PERCENT_DONE, "Прогресс в профиле некорректный"


class TestSubscriptionDataResponse:
    """
    Тесты пути: `/progress/subscription-data/`
    """

    def test_subscription_new_sub_data(self, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.SUBSCRIBTION_USER_DATA_PATH)
        response_dct = response.json()

        assert response_dct["is_subscribed"] is True, "Подписка должна быть активной"
        assert response_dct["is_autopay_allowed"] is False, "Автопродление не понятно откуда взялось"

    def test_subscription_wo_sub_data(self, api_auth_without_sub_client: APIClient):
        response = api_auth_without_sub_client.get(constants.SUBSCRIBTION_USER_DATA_PATH)
        response_dct = response.json()

        assert response_dct["is_subscribed"] is False, "Подписка должна быть не активной (не покупалась)"
        assert response_dct["is_autopay_allowed"] is False, "Автопродление не понятно откуда взялось"

    def test_subscription_old_sub_data(self, api_auth_with_old_sub_client: APIClient):
        response = api_auth_with_old_sub_client.get(constants.SUBSCRIBTION_USER_DATA_PATH)
        response_dct = response.json()

        assert response_dct["is_subscribed"] is True, "Подписка должна быть активной"
        assert response_dct["is_autopay_allowed"] is False, "Автопродление не понятно откуда взялось"

    def test_subscription_overdue_sub_data(self, api_auth_with_overdue_sub_client: APIClient):
        response = api_auth_with_overdue_sub_client.get(constants.SUBSCRIBTION_USER_DATA_PATH)
        response_dct = response.json()

        assert response_dct["is_subscribed"] is False, "Подписка должна быть неактивной (просрочена)"
        assert response_dct["is_autopay_allowed"] is False, "Автопродление не понятно откуда взялось"

# TODO Тесты:
# Они пока в принципе не работают/работают некорректно.
#   - /progress/add-skills/
#   - /progress/update-auto-renewal/
# Запрос на внешний сервис:
#   - /progress/user-data/
