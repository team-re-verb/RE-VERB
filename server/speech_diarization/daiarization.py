import torch
import spectralcluster
from pydub import AudioSegment
from collections import Counter

import utils
import network
import hparam as hp


def get_fb(filename):
    '''
    Returns the log mel filterbank for a given file

    :param filename: the path of the file
    :returns: 
        the log mel filterbank
        :type: np.ndarray of shape (num_utterances, num_filters)
    '''

    tmp_path = filename + '.tmp'

    audiofile = AudioSegment.from_file(filename)
    audiofile = utils.adjust_file(audiofile)

    vad = utils.vad(audiofile)
    vad.export(tmp_path, format='wav')

    return utils.get_logmel_fb(tmp_path)



#IMPORTANT: We need to get the actual voice timestamps and then return the diarization timestamps according to the relative times

def get_timestamps(results):
    '''
    Gets the timestamps from the results of the clusterer

    :param results: the results of the full diarization process
    :type results: list (of speaker numbers)

    :returns:
        the timestamps for each speaker
        :type: dict
    '''

    occurences = { x:[] for x in Counter(results).keys() }

    ts = 0
    segment = 25

    for ts,speaker in enumerate(results):
        occurences[speaker].append(ts * segment)
    
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
    net.load_state_dict(torch.load(hp.model.modelpath))
    net.eval()

    embeddings = torch.Tensor()
    filter_banks = get_fb(filename)

    clusterer = spectralcluster.SpectralClusterer(min_clusters=2, max_clusters=100, p_percentile=0.95, gaussian_blur_sigma=1)

    for utterance in filter_banks:
        torch.stack((embeddings, net(utterance)))
    embeddings = embeddings.numpy()

    results = clusterer.predict(embeddings)

    timestamps = get_timestamps(results)
    print(timestamps)

    return timestamps


if  __name__ == "__main__":
    get_diarization("tmp.wav")