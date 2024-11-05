import pytest

from model_bakery import baker

from files.models import FileModel


@pytest.fixture
def random_file_intance():
    """Рандомный файл."""
    return baker.make(FileModel)
