# syntax=docker/dockerfile:1

FROM python:3.8-alpine

WORKDIR /usr/src/VkDynamicCover

COPY requirements.txt requirements.txt
RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "-m", "VkDynamicCover"]
