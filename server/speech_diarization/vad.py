import webrtcvad
import wave
from collections import namedtuple
from collections import deque
from pydub import AudioSegment


#TODO split to frames of 240ms with overlap and check code


class VAD():

    def __init__(self, path):
        try:
            self.path = path

            self.padding_duration = 300
            self.frame_duration = 30

            self.file = wave.open(path, 'rb')

        except:
            raise ValueError("Audio file not found.")

    
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

        Frame = namedtuple("Frame", ["buffer", "timestamp", "duration"])
        count = 0
        fuck_count = 0

        audiofile = AudioSegment.from_wav(self.path)
            
        for frame in audiofile[:: duration]:
            yield Frame(frame.raw_data, count, duration)
            count += duration

    

    def detect_voice_activity(self):    
        #containes all of the speech frames
        voice_frames = [] 
        #tmp buffer for audioframes
        buffer_frames = deque(maxlen=int(self.padding_duration / self.frame_duration))

        speech_precent = 0.9 #Used for determine when frames are speech 
        detected_voice = False

        vad = webrtcvad.Vad(3)
        sample_rate = self.file.getframerate()


        for frame in self.split_frames():

            try:
                is_speech = vad.is_speech(frame.buffer, sample_rate)
            except:
                continue

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

    voice = VAD("example.wav")
    print(len(voice.detect_voice_activity()))