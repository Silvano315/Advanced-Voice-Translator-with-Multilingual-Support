import speech_recognition as sr
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import wave
import io
from pydub import AudioSegment
from pydub.silence import split_on_silence
import numpy as np

def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Parla ora...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    return audio

def speech_to_text(audio):
    recognizer = sr.Recognizer()
    try:
        text = recognizer.recognize_google(audio, language = "it-IT")
        return text
    except sr.UnknownValueError:
        print("Non ho capito l'audio")
    except sr.RequestError:
        print("Errore nel servizio di riconosciemento vocale")

def remove_silence(audio):
    wav_io = io.BytesIO(audio.get_wav_data())
    with wave.open(wav_io, 'rb') as wav_file:
        params = wav_file.getparams()
        frames = wav_file.readframes(wav_file.getnframes())
    
    audio_segment = AudioSegment(
        data=frames,
        sample_width=params.sampwidth,
        frame_rate=params.framerate,
        channels=params.nchannels
    )
    
    chunks = split_on_silence(audio_segment, min_silence_len=500, silence_thresh=-40)
    output_audio = sum(chunks, AudioSegment.silent(duration=1000))
    wav_io = io.BytesIO()
    output_audio.export(wav_io, format="wav")
    wav_io.seek(0)
    with wave.open(wav_io, 'rb') as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
        sample_rate = wav_file.getframerate()
        sample_width = wav_file.getsampwidth()
    
    return sr.AudioData(frames, sample_rate, sample_width)

def translate_text(text):

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-it-en").to(device)
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-it-en")
    translator = pipeline("translation", model = model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)
    translation = translator(text)[0]["translation_text"]
    return translation

def main():
    while True:
        audio = record_audio()
        audio = remove_silence(audio)
        italian_text = speech_to_text(audio)
        if italian_text:
            print(f"Testo italiano: {italian_text}")
            english_text = translate_text(italian_text)
            print(f"Traduzione inglese: {english_text}")

        next_audio = input("Vuoi continuare? (y/n): ")
        if next_audio.lower() != 'y':
            break


if __name__ == "__main__":
    main()