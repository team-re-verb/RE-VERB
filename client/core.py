#!/bin/python

import json
import requests
import base64

from recorder import read_audio,record_audio

RECORD_FILENAME = "audio/record.wav"


def main():

    url = 'http://localhost:4040/'
    #params = {"req" : str(base64.b64encode(read_audio(RECORD_FILENAME)))}
    params = {"req" : "hello"}

    res = requests.get(url=url , json=params)
    print(res.json())


if __name__ == "__main__":
    #record_audio(5, RECORD_FILENAME)
    main()