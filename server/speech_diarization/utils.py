from pydub import AudioSegment
import webrtcvad
import scipy.io.wavfile as wav
import speechpy
import torch.nn.functional as F
import os


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



def vad(audiofile, frame_len=30):
    '''
    Performes Voice Activity Detection on an audio file

    :param audiofile: the audio file to perform the vad on
    :type audiofile: pydub.AudioSegment

    :returns: the voice frames from the file
    '''
    
    speech = AudioSegment.empty()
    vad = webrtcvad.Vad()
    sample_rate = audiofile.frame_rate

    vad.set_mode(2) #Agressiveness of the vad

    for frame in audiofile[::frame_len]:
        if len(frame) == len(frame_len):
                if vad.is_speech(frame.raw_data, sample_rate):
                        speech += frame

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
    centroids = []
    for speaker in embeddings:
        centroid = speaker.sum()/len(speaker) # calc centroid per speaker
        centroids.append(centroid)
    centroids = torch.stack(centroids)
    return centroids

def get_centroid(embeddings, speaker_num, utterance_num):
    centroid = 0
    for utterance_id, utterance in enumerate(embeddings[speaker_num]):
        if utterance_id == utterance_num:
            continue
        centroid = centroid + utterance
    centroid = centroid/(len(embeddings[speaker_num])-1)
    return centroid

def get_cossim(embeddings, centroids):
    # Calculates cosine similarity matrix. Requires (N, M, feature) input
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
    # Calculates loss from (N, M, K) similarity matrix
    per_embedding_loss = torch.zeros(sim_matrix.size(0), sim_matrix.size(1))
    for j in range(len(sim_matrix)):
        for i in range(sim_matrix.size(1)):
            per_embedding_loss[j][i] = -(sim_matrix[j][i][j] - ((torch.exp(sim_matrix[j][i]).sum()+1e-6).log_()))
    loss = per_embedding_loss.sum()    
    return loss, per_embedding_loss