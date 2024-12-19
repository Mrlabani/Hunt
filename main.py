import telebot
import random
import requests
import time
from faker import Faker
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread

# Bot token
TOKEN = "7806510181:AAHWqzkO9XM_MvVxybRQlLvw8CuOqKP6B6k"
bot = telebot.TeleBot(TOKEN)
fake = Faker()

stop_flag = {}
stats = {}
sleep_times = {}

def generate_username(length):
    ABC = 'abcdefghijklmnopqrstuvwxyz'
    NUM = '0123456789'
    return ''.join(random.choice(ABC + NUM) for _ in range(length))

def check_username_availability(username):
    url = f"https://t.me/{username}"
    try:
        response = requests.get(url)
        if 'If you have <strong>Telegram</strong>, you can contact <a class="tgme_username_link"' in response.text:
            return True
    except requests.RequestException:
        return False
    return False

def reset_stats(chat_id):
    stats[chat_id] = {
        "working": 0,
        "not_working": 0,
        "total_checked": 0,
        "last_user": None,
        "last_status": None
    }

@bot.message_handler(commands=['start'])
def welcome_message(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🟢 Check Quadruple", callback_data="check_4"),
        InlineKeyboardButton("🟡 Check Quintuple", callback_data="check_5"),
        InlineKeyboardButton("🔵 Check Sextuple", callback_data="check_6")
    )
    keyboard.add(
        InlineKeyboardButton("🎯 Random Name Hunting", callback_data="check_names")
    )
    keyboard.add(
        InlineKeyboardButton("⏳ Set Speed", callback_data="set_speed"),
        InlineKeyboardButton("🗑 Clear Speed", callback_data="clear_time")
    )
    keyboard.add(
        InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/NOOBMETHOD")
    )
    bot.send_message(
        message.chat.id,
        f"""
👋 <b>Welcome, {message.from_user.first_name}!</b>
I am a bot for checking Telegram usernames with precision and speed.

🔹 <b>Select from the buttons below to get started:</b>
- Check usernames of a specific length (Quadruple, Quintuple, Sextuple).
- Hunt random usernames.

📌 <b>Additional Commands:</b>
- Check a specific username: <code>/ch username</code>
- Stop checking: <code>/stp</code>
        """,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def start_checking(call):
    chat_id = call.message.chat.id
    data = call.data.split("_")[1]

    if data.isdigit():
        length = int(data)
        start_username_checking(chat_id, length)
    elif data == "names":
        start_random_name_checking(chat_id)

def start_username_checking(chat_id, length):
    reset_stats(chat_id)
    stop_flag[chat_id] = False
    sleep_time = sleep_times.get(chat_id, 0)

    status_msg = bot.send_message(chat_id, f"""
🔍 <b>Started checking usernames of length {length} characters ✅</b>

📊 <b>Statistics:</b>
👤 <b>Last Username:</b> ---
⚙️ <b>Status:</b> ---
📈 <b>Available:</b> 0
📉 <b>Not Available:</b> 0
🔢 <b>Total Checked:</b> 0

📌 <b>To stop checking, send:</b> /stp
    """, parse_mode="HTML")

    while not stop_flag.get(chat_id, True):
        username = generate_username(length)
        is_available = check_username_availability(username)

        stats[chat_id]["total_checked"] += 1
        stats[chat_id]["last_user"] = username
        stats[chat_id]["last_status"] = "✅ Available" if is_available else "❌ Not Available"
        if is_available:
            stats[chat_id]["working"] += 1
            bot.send_message(
                chat_id,
                f"""
📢 <b>Username Available ✅</b>
👤 <b>Username:</b> @{username}
                """,
                parse_mode="HTML"
            )
        else:
            stats[chat_id]["not_working"] += 1

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text=f"""
🔍 <b>Checking usernames of length {length} characters in progress ✅</b>

👤 <b>Last Username:</b> @{username}
⚙️ <b>Status:</b> {stats[chat_id]["last_status"]}
📈 <b>Available:</b> {stats[chat_id]["working"]}
📉 <b>Not Available:</b> {stats[chat_id]["not_working"]}
🔢 <b>Total Checked:</b> {stats[chat_id]["total_checked"]}
📌 <b>To stop checking, send:</b> /stp
            """,
            parse_mode="HTML"
        )
        if sleep_time > 0:
            time.sleep(sleep_time)

@bot.callback_query_handler(func=lambda call: call.data == "set_speed")
def set_speed(call):
    bot.send_message(
        call.message.chat.id,
        "⏳ <b>Enter the delay between checks (in seconds):</b>\nFor continuous checking, enter 0.",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(call.message, save_sleep_time)

def save_sleep_time(message):
    chat_id = message.chat.id
    try:
        sleep_time = int(message.text.strip())
        if sleep_time < 0:
            raise ValueError
        sleep_times[chat_id] = sleep_time
        bot.send_message(
            chat_id,
            f"✅ <b>Delay set to: {sleep_time} seconds.</b>",
            parse_mode="HTML"
        )
    except ValueError:
        bot.send_message(
            chat_id,
            "❌ <b>Please enter a valid integer (0 or greater).</b>",
            parse_mode="HTML"
        )

@bot.message_handler(commands=['stp'])
def stop_checking(message):
    chat_id = message.chat.id
    stop_flag[chat_id] = True
    bot.send_message(chat_id, "❌ <b>Checking stopped successfully.</b>", parse_mode="HTML")

@bot.message_handler(commands=['ch'])
def check_specific_username(message):
    try:
        username = message.text.split(' ', 1)[1].replace('@', '').strip()
        if not username:
            bot.reply_to(message, "⚠️ <b>Please enter a username to check.</b>", parse_mode="HTML")
            return

        is_available = check_username_availability(username)
        bot.reply_to(
            message,
            f"""
👤 <b>Username:</b> @{username}
⚙️ <b>Status:</b> {"✅ Available" if is_available else "❌ Not Available"}
            """,
            parse_mode="HTML"
        )
    except IndexError:
        bot.reply_to(message, "⚠️ <b>Please enter a username to check.</b>", parse_mode="HTML")

# Flask App for 24/7 Hosting
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
      
