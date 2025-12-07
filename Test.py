import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import psutil
import time
import os

# تحميل نموذج Whisper
model = whisper.load_model("base")

SAMPLE_RATE = 48000

# دالة انتظار ضغط Enter لإيقاف التسجيل
stop_flag = False
def wait_enter():
    global stop_flag
    input(">>> Press Enter to stop recording...")
    stop_flag = True

# دالة تسجيل الصوت وحفظه
def record_audio_file():
    global stop_flag
    recorded_audio = []
    stop_flag = False
    print("\n--- Recording started ---")
    print("🎙️ Speak now...")
    thread = threading.Thread(target=wait_enter)
    thread.start()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.float32) as stream:
        while not stop_flag:
            frame = stream.read(1024)[0]
            recorded_audio.append(frame)

    print("\n--- Recording finished ---")
    audio_data = np.concatenate(recorded_audio, axis=0)
    audio_data = audio_data / np.max(np.abs(audio_data))
    filename = "my_recorded_audio.wav"
    wav.write(filename, SAMPLE_RATE, (audio_data * 32767).astype(np.int16))
    return filename

# دالة تقدير استهلاك الطاقة
def estimate_energy(cpu_percent, elapsed_time):
    power = cpu_percent * 0.15  # W
    energy = power * elapsed_time  # Joules
    return power, energy

# دالة التفريغ الصوتي
def transcribe(file_path):
    if not os.path.exists(file_path):
        print(f"[ERROR] File '{file_path}' not found.")
        return

    print(f"\n--- Transcribing '{file_path}' ---")
    cpu_before = psutil.cpu_percent(interval=1)
    ram_before = psutil.virtual_memory().used / (1024 * 1024)
    start = time.time()
    
    result = model.transcribe(file_path, language="ar", fp16=False)
    
    end = time.time()
    cpu_after = psutil.cpu_percent(interval=1)
    ram_after = psutil.virtual_memory().used / (1024 * 1024)
    duration = end - start

    power_before, energy_before = estimate_energy(cpu_before, duration)
    power_after, energy_after = estimate_energy(cpu_after, duration)


    print("\n=== Transcribed Text ===")
    print(result["text"])

    # حفظ النص العربي في ملف نصي UTF-8
    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(result["text"])
    print("\n=== Performance Metrics ===")
    print(f"{'Processing Time:':25} {duration:.2f} s")
    print(f"{'RAM Usage:':25} Before = {ram_before:.2f} MB    After = {ram_after:.2f} MB")
    print(f"{'CPU Usage:':25} Before = {cpu_before:.2f}%    After = {cpu_after:.2f}%")
    print(f"{'Estimated Power:':25} Before = {power_before:.2f} W    After = {power_after:.2f} W")
    print(f"{'Total Energy:':25} Before = {energy_before:.2f} J    After = {energy_after:.2f} J")

    print("\n✅ Operation completed.")

# البرنامج الرئيسي مع حلقة الخيارات
def main():
    print("\n===============================")
    print("🎤 Welcome to My Speech-to-Text Tool 🎤")
    print("===============================\n")

    while True:
        print("\nPlease choose one of the following actions:")
        print("1 - Start recording a new audio clip")
        print("2 - Convert an existing audio file to text")
        print("3 - Exit the program")

        choice = input("\nEnter your choice (1, 2, or 3): ").strip()

        if choice == "1":
            file = record_audio_file()
            transcribe(file)
        elif choice == "2":
            file = input("\nPlease type the filename (include .wav extension): ").strip()
            transcribe(file)
        elif choice == "3":
            print("\nExiting the program. Goodbye!")
            break
        else:
            print("\n[ERROR] Invalid option selected. Please try again.")

        input("\nPress Enter to continue...")  # يبقي الرسالة على الشاشة قبل العودة للقائمة

if __name__ == "__main__":
    main()
