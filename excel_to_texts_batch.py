import pandas as pd
import os
import sys
import time
import socket

# =========================
# NETWORK / FILE WAIT
# =========================
def network_available(host="google.com", port=80, timeout=3):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except:
        return False

def wait_for_file(path, check_net=False):
    while not os.path.exists(path):
        if check_net and not network_available():
            print("Waiting for network...")
        else:
            print("Waiting for file:", path)
        time.sleep(10)

# =========================
# COMMON CONFIG
# =========================
BASE = "C:/PA_AI/texts"
CANTEEN_BASE = os.path.join(BASE, "canteen")

CANTEEN_EXCEL = os.path.join(BASE, "canteen.xlsx")
SHIFT_EXCEL = os.path.join(BASE, "shift.xlsx")

TOTAL_DAYS = 31

# =========================
# WAIT FOR INPUT FILES
# =========================
wait_for_file(CANTEEN_EXCEL, check_net=True)
wait_for_file(SHIFT_EXCEL, check_net=True)

# =========================
# PART 1 – CANTEEN EXCEL
# =========================
print("Processing CANTEEN excel")

df1 = pd.read_excel(CANTEEN_EXCEL, sheet_name=0)

for _, row in df1.iterrows():
    time_val = str(row.get("Time", "")).strip()
    text = str(row.get("Announcement Text", "")).strip()

    if not text:
        continue

    if time_val.startswith("09"):
        folder = "9AM"
    elif time_val.startswith("17"):
        folder = "5PM"
    else:
        continue

    out_dir = os.path.join(CANTEEN_BASE, folder)
    os.makedirs(out_dir, exist_ok=True)

    for d in range(1, TOTAL_DAYS + 1):
        out_file = os.path.join(out_dir, f"Day{d:02d}.txt")
        if os.path.exists(out_file):
            continue
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text)

# ---- SHEET 2: 10AM
df2 = pd.read_excel(CANTEEN_EXCEL, sheet_name=1)
out_dir = os.path.join(CANTEEN_BASE, "10AM")
os.makedirs(out_dir, exist_ok=True)

for _, row in df2.iterrows():
    text = str(row.get("Announcement Text", "")).strip()
    if not text:
        continue
    day = int(row["Day"])
    out_file = os.path.join(out_dir, f"Day{day:02d}.txt")
    if os.path.exists(out_file):
        continue
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)

# ---- SHEET 3: 05:30PM
df3 = pd.read_excel(CANTEEN_EXCEL, sheet_name=2)
out_dir = os.path.join(CANTEEN_BASE, "0530PM")
os.makedirs(out_dir, exist_ok=True)

for _, row in df3.iterrows():
    text = str(row.get("Announcement Text", "")).strip()
    if not text:
        continue
    day = int(row["Day"])
    out_file = os.path.join(out_dir, f"Day{day:02d}.txt")
    if os.path.exists(out_file):
        continue
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(text)

print("CANTEEN text files done")

# =========================
# PART 2 – SHIFT EXCEL
# =========================
print("Processing SHIFT excel")

shift_book = pd.ExcelFile(SHIFT_EXCEL)

for sheet in shift_book.sheet_names:
    df = pd.read_excel(SHIFT_EXCEL, sheet_name=sheet)

    if "Shift" not in df.columns:
        print("Shift column missing in sheet:", sheet)
        continue

    for _, row in df.iterrows():
        text = str(row.get("Announcement Text", "")).strip()
        if not text:
            continue

        shift_val = str(row["Shift"]).strip().lower()
        day = int(row["Day"])

        out_dir = os.path.join(BASE, shift_val)
        os.makedirs(out_dir, exist_ok=True)

        out_file = os.path.join(out_dir, f"Day{day:02d}.txt")
        if os.path.exists(out_file):
            continue

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text)

print("SHIFT text files done")

# =========================
# PART 3 – EMERGENCY TEXT
# =========================
print("Processing EMERGENCY text")

EMERGENCY_DIR = os.path.join(BASE, "emergency")
os.makedirs(EMERGENCY_DIR, exist_ok=True)
EMERGENCY_FILE = os.path.join(EMERGENCY_DIR, "Emergency.txt")

emergency_text = ""

em_excel = os.path.join(BASE, "emergency.xlsx")
em_txt = os.path.join(BASE, "emergency.txt")
em_docx = os.path.join(BASE, "emergency.docx")

if os.path.exists(em_excel):
    df = pd.read_excel(em_excel)
    if "Announcement Text" in df.columns:
        emergency_text = "\n".join(df["Announcement Text"].dropna().astype(str))

elif os.path.exists(em_txt):
    emergency_text = open(em_txt, "r", encoding="utf-8").read().strip()

elif os.path.exists(em_docx):
    try:
        from docx import Document
        doc = Document(em_docx)
        emergency_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except:
        emergency_text = ""

with open(EMERGENCY_FILE, "w", encoding="utf-8") as f:
    f.write(emergency_text)

if emergency_text:
    print("Emergency content detected and updated")
else:
    print("No emergency content, blank Emergency.txt created")

print("ALL TEXT FILES GENERATED SUCCESSFULLY")
