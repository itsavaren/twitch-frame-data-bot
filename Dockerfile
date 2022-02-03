FROM python:3.9.7-slim-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r ./requirements.txt
RUN apt update
RUN apt upgrade -y
RUN apt install ffmpeg -y
ADD . /app
VOLUME ["/app/db"]
ENTRYPOINT ["python", "frame_bot.py"]
