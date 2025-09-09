# Newer maintained base image
FROM openwhisk/action-python-v3.11:latest

# Install FFmpeg
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Python deps (pin whatever you actually need)
RUN pip3 install --no-cache-dir chameleon six igraph transformers torch numpy
ENV PYTHONIOENCODING=UTF-8
