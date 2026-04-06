import tkinter as tk
from tkinter import simpledialog, messagebox
import os
from datetime import datetime

BASE = "C:/PA_AI"
TEXT_FILE = f"{BASE}/texts/emergency.txt"
LOG_FILE = f"{BASE}/logs/emergency_entry.log"

PASSWORD = "2203"   # Change this

# ===== Password Prompt =====
root = tk.Tk()
root.withdraw()

pwd = simpledialog.askstring("Emergency Access", "Enter Password:", show="*")

if pwd != PASSWORD:
    messagebox.showerror("Access Denied", "Wrong Password")
    root.destroy()
    exit()

# ===== Message Entry Window =====
entry_window = tk.Toplevel()
entry_window.title("Emergency Message Entry")
entry_window.geometry("500x300")

tk.Label(entry_window, text="Enter Emergency Message:",
         font=("Arial", 12)).pack(pady=10)

text_box = tk.Text(entry_window, height=10, width=50)
text_box.pack(pady=5)

def save_message():
    message = text_box.get("1.0", tk.END).strip()

    if not message:
        messagebox.showwarning("Empty", "Message cannot be empty")
        return

    os.makedirs(f"{BASE}/texts", exist_ok=True)
    os.makedirs(f"{BASE}/logs", exist_ok=True)

    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(message)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"{datetime.now()} | Emergency Created\n")
        log.write(message + "\n")
        log.write("-" * 50 + "\n")

    messagebox.showinfo("Success", "Emergency Message Saved & Triggered")
    entry_window.destroy()

tk.Button(entry_window, text="SAVE & ANNOUNCE",
          command=save_message,
          bg="red", fg="white",
          font=("Arial", 12)).pack(pady=15)

entry_window.mainloop()