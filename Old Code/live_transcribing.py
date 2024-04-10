import sounddevice as sd
import wave
import tempfile
from openai import OpenAI
import threading
import time

OPENAI_API_KEY = open("OPENAI_API_KEY", "r").read()
client = OpenAI(api_key=OPENAI_API_KEY)
# Set your OpenAI API key

def transcribe_audio_chunk(filename):
    with open(filename, "rb") as audio_file:
        # Adding a delay before making a request to OpenAI API
        time.sleep(1.2)
        response = client.audio.transcribe(model="whisper-1", file=audio_file, response_format="text", language="english")
        transcript = response.choices[0].text
        print(transcript)

def audio_callback(indata, frames, time, status):
    # Writing the audio data to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        with wave.open(temp_wav.name, 'wb') as wf:
            wf.setnchannels(1)
            # Get the sample width from the audio data's dtype
            sample_width = indata.dtype.itemsize
            # Obtain the samplerate of the input device
            samplerate = sd.query_devices(kind='input')['default_samplerate']
            wf.setsampwidth(sample_width)
            wf.setframerate(samplerate)  # Set the samplerate
            wf.writeframes(indata.tobytes())
        # Creating a new thread to send the audio chunk for transcription
        threading.Thread(target=transcribe_audio_chunk, args=(temp_wav.name,)).start()


# Set up the audio stream
with sd.InputStream(callback=audio_callback):
    print("Press Ctrl+C to stop")
    sd.sleep(1000000)  # Keep the stream alive
