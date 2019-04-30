FROM python:3.6

WORKDIR /reverb/speech_diarization

COPY requirements.txt requirements.txt

COPY server.py server.py

COPY diarization.py diarization.py
COPY model.model model.model
#COPY model/hparam.py model/hparam.py
#COPY model/utils.py model/utils.py
#COPY model/network.py model/network.py

COPY model model

RUN pip install -r requirements.txt