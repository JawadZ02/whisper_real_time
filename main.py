import customtkinter
import subprocess
from threading import Thread
from threading import Event
import queue
import time

runningProcess = None

def enqueue_output(out, err, queue):
    try:
        for line in iter(out.readline, b''):
            queue.put(line)
    except Exception as e:
        print(f"Error reading from stdout: {e}")
    finally:
        try:
            out.close()
        except Exception as e:
            print(f"Error closing stdout: {e}")

    #out.close()
    #runningProcess.wait()

def update_text_en(output_queue): # runningProcess argument removed
    '''
    # Read the output of the process line by line
    while True:
        output_line = runningProcess.stdout.readline()
        if output_line == '' and runningProcess.poll() is not None:
            break  # No more output and the process has finished

        # Insert the new line into the Text widget
        transcriptionBox.insert('end', ' ' + output_line)

        # Scroll to the bottom to show the latest output
        transcriptionBox.yview('end')

        # Allow Tkinter to update the window
        root.update()

    # Optionally, wait for the process to complete and get any remaining output
    remaining_output, _ = runningProcess.communicate()
    if remaining_output:
        transcriptionBox.insert('end', ' ' + remaining_output)
    '''
    while not stop_flag.is_set():
        try:
            output_line = output_queue.get_nowait()
        except queue.Empty:
            # Queue is empty, sleep for a short time to avoid busy waiting
            time.sleep(0.01)
            continue

        if runningProcess.poll() is not None:
            break  # The process has finished

        # Insert the new line into the Text widget
        transcriptionBox.insert('end', ' ' + output_line)

        # Scroll to the bottom to show the latest output
        transcriptionBox.yview('end')

        # Allow Tkinter to update the window
        root.update()

    # Optionally, wait for the process to complete and get any remaining output
    remaining_output, _ = runningProcess.communicate()
    if remaining_output:
        transcriptionBox.insert('end', ' ' + remaining_output)

def update_text_ar(runningProcess):
    # Read the output of the process line by line
    while True:
        output_line = runningProcess.stdout.readline()
        if output_line == '' and runningProcess.poll() is not None:
            break  # No more output and the process has finished

        # Insert the new line into the Text widget
        transcriptionBox.insert(1.0, ' ' + ' '.join(reversed(output_line.split(' '))))

        # Scroll to the bottom to show the latest output
        transcriptionBox.yview('end')

        # Allow Tkinter to update the window
        root.update()

    # Optionally, wait for the process to complete and get any remaining output
    remaining_output, _ = runningProcess.communicate()
    if remaining_output:
        transcriptionBox.insert(1.0, ' ' + ' '.join(reversed(remaining_output.split(' '))))

# Use a flag to signal the update thread to stop when the process is terminated
stop_flag = Event()

def runEnglishTranscription():
    buttonEng.configure(border_width=1)
    buttonAr.configure(state='disabled')
    global runningProcess
    runningProcess = subprocess.Popen(
        ["python", "transcribe_demo.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered, so we can read output line by line
        universal_newlines=True  # Ensure newline conversion
    )

    #output_line = runningProcess.stdout.readline()
    #print(output_line)
    #Thread(target=update_text_en, args=(runningProcess,), daemon=True).start()

    # Use a queue to communicate between threads
    output_queue = queue.Queue()

    # Start the thread to read and update the text periodically
    Thread(target=enqueue_output, args=(runningProcess.stdout, runningProcess.stderr, output_queue), daemon=True).start()

    # Start the thread to periodically check the queue and update the text widget
    Thread(target=update_text_en, args=(output_queue,), daemon=True).start()

def runArabicTranscription():
    buttonAr.configure(border_width=1)
    buttonEng.configure(state='disabled')
    global runningProcess
    runningProcess = subprocess.Popen(
        ["python", "transcribe_demo.py", "--non_english", "--model", "small"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered, so we can read output line by line
        universal_newlines=True  # Ensure newline conversion
    )

    #Thread(target=update_text_ar, args=(runningProcess,), daemon=True).start()

def endProcess():
    global runningProcess
    if runningProcess is not None:
        stop_flag.set()
        runningProcess.terminate()
        runningProcess.wait()
        runningProcess = None
        print('\nStopped listening.')
        buttonEng.configure(state='normal')
        buttonAr.configure(state='normal')
        buttonEng.configure(border_width=0)
        buttonAr.configure(border_width=0)
        transcriptionBox.delete(1.0, 'end')
    else:
        print('Transcription already stopped.')

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

buttonStop = customtkinter.CTkButton(master=frame, text='Stop transcription', command=endProcess)
buttonStop.pack(pady=10, padx=10)

transcriptionBox = customtkinter.CTkTextbox(master=frame)
transcriptionBox.pack(pady=10, padx=10, fill = 'both')

'''
transcriptionBox.insert(1.0, ' ' + ' '.join(reversed('السلام عليكم'.split(' '))))
transcriptionBox.insert(1.0, ' ' + ' '.join(reversed('كيف الحال'.split(' '))))
transcriptionBox.insert(1.0, ' ' + ' '.join(reversed('انا اسمي احمد'.split(' '))))
'''

if __name__ == '__main__':
    root.mainloop()