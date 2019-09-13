FROM python:3.7

LABEL maintainer="jasonxh@gmail.com"

WORKDIR /arlo-mqtt
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT [ "/arlo-mqtt/arlo-mqtt.py" ]
