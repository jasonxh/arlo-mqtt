FROM python:3.7-alpine

LABEL maintainer="jasonxh@gmail.com"

WORKDIR /arlo-mqtt
COPY . .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers \
 && pip install -r requirements.txt \
 && apk del .build-deps

ENTRYPOINT [ "/arlo-mqtt/arlo-mqtt.py" ]
