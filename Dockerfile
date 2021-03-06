FROM python:3.7-alpine

LABEL maintainer="jasonxh@gmail.com"

WORKDIR /arlo-mqtt

COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers \
 && pip install -r requirements.txt \
 && apk del .build-deps

COPY . .

ENTRYPOINT [ "/arlo-mqtt/arlo-mqtt.py" ]
