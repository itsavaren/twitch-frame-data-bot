FROM python:3.9.7-slim-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r ./requirements.txt
ADD . /app
ENTRYPOINT ["python", "frame_bot.py"]
