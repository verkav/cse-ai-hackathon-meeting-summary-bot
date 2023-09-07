# zoom automation 
import pyautogui as pyg
import webbrowser as wb
from pytz import timezone as tz
from datetime import datetime
import time
#sound recornding 
import wave
import sys
import pyaudio
#speech recognition 
import speech_recognition as sr
from pocketsphinx import AudioFile

# browser settings - Windows VM only
#chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
#wb.register('chrome', None, wb.BackgroundBrowser(chrome_path))


# -----------------helper functions----------------
def minutes_to_seconds(minutes):
    seconds_in_minute = 60
    seconds = minutes * seconds_in_minute
    rounded_seconds = round(seconds)
    return rounded_seconds

# produce number of minutes and seconds from RECORD SECONDS
def recording_seconds_to_minutes_and_seconds(seconds):
    minutes, remainder_seconds = divmod(seconds, 60)
    print(f"recording length: {minutes}m and {remainder_seconds}s")
    return minutes, remainder_seconds

#create filename from current datetime
def create_datetime_string():
    # datetime settings
    current_datetime = datetime.now()
    formatted_datetime_string = current_datetime.strftime("%Y-%m-%d_%H.%M.%S")
    return formatted_datetime_string


# write to file
def write_to_text_file(filename, string):
    text_file = open(filename, "w")
    text_file.write(string)
    text_file.close()

# -----------------main functions----------------
#join the meeting (right now)
def join_meeting(zoom_link):

    # zoom app related - default options need changing on VM
    wb.get(using='chrome').open(zoom_link, new=2) #open zoom link in a new window
    time.sleep(5) # given time for the link to show app top-up window
    pyg.click(x=805, y=254, clicks=1, interval=0, button='left') # click on open zoom.app option
    time.sleep(5) # wait for 5 sec
    
    #VM does not have sound options, below is code for cancelling the audio devices prompt

    #cancel_button_coords = pyg.locateCenterOnScreen('cancel_button.PNG') #find cancel button
    #time.sleep(2) #give python autogui time to find cancel button
    #pyg.click(cancel_button_coords[0], cancel_button_coords[1], clicks = 1, interval=0, button='left') #click cancel button


#start recording meeting sound
def record_meeting_audio(filename, recording_length_s):
    # pyAudio settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1 if sys.platform == 'darwin' else 2
    RATE = 44100  # common rate for microphones
    RECORD_SECONDS = recording_length_s  #number of seconds to record
    WAVE_OUTPUT_FILENAME = filename # include recording datetime

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    print("* recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* recording complete")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def generate_transcript(input_audio_file_path, output_file_name, recording_length_s, prompt):
    r = sr.Recognizer()
    # if using PocketSphinx, convert file to raw
    # if using Google services, keep as wav
    meeting_audio = sr.AudioFile(input_audio_file_path)
    
    full_transcript = ""
    audio_snippets = []
    transcript_snippets = []

    with meeting_audio as source:
        #record in chunks of 1 minute (or less)
        if recording_length_s > 60 :
            minutes, remainder_seconds = recording_seconds_to_minutes_and_seconds(recording_length_s)
            for i in range(minutes):
                #split snippet
                current_audio_snippet = r.record(source, duration = 60)
                #store snippet
                audio_snippets.append(current_audio_snippet)
                #transcribe snippet
                transcript_snippet = r.recognize_google(current_audio_snippet, language = 'en-EN')
                #output to console for testing
                print(f"processing recording snippet {i+1} of {minutes+1 if remainder_seconds !=0 else minutes}...\n")
                #store strancription snippet
                transcript_snippets.append(transcript_snippet + "\n")

            if remainder_seconds != 0:
                #record final snippet
                final_audio_snippet = r.record(source, duration = remainder_seconds)
                #store
                audio_snippets.append(final_audio_snippet)
                #transcribe
                final_transcript_snippet = r.recognize_google(final_audio_snippet, language = 'en-EN')
                #output to console for testing
                print(f"processing recording snippet {minutes+1} of {minutes+1}...\n")
                #store strancription snippet
                transcript_snippets.append(final_transcript_snippet + "\n")
        else:
            #the snippet is les than a minute, transcribe in full
            single_audio_snippet = r.record(source)
            audio_snippets.append(single_audio_snippet)
            full_transcript = r.recognize_google(single_audio_snippet, language='en-EN')
            
    #turn snippets into a string and output it
    full_transcript = " ".join(transcript_snippets)
    write_to_text_file(output_file_name, prompt + full_transcript)    

# -----------------bot entrypoint----------------
#bot entrypoint
def cse_meeting_notes_bot(meeting_link, minutes_to_record):
    prompt = """This is a transcript of a meeting. Analyse it and make a summary. Mention and highlight all the names, numbers, dates, job titles, company titles, products, tools, names of locations. Only show the participant names in the beginning of the summary. Add the current date.
    Show the name of the main discussed topic. Create a separate sub-section for every change of subject and name it accordingly. If any requirement, web link, unresolved issue, promise or intention is mentioned, show it as an action point in the end of the summary. When there are several arguments in the same topic, add them as a bullet list. If there is a comparison with mentioned pros and cons - show in bullets.
    If there is a meeting suggestion, show in the format of name, date and time and the participants, if no meeting is suggested, skip. If meeting details aren’t specified, make a note that it needs clarification.
    Here is the transcript:\n\n"""
    #setup stage
    datetime_for_filenames = create_datetime_string()
    wav_filename = f"meeting_recording_{datetime_for_filenames}.wav"
    transcript_filename = f"meeting_transcript_{datetime_for_filenames}.txt"
    seconds_to_record = minutes_to_seconds(minutes_to_record)
    #run bot
    print("Joining meeting...")
    join_meeting(meeting_link)
    record_meeting_audio(wav_filename, seconds_to_record)
    print(f"meeting_recorded in file [{wav_filename}]")
    time.sleep(5) # wait for 5 sec, so file is created
    generate_transcript(wav_filename, transcript_filename, seconds_to_record, prompt)
    print(f"Your transcript is ready. [{transcript_filename}]")

#provide zoom meeting link and number of minutes to record
cse_meeting_notes_bot("https://unity3d.zoom.us/j/93405166024?pwd=L3kwcHkyL2lPRkl3TTE2TnZhd2ZFZz09", 12.3)