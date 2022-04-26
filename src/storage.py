import os
import tempfile
import random
import sqlite3
import smokesignal
from define import *

def sanitize(text):
    for char in "?:@$;,`+-*/><=~&|!^#\"\\/":
        text=text.replace(char, "")
    return text

class Song:
    def __init__(self, songid=-1, title="Unknown", album="Unknown", artist="Unknown", lyrics="Lyrics Not Available :(", cover=""):
        self.songid=songid
        self.title=title
        self.album=album
        self.artist=artist
        self.lyrics=lyrics
        self.cover=cover
        self.coverPath=os.path.join(tempfile.gettempdir(), self.title.strip().replace(" ", "")+"-"+str(random.randint(100,999))+".png")
        with open(self.coverPath, 'wb') as file:
            file.write(self.cover)

def createDB(dbpath=DB_PATH):
    db=sqlite3.connect(dbpath)
    cursor=db.cursor()
    cursor.execute('CREATE TABLE songData (songid INTEGER UNIQUE, title TEXT, album TEXT, artist TEXT, lyrics TEXT, cover BLOB);')
    cursor.execute('CREATE TABLE settings (key TEXT, value TEXT);')
    db.commit()
    db.close()

try:
    db=sqlite3.connect(DB_PATH)
    cursor=db.cursor()
    cursor.execute("SELECT songid FROM songData;")
    db.close()
except:
    createDB()

def getSong(title, artist):
    db=sqlite3.connect(DB_PATH)
    cursor=db.cursor()
    if artist not in ["Unknown", None]:
        try:
            cursor.execute('SELECT songid, title, album, artist, lyrics, cover FROM songData WHERE (title LIKE "%{}%" AND artist LIKE "%%");'.format(sanitize(title), sanitize(artist)))
        except Exception as err:
            pass
    else:
        cursor.execute('SELECT songid, title, album, artist, lyrics, cover FROM songData WHERE (title LIKE "%{}%");'.format(sanitize(title)))
    d=cursor.fetchall()
    if len(d)==0:
        return None
    try:
        return Song(d[0][0], d[0][1], d[0][2], d[0][3], d[0][4], d[0][5])
    except:
        return None

@smokesignal.on('songDataFoundGenius')
def onSongDataFound(song, album, cover):
    try:
        db=sqlite3.connect(DB_PATH)
        cursor=db.cursor()
        cursor.execute("INSERT INTO songData VALUES (?, ?, ?, ?, ?, ?);", (song.id, song.title, album, song.artist, song.lyrics, cover))
        db.commit()
        db.close()
    except Exception as err:
        print(err)