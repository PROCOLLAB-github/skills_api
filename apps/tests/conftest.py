import pytest


pytest_plugins = [
    "tests.fixtures.users",
    "tests.fixtures.subscription",
    "tests.fixtures.coureses",
    "tests.fixtures.files",
    "tests.fixtures.questions.fixtures_connect",
    "tests.fixtures.questions.fixtures_write",
    "tests.fixtures.questions.fixtures_exlude",
    "tests.fixtures.questions.fixtures_single",
    "tests.fixtures.questions.fixtures_infoslide",
    "tests.fixtures.questions.common",
]


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
