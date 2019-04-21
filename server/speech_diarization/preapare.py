import wget
import xml.etree.ElementTree as ET
import os
from zipfile import ZipFile
import operator
import json
from pydub import AudioSegment
import numpy as np
import random

from urllib.error import HTTPError


from pydub.playback import play

OUT_DIR = "dataset"
ANNOTATIONS_DIR = OUT_DIR + "/metadata/segments"
JSON_DIR = OUT_DIR + "/meetings"
AUDIO_DIR = OUT_DIR + "/audio"



ami_meetings = { 
    "ES": [ ("ES" + str(2000 + x)) for x in range(2,17)],
    "IS": [ ("IS" + str(1000 + x)) for x in range(10) ],
    "TS": [ ("TS" + str(3000 + x)) for x in range(3, 13)],
    "IB": [ ("IB" + str(4000 + x)) for x in range(1,12)],
    "IN": [ ("IN" + str(1000 + x)) for x in range(1,17)]
}


def download_meetings():
    '''
    Downloads all of the meetings audio files from ami corpus   
    '''
    URL = "http://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus"

    if not os.path.isdir(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    os.chdir(AUDIO_DIR)

    for meeting_id in ami_meetings:
        print(f"Downloading {meeting_id} meetings")

        for meeting in ami_meetings[meeting_id]:
            try:
                for i in ['a', 'b', 'c', 'd']:
                    if not os.path.isfile(f"{meeting}{i}.wav"):
                        print(f"\tPulling {meeting}{i}...[{URL}/{meeting}{i}/audio/{meeting}{i}.Mix-Headset.wav]")
                        wget.download(f"{URL}/{meeting}{i}/audio/{meeting}{i}.Mix-Headset.wav", meeting + i + ".wav")
                    else:
                        print(f"Meeting {meeting} already exists.")
                
            except HTTPError as e:
                print(f"Could not found {meeting}")
                continue

        
    os.chdir("../")


def download_annotations():
    '''
    Downloads the ami corpus metadata folder
    '''    
    os.chdir(OUT_DIR)
    wget.download("http://groups.inf.ed.ac.uk/ami/AMICorpusAnnotations/ami_public_manual_1.6.2.zip", "tmp.zip")

    with ZipFile("tmp.zip", 'r') as z:
        z.extractall("metadata")
        
    os.remove("tmp.zip")


def process_segment(filename):
    '''
    Processes every meeting segment parts from a xml file

    :returns: a list containing all of the speech timestamps (in ms)
    '''
    segments = []
    root = ET.parse(f"{ANNOTATIONS_DIR}/{filename}").getroot()

    for segment_tag in root.findall('segment'):
        segments.append(
            { 
                "start": float(segment_tag.get("transcriber_start")) * 1000,
                "end": float(segment_tag.get("transcriber_end")) * 1000 #convert to ms
            })

    return segments


def get_annotations():
    '''
    Gets the details of every meeting from the ami dataset directory

    :returns: the segmentation of speech parts for each meeting
    '''
    segments = {}


    if not os.path.isdir(ANNOTATIONS_DIR):
        download_annotations()
    

    for _, meetings in ami_meetings.items():
        for meeting in meetings:

            segments[meeting] = {}
            
            for filename in os.listdir(ANNOTATIONS_DIR):
                if filename.startswith(meeting):        
                    speaker = filename.split('.')[1]

                    if speaker not in segments[meeting].keys():
                        segments[meeting][speaker] = process_segment(filename)
    

    return segments


def save_json(annotations):
    '''
    Saves the details of each meeting in a json file (in the JSON_DIR directory)

    :param annotations: holds the segmentation information for each meeting
    :type annotations: dict

    :returns: None 
    '''
    for meeting in annotations:
        meeting_details = annotations[meeting]

        meeting_details = dict(sorted(meeting_details.items(), key=operator.itemgetter(0)))
        meeting_details["meeting"] = meeting

        if len(meeting_details.keys()) > 1:
            with open(f"{meeting}.json", "w+") as f:    
                json.dump(meeting_details, f, indent=2)


def slice_speech(json_file):
    '''
    Slices every meeting audio file into speech parts according to timestamps

    :param json_file: a json file which holds the speech segmentation info of a meeting
    :type json_file: file

    :returns: pydub AudioSegment parts of the utterances for each speaker
    '''
    with open(json_file, "r") as f:
        meeting = json.load(f) 
        meeting_id =  meeting["meeting"]
        
        del meeting["meeting"] #leaving the meeting dictionary with only the speech parts

        speech_segments = {speaker: [] for speaker in meeting.keys()} #dict which holds the raw speech segments for each speaker

        #every meeting file is split to 4 files which ends with a b c or d
        for file_index in ['a', 'b', 'c', 'd']:
            try:
                audiofile =  AudioSegment.from_wav(f"{AUDIO_DIR}/{meeting_id}{file_index}.wav")

                print(f'Slicing speech from {meeting_id}({file_index})')

                for speaker,utterances in meeting.items():
                    print(f"Speaker {speaker}")
                    for u in utterances:
                        speech_segments[speaker].append(audiofile[u["start"] : u["end"]])
                        
            except Exception as e:
                print(f"Error has Occured: {e}")
                continue

        return speech_segments


def concat_utterances(meeting_audio):
    '''
    Concats all of the sliced utterances of each speaker in each meeting into one audio
    
    :param meeting_audio: all of the utterances of every speaker in a meeting
    :type meeting_audio: dict

    :returns: a new dict containing the concated utterances
    
    '''

    full_audio = {speaker: AudioSegment.empty() for speaker in meeting_audio.keys()}

    for speaker, utternaces in meeting_audio.items():
        for u in utternaces:
            full_audio[speaker] += u

    return full_audio
        

def get_partial_utterances(utterances):
    '''
    Slices every speech segment into smaller, fixed sized segments which caontains the speech parts.

    We count every meeting as a batch, and every batch should have a random segments of length 140-180 ms with 
    window stride of 30 ms 

    :param utterances: the whole speech segments which their sizes are varied
    :type utterances: dict (of Pydub's AudioSegment)

    :returns: the fixed utterances as dict of matrices which caontains the utterances
    '''
    
    pass    




def main():

    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
        download_meetings()

    
    annotations = get_annotations()


    if not os.path.isdir(JSON_DIR):
        os.makedirs(JSON_DIR)

        os.chdir(JSON_DIR)
        save_json(annotations)

        os.chdir(os.path.dirname(__file__))


    speech_segments = {}

    for meeting_file in os.listdir(JSON_DIR):
        if not meeting_file.startswith("IB"):
            speech_segments[meeting_file] = slice_speech(f"{JSON_DIR}/{meeting_file}")


    for meeting, speakers in speech_segments.items():
        print(f"Playing {meeting}...")
        for speaker, utterances in speakers.items():
            print(f"Playing utternaces of speaker: {speaker}")

            for u in utterances:
                play(u)


if __name__ == "__main__":
    main()