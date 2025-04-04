import telebot
import json
import os

BOT_TOKEN = '7798896914:AAFgwT4vdRfnWXLE-_e-mHDG4t_SJbZX3-o'  # Replace with your bot token
bot = telebot.TeleBot(BOT_TOKEN)

# List of authorized user IDs (replace with your real ones)
AUTHORIZED_USERS = [5018478747, 2005048275, 7750385522, 7912929481]

# JSON file to store user-channel mapping
CHANNEL_FILE = 'channels.json'

def load_channels():
    if not os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, 'w') as f:
            json.dump({}, f)
    with open(CHANNEL_FILE, 'r') as f:
        return json.load(f)

def save_channels(data):
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to the Broadcast Bot!\n\nUse /addchannel, /removechannel, /showchannels to manage your channels.")

@bot.message_handler(commands=['addchannel'])
def add_channel(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return

    try:
        _, channel = message.text.strip().split()
    except:
        bot.reply_to(message, "❌ Usage: /addchannel @channel_username or -100xxxx")
        return

    data = load_channels()
    user_id = str(message.from_user.id)
    data.setdefault(user_id, [])
    if channel not in data[user_id]:
        data[user_id].append(channel)
        save_channels(data)
        bot.reply_to(message, f"✅ Channel `{channel}` added successfully!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Channel already exists!")

@bot.message_handler(commands=['removechannel'])
def remove_channel(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return

    try:
        _, channel = message.text.strip().split()
    except:
        bot.reply_to(message, "❌ Usage: /removechannel @channel_username or -100xxxx")
        return

    data = load_channels()
    user_id = str(message.from_user.id)
    if user_id in data and channel in data[user_id]:
        data[user_id].remove(channel)
        save_channels(data)
        bot.reply_to(message, f"✅ Channel `{channel}` removed!", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Channel not found!")

@bot.message_handler(commands=['showchannels'])
def show_channels(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return

    data = load_channels()
    user_id = str(message.from_user.id)
    channels = data.get(user_id, [])
    if channels:
        channel_list = '\n'.join(channels)
        bot.reply_to(message, f"📢 Your linked channels:\n\n{channel_list}")
    else:
        bot.reply_to(message, "❌ No channels linked yet.")

@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def broadcast(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        bot.reply_to(message, "❌ You're not authorized to use this bot.")
        return

    data = load_channels()
    user_id = str(message.from_user.id)
    channels = data.get(user_id, [])
    if not channels:
        bot.reply_to(message, "⚠️ No channels linked. Use /addchannel to add one.")
        return

    success = 0
    failed = 0

    for channel in channels:
        try:
            if message.content_type == 'text':
                bot.send_message(channel, message.text)
            elif message.content_type == 'photo':
                bot.send_photo(channel, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'video':
                bot.send_video(channel, message.video.file_id, caption=message.caption)
            elif message.content_type == 'document':
                bot.send_document(channel, message.document.file_id, caption=message.caption)
            success += 1
        except Exception as e:
            failed += 1
            print(f"❌ Failed to send to {channel}: {e}")

    bot.reply_to(message, f"✅ Sent to {success} channel(s)\n❌ Failed: {failed}")

bot.infinity_polling()
