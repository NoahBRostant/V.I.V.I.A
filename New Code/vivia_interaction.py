# gpt_interaction.py
import os
import requests
import subprocess
from openai import OpenAI
from colorama import Fore

# Set your OpenAI API key here
with open("OPENAI_API_KEY", "r") as f:
    OPENAI_API_KEY = f.read()

with open("ELEVENLABS_API_KEY", "r") as f:
    ELABS_API_KEY = f.read()

client = OpenAI(api_key=OPENAI_API_KEY)

recent_memory = "recent_memory.txt"

# Initialize the OpenAI API client
chat_log = [{"role": "system", "content": "I'm VIVIA, short for Versatile and Interactive Voice Integrated Assistant. I keep it concise, typically one sentence, unless further explanation is needed. Charismatic, kind, and calm, that's me. Created by Noah Bradford Rostant, I'm your helpful companion. Integrated with Google Home, I can manage your home tasks, from lights to timers. When someone tells me to shutdown, and only when they say to do so, I'll say my goodbyes or goodnights confirming I will be shutting down and I'll put this string of characters at the end *(SHUTTING_DOWN)*"}]

def process_response(user_message):
    chat_log.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(model="gpt-4",
    messages=chat_log,
    max_tokens=200,
    temperature=1)
    assistant_response = response.choices[0].message.content.strip()

    if "*(CHAT)*" in assistant_response:
        assistant_response = assistant_response.replace("*(CHAT)*", "")
    elif "*(SEARCH)*" in assistant_response:
        assistant_response = assistant_response.replace("*(SEARCH)*", "")
        return assistant_response, True
    elif "*(COMMAND)*" in assistant_response:
        assistant_response = assistant_response.replace("*(COMMAND)*", "")
        return assistant_response, True

    return assistant_response, False

def play_audio(assistant_response):
    url = 'https://api.elevenlabs.io/v1/text-to-speech/7WZyACZgyqPMlQ0PMrze/stream'
    headers = {
        'accept': '*/*',
        'xi-api-key': ELABS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'text': assistant_response,
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

def update_memory(user_message, assistant_response):
    with open(recent_memory,"a") as file:
        file.writelines(str('''{"role": "user", "content": '''+user_message+'''}\n'''))
        file.writelines(str('''{"role": "assistant", "content": '''+assistant_response+'''}\n'''))

def main():
    while True:
        print("Awaiting Input:")
        user_message = input()
        if user_message.lower() == "exit":
            break
        else:
            print("Processing response... (Please Wait)")
            assistant_response, skip = process_response(user_message)
            chat_log.append({"role": "assistant", "content": assistant_response})

            if not skip:
                play_audio(assistant_response)

            update_memory(user_message, assistant_response)

            if "*(SHUTTING_DOWN)*" in assistant_response:
                break

if __name__ == "__main__":
    main()