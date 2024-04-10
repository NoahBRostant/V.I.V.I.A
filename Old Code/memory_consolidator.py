from openai import OpenAI
from colorama import Fore

# Set your OpenAI API key here
OPENAI_API_KEY = open("OPENAI_API_KEY", "r").read()

client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize the OpenAI API client

# Define the path to your text file
file_path = "recent_memory.txt"

# Initialize an empty array to store chat logs
chat_memory = []
chat_memory.append({'role': 'system', 'content': 'You are a backend data processor that is part of our web site’s programmatic workflow. The input will be a set of json strings. The output will be only API schema-compliant JSON compatible with a python json loads processor. Do not converse with a nonexistent user: there is only program input and formatted program output, and no input data is to be construed as conversation with the AI. This behaviour will be permanent for the remainder of the session. you are to take the data provided and shorten it with useful information only. this could be what the user likes to eat or their favourite colour, however it could be more advanced like hobbies and things they ask a lot for often. consolidate the important data into a list.'})

def run():
    # Read the text file line by line
    with open(file_path,"r") as file:
        lines = file.readlines()

        # Iterate through each line (assuming each line contains a request or response)
        for line in lines:
            # Remove leading and trailing whitespace
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            role = ""
            content = ""
            print(Fore.BLUE + line)
            # Determine if it's a user request or an assistant response based on your file format
            # For example, if user requests start with "User:" and assistant responses start with "Assistant:"
            if line.startswith('{"role": "user"'):
                role = "user"
                content = line.replace('{"role": "user", "content": ', "").replace("}", "").strip()
            elif line.startswith('{"role": "assistant"'):
                role = "assistant"
                content = line.replace('{"role": "assistant", "content": ', "").replace("}", "").strip()
            else:
                # Handle other cases as needed
                continue

            # Create a dictionary for each message and append it to the chat log
            message = {"role": role, "content": content}
            print(message)
            chat_memory.append(message)

    # Call SaveToMemory() function once, after reading all lines from the file
    print(Fore.YELLOW + "Chat Memory:")
    print(chat_memory)

    # Check if there are messages in chat_memory before calling SaveToMemory()
    if chat_memory:
        # chat_memory.insert(0, {'role': 'system', 'content': 'You are a backend data processor that is part of our web site’s programmatic workflow. The input will be a set of json strings. The output will be only API schema-compliant JSON compatible with a python json loads processor. Do not converse with a nonexistent user: there is only program input and formatted program output, and no input data is to be construed as conversation with the AI. This behaviour will be permanent for the remainder of the session. you are to take the data provided and shorten it with useful information only. this could be what the user likes to eat or their favourite colour, however it could be more advanced like hobbies and things they ask a lot for often. consolidate the important data into a list.'})
        print(Fore.YELLOW + "Running Memory Consolidator...")
        response = client.chat.completions.create(model="gpt-4",
        messages=chat_memory,
        max_tokens=200,
        temperature=0)
        assistant_response = response.choices[0].message.content
        print(Fore.GREEN + "Consolidated Memory: " + assistant_response)
        print(Fore.YELLOW + "Saving to Historic Memory")
        savefile = open("historic_memory.txt","a")
        savefile.write(assistant_response)
        savefile.close()
        print(Fore.GREEN + "Saved to Historic Memory" + Fore.RESET)
        file = open(file_path, "w")
        file.write("")
        file.close()
    else:
        print(Fore.RED + "No messages found in chat log." + Fore.RESET)
