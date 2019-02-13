# ========================== Usage ============================
###############################################################
# Build: # docker build -t [image name] [directory (.)]       #
# Run:   # docker run -p localPort:containerPort [image name] #
# Kill:  # docker stop $(sudo docker ps -a -q)                #
###############################################################

# TODO 1. Fix things with port argument
# TODO 2. Create signal handleing in this file
# TODO 3. Create a shell script which runs docker in a bertter way
FROM alpine:3.7

COPY server/  /reverb/server
COPY scripts/ /reverb/scripts
COPY requirements.txt /reverb

WORKDIR /reverb

#ARG port
EXPOSE 4040

### Get basic things
RUN apk update \
&& apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache curl

### Get out packages
RUN apk add --no-cache nodejs redis portaudio


### Get Python, PIP
RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

### Install pip requirements
RUN pip install -r requirements.txt

### Run local script
CMD ["./scripts/run.sh", "4040"]