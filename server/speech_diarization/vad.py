import webrtcvad
import wave
from collections import namedtuple
from collections import deque
from pydub import AudioSegment
import sys


#TODO split to frames of 240ms with overlap and check code


class VAD():
    
    SEGMENT_MS = [10, 20, 30]
    SAMPLE_RATES = [8000, 16000, 32000, 48000]

    def __init__(self, path, frame_duration=30, overlap=5):
        try:
            self.path = path
            self.overlap = overlap
            self.frame_duration = frame_duration

            self.file = self.fix_file(path, frame_duration)
            
            self.print_details()
        except:
            raise ValueError("Audio file not found.")

    def print_details(self):
        print(f"channels: {self.file.channels}\nsample rate: {self.file.frame_rate}\nframe duration: {self.frame_duration}")


    def get_closest(self, lst, val):
        closest = min(lst)

        for i in sorted(lst):
            if i > val:
                return closest
            else:
                closest = i


    def fix_file(self, path, frame_duration):
        print('fixing file!')

        audiofile = AudioSegment.from_wav(self.path)
    
        if frame_duration not in VAD.SEGMENT_MS:
            print(f'setting frame duration to {self.get_closest(VAD.SEGMENT_MS, frame_duration)}')
            self.frame_duration = self.get_closest(VAD.SEGMENT_MS, frame_duration)    

        if audiofile.channels != 1:
            #print('setting file to mono')
            audiofile.set_channels(1)

        if audiofile.frame_rate not in VAD.SAMPLE_RATES:
            audiofile.set_frame_rate(self.get_closest(VAD.SAMPLE_RATES, audiofile.frame_rate))

        audiofile.export(path + "_fixed", format="wav")

        return AudioSegment.from_wav(path + "_fixed")

    
    def split_frames(self, duration=30):
        """
        Splits the file into frames in ms 

        Arguments
        ---------
        duration : int
            the specifed size of each frame in milisceconds

        Returns
        -------
        list
            A list of the frames
        """

        for frame in self.file[:: duration]:
            yield frame

    

    def detect_voice_activity(self):    
        #containes all of the speech frames
        voice_frames = [] 
        #tmp buffer for audioframes
        buffer_frames = deque(maxlen=int(len(self.file) / self.frame_duration))

        speech_precent = 0.9 #Used for determine when frames are speech 
        detected_voice = False

        vad = webrtcvad.Vad(3)
        sample_rate = self.file.sample_width


        for frame in self.split_frames():
            
            print(f"in detect_voice {frame}")
            is_speech = vad.is_speech(frame.raw_data, sample_rate)
            
            
            buffer_frames.append((is_speech, frame))

            voice_count = len([f for s,f in buffer_frames if s])
            not_voice_count = len(buffer_frames) - voice_count

            
            if not detected_voice:
                #in this state we already detecting speech  
                if voice_count >= speech_precent * buffer_frames.maxlen:
                    detected_voice = True

                    for s,buff in buffer_frames:
                        voice_frames.append(buff)
                    
                    buffer_frames.clear()
            else:
                if not_voice_count >= speech_precent * buffer_frames.maxlen:
                    detected_voice = False

                    for s,buff in buffer_frames:
                        if s:
                            voice_frames.append(buff)

                    buffer_frames.clear()
        

        return voice_frames




if __name__ == "__main__":

    voice = VAD("alive.wav")
    print(len(voice.detect_voice_activity()))
    print("Success!")