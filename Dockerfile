FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./ /code/

RUN pip install --upgrade pip && pip install --upgrade setuptools wheel
RUN pip install -r requirements.txt
RUN pip install django-cors-headers

RUN python manage.py migrate
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
