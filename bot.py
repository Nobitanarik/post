import telebot
import json
import os

# Bot Token
BOT_TOKEN = "7798896914:AAFgwT4vdRfnWXLE-_e-mHDG4t_SJbZX3-o"
bot = telebot.TeleBot(BOT_TOKEN)

# Authorized Users (Your 4 Telegram IDs)
AUTHORIZED_USERS = [5018478747, 2005048275, 7750385522, 7912929481]

# File to store channel list
CHANNEL_FILE = "channels.json"

def load_channels():
    if not os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, 'w') as f:
            json.dump([], f)
    with open(CHANNEL_FILE, 'r') as f:
        return json.load(f)

def save_channels(data):
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "👋 Welcome! Send any message, and I'll post it to all added channels!")

@bot.message_handler(commands=['addchannel'])
def add_channel(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return bot.reply_to(message, "🚫 You are not authorized!")
    
    parts = message.text.split()
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Usage: /addchannel @channelusername")
    
    channel = parts[1]
    channels = load_channels()
    if channel not in channels:
        channels.append(channel)
        save_channels(channels)
        bot.reply_to(message, f"✅ Channel {channel} added!")
    else:
        bot.reply_to(message, "⚠️ This channel is already added!")

@bot.message_handler(commands=['removechannel'])
def remove_channel(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return bot.reply_to(message, "🚫 You are not authorized!")
    
    parts = message.text.split()
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ Usage: /removechannel @channelusername")
    
    channel = parts[1]
    channels = load_channels()
    if channel in channels:
        channels.remove(channel)
        save_channels(channels)
        bot.reply_to(message, f"✅ Channel {channel} removed!")
    else:
        bot.reply_to(message, "⚠️ This channel is not in the list!")

@bot.message_handler(commands=['showchannels'])
def show_channels(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return bot.reply_to(message, "🚫 You are not authorized!")
    
    channels = load_channels()
    if not channels:
        bot.reply_to(message, "⚠️ No channels added yet!")
    else:
        bot.reply_to(message, "📢 Added Channels:\n" + "\n".join(channels))

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'animation', 'poll'])
def broadcast_post(message):
    if message.from_user.id not in AUTHORIZED_USERS:
        return bot.reply_to(message, "🚫 You are not authorized!")
    
    channels = load_channels()
    if not channels:
        return bot.reply_to(message, "⚠️ No channels added yet!")
    
    sent_count = 0
    failed_count = 0
    
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
            elif message.content_type == 'audio':
                bot.send_audio(channel, message.audio.file_id, caption=message.caption)
            elif message.content_type == 'voice':
                bot.send_voice(channel, message.voice.file_id)
            elif message.content_type == 'animation':
                bot.send_animation(channel, message.animation.file_id, caption=message.caption)
            elif message.content_type == 'poll':
                bot.send_poll(channel, message.poll.question, options=[o.text for o in message.poll.options])
            
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send to {channel}: {e}")
    
    bot.reply_to(message, f"✅ Sent to {sent_count} channels\n❌ Failed: {failed_count}")

bot.polling(none_stop=True)
