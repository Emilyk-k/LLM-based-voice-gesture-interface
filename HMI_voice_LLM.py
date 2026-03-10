from ollama import chat
from ollama import ChatResponse
import serial
import json
import speech_recognition as sr
from gtts import gTTS
import os
import time
import pygame

SERIAL_PORT = 'COM6'
BAUD_RATE = 115200
LANGUAGE = 'pl-PL'

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()


def speak(text):
    print(f"TTS: {text}")
    tts = gTTS(text=text, lang='pl')
    filename = "response.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()
    os.remove(filename)


def get_serial_data():
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').strip()
            data = json.loads(line)
            return data
        except Exception as e:
            print(f"Serial Error: {e}")
    return None


def listen_and_process():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nSłucham...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        data = get_serial_data()
        print(data)
        command = recognizer.recognize_google(audio, language=LANGUAGE).lower()
        print(f"Rozpoznano: {command}\n")

        data = str(data).replace('xraw', 'x surowe')
        data = data.replace('yraw', 'y surowe')

        response: ChatResponse = chat(model='gemma3:1b', messages=[
            {
                'role': 'system',
                'content': 'Jesteś głosowym asystentem przy obsłudze silnika elektrycznego. Twoim zadaniem jest '
                           'podawanie użytkownikowi liczbę przypisaną do zmiennej, o którą prosi. Używaj zawsze '
                           'krótkich zdań. Dostępne zmienne to "t", "x", "y", "surowe x", "surowe y". Masz zakaz używania w '
                           'odpowiedziach znaków specjalnych, szczególnie * i -. Podawaj liczbę przypisaną do zmiennej '
                           f'według tych danych w formacie json: {data}.'
            },
            {
                'role': "user",
                'content': f'{command}',
            },
        ])

        message = response.message.content
        message = message.replace('.', ',')
        message = message.replace('raw', ' surowy')
        speak(message)

    except sr.UnknownValueError:
        print("Nie zrozumiałem dźwięku.")
    except sr.RequestError as e:
        print(f"Błąd usługi rozpoznawania mowy: {e}")


if __name__ == "__main__":
    speak("System gotowy")
    try:
        while True:
            listen_and_process()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nZamykanie...")
        ser.close()
