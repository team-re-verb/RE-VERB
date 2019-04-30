#!/bin/python

import json
import requests
import base64

from recorder import read_audio,record_audio
RECORD_FILENAME = "audio/record.wav"


def main():

    url = 'http://localhost:1337/upload'
    recording = { "file" : ("recording", open(RECORD_FILENAME, "rb"))}
    
    res = requests.post(url=url , files=recording)
    print(res.content)


if __name__ == "__main__":
    #input("Press enter to start recording...")
    #record_audio(5, RECORD_FILENAME)
    main()
