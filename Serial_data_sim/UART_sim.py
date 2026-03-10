import serial
import time

# --- Configuration ---
SERIAL_PORT = 'COM1'
BAUD_RATE = 115200
FILE_PATH = 'UART_data.txt'
INTERVAL = 0.2


def stream_uart_loop():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}. Starting continuous loop...")
        print("Press Ctrl+C to stop.")

        while True:  # Infinite loop
            with open(FILE_PATH, 'r') as file:
                for line in file:
                    clean_line = line.strip()
                    if not clean_line:
                        continue

                    # Send data
                    ser.write((clean_line + '\r\n').encode('utf-8'))
                    time.sleep(INTERVAL)

            print("--- End of file reached. Restarting transmission... ---")

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nTransmission stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")


if __name__ == "__main__":
    stream_uart_loop()