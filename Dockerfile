FROM python:3.9.7-slim-bullseye
WORKDIR /app
RUN apt update
RUN apt upgrade -y
RUN apt install git -y
RUN apt install nano -y
COPY requirements.txt requirements.txt
RUN pip install -r ./requirements.txt
RUN pip install git+https://github.com/meraki-analytics/cassiopeia.git
RUN apt install ffmpeg -y
ADD . /app
VOLUME ["/app/db"]
ENTRYPOINT ["python","-u", "frame_bot.py"]
