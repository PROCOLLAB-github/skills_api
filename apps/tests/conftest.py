import pytest


pytest_plugins = [
    "tests.fixtures.users",
    "tests.fixtures.subscription",
    "tests.fixtures.coureses",
    "tests.fixtures.files",
]


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
