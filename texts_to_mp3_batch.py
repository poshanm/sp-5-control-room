
import os
import requests
import time
import socket

# =========================
# NETWORK CHECK
# =========================
def network_available(host="eastus.tts.speech.microsoft.com", port=443, timeout=3):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except:
        return False



# =========================
# AZURE CONFIG
# =========================
AZURE_KEY = "9Be6oDIEHejl3cfGazyLdCsgeyw029Pu2Zh6iTvCYbIMyrSVgahcJQQJ99CBACYeBjFXJ3w3AAAYACOGf6Ga"     # <-- yahan apni KEY1 paste karo
REGION = "eastus"                 # East US (as confirmed)
VOICE = "hi-IN-SwaraNeural"       # Female Hindi (best)


ENDPOINT = f"https://eastus.tts.speech.microsoft.com/cognitiveservices/v1"

HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
}




TEXT_BASE = "C:/PA_AI/texts"
AUDIO_BASE = "C:/PA_AI/audio"

# =========================
# HELPER (REPLACED)
# =========================
def txt_to_mp3(text, out_mp3):
    if not text.strip():
        return

    # Already exists → skip
    if os.path.exists(out_mp3):
        print("SKIP (exists):", out_mp3)
        return

    # Wait for network
    while not network_available():
        print("Waiting for network...")
        time.sleep(10)

    ssml = f"""
<speak version='1.0' xml:lang='hi-IN'>
    <voice name='{VOICE}'>
        {text}
    </voice>
</speak>
"""
    try:
        r = requests.post(
            ENDPOINT,
            headers=HEADERS,
            data=ssml.encode("utf-8"),
            timeout=10
        )

        if r.status_code == 200:
            with open(out_mp3, "wb") as f:
                f.write(r.content)
            print("MP3 generated:", out_mp3)
        else:
            print("Azure error:", r.status_code)
            time.sleep(10)

    except Exception as e:
        print("Network error, retrying...")
        time.sleep(10)

# =========================
# SHIFT FOLDERS
# =========================
if os.path.exists(TEXT_BASE):
    for folder in os.listdir(TEXT_BASE):
        if folder.lower().startswith("shift"):
            src = os.path.join(TEXT_BASE, folder)
            if not os.path.isdir(src):
                continue

            shift_no = "".join(filter(str.isdigit, folder))
            if not shift_no:
                continue

            dst = os.path.join(AUDIO_BASE, folder.lower())
            os.makedirs(dst, exist_ok=True)

            for file in os.listdir(src):
                if file.lower().endswith(".txt"):
                    with open(os.path.join(src, file), "r", encoding="utf-8") as f:
                        text = f.read().strip()

                    day = file.replace("Day", "").replace(".txt", "")
                    out_mp3 = os.path.join(dst, f"S{shift_no}_D{day}.mp3")
                    txt_to_mp3(text, out_mp3)

# =========================
# CANTEEN FOLDERS
# =========================
canteen_src = os.path.join(TEXT_BASE, "canteen")

if os.path.exists(canteen_src):
    for time_folder in os.listdir(canteen_src):
        src = os.path.join(canteen_src, time_folder)
        if not os.path.isdir(src):
            continue

        dst = os.path.join(AUDIO_BASE, "canteen", time_folder)
        os.makedirs(dst, exist_ok=True)

        for file in os.listdir(src):
            if file.lower().endswith(".txt"):
                with open(os.path.join(src, file), "r", encoding="utf-8") as f:
                    text = f.read().strip()

                out_mp3 = os.path.join(dst, file.replace(".txt", ".mp3"))
                txt_to_mp3(text, out_mp3)

print("TXT TO MP3 BATCH COMPLETED")
