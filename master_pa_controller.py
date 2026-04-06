import os
import sys
import psutil

LOCK_FILE = "C:/PA_AI/master.lock"

def already_running():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE,"r") as f:
            pid = int(f.read())

        if psutil.pid_exists(pid):
            return True
    return False

if already_running():
    print("Master already running")
    sys.exit()

with open(LOCK_FILE,"w") as f:
    f.write(str(os.getpid()))
    
import os
import time
import datetime
import pandas as pd
import serial
import socket
import requests
from playsound import playsound

# ================= CONFIG =================
BASE = "C:/PA_AI"
AUDIO = f"{BASE}/audio"
SCHEDULE = f"{BASE}/schedule.csv"

BELL = f"{AUDIO}/bell/dingdong_soft.wav"
EMERGENCY_TXT = f"{BASE}/texts/emergency.txt"

LOG_FILE = f"{BASE}/logs/master_log.txt"
AUDIO_FOLDER = f"{AUDIO}/emergency"

os.makedirs(f"{BASE}/logs", exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# ================= RELAY (COM6) =================
try:
    relay = serial.Serial("COM4", 9600, timeout=1)
    RELAY_ON  = bytes.fromhex("A0 01 01 A2")
    RELAY_OFF = bytes.fromhex("A0 01 00 A1")
    print("Relay connected on COM4")
except Exception as e:
    relay = None
    print("Relay NOT connected:", e)

def page_hold():
    if relay:
        relay.write(RELAY_ON)
        time.sleep(0.5)

def page_release():
    if relay:
        relay.write(RELAY_OFF)
        time.sleep(0.2)

# ================= VOLUME =================
try:
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    def set_volume(percent):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(percent / 100.0, None)

    print("Volume control ready")
except:
    def set_volume(percent):
        pass
    print("Volume control not available")

# ================= AZURE =================
AZURE_KEY = "9Be6oDIEHejl3cfGazyLdCsgeyw029Pu2Zh6iTvCYbIMyrSVgahcJQQJ99CBACYeBjFXJ3w3AAAYACOGf6Ga"     # <-- yahan apni KEY1 paste karo
REGION = "eastus"                 # East US (as confirmed)
VOICE = "hi-IN-SwaraNeural"       # Female Hindi (best)


ENDPOINT = f"https://eastus.tts.speech.microsoft.com/cognitiveservices/v1"
HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
}

def network_available():
    try:
        socket.create_connection(("eastus.tts.speech.microsoft.com", 443), 3)
        return True
    except:
        return False

def text_to_mp3(text):
    while not network_available():
        time.sleep(5)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_mp3 = f"{AUDIO_FOLDER}/emergency_{timestamp}.mp3"

    ssml = f"""
<speak version='1.0' xml:lang='hi-IN'>
    <voice name='{VOICE}'>
        {text}
    </voice>
</speak>
"""

    r = requests.post(
        ENDPOINT,
        headers=HEADERS,
        data=ssml.encode("utf-8"),
        timeout=15
    )

    if r.status_code == 200:
        with open(new_mp3, "wb") as f:
            f.write(r.content)
        return new_mp3
    return None

# ================= STATE =================
played_keys = set()
last_date = datetime.date.today()
is_playing = False

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} | {msg}\n")

# ================= PLAY FUNCTION =================
def play_audio(mp3, tag):
    global is_playing

    if is_playing:
        print("⚠ Already playing, skipping trigger:", tag)
        return

    is_playing = True
    print("▶ START:", tag)

    page_hold()
    set_volume(20)

    if tag == "EMERGENCY":
        repeat = 2
    else:
        repeat = 1

    for i in range(repeat):

        print(f"Playing {tag} round {i+1}")

        if os.path.exists(BELL):
            playsound(BELL)
            time.sleep(1)

        playsound(mp3)

        if repeat == 2 and i == 0:
            time.sleep(3)

    page_release()

    log(f"{tag} | {mp3}")
    print("■ END:", tag)

    is_playing = False

# ================= MAIN LOOP =================
print("🔥 MASTER PA CONTROLLER RUNNING 🔥")

while True:

    now = datetime.datetime.now()
    hhmm = now.strftime("%H:%M")
    day = f"{now.day:02d}"
    current_key = now.strftime("%Y-%m-%d %H:%M")

    # Daily reset
    if datetime.date.today() != last_date:
        played_keys.clear()
        last_date = datetime.date.today()

    # ================= EMERGENCY =================
    if os.path.exists(EMERGENCY_TXT):

        with open(EMERGENCY_TXT, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if text:
            print("🚨 EMERGENCY DETECTED")
            mp3 = text_to_mp3(text)

            if mp3:
                play_audio(mp3, "EMERGENCY")

            open(EMERGENCY_TXT, "w").write("")
            time.sleep(2)
            continue

    # ================= SCHEDULE =================
    try:
        df = pd.read_csv(SCHEDULE, dtype=str)
    except:
        time.sleep(10)
        continue

    for _, r in df.iterrows():

        csv_time = str(r["time"]).strip()[:5]

        if csv_time == hhmm and current_key not in played_keys:

            mp3 = None

            if r["type"] == "shift":
                mp3 = f"{AUDIO}/{r['shift']}/S{r['shift'][-1]}_D{day}.mp3"

            elif r["type"] == "canteen":
                if r["shift"] == "09":
                    mp3 = f"{AUDIO}/canteen/9AM/Day{day}.mp3"
                elif r["shift"] == "10":
                    mp3 = f"{AUDIO}/canteen/10AM/Day{day}.mp3"
                elif r["shift"] == "17":
                    mp3 = f"{AUDIO}/canteen/5PM/Day{day}.mp3"
                elif r["shift"] == "0530":
                    mp3 = f"{AUDIO}/canteen/0530PM/Day{day}.mp3"

            if mp3 and os.path.exists(mp3):
                play_audio(mp3, "SCHEDULE")
                played_keys.add(current_key)
                break

    time.sleep(2)
import atexit

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

atexit.register(remove_lock)