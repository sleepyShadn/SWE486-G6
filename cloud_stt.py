import requests
import json
import psutil
import time
import os
import numpy as np

API_KEY = "1dc2c7c1d2014c558119ebfa3679a32a"
UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_URL = "https://api.assemblyai.com/v2/transcript"

headers = {
    "authorization": API_KEY,
    "content-type": "application/json"
}

# تقدير الطاقة
def estimate_energy(cpu_percent, elapsed_time):
    power = cpu_percent * 0.15
    energy = power * elapsed_time
    return power, energy

# رفع الملف للسحابة
def upload_audio_file(file_path):
    if not os.path.exists(file_path):
        print(f"[ERROR] File '{file_path}' not found.")
        return None

    print("\n--- Uploading audio file to cloud ---")
    
    with open(file_path, "rb") as f:
        response = requests.post(
            UPLOAD_URL,
            headers={"authorization": API_KEY},
            data=f
        )
    return response.json().get("upload_url", None)

# التفريغ السحابي
def transcribe_cloud(file_path):
    audio_url = upload_audio_file(file_path)
    if audio_url is None:
        return

    print(f"\n--- Transcribing '{file_path}' on cloud ---")

    cpu_before = psutil.cpu_percent(interval=1)
    ram_before = psutil.virtual_memory().used / (1024 * 1024)
    start = time.time()

    request_body = {
        "audio_url": audio_url,
        "language_code": "ar"
    }

    response = requests.post(
        TRANSCRIBE_URL,
        json=request_body,
        headers=headers
    )
    transcript_id = response.json().get("id")

    print("\n--- Processing on cloud... ---")

    while True:
        poll = requests.get(f"{TRANSCRIBE_URL}/{transcript_id}", headers=headers).json()
        if poll["status"] == "completed":
            result_text = poll["text"]
            break
        elif poll["status"] == "error":
            print("\n[ERROR]", poll["error"])
            return
        time.sleep(1)

    end = time.time()
    duration = end - start
    cpu_after = psutil.cpu_percent(interval=1)
    ram_after = psutil.virtual_memory().used / (1024 * 1024)

    power_before, energy_before = estimate_energy(cpu_before, duration)
    power_after, energy_after = estimate_energy(cpu_after, duration)

    print("\n=== Transcribed Text ===")
    print(result_text)

    with open("cloud_transcription.txt", "w", encoding="utf-8") as f:
        f.write(result_text)

    print("\n=== Performance Metrics ===")
    print(f"{'Processing Time:':25} {duration:.2f} s")
    print(f"{'RAM Usage:':25} Before = {ram_before:.2f} MB    After = {ram_after:.2f} MB")
    print(f"{'CPU Usage:':25} Before = {cpu_before:.2f}%    After = {cpu_after:.2f}%")
    print(f"{'Estimated Power:':25} Before = {power_before:.2f} W    After = {power_after:.2f} W")
    print(f"{'Total Energy:':25} Before = {energy_before:.2f} J    After = {energy_after:.2f} J")

    print("\n--- Cloud transcription completed ---")

# القائمة الرئيسية
def main():
    print("\n===============================")
    print(" Speech-to-Text Cloud Tool ")
    print("===============================\n")

    while True:
        print("\nPlease choose one of the following actions:")
        print("1 - Upload existing audio file")
        print("2 - Exit the program")

        choice = input("\nEnter your choice (1 or 2): ").strip()

        if choice == "1":
            file = input("\nPlease type the filename (include .wav extension): ").strip()
            transcribe_cloud(file)

        elif choice == "2":
            print("\nExiting the program. Goodbye!")
            break

        else:
            print("\n[ERROR] Invalid option selected. Please try again.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()