#! python3.7

import argparse
import os
import numpy as np
import speech_recognition as sr
from faster_whisper import WhisperModel
from correction import TextCorrection
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform
from threading import Thread
from threading import Event


def main(model_size='base', non_english=False, energy_threshold=500, record_timeout=4, phrase_timeout=3):

    transcriptionBox.delete(1.0, 'end')
    transcriptionBox.insert('end', 'Loading...\n')

    if 'linux' in platform:
        default_microphone = 'pulse'
        
    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    # Important for linux users.
    # Prevents permanent application hang and crash by using the wrong Microphone
    if 'linux' in platform:
        mic_name = default_microphone
        if not mic_name or mic_name == 'list':
            #print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                #print(f"Microphone with name \"{name}\" found")
                pass
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    # Load / Download model
    model = model_size
    if model_size != "large" and not non_english:
        model = model + ".en"
    audio_model = WhisperModel(model, device="cpu", compute_type="int8")

    # Create text correction instance for (arabic) spell check
    #tc = TextCorrection()

    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    stop_listening = recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    #print("Listening...\n")
    transcriptionBox.delete(1.0, 'end')
    transcriptionBox.insert('end', "Listening...")

    while not stop_event.is_set():
        
        now = datetime.utcnow()
        # Pull raw recorded audio from the queue.
        if not data_queue.empty():
            
            phrase_complete = False
            # If enough time has passed between recordings, consider the phrase complete.
            # Clear the current working audio buffer to start over with the new data.
            if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                phrase_complete = True
            # This is the last time we received new audio data from the queue.
            phrase_time = now
            
            # Combine audio data from queue
            audio_data = b''.join(data_queue.queue)
            data_queue.queue.clear()
            
            # Convert in-ram buffer to something the model can use directly without needing a temp file.
            # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
            # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Read the transcription.
            if non_english:
                _language = 'ar'
            else:
                _language = 'en'

            result, info = audio_model.transcribe(audio_np, vad_filter=True, language=_language)
            text = ''
            for segment in result:
                text += segment.text

            # proofread arabic to eliminate spelling errors to improve accuracy
            '''
            original_text = text
            if _language == 'ar':
                words = text.split()
                corrected_words = []
                for word in words:
                    corrected_word = tc.correction(word)[0]
                    corrected_words.append(word)
                text = ' '.join(corrected_words)
            print('original:', original_text)
            print('corrected:', text)
            '''

            # If we detected a pause between recordings, add a new item to our transcription.
            # Otherwise edit the existing one.
                       
            if phrase_complete:
                transcription.append(text)
            else:
                transcription[-1] = text
            
            # Clear the console to reprint the updated transcription.
            #os.system('cls' if os.name=='nt' else 'clear')
            transcriptionBox.delete(1.0, 'end')
            for line in transcription:
                if line != '':
                    #print(line)
                    if _language == 'en':
                        transcriptionBox.insert('end', line + '\n')
                    elif _language == 'ar':
                        transcriptionBox.insert('end', ' '.join(reversed(line.split(' '))) + '\n')
            transcriptionBox.yview('end')
            # Flush stdout.
            #print('', end='', flush=True)
            
            # Infinite loops are bad for processors, must sleep.
            sleep(0.001)
    
    stop_listening(wait_for_stop=True)
    stop_event.clear()
    transcriptionBox.delete(1.0, 'end')
    transcriptionBox.insert('end', 'Stopped listening.')
    #print('\nStopped listening.')

#########################################################################################################

import customtkinter
from threading import Thread
from threading import Event
import sys

stop_event = Event()

def stopTranscription():
    stop_event.set()
    buttonEng.configure(state='normal')
    buttonAr.configure(state='normal')
    buttonEng.configure(border_width=0)
    buttonAr.configure(border_width=0)

def runEnglishTranscription():
    Thread(target=main, daemon=True).start()
    buttonEng.configure(border_width=1)
    buttonEng.configure(state='disabled')
    buttonAr.configure(state='disabled')

def runArabicTranscription():
    Thread(target=lambda:main('base', True), daemon=True).start()
    buttonAr.configure(border_width=1)
    buttonEng.configure(state='disabled')
    buttonAr.configure(state='disabled')

def exitProgram():
    stopTranscription()
    sys.exit()

customtkinter.set_appearance_mode('dark')
customtkinter.set_default_color_theme('dark-blue')
root = customtkinter.CTk()
root.geometry('500x350')

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill='both', expand=True)

label = customtkinter.CTkLabel(master=frame, text='Select transcription language.', font=('',20))
label.pack(pady=10, padx=10)

buttonEng = customtkinter.CTkButton(master=frame, text='English', command=runEnglishTranscription, border_color='red', border_width=0)
buttonEng.pack(pady=10, padx=10)

buttonAr = customtkinter.CTkButton(master=frame, text='Arabic', command=runArabicTranscription, border_color='red', border_width=0)
buttonAr.pack(pady=10, padx=10)

buttonStop = customtkinter.CTkButton(master=frame, text='Stop transcription', command=stopTranscription)
buttonStop.pack(pady=10, padx=10)

buttonExit = customtkinter.CTkButton(master=frame, text='Exit', command=exitProgram)
buttonExit.pack(pady=10, padx=10)

transcriptionBox = customtkinter.CTkTextbox(master=frame)
transcriptionBox.pack(pady=10, padx=10, fill = 'both')

if __name__ == '__main__':
    root.mainloop()