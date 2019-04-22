from pydub import AudioSegment
import webrtcvad
import scipy.io.wavfile as wav
import speechpy


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


def slice_audio(audio, len_window=25, stride=10):
    '''
    Slices an audio file into sliding windows with stride

    :param audio: the audio to slice
    :type audio: pydub.AudioSegment

    :param len_window: the length of each window
    :param stride: the stride bwtween neighboring windows

    :returns: the slcied audio
    '''
    
    frames = []

    j = 0
    i = len_window

    for k in range(len(audio) / len_window):
        frames.append(audio[j: i])

        j = i - stride
        i += stride





def adjust_file(audiofile):
    '''
    Adjusts an audiofile for vad and network

    :param audiofile: an audio file
    :type audiofile: pydub.AudioSegment

    :returns: ???
    '''

    audiofile.set_frame_rate(16000)
    audiofile.set_channels(1)
    #save file??



def vad(audiofile, frame_len=30):
    '''
    Performes Voice Activity Detection on an audio file

    :param audiofile: the audio file to perform the vad on
    :type audiofile: pydub.AudioSegment

    :returns: the voice frames from the file
    '''
    
    speech = []
    vad = webrtcvad.Vad()
    sample_rate = audiofile.frame_rate

    vad.set_mode(2) #Agressiveness of the vad

    for frame in audiofile[::frame_len]:
        if vad.is_speech(frame.raw_data, sample_rate):
            speech.append(frame)

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