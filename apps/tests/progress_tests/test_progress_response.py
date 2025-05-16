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
    """

    POINTS_IN_PROFILE: int = 20
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

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_progress_profile_new_sub_after_free_answer(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.USER_PROFILE_PATH)
        response_dct = response.json()

        assert response_dct["user_data"]["points"] == 0, "Бесплтаный курс не должен давать поинтов"
        assert len(response_dct["skills"]) == 1, "После ответа скилл не перешел в профиль"
        assert response_dct["skills"][0]["skill_progress"] == self.SKILL_PERCENT_DONE, "Прогресс в профиле некорректный"

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_progress_profile_wo_sub_after_free_answer(self, api_auth_without_sub_client: APIClient):
        api_auth_without_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_without_sub_client.get(constants.USER_PROFILE_PATH)
        response_dct = response.json()

        assert response_dct["user_data"]["points"] == 0, "(Без подп.) Бесплтаный курс не должен давать поинтов"
        assert len(response_dct["skills"]) == 1, "(Без подп.) После ответа скилл не перешел в профиль"
        assert (
            response_dct["skills"][0]["skill_progress"] == self.SKILL_PERCENT_DONE
        ), "(Без подп.) Прогресс в профиле некорректный"


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


class TestUserScoreRating:
    """
    Тесты пути: `/progress/user-rating/?time_frame=...`
    """

    SINGLE_SCORE_COUNT = 20

    @pytest.mark.parametrize("time_frame", ("last_day", "last_month", "last_year"))
    def test_empty_data_without_answers(self, time_frame: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.USER_SCORE_RATING_PATH + f"?time_frame={time_frame}")
        response_dct = response.json()

        assert response_dct["count"] == 0, "Не было ответов, в рейтинге кто-то уже есть"
        assert response_dct["results"] == [], "Не было ответов, в рейтинге кто-то уже есть"

    @pytest.mark.parametrize("time_frame", ("last_day", "last_month", "last_year"))
    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_single_answer_by_new_sub(self, time_frame: str, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.USER_SCORE_RATING_PATH + f"?time_frame={time_frame}")
        response_dct = response.json()

        assert response_dct["count"] == 1, "После ответа пользователь не появился в рейтинге"
        assert response_dct["results"][0]["score_count"] == self.SINGLE_SCORE_COUNT, "Баллы в рейтинге некорректны"

    @pytest.mark.parametrize("time_frame", ("last_day", "last_month", "last_year"))
    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_free_single_answer_by_new_sub(self, time_frame: str, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.USER_SCORE_RATING_PATH + f"?time_frame={time_frame}")
        response_dct = response.json()

        assert response_dct["count"] == 0, "Бесплатные навыки не дают баллов, соотв не должны быть в рейтинге"
        assert response_dct["results"] == [], "Бесплатного навыка не должно быть в рейтинге"

    @pytest.mark.parametrize("time_frame", ("last_day", "last_month", "last_year"))
    @pytest.mark.usefixtures("skill_three_users_answers")
    @override_settings(task_always_eager=True)
    def test_user_rating_with_different_roles(self, time_frame: str, api_auth_with_sub_client: APIClient):
        """Все ответы даны в 1 время, таймлайн не решает, рейтинг по дате должен быть одинаковым."""
        response = api_auth_with_sub_client.get(constants.USER_SCORE_RATING_PATH + f"?time_frame={time_frame}")
        print("1"*100)
        print(response)
        response_dct = response.json()
        print("1"*100)
        print(response_dct)
        assert (
            response_dct["count"] == 1
        ), "В рейтинге должeн быть 1 пользователь (Стафф и админ не должны отображаться)"
        assert (
            response_dct["results"][0]["score_count"] == self.SINGLE_SCORE_COUNT * 1
        ), "Неверные баллы у 1го в рейтинге"

    @pytest.mark.parametrize("time_frame, count_users", (("last_day", 1), ("last_month", 2), ("last_year", 3)))
    @pytest.mark.usefixtures("skill_three_users_some_old_answers")
    @override_settings(task_always_eager=True)
    def test_user_count_in_different_timeline(
        self, time_frame: str, count_users: int, api_auth_with_sub_client: APIClient
    ):
        """В фикстуре на каждый таймлайн по 1му пользователю, где: сегодня - 1, за ласт год - 3 юзера в рейтинге."""
        response = api_auth_with_sub_client.get(constants.USER_SCORE_RATING_PATH + f"?time_frame={time_frame}")
        response_dct = response.json()
        user_points: list[int] = [user["score_count"] for user in response_dct["results"]]

        assert response_dct["count"] == count_users, "Таймлан фильтра по пользователям отработал некорректно"
        assert user_points == sorted(user_points, reverse=True), "Порядок пользователей в рейтиге не убывает"


# TODO Тесты:
# Они пока в принципе не работают/работают некорректно.
#   - /progress/add-skills/
#   - /progress/update-auto-renewal/
# Запрос на внешний сервис:
#   - /progress/user-data/
