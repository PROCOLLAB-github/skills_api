import pytest

from rest_framework.test import APIClient

from . import constants


@pytest.mark.parametrize("path", constants.COURSES_ALL_PATHS)
def test_anymous_user_no_access(path, api_anonymous_client: APIClient):
    response = api_anonymous_client.get(path)
    assert response.status_code == 403, f"Аноним НЕ должен иметь доступа к {path}"


class TestPaidSKillTasks:
    """Тесты ПЛАТНОГО курса/задач"""

    @pytest.mark.parametrize("path", constants.COURSES_ALL_PATHS)
    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_auth_user_with_sub_have_access(self, path, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(path)
        assert response.status_code == 200, f"Пользователь c подпиской должен иметь доступ к {path}"

    @pytest.mark.parametrize("path", constants.COURSES_NO_ACCESS_PATHS)
    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_auth_user_wo_sub_no_access(self, path, api_auth_without_sub_client: APIClient):
        response = api_auth_without_sub_client.get(path)
        assert response.status_code == 403, f"Пользователь без подписки НЕ должен иметь доступ к {path}"

    @pytest.mark.parametrize("path", constants.COURSES_NO_ACCESS_PATHS)
    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_auth_with_overdue_sub_no_access(self, path, api_auth_with_overdue_sub_client: APIClient):
        response = api_auth_with_overdue_sub_client.get(path)
        assert response.status_code == 403, f"Пользователь с просроченной подписокй НЕ должен иметь доступ к {path}"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_only_stuff_skill")
    def test_tasks_paths_for_stuff_by_default_user(self, task_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(task_path)
        assert response.status_code == 404, "Юзеру не должны быть доступны таски staff only"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_draft_skill")
    def test_tasks_paths_for_admin_by_default_user(self, task_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(task_path)
        assert response.status_code == 404, "Юзеру не должны быть доступны таски draft"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_draft_skill")
    def test_tasks_paths_for_admin_by_stuff_user(self, task_path: str, api_auth_with_sub_client_staff: APIClient):
        response = api_auth_with_sub_client_staff.get(task_path)
        assert response.status_code == 404, "Персоналу не должны быть доступны таски draft"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_published_skill")
    def test_tasks_paths_published_by_admin(self, task_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(task_path)
        assert response.status_code == 200, "Админу должны быть доступны publish таски"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_only_stuff_skill")
    def test_tasks_paths_staff_only_by_admin(self, task_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(task_path)
        assert response.status_code == 200, "Админу должны быть доступны staff_only таски"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_draft_skill")
    def test_tasks_paths_draft_by_admin(self, task_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(task_path)
        assert response.status_code == 200, "Админу должны быть доступны draft таски"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_only_stuff_skill")
    def test_skills_paths_for_stuff_by_default_user(self, skills_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(skills_path)
        assert response.status_code == 404, "Юзеру НЕ должны быть доступны навыки staff only"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_draft_skill")
    def test_skills_paths_draft_by_default_user(self, skills_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(skills_path)
        assert response.status_code == 404, "Юзеру НЕ должны быть доступны навыки draft"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_draft_skill")
    def test_skills_paths_draft_by_staff(self, skills_path: str, api_auth_with_sub_client_staff: APIClient):
        response = api_auth_with_sub_client_staff.get(skills_path)
        assert response.status_code == 404, "Персоналу НЕ должны быть доступны навыки draft"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_only_stuff_skill")
    def test_skills_paths_only_staff_by_staff(self, skills_path: str, api_auth_with_sub_client_staff: APIClient):
        response = api_auth_with_sub_client_staff.get(skills_path)
        assert response.status_code == 200, "Персоналу должны быть доступны навыки staff only"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_only_stuff_skill")
    def test_skills_paths_only_staff_by_overdue_staff(
        self,
        skills_path: str,
        api_auth_with_overdue_sub_client_staff: APIClient
    ):
        response = api_auth_with_overdue_sub_client_staff.get(skills_path)
        assert response.status_code == 200, "(ПРОСРОЧЕННАЯ подп.) Персоналу должны быть доступны навыки staff only"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_only_stuff_skill")
    def test_skills_paths_only_staff_by_admin(self, skills_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(skills_path)
        assert response.status_code == 200, "Админу должны быть доступны навыки staff only"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_draft_skill")
    def test_skills_paths_draft_by_admin(self, skills_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(skills_path)
        assert response.status_code == 200, "Админу должны быть доступны навыки draft"


class TestFreeSKillTasks:
    """Тесты ПЛАТНОГО курса/задач"""

    @pytest.mark.parametrize("path", constants.COURSES_ALL_PATHS)
    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_auth_user_with_sub_have_access(self, path, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(path)
        assert response.status_code == 200, f"(Бесплатно) Пользователь c подпиской ДОЛЖЕН иметь доступ к {path}"

    @pytest.mark.parametrize("path", constants.COURSES_FREE_AUTH_PATHS)
    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_auth_user_wo_sub_no_access(self, path, api_auth_without_sub_client: APIClient):
        response = api_auth_without_sub_client.get(path)
        assert response.status_code == 200, f"(Бесплатно) Пользователь без подписки ДОЛЖЕН иметь доступ к {path}"

    @pytest.mark.parametrize("path", constants.COURSES_FREE_AUTH_PATHS)
    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_auth_with_overdue_sub_no_access(self, path, api_auth_with_overdue_sub_client: APIClient):
        response = api_auth_with_overdue_sub_client.get(path)
        assert response.status_code == 200, (
            f"(Бесплатно) Пользователь с просроченной подписокй ДОЛЖЕН иметь доступ к {path}"
        )

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_free_only_stuff_skill")
    def test_tasks_paths_for_stuff_by_default_user(self, task_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(task_path)
        assert response.status_code == 404, "(Бесплатно) Юзеру НЕ должны быть доступны таски staff only"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_free_draft_skill")
    def test_tasks_paths_for_admin_by_default_user(self, task_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(task_path)
        assert response.status_code == 404, "(Бесплатно) Юзеру НЕ должны быть доступны таски draft"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_free_draft_skill")
    def test_tasks_paths_for_admin_by_stuff_user(self, task_path: str, api_auth_with_sub_client_staff: APIClient):
        response = api_auth_with_sub_client_staff.get(task_path)
        assert response.status_code == 404, "(Бесплатно) Персоналу НЕ должны быть доступны таски draft"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_free_published_skill")
    def test_tasks_paths_published_by_admin(self, task_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(task_path)
        assert response.status_code == 200, "(Бесплатно) Админу ДОЛЖНЫ быть доступны publish таски"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_free_only_stuff_skill")
    def test_tasks_paths_staff_only_by_admin(self, task_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(task_path)
        assert response.status_code == 200, "(Бесплатно) Админу ДОЛЖНЫ быть доступны staff_only таски"

    @pytest.mark.parametrize("task_path", (constants.TASK_LIST_PATH, constants.TASK_RESULT))
    @pytest.mark.usefixtures("full_filled_free_draft_skill")
    def test_tasks_paths_draft_by_admin(self, task_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(task_path)
        assert response.status_code == 200, "(Бесплатно) Админу ДОЛЖНЫ быть доступны draft таски"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_free_only_stuff_skill")
    def test_skills_paths_for_stuff_by_default_user(self, skills_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(skills_path)
        assert response.status_code == 404, "(Бесплатно) Юзеру НЕ ДОЛЖНЫ быть доступны навыки staff only"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_free_draft_skill")
    def test_skills_paths_draft_by_default_user(self, skills_path: str, api_auth_with_sub_client: APIClient):
        response = api_auth_with_sub_client.get(skills_path)
        assert response.status_code == 404, "(Бесплатно) Юзеру НЕ ДОЛЖНЫ быть доступны навыки draft"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_free_draft_skill")
    def test_skills_paths_draft_by_staff(self, skills_path: str, api_auth_with_sub_client_staff: APIClient):
        response = api_auth_with_sub_client_staff.get(skills_path)
        assert response.status_code == 404, "(Бесплатно) Персоналу НЕ ДОЛЖНЫ быть доступны навыки draft"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_free_only_stuff_skill")
    def test_skills_paths_only_staff_by_staff(self, skills_path: str, api_auth_with_sub_client_staff: APIClient):
        response = api_auth_with_sub_client_staff.get(skills_path)
        assert response.status_code == 200, "(Бесплатно) Персоналу ДОЛЖНЫ быть доступны навыки staff only"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_free_only_stuff_skill")
    def test_skills_paths_only_staff_by_overdue_staff(
        self,
        skills_path: str,
        api_auth_with_overdue_sub_client_staff: APIClient
    ):
        response = api_auth_with_overdue_sub_client_staff.get(skills_path)
        assert response.status_code == 200, (
            "(ПРОСРОЧЕННАЯ подп.) (Бесплатно) Персоналу должны быть доступны навыки staff only"
        )

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_free_only_stuff_skill")
    def test_skills_paths_only_staff_by_admin(self, skills_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(skills_path)
        assert response.status_code == 200, "(Бесплатно) Админу ДОЛЖНЫ быть доступны навыки staff only"

    @pytest.mark.parametrize("skills_path", (constants.SKILL_DETAILS_PATH, constants.TASKS_OF_SKILL))
    @pytest.mark.usefixtures("full_filled_free_draft_skill")
    def test_skills_paths_draft_by_admin(self, skills_path: str, api_auth_with_sub_client_admin: APIClient):
        response = api_auth_with_sub_client_admin.get(skills_path)
        assert response.status_code == 200, "(Бесплатно) Админу ДОЛЖНЫ быть доступны навыки draft"
