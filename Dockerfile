FROM python:3.10.13

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY ./app /app