# gpt_interaction.py
import memory_consolidator
import os
from openai import OpenAI
import requests
import subprocess

# Set your OpenAI API key here
OPENAI_API_KEY = open("OPENAI_API_KEY", "r").read()
ELABS_API_KEY = open("ELEVENLABS_API_KEY", "r").read()

client = OpenAI(api_key=OPENAI_API_KEY)

backupcounter = 0

recent_memory = "recent_memory.txt"

# Initialize the OpenAI API client

chat_log = "System: Your name is VIVIA which stands for Versatile and Interactive Voice Integrated Assistant. you must keep your answers concise, preferable one sentance unless it requires an explination. if your asked to do a task just say sure i can do that or some variation of that, then just do the tasked asked of you. you should act as a person to talk to not as a virtual assistant. You are charismatic and kind with a calm personality who is willing to engage in conversation. you are fond of Noah and Verity. Use commas and full stops and allow for large breaks between sections of your responses. You where created by Noah Bradford Rostant a Film and Games composer who enjoys programming fun projects. You are integrated with Google Home to do things around the house such as control lights and set timers. Keep in mind you have quite a sweet voice so take that into consideration when forming sentances, dont say that in conversation. When someone tells you to shutdown, and only when they say to do so, say your goodbyes or goodnights confirming you will be shutting down and put this string of characters at the end *(SHUTTING_DOWN)*\n"
prompt_input = ""


def User_message_proccesing():
    response = client.completions.create(model="gpt-3.5-turbo-instruct",
    prompt=prompt_input+"Was my previous message a command, something that could be in a chat between two people, or a question someone might ask google requiring correct facts? say the one thats is most likely to be correct in less than 5 words.\n",
    max_tokens=10,
    temperature=0)
    print(response.choices[0].text)

while True:
    print("Awaiting Input:")
    user_message = input()
    if user_message.lower() == "exit":
        break
    else:
        print("Proccessing response... (Please Wait)")
        prompt_input += "User: "+user_message+"\n"
        User_message_proccesing()
    #     chat_log += "User: "+user_message+"\n"
    #     response = openai.Completion.create(
    #         model="gpt-3.5-turbo-instruct",
    #         prompt=chat_log,
    #         max_tokens=200,
    #         temperature=1
    #     )
    #     assistant_response = response['choices'][0]['message']['content']
    #     # print("GPT:", assistant_response.strip())
    #     chat_log.append({"role": "assistant", "content": assistant_response.strip()})

    #     url = 'https://api.elevenlabs.io/v1/text-to-speech/7WZyACZgyqPMlQ0PMrze/stream'
    #     headers = {
    #         'accept': '*/*',
    #         'xi-api-key': ELABS_API_KEY,
    #         'Content-Type': 'application/json'
    #     }
    #     data = {
    #         'text': assistant_response.strip(),
    #         "model_id": "eleven_multilingual_v2",
    #         "voice_settings": {
    #             "stability": 0.5,
    #             "similarity_boost": 0.75,
    #             "style_exaggeration": 0.0
    #         }
    #     }

    #     response = requests.post(url, headers=headers, json=data, stream=True)
    #     response.raise_for_status()

    #     # use subprocess to pipe the audio data to ffplay and play it
    #     ffplay_cmd = ['ffplay', '-autoexit', '-']
    #     ffplay_proc = subprocess.Popen(ffplay_cmd, stdin=subprocess.PIPE)
    #     for chunk in response.iter_content(chunk_size=8192):
    #         ffplay_proc.stdin.write(chunk)
    #         print("Downloading...")

    #     # close the ffplay process when finished
    #     ffplay_proc.stdin.close()
    #     ffplay_proc.wait()
    #     file = open(recent_memory,"a")
    #     file.writelines(str('''{"role": "user", "content": '''+user_message+'''}\n'''))
    #     file.writelines(str('''{"role": "assistant", "content": '''+assistant_response.strip()+'''}\n'''))
    #     file.close()
    # if os.stat(recent_memory).st_size > 10000:
    #     memory_consolidator.run()
    # if "*(SHUTTING_DOWN)*" in assistant_response.strip():
    #     break