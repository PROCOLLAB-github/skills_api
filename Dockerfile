FROM python:3.12

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install --upgrade setuptools wheel
RUN pip install -r requirements.txt
RUN pip install django-cors-headers


COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
