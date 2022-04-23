import os
import random
import tempfile
from tkinter.filedialog import askopenfilenames
import webview
from just_playback import Playback
import threading
import smokesignal
from tinytag import TinyTag
import base64
import time
from colorsys import rgb_to_hls, hls_to_rgb
from PIL import Image

WINDOW_WIDTH=410
WINDOW_HEIGHT=700

playlist=None
playback=None
window=None

def adjustColorLightness(r, g, b, factor):
        h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        l = max(min(l * factor, 1.0), 0.0)
        r, g, b = hls_to_rgb(h, l, s)
        return int(r * 255), int(g * 255), int(b * 255)

def darkenColor(r, g, b, factor=0.1):
    return adjustColorLightness(r, g, b, 1 - factor)

def getDominantColor(pil_img):
    img = pil_img.copy()
    img = img.convert("RGBA")
    img = img.resize((1, 1), resample=0)
    dominant_color = img.getpixel((0, 0))
    return dominant_color

class Song:
    path=""
    title=""
    album=""
    artist=""
    cover=None
    coverPath=""

    def __init__(self, songpath):
        self.path=songpath
        tag=TinyTag.get(songpath, image=True)
        self.title=tag.title
        if self.title==None:
            self.title=os.path.split(songpath)[-1].split('.')[0]
        self.album=tag.album
        if self.album==None:
            self.album="Unknown"
        self.artist=tag.artist
        if self.artist==None:
            self.artist="Unknown"
        self.cover=tag.get_image()
        self.coverPath=None
        if self.cover!=None:
            self.coverPath=os.path.join(tempfile.gettempdir(), self.title.strip().replace(" ", "")+"-"+str(random.randint(100,999))+".png")
            with open(self.coverPath, 'wb') as f:
                f.write(self.cover)

class Playlist:
    current=-1
    queue=[]

    def add(self, songpath):
        self.queue.append(Song(songpath))
    
    def remove(self, number):
        self.queue.remove(number)
    
    def clear(self):
        self.current=-1
        self.queue=[]

class JSApi:
    playlistVisible=False

    def addToPlaylist(self):
        filenames=askopenfilenames(filetypes=(("Audio Files", ".wav .ogg .mp3 .flac .aac .wma"),   ("All Files", "*.*")))
        if len(filenames)!=0:
            for f in filenames:
                playlist.add(f)
        self.refreshPlaylist()
    
    def play(self):
        if not playback.paused:
            return
        if playlist.current==-1:
            playback.play()
        else:
            playback.resume()
        smokesignal.emit('playStatus', "PLAYING")

    def pause(self):
        playback.pause()
        smokesignal.emit('playStatus', "PAUSED")
    
    def prev(self):
        if len(playlist.queue)==0 or playlist.current==0:
            return
        playlist.current-=1
        playback.load_file(playlist.queue[playlist.current].path)
        playback.play()
        smokesignal.emit('songChanged', playlist.queue[playlist.current])

    def next(self):
        if len(playlist.queue)-1==playlist.current or playlist.current==-1:
            return
        playlist.current+=1
        playback.load_file(playlist.queue[playlist.current].path)
        playback.play()
        smokesignal.emit('songChanged', playlist.queue[playlist.current])
    
    def seekPosition(self):
        return {'position': playback.curr_pos, 'total': playback.duration}
    
    def setSeek(self, position):
        if playback.active:
            playback.seek(position)
    
    def switchTo(self, id):
        if len(playlist.queue)<=id or id<0:
            return
        playlist.current=id
        playback.load_file(playlist.queue[playlist.current].path)
        playback.play()
        smokesignal.emit('songChanged', playlist.queue[playlist.current])
    
    def refreshPlaylist(self):
        playlistContent=""
        c=0
        for item in playlist.queue:
            if c==playlist.current:
                playlistContent+="<div class='expandedContent-row expandedContent-row-selected' onclick='pywebview.api.switchTo({})'><div class='expandedContent-item-text'>{}</div></div>".format(c, item.title)
            else:
                playlistContent+="<div class='expandedContent-row' onclick='pywebview.api.switchTo({})'><div class='expandedContent-item-text'>{}</div></div>".format(c, item.title)
            c+=1
        window.evaluate_js('document.getElementById("playlistContent").innerHTML=`{}`;'.format(playlistContent))

    def togglePlaylistView(self):
        if not self.playlistVisible:
            self.refreshPlaylist()            
            window.evaluate_js('document.getElementById("playlist").style.display="block";')
            self.playlistVisible=True
        else:
            window.evaluate_js('document.getElementById("playlist").style.display="none";')
            self.playlistVisible=False

def player():
    global playlist
    global playback

    while True:
        if not playback.active:
            if playback.paused:
                return
            if len(playlist.queue)-1>playlist.current:
                playlist.current+=1
                playback.stop()
                playback=Playback()
                playback.load_file(playlist.queue[playlist.current].path)
                playback.play()
                smokesignal.emit('songChanged', playlist.queue[playlist.current])
                smokesignal.emit('playStatus', (lambda x: "PAUSED" if x else "PLAYING")(playback.paused))
        time.sleep(.5)

playback=Playback()
playlist=Playlist()

playerThread=threading.Thread(target=player)
playerThread.start()

@smokesignal.on('songChanged')
def onSongChange(song):
    api.refreshPlaylist()
    window.evaluate_js("document.getElementById('title').innerText='{}';document.getElementById('album').innerText='{}';document.getElementById('artist').innerText='{}';".format(song.title, song.album, song.artist))
    if song.cover!=None:
        window.evaluate_js("document.getElementById('albumart').src='data:image/png;base64, {}';".format(base64.b64encode(song.cover).decode()))
        dominantColor=getDominantColor(Image.open(song.coverPath))
        lightenedColor=darkenColor(r=dominantColor[0], g=dominantColor[1], b=dominantColor[2])
        if (lambda R, G, B: (0.2126*R)+(0.7152*G)+(0.0722*B))(dominantColor[0], dominantColor[1], dominantColor[2])>20:
            window.evaluate_js("document.getElementsByTagName('body')[0].style.color='#000000';")
        else:
            window.evaluate_js("document.getElementsByTagName('body')[0].style.color='#f5f5f5';")
        window.evaluate_js("document.getElementsByClassName('bg')[0].style.background='linear-gradient(170deg, rgba{}, rgb{})';".format(dominantColor, lightenedColor))
    else:
        window.evaluate_js("document.getElementById('albumart').src='data:image/png;base64, {}';".format("iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAMAAADDpiTIAAAAzFBMVEW1tbW1tbW1tbXIyMi+vr7////e3t7q6uqvr6/4+Pibm5unp6e9vb3p6emsrKytra3Dw8O6urrS0tLAwMDt7e3b29vR0dH5+fnv7+/w8PDx8fH6+vrj4+Pa2trs7Ozi4uKmpqaKiorW1taWlpaXl5fh4eGqqqq8vLyTk5Oenp6hoaGPj4+NjY3n5+eysrKZmZnd3d2RkZHLy8uwsLC/v7/FxcWdnZ22trbExMTr6+vKysro6OjZ2dmkpKSIiIj29vaQkJDMzMzk5OSlpaWmSmUvAAAAAnRSTlPs9UmPd0sAAAcMSURBVHhe7MABAQAAAAGg/D9tCJFhR9mlYwIAQBgGYHTDv2ZePDTRkKlGeQBOphgRQAAEQAAEaCUAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAiAAAhABBEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABNjfFaDOY9d++9MmozCO66EXJiKB4GRSGtaUvyE1bDoVnRxaff/vyTkzxoTZtXmUXNfv6f3wfHOH8wk4rs0NQAC+CqgBCED4NTUAAUCHG4AAfMMNQAC6ETUAAUCPG4AAtLgBCEAYUAMQAPS5AQhAGFMDEAAMuAEIAL7lBiAAz7gBCAC+4wYgABhyAxCA531qAAKA5xfUAAQA38fUAAQAo5gagADgMqYGIAC47FMDEACM+9QABADjFjUAAQCG3AAEAG1uAAKAq5gDgACwroMCUMa6DAjAg42H1AAEAEi4AQgArrgBCAAmMQEAAWBcBgSAXIAAkAsQAHIBAsAuQABOCz8lgAOAAPQSnO8FBQABuE57Ic52QwFAADrT2Rxn6zMAEICFddIlzvUspgAgABasshHOdMMBQADM1vkAZ1qSABAAi26XOO0HFgACYMUmC3FSnwWAAJitZ92T05c8AATAolenAogACIAFp3fAj0QABMCKEwGjgAWAAJwX8BMTAAGw4r+7wGsqAAJgRYSPSiIqAAJgwc84LlxzARAAW4xw3C9kAATAfsVxHTYAAmAvPhJSsAEQgNc4artgAyAA9hs3AAH4/RhARgdAAGJuAAJgb7gBCMAf3AAEYIhDRghAAFpHQsgBCMCOGoAA+IIZgACE3AAEYO7GDEAAtikhAAFIPpyvqAEIgGeEAARggrLEF4QABGCPMnNjBqCvgfmUEIAAtFCW+I4QgAAkKDMvCAEIwKQ8DPOpEQIQAJQNfEcIQABaKJulBSEAAWgfvgNsjBCAAOzLs54HhAAEoF8ejXxlhAAEoF0eLb3DCEAA9u93wFsjBCAAw/Jk62tCAAIQj99fAGlBCEAA2ocLIDNCAAJQXgBdTwtGAAJQzj/3zBgBCEBrBGCe+51RAhAA8+x65n5XkAIQgMWtu68KIwUgAGbRIjCjASAALAmAAAiAADAnAAIgAMwJgAAIAHMCIAACwJEACMBF69/oAAhAfJ9M9vjQ5Gp4wQJAAPrtS5xp3241H4AAxDeX+GT7pNkABOAiGeOhBKCxxeX4OQEIwP0YoAUgAPEbgBeAALTGIAYgAEOAGIAAXOGJCYDmj5wagOYPJwWg93+ZFwJQ5/qomFuNE4B4Tw1AAK5QsVAA6lwLVZsLQJ2bVAeQMgPQBYDtihmALgAsBaC+XaB6WSYAta2NyoW+FoDadonKJR4JQF2LUT1LjRiAdoDQpwJQ2xJUbus7YgACEOapEQMQgKVnxAAEYO5pwQtAfwUJZ742XgDaAnq+MgGoc6iUeRoIQK37ExUauHeMFoB+BAzcd1bvBCAOq8x/YwJQ917iiVkj5i8ASzypsCHzFwC7xxPqZk15/wtA0MWjG+Se7kwAmtEuxOMKe+53kQlAU/orfOzj75vCGpMAFJsuPrv5tXvasQYlABa9SvB5jXrevMdfACy4W4Z4uLm5+2phTUsArJjOBnigwbW733bMBKCJrdP/JZBY7u6rnTU0AbBg47klONNo8G76vllYmQA0lYDnve28i0PzZNub+T9Nd4U1OwEwK3ZTf1d2/baZl91uCKYvAKWBTra680OradYJjCcBKIsWbwv+ZpcOCAAAQBAAlf9Ht6AFwgbyEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEAABEECAIAACIEArARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARAAARCAnVRjUo1rBw4IAAAACADl/2lDiAw7BQlRmkgBzmH1AAAAAElFTkSuQmCC"))
        window.evaluate_js("document.getElementsByClassName('bg')[0].style.background='linear-gradient(170deg, #c8dcec, #8596ab)';")
        window.evaluate_js("document.getElementsByTagName('body')[0].style.color='#000000';")

@smokesignal.on('playStatus')
def onPlayStatusChange(status):
    if status=="PLAYING":
        window.evaluate_js("document.getElementById('playbutton').style.display='none';document.getElementById('pausebutton').style.display='block';")
    if status=="PAUSED":
        window.evaluate_js("document.getElementById('pausebutton').style.display='none';document.getElementById('playbutton').style.display='block';")

def on_closed():
    os.kill(os.getpid(), 9)

api=JSApi()
window=webview.create_window("Aoede", "web/app.html", width=WINDOW_WIDTH, height=WINDOW_HEIGHT, resizable=True, frameless=False, js_api=api)
window.events.closed+=on_closed
webview.start()