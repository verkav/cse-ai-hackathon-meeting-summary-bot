# audio to text transcription
import speech_recognition as sr
from pocketsphinx import AudioFile

# sample recording is 12mins 20secs
#12*60+20 600 + 120 + 20 = 740
RECORD_SECONDS = 740

# -----------------helper functions----------------
# produce number of minutes and seconds from RECORD SECONDS
def recording_seconds_to_minutes_and_seconds(seconds):
    minutes, remainder_seconds = divmod(seconds, 60)
    print(f"recording length: {minutes}m and {remainder_seconds}s")
    return minutes, remainder_seconds
def write_to_text_file(filename, string):
    text_file = open(filename, "w")
    text_file.write(string)
    text_file.close()


def generate_transcript(input_audio_file_path, output_file_name):

    prompt = """This is a transcript of a meeting. Analyse it and make a summary. Mention and highlight all the names, numbers, dates, job titles, company titles, products, tools, names of locations. Only show the participant names in the beginning of the summary. Add the current date.
    Show the name of the main discussed topic. Create a separate sub-section for every change of subject and name it accordingly. If any requirement, web link, unresolved issue, promise or intention is mentioned, show it as an action point in the end of the summary. When there are several arguments in the same topic, add them as a bullet list. If there is a comparison with mentioned pros and cons - show in bullets.
    If there is a meeting suggestion, show in the format of name, date and time and the participants, if no meeting is suggested, skip. If meeting details aren’t specified, make a note that it needs clarification.
    Here is the transcript:\n\n"""

    r = sr.Recognizer()
    # if using PocketSphinx, convert file to raw
    # if using Google services, keep as wav
    meeting_audio = sr.AudioFile(input_audio_file_path)
    
    full_transcript = ""
    audio_snippets = []
    transcript_snippets = []

    with meeting_audio as source:
        #record in chunks of 1 minute (or less)
        if RECORD_SECONDS > 60 :
            minutes, remainder_seconds = recording_seconds_to_minutes_and_seconds(RECORD_SECONDS)
            for i in range(minutes):
                #split snippet
                current_audio_snippet = r.record(source, duration = 60)
                #store snippet
                audio_snippets.append(current_audio_snippet)
                #transcribe snippet
                transcript_snippet = r.recognize_google(current_audio_snippet, language = 'en-EN')
                #output to console for testing
                print(f"processing recording snippet {i+1} of {minutes+1}...\n")
                #store strancription snippet
                transcript_snippets.append(transcript_snippet + "\n")

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


generate_transcript('cse-ai-hackathon-meeting-summary-bot/meeting-recording-test-files/test-meeting.wav','cse-ai-hackathon-meeting-summary-bot/meeting-recording-test-files/test-meeting-transcript.txt')