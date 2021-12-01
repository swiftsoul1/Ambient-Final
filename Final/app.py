from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import multiprocessing
import vlc
import spotipy
import time
from spotipy.oauth2 import SpotifyClientCredentials

# functions
def watch_for_end():
    global media_player
    while True:
        state = media_player.get_state()
        print(state)
        if str(state) == "State.Ended":
            next_song()
        time.sleep(5)
def watch_for_button():
    global running, media_player, btnPin
    while True:
        print("yea we be here")
        if GPIO.input(btnPin) == GPIO.HIGH:
            print("pressed")
            if running:
                pause_song()
            elif not running:
                play_song()
        time.sleep(1)               
def pause_song():
    global running, media_player
    if running:
        running = False
        media_player.pause()
def play_song():
    global running, media_player
    if not running:
        running = True
        media_player.play()
def next_song():
    global sQueue, media_player
    if(len(sQueue) > 0):
        sQueue.pop(0)
        if(len(sQueue) > 0):
            media = vlc.Media(sQueue[0][0])
            media_player.set_media(media)
def add_song_to_queue(url, artist_name, song_name):
    global sQueue
    sQueue.append((url, artist_name, song_name)) 
# setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
btnPin = 10
GPIO.setup(btnPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
running = False
sQueue = [(0,0,0)]
media_player = vlc.MediaPlayer()
app = Flask(__name__)
multiprocessing.Process(target=watch_for_button).start()
multiprocessing.Process(target=watch_for_end).start()

@app.route("/", methods={"GET", "POST"})
def index():
    global running,sQueue
    if request.method == "GET":
        if len(sQueue) > 0:
            return render_template('MediaPlayer.html', queue=sQueue)
        else:
            return render_template('MediaPlayer.html')
    if request.method == "POST":
        if "action" in request.form:
            if request.form["action"] == "play_song":
                add_song_to_queue(request.form["url"], request.form["artist_name"], request.form["song_name"])
                if len(sQueue) > 1:
                    next_song()
                return render_template('MediaPlayer.html', queue=sQueue)
        elif "search" in request.form:
            results = sp.search(q=request.form['search'], type="track", limit=5)
            if len(sQueue) > 0:
                return render_template('MediaPlayer.html',queue-sQueue, searchResults=results['tracks']['items'])
            else:
                return render_template('MediaPlayer.html', searchResults=results['tracks']['items'])
        
                
    
    
    
    
    
    
    