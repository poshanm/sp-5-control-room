import os
import subprocess
import psutil

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = "8593415577:AAHbWCoTV8mYoriMX8MmBq6aj8cBPmGfmhM"

BASE = r"C:\PA_AI"

REPORT = BASE + r"\report_sender.py"
LED = BASE + r"\LED\led_update_manual.py"
PA = BASE + r"\master_pa_controller.py"

EMERGENCY_FILE = r"C:\PA_AI\texts\emergency.txt"

PASSWORD = "2203"


# ================= PROCESS CHECK =================

def script_running(name):

    for p in psutil.process_iter(['cmdline']):
        try:
            cmd = " ".join(p.info['cmdline'])
            if name in cmd:
                return True
        except:
            pass

    return False


# ================= MENU =================

def control_menu():

    keyboard = [

        [InlineKeyboardButton("📊 System Status", callback_data="status")],

        [InlineKeyboardButton("📤 Send Report", callback_data="report")],

        [InlineKeyboardButton("📺 LED Update", callback_data="led")],

        [InlineKeyboardButton("📢 Manual PA", callback_data="pa")],

        [InlineKeyboardButton("🚨 Emergency PA", callback_data="emergency")]

    ]

    return InlineKeyboardMarkup(keyboard)


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🏭 PA_AI Control Panel",
        reply_markup=control_menu()
    )


# ================= BUTTON =================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data


    if data == "report":

        subprocess.Popen(["python", REPORT])

        await query.edit_message_text("📤 Report Sending Started")


    elif data == "led":

        subprocess.Popen(["python", LED])

        await query.edit_message_text("📺 LED Update Started")


    elif data == "pa":

        subprocess.Popen(["python", PA])

        await query.edit_message_text("📢 PA Announcement Triggered")


    elif data == "status":

        pa = "🟢 RUNNING" if script_running("master_pa_controller.py") else "🔴 STOPPED"

        led = "🟢 RUNNING" if script_running("led_update") else "🔴 STOPPED"

        msg = f"""
🏭 SYSTEM STATUS

PA System : {pa}
LED System : {led}
"""

        await query.edit_message_text(msg)


    elif data == "emergency":

        context.user_data["awaiting_password"] = True

        await query.edit_message_text(
            "🔐 Enter Emergency Password"
        )


# ================= PASSWORD CHECK =================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text


    # PASSWORD CHECK

    if context.user_data.get("awaiting_password"):

        if text == PASSWORD:

            context.user_data["awaiting_password"] = False
            context.user_data["awaiting_emergency"] = True

            await update.message.reply_text(
                "🚨 Enter Emergency Announcement Text"
            )

        else:

            await update.message.reply_text(
                "❌ Wrong Password"
            )

        return


    # EMERGENCY TEXT

    if context.user_data.get("awaiting_emergency"):

        os.makedirs(r"C:\PA_AI\texts", exist_ok=True)

        with open(EMERGENCY_FILE, "w", encoding="utf-8") as f:

            f.write(text)

        context.user_data["awaiting_emergency"] = False

        await update.message.reply_text(
            "🚨 Emergency Announcement Queued"
        )


# ================= BOT =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(CallbackQueryHandler(button))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

print("Telegram Control Panel Running")

app.run_polling()