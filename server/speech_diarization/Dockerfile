FROM python:3.6-alpine3.9
#FROM python:3.6

WORKDIR /reverb/speech_diarization

COPY requirements.txt requirements.txt

RUN apk add  --no-cache ffmpeg musl-dev gcc 
RUN pip install -r requirements.txt


COPY server.py server.py
COPY diarization.py diarization.py

COPY model/*.py model/
COPY model/model.model model/model.model
COPY model/config model/config