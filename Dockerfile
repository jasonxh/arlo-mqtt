FROM python:3.7 AS builder

RUN pip install -U pip
RUN pip install poetry==1.1.7

WORKDIR /arlo-mqtt

COPY poetry.lock pyproject.toml ./

RUN poetry export -o requirements.txt


FROM python:3.7-alpine

LABEL maintainer="jasonxh@gmail.com"

WORKDIR /arlo-mqtt

COPY --from=builder /arlo-mqtt/requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers \
 && pip install -r requirements.txt \
 && apk del .build-deps

COPY . .

ENTRYPOINT [ "/arlo-mqtt/arlo-mqtt.py" ]
