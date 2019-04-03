import wget
import xml.etree.ElementTree as ET
import os
from zipfile import ZipFile
import operator
import json


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
    URL = "http://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus"

    if not os.path.isdir(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    os.chdir(AUDIO_DIR)

    for meeting_id in ami_meetings:
        print(f"Downloading {meeting_id} meetings")

        for meeting in ami_meetings[meeting_id]:
            for i in ['a', 'b', 'c', 'd']:
                print(f"\tPulling {meeting}{i}...[{URL}/{meeting}{i}/audio/{meeting}{i}.Mix-Headset.wav]")
                wget.download(f"{URL}/{meeting}{i}/audio/{meeting}{i}.Mix-Headset.wav", meeting + i + ".wav")
    
    os.chdir("../")


def download_annotations():    
    os.chdir(OUT_DIR)
    wget.download("http://groups.inf.ed.ac.uk/ami/AMICorpusAnnotations/ami_public_manual_1.6.2.zip", "tmp.zip")

    with ZipFile("tmp.zip", 'r') as z:
        z.extractall("metadata")
        
    os.remove("tmp.zip")


def process_segment(filename):
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
                
    print("done!")

    return segments


def save_json(annotations):
    for meeting in annotations:
        meeting_details = annotations[meeting]

        meeting_details = dict(sorted(meeting_details.items(), key=operator.itemgetter(0)))
        print(meeting_details)
        meeting_details["meeting"] = meeting

        with open(f"{meeting}.json", "w+") as f:    
            json.dump(meeting_details, f, indent=2)
        

if __name__ == "__main__":
    
    download_meetings()

    annotations = get_annotations()

    if not os.path.isdir(JSON_DIR):
        os.makedirs(JSON_DIR)

    os.chdir(JSON_DIR)
    save_json(annotations)

    for meeting in annotations:
        print(meeting)
        print(annotations[meeting].keys())