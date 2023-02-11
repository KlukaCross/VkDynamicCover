FROM python:3.8-slim

WORKDIR /app

COPY setup.py requirements.txt README.md ./
COPY ./VkDynamicCover ./VkDynamicCover

RUN apt-get update && \
    python3 -m pip install --upgrade pip && \
    apt-get install -y build-essential libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev && \
    pip3 --no-cache-dir install . && \
    apt-get -y autoremove

ENTRYPOINT ["python3", "-m", "VkDynamicCover"]
