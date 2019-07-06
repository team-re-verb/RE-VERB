from pydub import AudioSegment


class Frame():
    def __init__(self, start=0, end=0, audio=AudioSegment.empty()):
        self.start = start
        self.end = end
        self.audio = audio

    def __eq__(self, frame):
        return self.start == frame.start and self.end == frame.end

    def __len__(self):
        return self.end - self.start

    def __iadd__(self, frame):
        if len(self) == 0: # empty case
            self.start = frame.start
            self.end = frame.end
            self.audio = frame.audio

        elif self.start < frame.start:
            self.end = frame.end
            self.audio += frame.audio
        elif self.start > frame.start:
            self.start = frame.start
            self.audio = frame.audio + self.audio
        
        return self

    def __add__(self,frame):
        new_frame = Frame()

        if self.start < frame.start:
            new_frame.start = self.start
            new_frame.end = frame.end
            new_frame.audio = self.audio + frame.audio
        elif self.start > frame.start:
            new_frame.start = frame.start
            new_frame.end = self.end
            new_frame.audio = frame.audio + self.audio

        return new_frame

    def timestamps(self):
        return (self.start, self.end)