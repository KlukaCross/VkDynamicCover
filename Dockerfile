FROM python:3.8-slim

VOLUME /usr/src/VkDynamicCover
WORKDIR /usr/src/VkDynamicCover

COPY setup.py requirements.txt README.md ./
COPY ./VkDynamicCover ./VkDynamicCover

RUN apt-get update && \
    pip3 install . && \
    apt-get autoremove


ENTRYPOINT ["python3", "-m", "VkDynamicCover"]
