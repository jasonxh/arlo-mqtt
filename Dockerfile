FROM python:3.11-alpine

LABEL maintainer="jasonxh@gmail.com"

WORKDIR /arlo-mqtt

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers git libffi-dev \
 && pip install -r requirements.txt \
 && apk del .build-deps

COPY dist dist
RUN pip install --no-deps dist/*.whl

ENTRYPOINT [ "arlo-mqtt" ]
