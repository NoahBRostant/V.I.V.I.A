import sys
import os
import random
import requests
import subprocess
import threading
import numpy as np
import pyaudio
from openai import OpenAI
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit
)
from PyQt5.QtGui import QPainter, QColor, QIcon, QPixmap

# -------------------------------
# Configuration & Global Variables
# -------------------------------
DEBUG_AUDIO = False

# Audio scaling parameters.
AUDIO_SCALING_FACTOR = 5 / 32768.0  # Base scaling factor from 16-bit samples.
AUDIO_MULTIPLIER = 10               # Extra multiplier to amplify the effect.

# Global variable to hold the most recent audio waveform data.
# Expected to be a list of 1000 floats (one per dot).
global_audio_waveform = None

# -------------------------------
# API Keys and OpenAI Client Setup
# -------------------------------
with open("OPENAI_API_KEY", "r") as f:
    OPENAI_API_KEY = f.read().strip()

with open("ELEVENLABS_API_KEY", "r") as f:
    ELABS_API_KEY = f.read().strip()

client = OpenAI(api_key=OPENAI_API_KEY)

chat_log = [{
    "role": "system",
    "content": (
        "I'm VIVIA, short for Versatile and Interactive Voice Integrated Assistant. "
        "I keep it concise, typically one sentence, unless further explanation is needed. "
        "Charismatic, kind, and calm, that's me. Created by Noah Bradford Rostant, I'm your "
        "helpful companion. Integrated with Google Home, I can manage your home tasks, from "
        "lights to timers. When someone tells me to shutdown, and only when they say to do so, "
        "I'll say my goodbyes or goodnights confirming I will be shutting down and I'll put this "
        "string of characters at the end *(SHUTTING_DOWN)*"
    )
}]

# -------------------------------
# GPT & Audio Functions
# -------------------------------
def process_response(user_message):
    global chat_log
    chat_log.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="gpt-4",
        messages=chat_log,
        max_tokens=200,
        temperature=1
    )
    assistant_response = response.choices[0].message.content.strip()
    if "*(CHAT)*" in assistant_response:
        assistant_response = assistant_response.replace("*(CHAT)*", "")
    elif "*(SEARCH)*" in assistant_response:
        assistant_response = assistant_response.replace("*(SEARCH)*", "")
        return assistant_response, True
    elif "*(COMMAND)*" in assistant_response:
        assistant_response = assistant_response.replace("*(COMMAND)*", "")
        return assistant_response, True
    chat_log.append({"role": "assistant", "content": assistant_response})
    return assistant_response, False

def play_audio(assistant_response):
    """
    Retrieves the ElevenLabs stream, pipes it to ffmpeg for decoding into raw 16-bit PCM,
    then uses PyAudio to play the decoded PCM. Simultaneously, the PCM is processed to update
    the global audio waveform.
    """
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

    # Start ffmpeg to decode the incoming stream to raw PCM.
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', 'pipe:0',
        '-f', 's16le',
        '-ac', '1',
        '-ar', '44100',
        '-c:a', 'pcm_s16le',
        'pipe:1'
    ]
    ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Feed ffmpeg's stdin in a separate thread.
    def feed_ffmpeg():
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                try:
                    ffmpeg_proc.stdin.write(chunk)
                except Exception as e:
                    print("Error writing to ffmpeg stdin:", e)
        ffmpeg_proc.stdin.close()

    feeder_thread = threading.Thread(target=feed_ffmpeg)
    feeder_thread.start()

    # Setup PyAudio for playback.
    p = pyaudio.PyAudio()
    pa_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)

    buffer = bytearray()
    decode_chunk_size = 4096

    while True:
        data_chunk = ffmpeg_proc.stdout.read(decode_chunk_size)
        if not data_chunk:
            break
        pa_stream.write(data_chunk)
        buffer.extend(data_chunk)
        if len(buffer) >= decode_chunk_size:
            process_chunk = bytes(buffer[:decode_chunk_size])
            del buffer[:decode_chunk_size]
            try:
                samples = np.frombuffer(process_chunk, dtype=np.int16)
                if len(samples) > 1:
                    # Downsample to 1000 points (one per dot).
                    x_old = np.linspace(0, len(samples) - 1, num=len(samples))
                    x_new = np.linspace(0, len(samples) - 1, num=1000)
                    samples_downsampled = np.interp(x_new, x_old, samples)
                    total_factor = AUDIO_SCALING_FACTOR * AUDIO_MULTIPLIER
                    audio_waveform = samples_downsampled * total_factor
                    global global_audio_waveform
                    global_audio_waveform = audio_waveform.tolist()
            except Exception as e:
                print("Error processing audio chunk:", e)
    feeder_thread.join()
    pa_stream.stop_stream()
    pa_stream.close()
    p.terminate()
    ffmpeg_proc.stdout.close()
    ffmpeg_proc.wait()

def update_memory(user_message, assistant_response):
    with open("recent_memory.txt", "a") as file:
        file.writelines('{"role": "user", "content": ' + user_message + '}\n')
        file.writelines('{"role": "assistant", "content": ' + assistant_response + '}\n')

# -------------------------------
# Worker Threads
# -------------------------------
class GPTResponseWorker(QThread):
    finished = pyqtSignal(str, bool)
    def __init__(self, user_message, parent=None):
        super().__init__(parent)
        self.user_message = user_message
    def run(self):
        response, skip = process_response(self.user_message)
        self.finished.emit(response, skip)

class AudioPlayerWorker(QThread):
    def __init__(self, assistant_response, parent=None):
        super().__init__(parent)
        self.assistant_response = assistant_response
    def run(self):
        play_audio(self.assistant_response)

# -------------------------------
# Visualiser Widget
# -------------------------------
class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_dots = 1000
        self.dot_size = 2
        self.max_offset = 5
        # Default random motion targets.
        self.offsets = [0.0 for _ in range(self.num_dots)]
        self.random_targets = [random.uniform(-self.max_offset, self.max_offset) for _ in range(self.num_dots)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateWaveform)
        self.timer.start(16)

    def updateWaveform(self):
        global global_audio_waveform
        if global_audio_waveform is not None and len(global_audio_waveform) == self.num_dots:
            peak = max(abs(val) for val in global_audio_waveform)
            if peak > 0.01:  # Audio is active.
                smoothing = 0.2
                for i in range(self.num_dots):
                    target = global_audio_waveform[i]
                    self.offsets[i] += (target - self.offsets[i]) * smoothing
                self.update()
                return
        smoothing = 0.05
        for i in range(self.num_dots):
            target = self.random_targets[i]
            self.offsets[i] += (target - self.offsets[i]) * smoothing
            if abs(self.offsets[i] - target) < 0.1:
                self.random_targets[i] = random.uniform(-self.max_offset, self.max_offset)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#111111"))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#cecffa"))

        # Center the dots horizontally.
        drawing_width = self.width() * 0.9  # Use 90% of widget width.
        left_margin = (self.width() - drawing_width) / 2
        spacing = drawing_width / (self.num_dots + 1)
        h = self.height()
        baseline = h / 2
        for i in range(self.num_dots):
            x = left_margin + spacing * (i + 1)
            y = baseline + self.offsets[i]
            r = self.dot_size / 2
            painter.drawEllipse(int(x - r), int(y - r), self.dot_size, self.dot_size)

# -------------------------------
# Main Window (UI)
# -------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VIVIA - Visualiser & Chat")
        self.setStyleSheet("background-color: #111111;")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Top: Centered logo.
        self.logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png")
        self.logo_label.setPixmap(logo_pixmap.scaledToWidth(200, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        # Middle: Waveform visualiser.
        self.waveform = WaveformWidget(self)
        layout.addWidget(self.waveform, stretch=3)

        # Conversation display area.
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setStyleSheet("background-color: #1e1e1e; color: #cecffa;")
        layout.addWidget(self.conversation_display, stretch=1)

        # Input field and Send button (styled similar to bottom buttons).
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setStyleSheet(
            "background-color: #25242e; color: #cecffa; border: none; border-radius: 10px; padding: 10px;"
        )
        input_layout.addWidget(self.input_field, stretch=1)
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet(
            "background-color: #25242e; color: #cecffa; border: none; border-radius: 20px; padding: 10px;"
        )
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Bottom row: Profile button on the left and settings button on the right.
        bottom_layout = QHBoxLayout()
        self.profile_button = QPushButton()
        self.profile_button.setFixedSize(40, 40)
        profile_icon = QIcon("circle-user-solid.svg")
        self.profile_button.setIcon(profile_icon)
        self.profile_button.setIconSize(self.profile_button.size() * 0.6)
        self.profile_button.setStyleSheet(
            "background-color: #25242e; border: none; border-radius: 20px;"
        )
        bottom_layout.addWidget(self.profile_button)
        bottom_layout.addStretch()
        self.settings_button = QPushButton()
        self.settings_button.setFixedSize(40, 40)
        cog_icon = QIcon("gear-solid.svg")
        self.settings_button.setIcon(cog_icon)
        self.settings_button.setIconSize(self.settings_button.size() * 0.6)
        self.settings_button.setStyleSheet(
            "background-color: #25242e; border: none; border-radius: 20px;"
        )
        bottom_layout.addWidget(self.settings_button)
        layout.addLayout(bottom_layout)

        # Connect signals for sending messages.
        self.send_button.clicked.connect(self.handle_user_input)
        self.input_field.returnPressed.connect(self.handle_user_input)
        self.last_user_message = ""

    def handle_user_input(self):
        user_text = self.input_field.text().strip()
        if user_text:
            self.last_user_message = user_text
            self.conversation_display.append(f"<b>You:</b> {user_text}")
            self.input_field.clear()
            self.gpt_worker = GPTResponseWorker(user_text)
            self.gpt_worker.finished.connect(self.handle_gpt_response)
            self.gpt_worker.start()

    def handle_gpt_response(self, response_text, skip):
        self.conversation_display.append(f"<b>VIVIA:</b> {response_text}")
        update_memory(self.last_user_message, response_text)
        if not skip:
            self.audio_worker = AudioPlayerWorker(response_text)
            self.audio_worker.start()

# -------------------------------
# Main Entry Point
# -------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
