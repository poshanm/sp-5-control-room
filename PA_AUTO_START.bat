@echo off

cd C:\PA_AI

start "" "C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\pythonw.exe" master_pa_controller.py
start "" "C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\pythonw.exe" pa_tray_monitor.py
start "" "C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\pythonw.exe" report_sender.py 
start "" "C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\pythonw.exe" telegram_control.py
