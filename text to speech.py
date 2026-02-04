import tkinter as tk
from tkinter import ttk
import pyttsx3
import speech_recognition as sr
import threading

# =========================
# SPEECH-TO-TEXT LANGUAGES
# =========================
STT_LANGUAGES = {
    "English (US)": "en-US",
    "English (India)": "en-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Tamil": "ta-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Bengali": "bn-IN",
    "Urdu": "ur-IN",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Chinese (Mandarin)": "zh-CN",
    "Arabic": "ar-SA",
    "Russian": "ru-RU"
}

speaking = False

# =========================
# LOAD TTS VOICES
# =========================
engine = pyttsx3.init()
voices = engine.getProperty('voices')

TTS_VOICES = {}
for voice in voices:
    name = voice.name
    TTS_VOICES[name] = voice.id

# =========================
# TEXT TO SPEECH
# =========================
def speak_text():
    global speaking

    text = text_entry.get("1.0", tk.END).strip()
    if not text:
        status_label.config(text="Status: No text to speak.")
        return

    def run():
        global speaking
        speaking = True

        tts_engine = pyttsx3.init()
        selected_voice = tts_voice_var.get()

        if selected_voice in TTS_VOICES:
            tts_engine.setProperty('voice', TTS_VOICES[selected_voice])

        tts_engine.setProperty('rate', 150)
        tts_engine.setProperty('volume', 0.9)

        tts_engine.say(text)
        tts_engine.runAndWait()

        speaking = False
        status_label.config(text="Status: Finished speaking.")
        speak_button.config(state="normal")
        stop_button.config(state="disabled")

    status_label.config(text="Status: Speaking...")
    speak_button.config(state="disabled")
    stop_button.config(state="normal")

    threading.Thread(target=run, daemon=True).start()

# =========================
# STOP SPEAKING
# =========================
def stop_speaking():
    global speaking
    speaking = False
    try:
        pyttsx3.init().stop()
    except:
        pass

    status_label.config(text="Status: Stopped speaking.")
    speak_button.config(state="normal")
    stop_button.config(state="disabled")

# =========================
# SPEECH TO TEXT
# =========================
def listen_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        status_label.config(text="Status: Listening...")
        listen_button.config(state="disabled")
        root.update()

        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            status_label.config(text="Status: Recognizing...")
            root.update()

            lang_code = STT_LANGUAGES.get(stt_lang_var.get(), "en-US")
            text = recognizer.recognize_google(audio, language=lang_code)

            text_entry.delete("1.0", tk.END)
            text_entry.insert("1.0", text)

            status_label.config(text="Status: Speech recognized.")

        except sr.WaitTimeoutError:
            status_label.config(text="Status: No speech detected.")
        except sr.UnknownValueError:
            status_label.config(text="Status: Could not understand speech.")
        except sr.RequestError:
            status_label.config(text="Status: Network error.")
        finally:
            listen_button.config(state="normal")

# =========================
# CLOSE APP
# =========================
def on_closing():
    try:
        pyttsx3.init().stop()
    except:
        pass
    root.destroy()

# =========================
# GUI
# =========================
root = tk.Tk()
root.title("Text ↔ Speech Converter")
root.geometry("540x720")
root.configure(padx=20, pady=20)

tk.Label(root, text="Text to Speech & Speech to Text",
         font=("Helvetica", 16, "bold")).pack(pady=15)

# Text box
tk.Label(root, text="Enter text:", font=("Helvetica", 12)).pack(anchor="w")
text_entry = tk.Text(root, height=8, width=52, wrap="word", font=("Helvetica", 11))
text_entry.pack(pady=10)

# =========================
# TTS LANGUAGE (VOICE)
# =========================
tk.Label(root, text="Text to Speech Voice:", font=("Helvetica", 12)).pack(anchor="w")

tts_voice_var = tk.StringVar(value=list(TTS_VOICES.keys())[0])
tts_dropdown = ttk.Combobox(
    root,
    textvariable=tts_voice_var,
    values=list(TTS_VOICES.keys()),
    state="readonly",
    width=40
)
tts_dropdown.pack(pady=5)

# =========================
# STT LANGUAGE
# =========================
tk.Label(root, text="Speech to Text Language:", font=("Helvetica", 12)).pack(anchor="w")

stt_lang_var = tk.StringVar(value="English (US)")
stt_dropdown = ttk.Combobox(
    root,
    textvariable=stt_lang_var,
    values=list(STT_LANGUAGES.keys()),
    state="readonly",
    width=30
)
stt_dropdown.pack(pady=5)

# Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=15)

speak_button = ttk.Button(btn_frame, text="🔊 Speak Text", command=speak_text)
speak_button.grid(row=0, column=0, padx=10)

stop_button = ttk.Button(btn_frame, text="⏹ Stop", command=stop_speaking)
stop_button.grid(row=0, column=1, padx=10)
stop_button.config(state="disabled")

listen_button = ttk.Button(
    root,
    text="🎤 Speech to Text (Listen)",
    command=lambda: threading.Thread(target=listen_speech, daemon=True).start()
)
listen_button.pack(pady=20)

status_label = tk.Label(root, text="Status: Ready", fg="blue")
status_label.pack(pady=10)

tk.Label(
    root,
    text="• STT uses Google (Internet required)\n"
         "• TTS voices depend on system installed voices\n"
         "• Select correct language for best accuracy",
    font=("Helvetica", 9),
    fg="gray",
    justify="left"
).pack(pady=20)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
