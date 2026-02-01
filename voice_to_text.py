import tkinter as tk
import sounddevice as sd
import numpy as np
import soundfile as sf
import speech_recognition as sr
import threading
from datetime import datetime
import os

# ================= CONFIG =================
FS = 44100

BASE_DIR = os.getcwd()
AUDIO_DIR = os.path.join(BASE_DIR, "audio_files")
TEXT_DIR = os.path.join(BASE_DIR, "text_records")

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

recording = False
audio_chunks = []

# ================= RECORDING =================
def start_recording():
    global recording, audio_chunks
    recording = True
    audio_chunks = []
    status_label.config(text="🎤 Recording...")
    threading.Thread(target=record_audio).start()

def stop_recording():
    global recording
    recording = False
    status_label.config(text="⏹️ Processing...")
    threading.Thread(target=save_and_process).start()

def record_audio():
    with sd.InputStream(samplerate=FS, channels=1, callback=audio_callback):
        while recording:
            sd.sleep(100)

def audio_callback(indata, frames, time, status):
    audio_chunks.append(indata.copy())

# ================= SAVE & PROCESS =================
def save_and_process():
    if not audio_chunks:
        status_label.config(text="❌ No audio recorded")
        return

    audio = np.concatenate(audio_chunks, axis=0)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # ---- SAVE AUDIO ----
    audio_name = f"audio_{timestamp}.wav"
    audio_path = os.path.join(AUDIO_DIR, audio_name)
    sf.write(audio_path, audio, FS)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        recognized_text = recognizer.recognize_google(audio_data)
    except:
        recognized_text = "Speech could not be recognized."

    # ---- CREATE CLICKABLE LINK (IMPORTANT) ----
    audio_link = "file:///" + audio_path.replace("\\", "/").replace(" ", "%20")

    # 🔎 PRINT LINK TO TERMINAL (FOR VERIFICATION)
    print("AUDIO LINK:", audio_link)

    # ---- SAVE TXT FILE ----
    text_name = f"record_{timestamp}.txt"
    text_path = os.path.join(TEXT_DIR, text_name)

    with open(text_path, "w", encoding="utf-8") as f:
        f.write("===== VOICE RECORD =====\n\n")
        f.write(f"Timestamp:\n{timestamp}\n\n")
        f.write("AUDIO LINK (COPY / CTRL+CLICK IN VS CODE):\n")
        f.write(audio_link + "\n\n")
        f.write("RECOGNIZED TEXT:\n")
        f.write(recognized_text)

    result_label.config(text="📝 " + recognized_text)
    status_label.config(text="✅ Saved (Check TXT file)")

# ================= GUI =================
root = tk.Tk()
root.title("Voice to Text Logger")
root.geometry("540x380")

tk.Label(root, text="Voice to Text (Link Logger)", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="▶ START", width=22, command=start_recording).pack(pady=5)
tk.Button(root, text="⏹ STOP", width=22, command=stop_recording).pack(pady=5)

status_label = tk.Label(root, text="Idle")
status_label.pack(pady=10)

result_label = tk.Label(root, text="", wraplength=500)
result_label.pack(pady=10)

root.mainloop()
