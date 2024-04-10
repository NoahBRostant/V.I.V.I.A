import os
import pvleopard as pvleopard
import pvporcupine
import pyaudio
import struct
import wave
from openai import AsyncOpenAI
import requests
import subprocess
from colorama import Fore
import asyncio
import aiohttp

# Set your OpenAI API key here
OPENAI_API_KEY = open("OPENAI_API_KEY", "r").read()
ELABS_API_KEY = open("ELEVENLABS_API_KEY", "r").read()
PICO_API_KEY = open("PICOVOICE_API_KEY", "r").read()

aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Initialize the OpenAI API client

path = "vivia_en_linux_v3_0_0.ppn"

porcupine = pvporcupine.create(
    access_key=PICO_API_KEY,
    keywords=["jarvis"]
)

leopard = pvleopard.create(access_key=PICO_API_KEY)

# Initialize PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length * 2,
)

async def record_audio(filename, duration):
    frames = []

    for _ in range(0, int(porcupine.sample_rate / porcupine.frame_length * duration)):
        audio_data = stream.read(porcupine.frame_length, exception_on_overflow=False)
        audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_data)
        frames.append(audio_data)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(porcupine.sample_rate)
        wf.writeframes(b''.join(frames))

# Main loop
async def main():
    print("Listening for keywords...")
    try:
        while True:
            # Read audio data from the microphone
            audio_data = stream.read(porcupine.frame_length, exception_on_overflow=False)
            audio_frame = struct.unpack_from("h" * porcupine.frame_length, audio_data)

            # Process audio frame with Porcupine
            print(Fore.BLUE+"Test1"+Fore.RESET)
            keyword_index = porcupine.process(audio_frame)
            print(Fore.BLUE+"Test2"+Fore.RESET)

            if keyword_index == 0:
                print("Keyword detected! Recording speech...")

                # Record speech for a fixed duration
                duration_seconds = 5
                audio_file = "recorded_audio.wav"
                await record_audio(audio_file, duration_seconds)

                # Transcribe the recorded speech using Leopard
                print("Transcribing speech...")
                transcript, words = leopard.process_file(os.path.abspath(audio_file))
                print("Transcript:", transcript)
                assistant_response = ""
                await openai_response(transcript)
                await elabs_response(assistant_response, audio_file)
    finally:
        # Clean up resources
        stream.stop_stream()
        stream.close()
        audio.terminate()
        porcupine.delete()

async def openai_response(transcript):
    response = await aclient.chat.completions.create(model="gpt-4",
    messages=[{"role": "assistant", "content": ("Formulate a very short reply for the question. Here is the question:"+transcript)}],
    
    temperature=0.6)

    print(response.choices[0].message.content)
    assistant_response = response['choices'][0]['message']['content']
    return(assistant_response)

async def elabs_response(assistant_response, audio_file):
    # This pretty line of the code reads openAI response
    url = 'https://api.elevenlabs.io/v1/text-to-speech/7WZyACZgyqPMlQ0PMrze/stream'
    headers = {
        'accept': '*/*',
        'xi-api-key': ELABS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'text': assistant_response.strip(),
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style_exaggeration": 0.0
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()
            ffplay_proc = await asyncio.create_subprocess_exec(
                'ffplay', '-',
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print("ffplay process started.")
            try:
                async for chunk in response.content.iter_chunked(8192):
                    print(f"Received chunk of size: {len(chunk)}")
                    ffplay_proc.stdin.write(chunk)
                    await ffplay_proc.stdin.drain()
            except Exception as e:
                print(f"An error occurred while streaming audio: {e}")
            finally:
                # Close the stdin to let ffplay know there is no more data coming
                ffplay_proc.stdin.close()
                # Wait for ffplay to finish processing
                output, errors = await ffplay_proc.communicate()
                print(f"ffplay output: {output.decode()}")
                print(f"ffplay errors: {errors.decode()}")
                print("Finished streaming, closing ffplay.")
                ffplay_proc.stdin.close()
                await ffplay_proc.wait()

    # Remove the audio file if you don't need it
    os.remove(audio_file)

if __name__ == "__main__":
    asyncio.run(main())