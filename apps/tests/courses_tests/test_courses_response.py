import pytest
from django.test import override_settings

from rest_framework.test import APIClient

from . import constants


class TestTaskListPathResponse:
    """
    Тесты пути: `/courses/1`
    """
    OLD_SUB_AVAILABLE_WEEKS: int = 4
    OLD_SUB_AVAILABLE_TASKS: int = 4
    OLD_SUB_PROGRESS: int = 13
    NEW_SUB_PROGRESS: int = 50

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_response_info_with_new_sub(self, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.TASK_LIST_PATH)
        assert constants.FULL_FILLED_PUBLISHED_SKILL_RESPONSE_NEW_SUB == response.json()

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_response_info_with_old_sub(self, api_auth_with_old_sub_client: APIClient):
        response = api_auth_with_old_sub_client.get(constants.TASK_LIST_PATH)
        respose_dct = response.json()

        assert len(respose_dct["stats_of_weeks"]) == self.OLD_SUB_AVAILABLE_WEEKS, (
            f"Кол-во доступных недель у Старой подписки должно быть == {self.OLD_SUB_AVAILABLE_WEEKS}"
        )
        assert len(respose_dct["tasks"]) == 4, (
            f"Кол-во доступных задач должно быть == {self.OLD_SUB_AVAILABLE_TASKS}"
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_response_info_with_new_sub_progress(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASK_LIST_PATH)
        respose_dct = response.json()

        assert respose_dct["progress"] == self.NEW_SUB_PROGRESS, "Прогресс не соответствует."
        assert respose_dct["step_data"][0]["is_done"] is True, "Задание не отметилось как выполненное."

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_response_info_with_old_sub_progress(self, api_auth_with_old_sub_client: APIClient):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_old_sub_client.get(constants.TASK_LIST_PATH)
        respose_dct = response.json()

        assert respose_dct["progress"] == self.OLD_SUB_PROGRESS, "Прогресс не соответствует."
        assert respose_dct["step_data"][0]["is_done"] is True, "Задание не отметилось как выполненное."


class TestAllChooseSkillsPath:
    """
    Тесты путей:
        - `/courses/all-skills/`
        - `/courses/choose-skills/`
    """
    USER_AVAILABLE_SKILL_COUNT: int = 1
    STAFF_AVAILABLE_SKILL_COUNT: int = 2
    ADMIN_AVAILABLE_SKILL_COUNT: int = 3

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_all_skills_response_data_with_sub(self, api_auth_with_old_sub_client: APIClient):
        response = api_auth_with_old_sub_client.get(constants.ALL_SKILLS_PATH)
        respose_dct = response.json()

        assert respose_dct == constants.ALL_SKILLS_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.ALL_SKILLS_PATH}."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_choose_skills_response_data_with_sub(self, api_auth_with_old_sub_client: APIClient):
        response = api_auth_with_old_sub_client.get(constants.CHOOSE_SKILLS_PATH)
        respose_dct = response.json()

        assert respose_dct == constants.CHOOSE_SKILLS_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.ALL_SKILLS_PATH}."
        )

    @pytest.mark.usefixtures(
        "full_filled_published_skill",
        "full_filled_only_stuff_skill",
        "full_filled_draft_skill",
    )
    @pytest.mark.parametrize("path", (constants.ALL_SKILLS_PATH, constants.CHOOSE_SKILLS_PATH))
    def test_skills_response_by_user(self, path, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(path)
        respose_dct = response.json()

        assert respose_dct["count"] == self.USER_AVAILABLE_SKILL_COUNT, "Пользователь видит скрытые навыки."

    @pytest.mark.usefixtures(
        "full_filled_published_skill",
        "full_filled_only_stuff_skill",
        "full_filled_draft_skill",
    )
    @pytest.mark.parametrize("path", (constants.ALL_SKILLS_PATH, constants.CHOOSE_SKILLS_PATH))
    def test_skills_response_by_staff(self, path, api_auth_with_sub_client_staff: APIClient):
        response = api_auth_with_sub_client_staff.get(path)
        respose_dct = response.json()

        assert respose_dct["count"] == self.STAFF_AVAILABLE_SKILL_COUNT, "Стафф видит/не видит некоторые навыки."

    @pytest.mark.usefixtures(
        "full_filled_published_skill",
        "full_filled_only_stuff_skill",
        "full_filled_draft_skill",
    )
    @pytest.mark.parametrize("path", (constants.ALL_SKILLS_PATH, constants.CHOOSE_SKILLS_PATH))
    def test_skills_response_by_admin(self, path, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(path)
        respose_dct = response.json()

        assert respose_dct["count"] == self.ADMIN_AVAILABLE_SKILL_COUNT, "Админ не видит скрытые навыки (а должен)."


class TestSkillDetailPathResponse:
    """
    Тесты пути: `/courses/skill-details/1`
    """

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_skill_details_new_sub_response_data(self, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.SKILL_DETAILS_PATH)
        respose_dct = response.json()

        assert respose_dct == constants.SKILL_DETAILS_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.SKILL_DETAILS_PATH}."
        )


class TestTaskResultPathResponse:
    """
    Тесты пути: `/courses/task-result/1`
    """
    OLD_SUB_NEXT_TASK_ID: int = 2
    NEW_SUB_PERCENT_PROGRESS: int = 50
    OLD_SUB_PERCENT_PROGRESS: int = 13
    POINTS_GAINED: int = 5
    DONE_CORRECT: int = 1

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_result_auth_user_with_new_sub(self, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct == constants.TASK_RESULT_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.TASK_RESULT}."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_result_auth_user_with_old_sub(self, api_auth_with_old_sub_client: APIClient):
        response = api_auth_with_old_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["next_task_id"] == self.OLD_SUB_NEXT_TASK_ID, (
            "У пользователя (старая подписка) должна быть открыта 2 неделя | 2 задание."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_result_auth_user_with_new_sub_after_answer(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == self.POINTS_GAINED, "Пользователь не получил свои поинты"
        assert respose_dct["quantity_done_correct"] == self.DONE_CORRECT, "Не засчитало выполненное задание"
        assert respose_dct["progress"] == self.NEW_SUB_PERCENT_PROGRESS, "Не засчитало прогресс пользователю"

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_result_auth_user_with_old_sub_after_answer(self, api_auth_with_old_sub_client: APIClient):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_old_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == self.POINTS_GAINED, "Пользователь не получил свои поинты"
        assert respose_dct["quantity_done_correct"] == self.DONE_CORRECT, "Не засчитало выполненное задание"
        assert respose_dct["progress"] == self.OLD_SUB_PERCENT_PROGRESS, "Не засчитало прогресс пользователю"


class TestTaskOfSkillPathResponse:
    """
    Тесты пути: `/courses/tasks-of-skill/1`
    """
    NEW_SUB_PROGRESS: int = 50
    OLD_SUB_AVAILABLE_TASKS: int = 4
    OLD_SUB_AVAILABLE_WEEKS: int = 4
    OLD_SUB_PROGRESS: int = 13
    OLD_SUB_PROGRESS_1_WEEK_DONE: int = 25

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_of_skill_new_sub_data(self, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct == constants.TASKS_OF_SKILL_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.TASKS_OF_SKILL_RESPONSE_NEW_SUB}."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_of_skill_old_sub_data(self, api_auth_with_old_sub_client: APIClient):
        response = api_auth_with_old_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert len(response_dct["tasks"]) == self.OLD_SUB_AVAILABLE_TASKS, (
            f"Старой подписке должно быть доступно {self.OLD_SUB_AVAILABLE_TASKS} недели."
        )
        assert len(response_dct["stats_of_weeks"]) == self.OLD_SUB_AVAILABLE_WEEKS, (
            f"Старой подписке должно быть доступно {self.OLD_SUB_AVAILABLE_WEEKS} задачи."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_new_sub_done_one(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.NEW_SUB_PROGRESS, "Прогресс новой подписки неверный."
        assert response_dct["stats_of_weeks"][0]["is_done"] is False, "Засчитало неделю неверно."
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is None, "Засчитало неделю неверно."
        assert response_dct["tasks"][0]["status"] is False, "Засчитало задачу неверно."

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_new_sub_full_done(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        api_auth_with_sub_client.post("/questions/info-slide/check/2")
        response = api_auth_with_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == 100, "Прогресс новой подписки неверный."
        assert response_dct["stats_of_weeks"][0]["is_done"] is True, "Засчитало неделю неверно."
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is True, "Засчитало неделю неверно."
        assert response_dct["tasks"][0]["status"] is True, "Засчитало задачу неверно."

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_old_sub_done_one(self, api_auth_with_old_sub_client: APIClient):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_old_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.OLD_SUB_PROGRESS, "Прогресс старой подписки неверный."
        assert response_dct["stats_of_weeks"][0]["is_done"] is False, "Засчитало неделю неверно."
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is None, "Засчитало неделю неверно."
        assert response_dct["tasks"][0]["status"] is False, "Засчитало задачу неверно."

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_old_sub_full_done(self, api_auth_with_old_sub_client: APIClient):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        api_auth_with_old_sub_client.post("/questions/info-slide/check/2")
        response = api_auth_with_old_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.OLD_SUB_PROGRESS_1_WEEK_DONE, "Прогресс старой подписки неверный."
        assert response_dct["stats_of_weeks"][0]["is_done"] is True, "Засчитало неделю неверно."
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is False, "Засчитало неделю неверно."
        assert response_dct["tasks"][0]["status"] is True, "Засчитало задачу неверно."
