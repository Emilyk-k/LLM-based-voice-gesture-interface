import serial
import json
import time
import os
import pygame
from gtts import gTTS

SERIAL_PORT = 'COM7'
BAUD_RATE = 115200
TILT_THRESHOLD = 500
GESTURE_TIMEOUT = 1.0
LANGUAGE = 'pl'


def speak(text):
    print(f"TTS: {text}")
    try:
        tts = gTTS(text=text, lang=LANGUAGE)
        filename = "gesture_voice.mp3"
        tts.save(filename)

        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.quit()
        os.remove(filename)
    except Exception as e:
        print(f"TTS Error: {e}")


def detect_gestures():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print("Gesture Detection Active...")
    except Exception as e:
        print(f"Serial Error: {e}")
        return

    tilt_count = 0
    last_tilt_time = 0
    is_tilted = False

    while True:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                print(line)
                if not line: continue

                data = json.loads(line)
                y_raw = data.get('yraw', 2000)
                current_time = time.time()

                if y_raw < TILT_THRESHOLD and not is_tilted:
                    is_tilted = True

                    if current_time - last_tilt_time <= GESTURE_TIMEOUT:
                        tilt_count += 1
                    else:
                        tilt_count = 1

                    last_tilt_time = current_time
                    print(f"Tilt {tilt_count}/2 detected")

                    if tilt_count >= 2:
                        print(">>> GESTURE DETECTED <<<")

                        t = data.get('t', 0)
                        x = data.get('x', 0)
                        y = data.get('y', 0)

                        msg = f"Te to {t}, iks to {str(x).replace('.', ',')}, igrek to {str(y).replace('.', ',')}"
                        speak(msg)

                        tilt_count = 0

                elif y_raw > TILT_THRESHOLD:
                    is_tilted = False

            except (json.JSONDecodeError, KeyError):
                continue
            except Exception as e:
                print(f"Loop Error: {e}")

        time.sleep(0.01)


if __name__ == "__main__":
    detect_gestures()