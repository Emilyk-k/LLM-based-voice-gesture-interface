
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
        command = recognizer.recognize_google(audio, language=LANGUAGE).lower()
        print(f"Rozpoznano: {command}")

        if "podaj" in command or "daj" in command:
            target_var = ""
            if "x" in command:
                if "surowy" in command or "surowe" in command:
                    target_var = "xraw"
                else:
                    target_var = "x"
            elif "y" in command:
                if "surowy" in command or "surowe" in command:
                    target_var = "yraw"
                else:
                    target_var = "y"
            elif "t" or "T" in command:
                target_var = "t"

            if target_var:
                data = get_serial_data()
                if data and target_var in data:
                    val = data[target_var]
                    print(data)
                    val = str(val).replace('.', ',')
                    if "raw" in target_var:
                        speak(f"Wartość {target_var[0]} surowe to {val}")
                    else:
                        speak(f"Wartość {target_var} to {val}")
                else:
                    speak("Błąd portu szeregowego.")
            else:
                speak("Nie zrozumiałem, o którą wartość pytasz.")
        elif "koniec" in command or "zakończ" in command or "zamknij" in command:
            speak("Zamykam program")
            exit('Zamykanie...')
        elif "pomoc" in command or "pomóż" in command:
            speak("Dostępne komendy: podaj wartość, koniec.")
        else:
            speak("Przepraszam, nie rozumiem.")

    except sr.UnknownValueError:
        print("Nie zrozumiałem dźwięku.")
    except sr.RequestError as e:
        print(f"Błąd usługi rozpoznawania mowy: {e}")


if __name__ == "__main__":
    speak("System gotowy")
    try:
        while True:
            listen_and_process()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nZamykanie...")
        ser.close()