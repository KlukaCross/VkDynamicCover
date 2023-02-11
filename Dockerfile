FROM python:3.8-slim

WORKDIR /app

COPY setup.py requirements.txt README.md ./
COPY ./VkDynamicCover ./VkDynamicCover

RUN apt-get update && \
    python3 -m pip install --upgrade pip && \
    apt-get install -y build-essential libjpeg-dev zlib1g-dev libpng-dev && \
    pip3 --no-cache-dir install . && \
    apt-get -y autoremove

ENTRYPOINT ["python3", "-m", "VkDynamicCover"]
