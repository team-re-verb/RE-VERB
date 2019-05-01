import torch
import spectralcluster
from pydub import AudioSegment
from collections import Counter
import numpy as np
import json
import os


import model.utils as utils
import model.network as network
from model.hparam import hp


def prepeare_file(filename):
    '''
    Returns the necessary data for dirarization for a given file (log mel filterbank and voice time stamps)

    :param filename: the path of the file
    :returns: 
        the log mel filterbank and the time stamps
        :type: tuple of (np.ndarray of shape (num_utterances, num_filters), list)
    '''

    tmp_path = filename + '.tmp'

    audiofile = AudioSegment.from_file(filename)
    audiofile = utils.adjust_file(audiofile)

    vad, timestemps = utils.vad(audiofile, agressiveness=1)
    vad.export(tmp_path, format='wav')

    return utils.get_logmel_fb(tmp_path), timestemps



def get_timestamps(vad_ts, diar_res, diar_frame=25, diar_stride=10):
    '''
    Gets the timestamps from the results of the clusterer

    :param vad_ts: the time-stamps of when the speakers had spoken in the conversation
    :type vad_ts: list (of tuples which contains the pairs of timestamps)

    :param diar_res: the results of the full diarization process
    :type diar_res: list (of speaker numbers)

    :param diar_frame: the length of each utterance
    :type diar_frame: int

    :param diar_stride: the not-overlapping part of each utterance
    :type diar_stride: int

    :returns:
        the timestamps of each speaker in the conversation
        :type: dict
    '''

    occurences = { x:[] for x in Counter(diar_res).keys() }
    count = 0

    for times in vad_ts:
        for ts in range(times[0], times[1], diar_stride):
            occurences[diar_res[count]].append(ts)
            count += 1
            #del diar_res[0]
            #Not 100% accurate because we need to consider the last ebedding of a speaker and appent the diar_frame to it


    for speaker, timestamps in occurences.items():
        for i in range(len(timestamps) - 1):
            if i + 1 < len((timestamps)):
                if timestamps[i + 1] - timestamps[i] == diar_stride:
                    del timestamps[i + 1]
                    #Removing unessecary timestemps

        occurences[speaker] = list(zip(timestamps[0::2], timestamps[1::2])) #Ordering each pair of timestamps in tuples

    return occurences


def get_diarization(filename):
    '''
    Gets the speaker diarization results for a given audio file

    :param filename: the path for the audio file
    :returns:
        timestamps of each speaker occurance in the audio file
        :type: dict
    '''

    net = network.SpeechEmbedder()
    net.load_state_dict(torch.load(hp.model.model_path))
    net.eval()

    print(f'Loaded model from {hp.model.model_path}!') #{hp.model.model_path}

    embeddings = []
    filter_banks, voice_timestamps = prepeare_file(filename)
    #os.remove(f"{filename}.tmp")

    print('Extracted filerbank and vad time stamps')

    clusterer = spectralcluster.SpectralClusterer(min_clusters=2, max_clusters=100, p_percentile=0.95, gaussian_blur_sigma=1)

    print('Initiated clusterer')
    
    for utterance in filter_banks:
        utterance = torch.Tensor(utterance).unsqueeze_(0).unsqueeze_(0)
        embeddings.append(net(utterance))
    
    embeddings = torch.squeeze(torch.stack(embeddings))
    
    print('Got result from network!')

    embeddings = embeddings.detach().numpy()
    print('Converted to numpy')
    
    for i in range(embeddings.shape[0]):
        for j in range(embeddings.shape[1]):
            if np.isnan(embeddings[i,j]):
                print(f"Nan: ({i},{j})")
            elif np.isinf(embeddings[i,j]):
                print(f"Inf: ({i},{j})")

    results = clusterer.predict(embeddings)
    print(f'Predicted results from clusterer {results}')

    diarization_res = get_timestamps(voice_timestamps, results)
    diarization_res = {str(x):y for x,y in diarization_res.items()}


    return json.dumps(diarization_res, indent=2)