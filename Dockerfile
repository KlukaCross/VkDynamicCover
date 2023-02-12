FROM python:3.9-slim

WORKDIR /app

COPY setup.py requirements.txt README.md ./
COPY ./VkDynamicCover ./VkDynamicCover

# Install system dependencies
#
#	numpy dependencies
#		libatlas-base-dev
#
#	Pillow dependencies
#		libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev
#       libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk

RUN apt-get update && \
    python3 -m pip install --upgrade pip && \
    apt-get install -y libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev \
            libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
            libatlas-base-dev && \
    pip3 install --extra-index-url=https://www.piwheels.org/simple --no-cache-dir .

ENTRYPOINT ["python3", "-m", "VkDynamicCover"]
