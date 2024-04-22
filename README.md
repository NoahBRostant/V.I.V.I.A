# V.I.V.I.A

## Overview
V.I.V.I.A (Versatile and Interactive Voice Integrated Assistant) is a project created to explore the potential of AI, particularly in building a virtual assistant. This leverages the advanced capabilities of OpenAI's GPT-4 and ElevenLabs’ Multilingual Voice v2 APIs, offering unique, multilingual interactions.

## Features
- **AI-Powered Conversations**: Engage with an assistant powered by the latest GPT-4 model for natural and informative interactions.
- **Multilingual Support**: Utilizes ElevenLabs’ Multilingual Voice v2 for seamless communication in multiple languages.
- **Custom Synthetic Voice**: Integration with ffmpeg to asynchronously generate speech, enhancing the user experience with a custom ElevenLabs synthetic voice.

---

https://github.com/NoahBRostant/V.I.V.I.A/assets/77655703/b6926f77-ba5e-4db7-bf59-a8d5ad2a0495

## Requirements
- Python 3 (built using 3.12)
- OpenAI API key
- ElevenLabs API key
- ffmpeg installed on your system or environment (Recommended)

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
1. Clone the repository or download the project: 2. Ensure you have the complete folder structure as outlined above.
3. Install Python: If not already installed, download and install Python.
4. Set up a virtual environment (recommended):Navigate to the project directory in your terminal.
5. Run python -m venv venv to create a virtual environment.
6. Activate the environment:
- Windows: venv\Scripts\activate
- macOS/Linux: source venv/bin/activate
7. Install dependencies:
- Ensure you are in the project directory where the requirements folder is located.
8. Run pip install -r requirements/requirements.txt to install the required Python packages.

## Usage
To start V.I.V.I.A, run the main script from your (environment) terminal:
```
python "New_Code/vivia_interaction.py"
```
Follow the on-screen prompts to interact with your assistant.

## Contribution
Your contributions are welcome! If you have suggestions for improvements or have found bugs, please open an issue or submit a pull request.

## Acknowledgments
A special thank you to OpenAI and ElevenLabs for providing the APIs that made this project possible. This project was created for educational purposes to understand the workings and integration of AI in virtual assistants.

---


