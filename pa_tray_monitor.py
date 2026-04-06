import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import psutil
import os
import threading
import time

BASE = "C:/PA_AI"

SCRIPTS = [
    #"led_update_auto.py",
    "master_pa_controller.py",
    #"report_sender.py"
]


def create_icon(color):
    img = Image.new('RGB', (64, 64), color)
    return img


def running_scripts():
    running = []

    for p in psutil.process_iter(['cmdline']):
        try:
            cmd = " ".join(p.info['cmdline'])
            for s in SCRIPTS:
                if s in cmd and s not in running:
                    running.append(s)
        except:
            pass

    return running


def missing_scripts():
    running = running_scripts()
    return [s for s in SCRIPTS if s not in running]


def restart_system(icon, item):

    miss = missing_scripts()

    for s in miss:
        subprocess.Popen(["pythonw", os.path.join(BASE, s)])


def quit_app(icon, item):
    icon.stop()


def running_text(item):
    r = running_scripts()
    if not r:
        return "Running: None"
    return "Running: " + ", ".join(r)


def missing_text(item):
    m = missing_scripts()
    if not m:
        return "Missing: None"
    return "Missing: " + ", ".join(m)


def update_icon(icon):

    while True:

        miss = missing_scripts()

        if not miss:
            icon.icon = create_icon("green")
            icon.title = "PA System - All Running"

        else:
            icon.icon = create_icon("red")
            icon.title = "Missing: " + ", ".join(miss)

        time.sleep(5)


icon = pystray.Icon(
    "PA System",
    create_icon("green"),
    menu=pystray.Menu(
        item(lambda item: running_text(item), None, enabled=False),
        item(lambda item: missing_text(item), None, enabled=False),
        item("Restart Missing Scripts", restart_system),
        item("Exit", quit_app)
    )
)

threading.Thread(target=update_icon, args=(icon,), daemon=True).start()

icon.run()