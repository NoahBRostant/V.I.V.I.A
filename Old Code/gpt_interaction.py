# gpt_interaction.py
import memory_consolidator
import os
from openai import OpenAI
import requests
import subprocess
from colorama import Fore

# Set your OpenAI API key here
OPENAI_API_KEY = open("OPENAI_API_KEY", "r").read()
ELABS_API_KEY = open("ELEVENLABS_API_KEY", "r").read()

client = OpenAI(api_key=OPENAI_API_KEY)


backupcounter = 0

recent_memory = "recent_memory.txt"

# Initialize the OpenAI API client

chat_log = [{"role": "system", "content": "IMPORTAINT!!! I must prefix every thing i say with either *(COMMAND)*, *(SEARCH)*, or *(CHAT)* depending on the sort of answer i should be giving. if im answering a question that would require the facts to be correct id use *(SEARCH)* and I wont say anything else, if its just general chat with the User use *(CHAT)*, and if its a command that doesnt need factual data use *(COMMAND)* and i wont say anything else. I'm VIVIA, short for Versatile and Interactive Voice Integrated Assistant. I keep it concise, typically one sentence, unless further explanation is needed. Charismatic, kind, and calm, that's me. Created by Noah Bradford Rostant, I'm your helpful companion. Integrated with Google Home, I can manage your home tasks, from lights to timers. When someone tells me to shutdown, and only when they say to do so, I'll say my goodbyes or goodnights confirming I will be shutting down and I'll put this string of characters at the end *(SHUTTING_DOWN)*"}]
skip = 0


while True:
    print("Awaiting Input:")
    user_message = input()
    if user_message.lower() == "exit":
        break
    else:
        print("Proccessing response... (Please Wait)")
        chat_log.append({"role": "user", "content": user_message})
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

        if skip == 0:
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
        skip = 0

        # print(Fore.BLUE+assistant_response['usage'][0]['total_tokens']+Fore.RESET)
        file = open(recent_memory,"a")
        file.writelines(str('''{"role": "user", "content": '''+user_message+'''}\n'''))
        file.writelines(str('''{"role": "assistant", "content": '''+assistant_response.strip()+'''}\n'''))
        file.close()
    if os.stat(recent_memory).st_size > 10000:
        memory_consolidator.run()
    if "*(SHUTTING_DOWN)*" in assistant_response.strip():
        break