import json

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from tests.questions_tests import constants as questions_constants

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
        response = api_auth_with_sub_client.get(constants.TASK_DETAIL_PATH)

        assert response.json() == constants.FULL_FILLED_PUBLISHED_SKILL_RESPONSE_NEW_SUB

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_free_task_response_info_with_new_sub(
        self, api_auth_with_sub_client: APIClient
    ):
        response = api_auth_with_sub_client.get(constants.TASK_DETAIL_PATH)
        respose_dct = response.json()

        assert respose_dct["stats_of_weeks"] == [], (
            "(Бесплатно) В навыке c учет недель не доджен идти"
        )
        assert len(respose_dct["tasks"]) == 4, (
            "(Бесплатно) Все задачи должны быть доступны (4шт.)"
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_response_info_with_old_sub(
        self, api_auth_with_old_sub_client: APIClient
    ):
        response = api_auth_with_old_sub_client.get(constants.TASK_DETAIL_PATH)
        respose_dct = response.json()

        assert len(respose_dct["stats_of_weeks"]) == self.OLD_SUB_AVAILABLE_WEEKS, (
            f"Кол-во доступных недель у СТАРОЙ подписки должно быть == {self.OLD_SUB_AVAILABLE_WEEKS}"
        )
        assert len(respose_dct["tasks"]) == 4, (
            f"Кол-во доступных задач должно быть == {self.OLD_SUB_AVAILABLE_TASKS}"
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_free_task_response_info_wo_sub(
        self, api_auth_without_sub_client: APIClient
    ):
        response = api_auth_without_sub_client.get(constants.TASK_DETAIL_PATH)
        respose_dct = response.json()

        assert respose_dct["stats_of_weeks"] == [], (
            "(Бесплатно) В навыке c учет недель не доджен идти"
        )
        assert len(respose_dct["tasks"]) == 4, (
            "(Бесплатно) Все задачи должны быть доступны (4шт.)"
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_response_info_with_overdue_sub_staff(
        self, api_auth_with_overdue_sub_client_staff: APIClient
    ):
        response = api_auth_with_overdue_sub_client_staff.get(
            constants.TASK_DETAIL_PATH
        )
        respose_dct = response.json()

        assert len(respose_dct["stats_of_weeks"]) == self.OLD_SUB_AVAILABLE_WEEKS, (
            f"Кол-во доступных недель у ЛЮБОГО СТАФФА должно быть == {self.OLD_SUB_AVAILABLE_WEEKS}"
        )
        assert len(respose_dct["tasks"]) == 4, (
            f"Кол-во доступных задач у ЛЮБОГО СТАФФА должно быть == {self.OLD_SUB_AVAILABLE_TASKS}"
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_response_info_with_new_sub_progress(
        self, api_auth_with_sub_client: APIClient
    ):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASK_DETAIL_PATH)
        respose_dct = response.json()

        assert respose_dct["progress"] == self.NEW_SUB_PROGRESS, (
            "Прогресс не соответствует."
        )
        assert respose_dct["step_data"][0]["is_done"] is True, (
            "Задание не отметилось как выполненное."
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_response_info_wo_sub(self, api_auth_without_sub_client: APIClient):
        api_auth_without_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_without_sub_client.get(constants.TASK_DETAIL_PATH)
        respose_dct = response.json()

        assert respose_dct["progress"] == self.OLD_SUB_PROGRESS, (
            "(Бесплатно)(Без подписки) Прогресс не соответствует."
        )
        assert respose_dct["step_data"][0]["is_done"] is True, (
            "(Бесплатно)(Без подписки) Задание не отметилось как выполненное."
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_response_info_with_overdue_sub(
        self, api_auth_with_overdue_sub_client: APIClient
    ):
        api_auth_with_overdue_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_overdue_sub_client.get(constants.TASK_DETAIL_PATH)
        respose_dct = response.json()

        assert respose_dct["progress"] == self.OLD_SUB_PROGRESS, (
            "(Бесплатно)(Просроч. подп.) Прогресс не соответствует."
        )
        assert respose_dct["step_data"][0]["is_done"] is True, (
            "(Бесплатно)(Просроч. подп.) Задание не отметилось как выполненное."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_response_info_with_old_sub_progress(
        self, api_auth_with_old_sub_client: APIClient
    ):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_old_sub_client.get(constants.TASK_DETAIL_PATH)
        respose_dct = response.json()

        assert respose_dct["progress"] == self.OLD_SUB_PROGRESS, (
            "Прогресс не соответствует."
        )
        assert respose_dct["step_data"][0]["is_done"] is True, (
            "Задание не отметилось как выполненное."
        )


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
    def test_all_skills_response_data_with_sub(
        self, api_auth_with_old_sub_client: APIClient
    ):
        response = api_auth_with_old_sub_client.get(constants.ALL_SKILLS_PATH)
        respose_dct = response.json()

        assert respose_dct == constants.ALL_SKILLS_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.ALL_SKILLS_PATH}."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_choose_skills_response_data_with_sub(
        self, api_auth_with_old_sub_client: APIClient
    ):
        response = api_auth_with_old_sub_client.get(constants.CHOOSE_SKILLS_PATH)
        respose_dct = response.json()

        assert respose_dct == constants.CHOOSE_SKILLS_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.ALL_SKILLS_PATH}."
        )

    @pytest.mark.usefixtures(
        "full_filled_free_published_skill",
        "full_filled_free_only_stuff_skill",
        "full_filled_free_draft_skill",
    )
    def test_skills_response_by_user(self, api_auth_without_sub_client: APIClient):
        response = api_auth_without_sub_client.get(constants.ALL_SKILLS_PATH)
        respose_dct = response.json()

        assert respose_dct["count"] == self.USER_AVAILABLE_SKILL_COUNT, (
            "(Бесплатно)(Без подп.) Пользователь видит|не видит скрытые навыки."
        )

    @pytest.mark.usefixtures(
        "full_filled_published_skill",
        "full_filled_only_stuff_skill",
        "full_filled_draft_skill",
    )
    @pytest.mark.parametrize(
        "path", (constants.ALL_SKILLS_PATH, constants.CHOOSE_SKILLS_PATH)
    )
    def test_skills_response_by_user_wo_sub(
        self, path, api_auth_with_sub_client: APIClient
    ):
        response = api_auth_with_sub_client.get(path)
        respose_dct = response.json()

        assert respose_dct["count"] == self.USER_AVAILABLE_SKILL_COUNT, (
            "Пользователь видит скрытые навыки."
        )

    @pytest.mark.usefixtures(
        "full_filled_published_skill",
        "full_filled_only_stuff_skill",
        "full_filled_draft_skill",
    )
    @pytest.mark.parametrize(
        "path", (constants.ALL_SKILLS_PATH, constants.CHOOSE_SKILLS_PATH)
    )
    def test_skills_response_by_staff(
        self, path, api_auth_with_sub_client_staff: APIClient
    ):
        response = api_auth_with_sub_client_staff.get(path)
        respose_dct = response.json()

        assert respose_dct["count"] == self.STAFF_AVAILABLE_SKILL_COUNT, (
            "Стафф видит/не видит некоторые навыки."
        )

    @pytest.mark.usefixtures(
        "full_filled_published_skill",
        "full_filled_only_stuff_skill",
        "full_filled_draft_skill",
    )
    @pytest.mark.parametrize(
        "path", (constants.ALL_SKILLS_PATH, constants.CHOOSE_SKILLS_PATH)
    )
    def test_skills_response_by_admin(
        self, path, api_auth_with_sub_client_admin: APIClient
    ):
        response = api_auth_with_sub_client_admin.get(path)
        respose_dct = response.json()

        assert respose_dct["count"] == self.ADMIN_AVAILABLE_SKILL_COUNT, (
            "Админ не видит скрытые навыки (а должен)."
        )


class TestSkillDetailPathResponse:
    """
    Тесты пути: `/courses/skill-details/1`
    """

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_skill_details_new_sub_response_data(
        self, api_auth_with_sub_client: APIClient
    ):

        response = api_auth_with_sub_client.get(constants.SKILL_DETAILS_PATH)

        respose_dct = response.json()

        assert respose_dct == constants.SKILL_DETAILS_RESPONSE_NEW_SUB, (
            f"Response не соотв. - {constants.SKILL_DETAILS_PATH}."
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_skill_details_wo_sub_response_data(
        self, api_auth_without_sub_client: APIClient
    ):
        response = api_auth_without_sub_client.get(constants.SKILL_DETAILS_PATH)
        respose_dct = response.json()

        assert respose_dct == constants.SKILL_DETAILS_RESPONSE_FREE, (
            f"(Бесплатно)(Без подп.)Response не соотв. - {constants.SKILL_DETAILS_PATH}."
        )


class TestTaskResultPathResponse:
    """
    Тесты пути: `/courses/task-result/1`
    """

    OLD_SUB_NEXT_TASK_ID: int = 2
    NEW_SUB_PERCENT_PROGRESS: int = 50
    OLD_SUB_PERCENT_PROGRESS: int = 13
    POINTS_GAINED: int = 20
    DONE_CORRECT: int = 1

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_result_auth_user_with_new_sub(
        self, api_auth_with_sub_client: APIClient
    ):
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct == constants.TASK_RESULT_RESPONSE_NEW_SUB, (
            "Response не соотв. ожидаемому."
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_task_result_auth_user_with_new_sub_free(
        self, api_auth_with_sub_client: APIClient
    ):
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct == constants.TASK_RESULT_RESPONSE_FREE, (
            "(Бесплатно)Response не соотв. ожидаемому"
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_task_result_auth_user_wo_sub_free(
        self, api_auth_without_sub_client: APIClient
    ):
        response = api_auth_without_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct == constants.TASK_RESULT_RESPONSE_FREE, (
            "(Бесплатно)(Без подп.)Response не соотв. ожидаемому."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_task_result_auth_user_with_old_sub(
        self, api_auth_with_old_sub_client: APIClient
    ):
        response = api_auth_with_old_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["next_task_id"] == self.OLD_SUB_NEXT_TASK_ID, (
            "У пользователя (старая подписка) должна быть открыта 2 неделя | 2 задание."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_result_auth_user_with_new_sub_after_answer(
        self, api_auth_with_sub_client: APIClient
    ):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == self.POINTS_GAINED, (
            "Пользователь не получил свои поинты"
        )
        assert respose_dct["quantity_done_correct"] == self.DONE_CORRECT, (
            "Не засчитало выполненное задание"
        )
        assert respose_dct["progress"] == self.NEW_SUB_PERCENT_PROGRESS, (
            "Не засчитало прогресс пользователю"
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_result_auth_user_with_old_sub_after_answer(
        self, api_auth_with_old_sub_client: APIClient
    ):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_old_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == self.POINTS_GAINED, (
            "Пользователь не получил свои поинты"
        )
        assert respose_dct["quantity_done_correct"] == self.DONE_CORRECT, (
            "Не засчитало выполненное задание"
        )
        assert respose_dct["progress"] == self.OLD_SUB_PERCENT_PROGRESS, (
            "Не засчитало прогресс пользователю"
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_free_task_result_auth_user_with_new_sub_after_answer(
        self, api_auth_with_sub_client: APIClient
    ):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == 0, "(Бесплатно) Должно быть 0 баллов"
        assert respose_dct["quantity_done_correct"] == self.DONE_CORRECT, (
            "(Бесплатно)Не засчитало выполненное задание"
        )
        assert respose_dct["progress"] == self.OLD_SUB_PERCENT_PROGRESS, (
            "(Бесплатно)Не засчитало прогресс пользователю"
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_free_task_result_auth_user_wo_sub_after_answer(
        self, api_auth_without_sub_client: APIClient
    ):
        api_auth_without_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_without_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == 0, "(Бесплатно) Должно быть 0 баллов"
        assert respose_dct["quantity_done_correct"] == self.DONE_CORRECT, (
            "(Бесплатно)Не засчитало выполненное задание"
        )
        assert respose_dct["progress"] == self.OLD_SUB_PERCENT_PROGRESS, (
            "(Бесплатно)Не засчитало прогресс пользователю"
        )

    @pytest.mark.usefixtures("single_question_data_with_tryes")
    @override_settings(task_always_eager=True)
    def test_task_result_user_with_sub_after_wrong_answer(
        self, api_auth_with_sub_client: APIClient
    ):
        """
        Делается 2 запроса (2 попытки к ответу) с проверкой результата.
        Оба запроса совершаются с неправильным ответом (для проверки посчета).
        """
        data = {"answer_id": 2}

        api_auth_with_sub_client.post(
            questions_constants.SINGLE_CORRECT_POST,
            data=json.dumps(data),
            content_type="application/json",
        )
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == 0, (
            "Должно быть 0 баллов (неверный ответ)"
        )
        assert respose_dct["quantity_done"] == 0, (
            "Должно быть 0 отвеченных (неверный ответ)"
        )
        assert respose_dct["quantity_done_correct"] == 0, (
            "Должно быть 0 отвеченных верно (неверный ответ)"
        )
        assert respose_dct["progress"] == 0, "Должно быть 0, еще 1 попытка для ответа"

        api_auth_with_sub_client.post(
            questions_constants.SINGLE_CORRECT_POST,
            data=json.dumps(data),
            content_type="application/json",
        )
        response = api_auth_with_sub_client.get(constants.TASK_RESULT)
        respose_dct = response.json()

        assert respose_dct["points_gained"] == 0, (
            "Должно быть 0 баллов (неверный ответ)"
        )
        assert respose_dct["quantity_done"] == 1, "1 ответ должен быть засчитан"
        assert respose_dct["quantity_done_correct"] == 0, (
            "Должно быть 0 отвеченных верно (неверный ответ)"
        )
        assert respose_dct["progress"] == 100, "Должно быть 0, еще 1 попытка для ответа"


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
            f"Старой подписке должно быть доступно {self.OLD_SUB_AVAILABLE_TASKS} задачи."
        )
        assert len(response_dct["stats_of_weeks"]) == self.OLD_SUB_AVAILABLE_WEEKS, (
            f"Старой подписке должно быть доступно {self.OLD_SUB_AVAILABLE_WEEKS} недели."
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_free_task_of_skill_new_sub_data(self, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert len(response_dct["tasks"]) == self.OLD_SUB_AVAILABLE_TASKS, (
            f"(Бесплатно)Новой подписке должно быть доступно {self.OLD_SUB_AVAILABLE_TASKS} задачи."
        )
        assert response_dct["stats_of_weeks"] == [], (
            "(Бесплатно) недели не учитываются."
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_free_task_of_skill_wo_sub_data(
        self, api_auth_without_sub_client: APIClient
    ):
        response = api_auth_without_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert len(response_dct["tasks"]) == self.OLD_SUB_AVAILABLE_TASKS, (
            f"(Бесплатно)(Без подп.) должно быть доступно {self.OLD_SUB_AVAILABLE_TASKS} задачи."
        )
        assert response_dct["stats_of_weeks"] == [], (
            "(Бесплатно) недели не учитываются."
        )

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_new_sub_done_one(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.NEW_SUB_PROGRESS, (
            "Прогресс новой подписки неверный."
        )
        assert response_dct["stats_of_weeks"][0]["is_done"] is False, (
            "Засчитало неделю неверно."
        )
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is None, (
            "Засчитало неделю неверно."
        )
        assert response_dct["tasks"][0]["status"] is False, "Засчитало задачу неверно."

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_new_sub_full_done(self, api_auth_with_sub_client: APIClient):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        api_auth_with_sub_client.post("/questions/info-slide/check/2")
        response = api_auth_with_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == 100, "Прогресс новой подписки неверный."
        assert response_dct["stats_of_weeks"][0]["is_done"] is True, (
            "Засчитало неделю неверно."
        )
        # Значение изменено на False: 
        # система больше не учитывает бонусные баллы за месяц. 
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is False, (
            "Засчитало неделю неверно."
        )
        assert response_dct["tasks"][0]["status"] is True, "Засчитало задачу неверно."

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_old_sub_done_one(
        self, api_auth_with_old_sub_client: APIClient
    ):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_old_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.OLD_SUB_PROGRESS, (
            "Прогресс старой подписки неверный."
        )
        assert response_dct["stats_of_weeks"][0]["is_done"] is False, (
            "Засчитало неделю неверно."
        )
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is None, (
            "Засчитало неделю неверно."
        )
        assert response_dct["tasks"][0]["status"] is False, "Засчитало задачу неверно."

    @pytest.mark.usefixtures("full_filled_published_skill")
    @override_settings(task_always_eager=True)
    def test_task_of_skill_old_sub_full_done(
        self, api_auth_with_old_sub_client: APIClient
    ):
        api_auth_with_old_sub_client.post("/questions/info-slide/check/1")
        api_auth_with_old_sub_client.post("/questions/info-slide/check/2")
        response = api_auth_with_old_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.OLD_SUB_PROGRESS_1_WEEK_DONE, (
            "Прогресс старой подписки неверный."
        )
        assert response_dct["stats_of_weeks"][0]["is_done"] is True, (
            "Засчитало неделю неверно."
        )
        assert response_dct["stats_of_weeks"][0]["done_on_time"] is False, (
            "Засчитало неделю неверно."
        )
        assert response_dct["tasks"][0]["status"] is True, "Засчитало задачу неверно."

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_free_task_of_skill_new_sub_done_one(
        self, api_auth_with_sub_client: APIClient
    ):
        api_auth_with_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_with_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.OLD_SUB_PROGRESS, (
            "(Бесплатно) Прогресс новой подписки неверный."
        )
        assert response_dct["stats_of_weeks"] == [], (
            "(Бесплатно)Недель не должно быть в бесп. навыке."
        )
        assert response_dct["tasks"][0]["status"] is False, (
            "(Бесплатно)Засчитало задачу неверно."
        )

    @pytest.mark.usefixtures("full_filled_free_published_skill")
    @override_settings(task_always_eager=True)
    def test_free_task_of_skill_wo_sub_done_one(
        self, api_auth_without_sub_client: APIClient
    ):
        api_auth_without_sub_client.post("/questions/info-slide/check/1")
        response = api_auth_without_sub_client.get(constants.TASKS_OF_SKILL)
        response_dct = response.json()

        assert response_dct["progress"] == self.OLD_SUB_PROGRESS, (
            "(Бесплатно)(Без подп.) Прогресс новой подписки неверный."
        )
        assert response_dct["stats_of_weeks"] == [], (
            "(Бесплатно)(Без подп.)Недель не должно быть в бесп. навыке."
        )
        assert response_dct["tasks"][0]["status"] is False, (
            "(Бесплатно)(Без подп.)Засчитало задачу неверно."
        )
