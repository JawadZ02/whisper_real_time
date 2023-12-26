import customtkinter
from threading import Thread
from threading import Event
import sys
from transcription2 import transcription

stop_event = Event()

def stopTranscription():
    stop_event.set()
    buttonEng.configure(state='normal')
    buttonAr.configure(state='normal')
    buttonEng.configure(border_width=0)
    buttonAr.configure(border_width=0)

def runEnglishTranscription():
    Thread(target=t.transcribe, daemon=True).start()
    buttonEng.configure(border_width=1)
    buttonEng.configure(state='disabled')
    buttonAr.configure(state='disabled')

def runArabicTranscription():
    Thread(target=lambda:t.transcribe('base', True), daemon=True).start()
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

t = transcription(transcriptionBox, stop_event)

if __name__ == '__main__':
    root.mainloop()