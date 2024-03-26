FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install --upgrade setuptools wheel
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN pip install django-cors-headers


COPY . .

EXPOSE 8000
CMD ["gunicorn", "univer.wsgi:application", "--bind", "0.0.0.0:8000"]
