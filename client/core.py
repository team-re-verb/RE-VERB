#!/bin/python

import json
import requests
<<<<<<< HEAD
import base64

from recorder import read_audio,record_audio

RECORD_FILENAME = "audio/record.wav"

=======
>>>>>>> 02544c90e2a4a916cd0ed171c2ae3e248a3ea1d3

def main():

    url = 'http://localhost:4040/'
    #params = {"req" : str(base64.b64encode(read_audio(RECORD_FILENAME)))}
    params = {"req" : "hello"}

    res = requests.get(url=url , json=params)
    print(res.json())


if __name__ == "__main__":
<<<<<<< HEAD
    #record_audio(5, RECORD_FILENAME)
    main()
=======
    main()
>>>>>>> 02544c90e2a4a916cd0ed171c2ae3e248a3ea1d3
