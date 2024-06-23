import os
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from groq import Groq


def install_dependencies():
    os.system("pip install sounddevice pydub groq")


def record_audio(seconds):
    print("Recording audio...")
    fs = 44100  # Sample rate
    duration = seconds  # Duration in seconds
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")
    return recording, fs


def append_silence(recording, seconds_to_append, sample_rate):
    print(f"Appending {seconds_to_append} seconds of silence...")
    # Create a silence array with the same number of channels as the recording
    silence = np.zeros(
        (int(seconds_to_append * sample_rate), recording.shape[1]), dtype=np.int16
    )
    return np.concatenate((recording, silence))


def save_to_m4a(audio_data, sample_rate, filename):
    # Convert numpy array to AudioSegment
    audio = AudioSegment(
        audio_data.tobytes(),
        frame_rate=sample_rate,
        sample_width=audio_data.dtype.itemsize,
        channels=1,
    )

    # Export as M4A
    audio.export(filename, format="mp3")


def perform_transcription(filename):
    client = Groq(api_key="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")
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3",
            prompt="Specify context or spelling",  # Optional
            response_format="json",  # Optional
            language="en",  # Optional
            temperature=0.0,  # Optional
        )
    return transcription.text


def make_sample():
    # Record audio for 10 seconds
    audio_data, sample_rate = record_audio(10)
    # Append 20 seconds of silence to the recorded audio
    audio_data = append_silence(audio_data, 20, sample_rate)
    # Save the recorded audio to an M4A file
    filename = "./sample.m4a"
    save_to_m4a(audio_data, sample_rate, filename)
    print(f"Sample audio saved to {filename}")
    return filename


def main():
    filename = make_sample()
    # Perform transcription using Groq API
    transcription_text = perform_transcription(filename)
    print("Transcription Result:")
    print(transcription_text)


if __name__ == "__main__":
    main()
