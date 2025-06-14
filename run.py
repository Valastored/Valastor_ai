import winsound
import sys
import time
import keyboard
import json
import speech_recognition as sr
import json
import requests
from config import *
from abba.promptMaker import *
from abba.TTS import *




sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

conversation = []

history = {"history": conversation}

mode = 0
total_characters = 0
chat = ""
chat_now = ""
chat_prev = ""
is_Speaking = False
owner_name = "Valastor"
blacklist = ["Nightbot", "streamelements"]

# function to get the user's input audio
def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Recording...")
        audio = r.listen(source)
        print("Stopped recording.")
        with open("recorded_audio.wav", "wb") as file:
            file.write(audio.get_wav_data())

        print("Audio saved to recorded_audio.wav")
        return audio

# function to transcribe the user's audio
def transcribe_audio(audio):
    global chat_now
    r = sr.Recognizer()
    try:
        chat_now = r.recognize_google(audio)
        print ("Question: " + chat_now)
        result = owner_name + " said " + chat_now
        conversation.append({'role': 'user', 'content': result})
        ask_ai(chat_now)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def ask_ai(question):
    # Read the identity from the identity.txt file
    with open('characterConfig/Pina/identity.txt', 'r') as file:
        identity = file.read().strip()

    memories = [
        {
            "content": identity,
            "role": "system"
        },
        {
            "content": question,
            "role": "user"
        }
    ]

    data = {
        "messages": memories,
        "model": "mistral-ins-7b-q4",
        "stream": False,
        "max_tokens": 4096,
        "stop": ["\n", "Human:", "AI:"],
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "temperature": 0.7,
        "top_p": 0.95
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.post('http://localhost:1337/v1/chat/completions', headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        answer = response_data['choices'][0]['message']['content']
        print("Answer: " + answer)
        talk(answer)
    else:
        print(f"Request failed with status code {response.status_code}")


def talk(text):
    silero_tts(text, "en", "v3_en", "en_21")

    is_Speaking = True
    winsound.PlaySound("test.wav", winsound.SND_FILENAME)
    is_Speaking = False

    # Clear the text files after the assistant has finished speaking
    time.sleep(1)
    with open ("output.txt", "w") as f:
        f.truncate(0)
    with open ("chat.txt", "w") as f:
        f.truncate(0)


if __name__ == "__main__":
    print("Press and Hold Right Shift to record audio")
    while True:
        if keyboard.is_pressed('RIGHT_SHIFT'):
            audio = record_audio()
            transcribe_audio(audio)