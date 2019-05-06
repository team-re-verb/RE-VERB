FROM publysher/alpine-numpy:1.14.0-python3.6-alpine3.7

WORKDIR /reverb/speech_diarization

RUN apk add --no-cache python3-dev libstdc++ && \
    apk add --no-cache g++ && \
    apk add --no-cache ffmpeg && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    apk add --update-cache --no-cache libgcc libquadmath musl && \
    apk add --update-cache --no-cache libgfortran && \
    apk add --update-cache --no-cache lapack-dev && \
    pip3 install numpy


RUN apk --no-cache add lapack libstdc++ && \
    apk --no-cache add --virtual .builddeps g++ gcc gfortran musl-dev lapack-dev && \
    pip install scipy==1.0.0 && \ 
    apk del .builddeps && \ 
    rm -rf /root/.cache


COPY requirements.txt requirements.txt

#RUN apk add  --no-cache ffmpeg musl-dev gcc 
RUN pip3 install -r requirements.txt


COPY server.py server.py
COPY diarization.py diarization.py

COPY model/*.py model/
COPY model/model.model model/model.model
COPY model/config model/config