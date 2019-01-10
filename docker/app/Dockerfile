FROM python:3.6.8

ENV PYTHONUNBUFFERED 1

COPY ./docker/app/app-entrypoint.sh /
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

EXPOSE 5000

RUN pip install pip==9.0.1
RUN pip install -r requirements.txt