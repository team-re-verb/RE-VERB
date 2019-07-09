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

    filter_banks = []
    timestamps = []

    audiofile = AudioSegment.from_file(filename)
    audiofile = utils.adjust_file(audiofile)

    speech = utils.vad(
        audiofile, agressiveness=hp.diarization.vad_agressiveness)

    for frame in speech:
        filter_banks.append(utils.get_logmel_fb(frame.audio))
        timestamps.append(frame.timestamps())

    return filter_banks, timestamps


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

    occurrences = {x: [] for x in Counter(diar_res).keys()}

    for count, res in enumerate(diar_res):
        occurrences[res].append(vad_ts[count])

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

        # {hp.model.model_path}
        print(f'Loaded model from {hp.model.model_path}!')

        embeddings = []
        filter_banks, timestamps = prepeare_file(filename)

        # os.remove(f"{filename}.tmp")

        print('Extracted filerbank and vad time stamps')

        clusterer = spectralcluster.SpectralClusterer(
            min_clusters=hp.diarization.min_clusters,
            max_clusters=hp.diarization.max_clusters,
            p_percentile=hp.diarization.p_percentile,
            gaussian_blur_sigma=hp.diarization.gaussian_blur_sigma
        )

        print('Initiated clusterer')

        for utterance in filter_banks:
            # adding an empty 3rd dimention, to represent 1 speaker input
            utterance = torch.Tensor(utterance).unsqueeze_(0)
            embeddings.append(net(utterance))

        embeddings = torch.squeeze(torch.stack(embeddings))

        print('Got result from network!')

        embeddings = embeddings.detach().numpy()
        print('Converted to numpy')

        results = clusterer.predict(embeddings)
        print(f'Predicted results from clusterer {results}')

        diarization_res = get_timestamps(timestamps, results)
        diarization_res = {str(x): y for x, y in diarization_res.items()}

        return json.dumps(diarization_res)

    except Exception as e:
        print(e)
        return("ERROR")


if __name__ == "__main__":
    # for debug purposes
    print(get_diarization("../../client/basic-cli/audio/record.wav"))
