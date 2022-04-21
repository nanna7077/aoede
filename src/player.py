import pyaudio
from pydub import AudioSegment
from pydub.utils import make_chunks
import threading
import smokesignal

playerInstance=None

class PlayerLoop:
    start=0
    length=-1
    volume=100
    filepath=''
    songposition=-1
    changed=False
    repeat=False
    time=0

    def __init__(self, filepath='', loop=True):
        self.filepath=filepath
        self.loop=loop

    def play(self):
        self.loop=True

    def pause(self):
        self.start=self.time
        self.loop=False

    def run(self):
        while self.filepath=='' or (not self.loop):
            pass

        sound = AudioSegment.from_file(self.filepath)
        player = pyaudio.PyAudio()

        stream = player.open(format = player.get_format_from_width(sound.sample_width),
            channels = sound.channels,
            rate = sound.frame_rate,
            output = True)

        # PLAYBACK LOOP
        self.length = sound.duration_seconds
        self.volume = 100.0
        playchunk = sound[self.start*1000.0:(self.length)*1000.0] - (60 - (60 * (self.volume/100.0)))
        millisecondchunk = 50 / 1000.0

        while self.loop:
            self.time = self.start
            for chunks in make_chunks(playchunk, millisecondchunk*1000):
                self.time += millisecondchunk
                stream.write(chunks._data)
                if not self.loop:
                    break
                if self.changed:
                    break
                if self.time >= self.length:
                    break
            if self.changed:
                break
        if self.changed:
            smokesignal.emit('changed', self.songID)
            self.changed=False
            self.run()

        stream.close()
        player.terminate()
        if (not self.repeat) and (self.loop):
            self.filepath=''
            self.songposition=-1
        self.run()

def playFunc():
    global playerInstance
    print("[INFO] Player Daemon Started")
    playerInstance=PlayerLoop()
    playerInstance.run()

playerThread=threading.Thread(target=playFunc)
playerThread.name="Audio Player"

def setAudio(filepath, songposition):
    playerInstance.start=0
    playerInstance.filepath=filepath

def seek(position):
    playerInstance.start=position
    playerInstance.changed=True

def pause():
    """Just to keep things sane and uniform"""
    playerInstance.pause()

def play():
    """Just to keep things sane and uniform"""
    playerInstance.play()