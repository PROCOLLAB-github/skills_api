FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./ /code/

ENV POETRY_VERSION=1.2.2

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false \
    && poetry install  --no-root

RUN mkdir /staticfiles
RUN mkdir //static

RUN python manage.py migrate
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
