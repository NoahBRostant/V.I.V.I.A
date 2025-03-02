<p align="center">
    <img src="https://github.com/NoahBRostant/V.I.V.I.A/blob/main/HiPaint_1713786816890.png?raw=true" align="center" width="150px">
</p>

## Overview
V.I.V.I.A (Versatile and Interactive Voice Integrated Assistant) is a project created to explore the potential of AI, particularly in building a virtual assistant. This leverages the advanced capabilities of OpenAI's GPT-4 and ElevenLabs’ Multilingual Voice v2 APIs, offering unique, multilingual interactions.

## Features
- **AI-Powered Conversations**: Engage with an assistant powered by the latest GPT-4 model for natural and informative interactions.
- **Multilingual Support**: Utilizes ElevenLabs’ Multilingual Voice v2 for seamless communication in multiple languages.
- **Custom Synthetic Voice**: Integration with ffmpeg to asynchronously generate speech, enhancing the user experience with a custom ElevenLabs synthetic voice.
- **Use Your Voices**: Using your own API keys, you can create and use your own voices for the AI Assistant.

---

### New Animated UI

![Screenshot From 2025-03-02 12-29-59](https://github.com/user-attachments/assets/5097696d-7e53-43d8-bff2-353dbb5cb7c5)



https://github.com/user-attachments/assets/1ef100bd-84e2-4ded-95dd-833ea135d83e



## Requirements
- Python 3 (built using 3.12)
- OpenAI API key
- ElevenLabs API key
- ffmpeg installed on your system

```
vivia/
│
├── vivia_interaction.py  # Main Python script
├── requirements/
│   └── requirements.txt  # Dependency list
├── OPENAI_API_KEY  # File containing the OpenAI API key
├── ELEVENLABS_API_KEY  # File containing the Eleven Labs API key
└── recent_memory.txt  # File to store session memory
```

## Installation
1. Clone the repository or download the project:
    - Ensure you have the complete folder structure as outlined above.
2. Install Python: If not already installed, [download and install Python](https://www.python.org/downloads/).
3. Set up a virtual environment (recommended):
    - Navigate to the project directory in your terminal.
    - Run `python -m venv venv` to create a virtual environment.
    - Activate the environment:
        - Windows: `venv\Scripts\activate`
        - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
    - Ensure you are in the project directory where the requirements folder is located.
    - `Run pip install -r requirements/requirements.txt` to install the required Python packages.

## Usage
1. API Keys:
    - You need to have valid API keys from OpenAI and Eleven Labs.
    - Place your OpenAI API key in a file named OPENAI_API_KEY and your Eleven Labs API key in ELEVENLABS_API_KEY.
2. Running the script:
    - In the terminal (ensure your virtual environment is activated if you're using one), navigate to the directory containing gpt_interaction.py.
    - Run the script with `python gpt_interaction.py`.
    - Follow the on-screen prompts to interact with the application.

## Contribution
Your contributions are welcome! If you have suggestions for improvements or have found bugs, please open an issue or submit a pull request.

## Acknowledgments
A special thank you to OpenAI and ElevenLabs for providing the APIs that made this project possible. This project was created for educational purposes to understand the workings and integration of AI in virtual assistants.

---


