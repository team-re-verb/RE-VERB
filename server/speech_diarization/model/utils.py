from pydub import AudioSegment
import webrtcvad
import scipy.io.wavfile as wav
import speechpy

import torch
import torch.autograd as grad
import torch.nn.functional as F

import os

from frame import Frame


def get_logmel_fb(path, len_window=25, stride=10, filters=40):
    '''
    Gives the log mel filter bank features for each utterance in a audio

    :param path: the path to the wave file to be read from
    :param len_window: the length of each sliding window for the features to be extracted from
    :param stride: the non-overlapping part for each window
    :param filters: the number of filters (features)

    :returns:
        the logmel fb featues
        :type: numpy.ndarray
    '''

    sample_rate, signals = wav.read(path)

    #converting to ms
    len_window /= 1000
    stride /= 1000

    if len(signals.shape) != 1:
        signals = signals[:,0] #Getting only the first channel data

    return speechpy.feature.lmfe(signals,sample_rate,frame_length=len_window,frame_stride=stride,num_filters=filters)




def adjust_file(audiofile):
    '''
    Adjusts an audiofile for vad and network

    :param audiofile: an audio file
    :type audiofile: pydub.AudioSegment

    :returns: 
        new, Adjusted audio file
        :type: pydub.AudioSegment
    '''

    audiofile = audiofile.set_frame_rate(16000)
    audiofile = audiofile.set_channels(1)
    
    audiofile.export('tmp.wav', format='wav')
    audiofile = AudioSegment.from_file('tmp.wav')
    
    os.remove('tmp.wav')
    return audiofile



def vad(audiofile, frame_len=20, max_frame_len=400 ,agressiveness=1):
    '''
    Performes Voice Activity Detection on an audio file

    :param audiofile: the audio file to perform the vad on
    :type audiofile: pydub.AudioSegment

    :param agressiveness: the agressiveness for the vad (from 1 - 3)

    :returns: the voice frames from the file and a list of voice activity timestamps
    '''

    #speech = AudioSegment.empty()
    vad = webrtcvad.Vad()
    sample_rate = audiofile.frame_rate
    
    speech = [Frame()]


    voice_indexes = [i for i in range(0, len(audiofile), frame_len)] #every index represents a timestamp with jump of frame_len miliseconds
    voice_ts = []

    vad.set_mode(agressiveness) #Agressiveness of the vad



    for ts,frame in enumerate(audiofile[::frame_len]):
        if len(frame) == frame_len:
            if vad.is_speech(frame.audio_data, sample_rate):
                if len(speech[-1]) + frame_len <= max_frame_len:
                    speech[-1] += Frame(ts,ts+frame_len, frame)
                else:
                    speech.append(Frame())
                #if not voice_ts:
                #    voice_ts.append(voice_indexes[ts])
                #elif voice_ts[-1] + frame_len != voice_indexes[ts]:
                #    voice_ts.append(voice_indexes[ts]) #Adding the time-stamp if there is a voice in that frame

    
    #splitting the list of time-stamps into even and odd lists then zip them to get list of tuples of (start,end)
    #voice_ts = list(zip(voice_ts[0:][::2], voice_ts[1:][::2])) 
    return speech



def get_full_audio(frames):
    '''
    Gets the concated audio from frames

    :param frames: the frames to concat
    :type frames: list

    :returns: the concated frames
    '''

    full_audio = AudioSegment.empty()

    for f in frames:
        full_audio += f

    return full_audio

####---   GE2E loss utils   ---####

def get_centroids(embeddings):
    '''
    Calculates the centroids for each embeddings which belongs to the same speaker

    :param embeddings: the embeddings (d-vectors) of each speaker
    :type embeddings: np.ndarray with shape of N x M x F (num_speakers,num_utterances,num_features)

    :returns:
        the centroids of each speaker (from a pool of utterances)
        :type: np.ndarray with shape of N x F (num_speakers,num_features) 
    '''
    centroids = []

    for speaker in embeddings:
        centroid = speaker.sum() / len(speaker) # calculate centroid per speaker
        centroids.append(centroid)
        
    centroids = torch.stack(centroids)
    
    return centroids

def get_centroid(embeddings, speaker_num, utterance_num):
    '''
    Calculates the centoid of a pool of embeddings for a specific speaker.
    The calculation ignores the embedding which is the last output of the network

    :param embeddings: all of the embeddings outputed from the network
    :type embeddings: np.ndarray with shape of N x M x F (num_speakers,num_utterances,num_features)

    :param speaker_num: the number of the speaker in which the network outputed the last embedding
    :param utterance_num: the number of the utterance in which the network outputed the last embedding
    '''
    centroid = 0
    for utterance_id, utterance in enumerate(embeddings[speaker_num]):
        if utterance_id == utterance_num:
            continue
        centroid = centroid + utterance
    centroid = centroid/(len(embeddings[speaker_num])-1)
    return centroid


def get_cossim(embeddings, centroids):
    '''
    Calculates the similarity matrix as defined in the article

    :param embeddings: 
    :type embeddings:

    :param centroids:
    :type centroids:

    :returns:
        the similarity matrix
        :type: np.ndarray with shape of N x M x C (num_speakers, num_utterances, num_centroids)
    '''
    cossim = torch.zeros(embeddings.size(0),embeddings.size(1),centroids.size(0))

    for speaker_num, speaker in enumerate(embeddings):
        for utterance_num, utterance in enumerate(speaker):
            for centroid_num, centroid in enumerate(centroids):
                if speaker_num == centroid_num:
                    centroid = get_centroid(embeddings, speaker_num, utterance_num)
                output = F.cosine_similarity(utterance,centroid,dim=0)+1e-6
                cossim[speaker_num][utterance_num][centroid_num] = output
    return cossim


def calc_loss(sim_matrix):
    '''
    Calculates the GE2E loss from the similarity matrix (performes softmax on each cell in the matrix)

    :param sim_matrix: the similarity matrix between speakers d-vectors and their centroids
    :type sim_matrix: np.ndarray with shape of N x M x C (num_speakers, num_utterances, num_centroids)

    :returns:
        the total loss and the loss per embedding
        :type loss: float
        :type per_embedding_loss: np.ndarray of shape N x M (num_speakers,num_utterances) 
    '''

    per_embedding_loss = torch.zeros(sim_matrix.size(0), sim_matrix.size(1))
    
    for j in range(len(sim_matrix)):
        for i in range(sim_matrix.size(1)):
            per_embedding_loss[j][i] = -(sim_matrix[j][i][j] - ((torch.exp(sim_matrix[j][i]).sum()+1e-6).log_()))
            
            #loss with sigmoid
            #maxargs = torch.argsort(torch.sigmoid(sim_matrix[j][i]), dim=0, descending=True)
            #per_embedding_loss[j][i] = 1 - torch.sigmoid(sim_matrix[j][i][j]) + torch.sigmoid(sim_matrix[j][i])[maxargs[1] if maxargs[0] == j else maxargs[0]].item()   
            
            #maybe better loss than the current one
            #per_embedding_loss[j][i] = -(sim_matrix[j][i][j] - torch.logsumexp(sim_matrix[j][i].float(), 0))
            
    
    loss = per_embedding_loss.sum()
    
    return loss, per_embedding_loss



def average_embeddings(embeddings):
    ''' 
    Avrages the embedding d-vectors outputted from the network according
    '''
    pass