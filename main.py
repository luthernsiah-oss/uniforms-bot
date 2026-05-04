import telebot
import sqlite3
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrer INTEGER,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    args = message.text.split()
    referrer = None

    if len(args) > 1:
        referrer = int(args[1])

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id, referrer) VALUES (?, ?)", (user_id, referrer))
        conn.commit()

    bot.send_message(user_id,
                     "Welcome!\n\nBuy university forms here.\n\nUse /referral to earn ₵25 per sale.")


@bot.message_handler(commands=['referral'])
def referral(message):
    user_id = message.chat.id
    link = f"https://t.me/uniforms_bot?start={user_id}"

    bot.send_message(user_id, f"Your referral link:\n{link}")


@bot.message_handler(commands=['buy'])
def buy(message):
    user_id = message.chat.id

    bot.send_message(user_id,
                     "University forms: ₵295\nTechnical Universities: ₵250\n\nContact admin to pay.")

    # simulate purchase
    cursor.execute("SELECT referrer FROM users WHERE user_id=?", (user_id,))
    ref = cursor.fetchone()

    if ref and ref[0]:
        cursor.execute("UPDATE users SET balance = balance + 25 WHERE user_id=?", (ref[0],))
        conn.commit()


@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.chat.id

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cursor.fetchone()[0]

    bot.send_message(user_id, f"Your earnings: ₵{bal}")


bot.polling()
