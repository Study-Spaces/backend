FROM python:3.12

RUN mkdir -p /usr/app
WORKDIR /usr/app

COPY . .

ENV TZ=America/New_York
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -r requirements.txt
