# GUI implementation with Kivi

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from threading import Thread
from threading import Event
import sys
from transcription_kivy import transcription


class transcriptionApp(App):
    def build(self):
        self.stop_event = Event()

        self.window = GridLayout()
        self.window.cols = 1
        #self.window.size_hint = (0.4, 0.8) # width of main frame is 40%, height 80%
        self.window.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.window.padding = (400, 150)
        self.window.spacing = 20

        self.label = Label(text='Select transcription language.')
        self.window.add_widget(self.label)

        self.buttonEng = Button(text='English', size_hint=(0.4,0.6))
        self.buttonEng.bind(on_press=self.runEnglishTranscription)
        self.window.add_widget(self.buttonEng)

        self.buttonAr = Button(text='Arabic', size_hint=(0.4,0.6))
        self.buttonAr.bind(on_press=self.runArabicTranscription)
        self.window.add_widget(self.buttonAr)

        self.buttonStop = Button(text='Stop transcription', size_hint=(0.8,0.6))
        self.buttonStop.bind(on_press=self.stopTranscription)
        self.window.add_widget(self.buttonStop)

        self.buttonExit = Button(text='Exit', size_hint=(0.8,0.6))
        self.buttonExit.bind(on_press=self.exitProgram)
        self.window.add_widget(self.buttonExit)

        self.transcriptionBox = TextInput(size_hint=(0.4,0.6), font_name='ARIAL.TTF')
        self.window.add_widget(self.transcriptionBox)

        self.t = transcription(self.stop_event, self)

        return self.window

    def stopTranscription(self, instance):
        self.stop_event.set()

    def runEnglishTranscription(self, instance):
        Thread(target=self.t.transcribe, daemon=True).start()

    def runArabicTranscription(self, instance):
        Thread(target=lambda:self.t.transcribe('base', True), daemon=True).start()
    
    def exitProgram(self, instance):
        self.stopTranscription(instance)
        #sys.exit()
        App.get_running_app().stop()

    def updateTranscriptionBox(self, text):
        self.transcriptionBox.text = text


if __name__ == '__main__':
    transcriptionApp().run()