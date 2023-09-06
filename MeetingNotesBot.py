import pyautogui as pyg
import webbrowser as wb
from pytz import timezone as tz
from datetime import datetime
import time

import wave
import sys

import pyaudio

# browser settings
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
wb.register('chrome', None, wb.BackgroundBrowser(chrome_path))

# datetime settings
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H.%M.%S")

# pyAudio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100  # common rate for microphones
RECORD_SECONDS = 2 * 60  # 2 minutes
WAVE_OUTPUT_FILENAME = "meeting_recording_" + formatted_datetime + ".wav" # include recording datetime



#join the meeting (right now)
def join_meeting(zoom_link):

    # zoom app related - default options need changing on VM
    wb.get(using='chrome').open(zoom_link, new=2) #open zoom link in a new window
    time.sleep(5) # given time for the link to show app top-up window
    pyg.click(x=805, y=254, clicks=1, interval=0, button='left') # click on open zoom.app option
    time.sleep(5) # wait for 5 sec
    #VM does not have sound options 
    cancel_button_coords = pyg.locateCenterOnScreen('cancel_button.PNG') #find cancel button
    time.sleep(2) #give python autogui time to find cancel button
    pyg.click(cancel_button_coords[0], cancel_button_coords[1], clicks = 1, interval=0, button='left') #click cancel button



#leave meeting (right now via button clicks)

#check if meeting is active

#start recording meeting sound
def record_meeting_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

#bot entrypoint
def cse_meeting_notes_bot():
    join_meeting("https://unity3d.zoom.us/j/93405166024?pwd=L3kwcHkyL2lPRkl3TTE2TnZhd2ZFZz09")
    record_meeting_audio()

cse_meeting_notes_bot()