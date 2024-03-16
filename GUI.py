import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import soundfile as sf
import os
import threading
import argparse
import predict

class InstrumentRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Instrument Recognition App")
        
        self.master.configure(bg='black')
        
        button_color = 'red'
        button_text_color = 'white'

        self.record_button = tk.Button(master, text="Record", command=self.record, bg=button_color, fg=button_text_color, width=10)
        self.record_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="STOP", command=self.stop_recording, state=tk.DISABLED, bg=button_color, fg=button_text_color, width=10)
        self.stop_button.pack(pady=10)

        self.play_button = tk.Button(master, text="Play", command=self.play_audio, state=tk.DISABLED, bg=button_color, fg=button_text_color, width=10)
        self.play_button.pack(pady=10)

        self.check_button = tk.Button(master, text="Check", command=self.check_instrument, bg=button_color, fg=button_text_color, width=10)
        self.check_button.pack(pady=10)

        self.progressbar = ttk.Progressbar(master, mode="indeterminate", length=300)
        self.progressbar.pack(pady=10)

        self.recording_thread = None
        self.play_thread = None

    def record(self):
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)
        self.check_button.config(state=tk.DISABLED)

        self.progressbar.start()

        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()

    def record_audio(self):
        duration = 10
        fs = 44100
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()

        filename = "audios/sample.wav"
        sf.write(filename, recording, fs)

        self.progressbar.stop()
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        self.check_button.config(state=tk.NORMAL)

    def stop_recording(self):
        sd.stop()

    def play_audio(self):
        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progressbar.start()

        self.play_thread = threading.Thread(target=self.play_audio_thread)
        self.play_thread.start()

    def play_audio_thread(self):
        filename = "audios/sample.wav"
        try:
            data, fs = sf.read(filename, dtype='int16')
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while playing audio: {str(e)}")
        finally:
            self.progressbar.stop()
            self.stop_button.config(state=tk.DISABLED)
            self.play_button.config(state=tk.NORMAL)

    def check_instrument(self):
     try:
         self.progressbar.start()

         args = argparse.Namespace(model_fn='models/lstm.h5',
                                 pred_fn='y_pred',
                                 src_dir='wavfiles',
                                 dt=1.0,
                                 sr=16000,
                                 threshold=20)

         results = predict.make_prediction_sample(args)

         if not results:
             messagebox.showinfo("Instrument Recognition", "No instrument detected.")
         else:
             messagebox.showinfo("Instrument Recognition", f"Detected: {results[0][1]}")

     except Exception as e:
         messagebox.showerror("Error", f"An error occurred: {str(e)}")

     finally:
         self.progressbar.stop()

if __name__ == "__main__":
    root = tk.Tk()
    
    app = InstrumentRecognitionApp(root)
    root.mainloop()
