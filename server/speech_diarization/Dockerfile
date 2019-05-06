FROM pytorch/pytorch

WORKDIR /reverb/speech_diarization

RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/ffmpeg-4
RUN apt-get install -y ffmpeg
RUN apt-get update

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt --ignore-installed

COPY server.py server.py
COPY diarization.py diarization.py

COPY model/*.py model/
COPY model/model.model model/model.model
COPY model/config model/config