FROM python:3.9-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

COPY . .

RUN pip install -r requirements.txt

ENV fprocess="python3 handler.py"
CMD ["python3", "handler.py"]
