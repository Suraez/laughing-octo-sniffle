FROM openwhisk/action-python-v3.7:nightly

# Install Python packages
RUN pip3 install --no-cache-dir chameleon six transformers==4.18.0

# Install FFmpeg
USER root
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable for proper encoding
ENV PYTHONIOENCODING=UTF-8
