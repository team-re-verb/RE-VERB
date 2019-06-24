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

    occurrences = { x:[] for x in Counter(diar_res).keys() }
    count = 0
    curr_speaker = None
    curr_ts = None

    for times in vad_ts:
        for ts in range(times[0],times[1],diar_stride):
            speaker = diar_res[count]
            if speaker != curr_speaker: # new sequence
                if curr_ts != None:
                    occurrences[diar_res[count-1]].append(curr_ts)
                curr_ts = [ts, ts + diar_frame]
                curr_speaker = speaker
            else:
                curr_ts[1] += diar_stride

            count += 1
    return occurrences


def get_diarization(filename):
    '''
    Gets the speaker diarization results for a given audio file

    :param filename: the path for the audio file
    :returns:
        timestamps of each speaker occurance in the audio file
        :type: dict
    '''
    try:
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

        results = clusterer.predict(embeddings)
        print(f'Predicted results from clusterer {results}')
    
        diarization_res = get_timestamps(voice_timestamps, results)
        diarization_res = {str(x):y for x,y in diarization_res.items()}
    
    
        return json.dumps(diarization_res, indent=2)
    
    except:
        return ("ERROR")


if __name__ == "__main__":
    #for debug purposes
    print(get_diarization("../../client/basic-cli/audio/record.wav"))