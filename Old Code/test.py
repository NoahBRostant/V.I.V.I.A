#! python3.7

import argparse
import io
import os
import speech_recognition as sr
import whisper
import torch

from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from sys import platform

import os
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
import requests
import subprocess
from colorama import Fore

import asyncio

# Set your OpenAI API key here
OPENAI_API_KEY = open("OPENAI_API_KEY", "r").read()
ELABS_API_KEY = open("ELEVENLABS_API_KEY", "r").read()

backupcounter = 0

recent_memory = "recent_memory.txt"

# Initialize the OpenAI API client

chat_log = [{"role": "system", "content": "IMPORTAINT!!! I must prefix every thing i say with either *(COMMAND)*, *(SEARCH)*, or *(CHAT)* depending on the sort of answer i should be giving. if im answering a question that would require the facts to be correct id use *(SEARCH)* and I wont say anything else, if its just general chat with the User use *(CHAT)*, and if its a command that doesnt need factual data use *(COMMAND)* and i wont say anything else. I'm VIVIA, short for Versatile and Interactive Voice Integrated Assistant. I keep it concise, typically one sentence, unless further explanation is needed. Charismatic, kind, and calm, that's me. Created by Noah Bradford Rostant, I'm your helpful companion. Integrated with Google Home, I can manage your home tasks, from lights to timers. When someone tells me to shutdown, and only when they say to do so, I'll say my goodbyes or goodnights confirming I will be shutting down and I'll put this string of characters at the end *(SHUTTING_DOWN)*"}]
skip = 0

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Current raw audio bytes.
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    # Important for linux users.
    # Prevents permanent application hang and crash by using the wrong Microphone
    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    # Load / Download model
    model = args.model
    if args.model != "base" and not args.non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    temp_file = NamedTemporaryFile().name
    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    print("Model loaded.\n")
    print(Fore.GREEN+"Speak now, or forever hold your piece: "+Fore.RESET)

    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes.
                with open(temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                # Read the transcription.
                result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise edit the existing one.
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                # Clear the console to reprint the updated transcription.
                brain = asyncio.create_task(brainnspeak(transcription))
                await brain
                # Flush stdout.
                print('', end='', flush=True)

                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            break

async def brainnspeak(transcription):
    buffer = []
    for line in transcription:
        buffer.append(line)
    print(Fore.BLUE+str(buffer)+Fore.RESET)
    if len(buffer) > 1:
        chat_log.append({"role": "user", "content": str(buffer[0]+buffer[1])})
        response = client.chat.completions.create(model="gpt-4",
        messages=chat_log,
        max_tokens=200,
        temperature=1)
        assistant_response = response.choices[0].message.content
        # print("GPT:", assistant_response.strip())

        if "*(CHAT)*" in assistant_response.strip():
            assistant_response = assistant_response.strip().replace("*(CHAT)*", "")
        elif "*(SEARCH)*" in assistant_response.strip():
            assistant_response = assistant_response.strip().replace("*(SEARCH)*", "")
            skip = 1
        elif "*(COMMAND)*" in assistant_response.strip():
            assistant_response = assistant_response.strip().replace("*(COMMAND)*", "")
            skip = 1


        chat_log.append({"role": "assistant", "content": assistant_response.strip()})

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

        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        # use subprocess to pipe the audio data to ffplay and play it
        ffplay_cmd = ['ffplay', '-autoexit', '-']
        ffplay_proc = subprocess.Popen(ffplay_cmd, stdin=subprocess.PIPE)
        for chunk in response.iter_content(chunk_size=8192):
            ffplay_proc.stdin.write(chunk)
            print("Downloading...")

        # close the ffplay process when finished
        ffplay_proc.stdin.close()
        ffplay_proc.wait()

        # print(Fore.BLUE+assistant_response['usage'][0]['total_tokens']+Fore.RESET)
        file = open(recent_memory,"a")
        file.writelines(str('''{"role": "user", "content": '''+str(transcription)+'''}\n'''))
        file.writelines(str('''{"role": "assistant", "content": '''+assistant_response.strip()+'''}\n'''))
        file.close()
        del buffer[0]
    else:
        pass

if __name__ == "__main__":
    asyncio.run(main())