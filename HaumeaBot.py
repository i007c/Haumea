#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Programmer 007

import telegram
from telegram import ChatAction, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
import json
import os
import youtube_dl
import utube_search
import datetime
import traceback
import ffmpeg
import random
import string

def get_random_string(l:int=20):
    """
    l: The length of your desired string
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=l))

def save_error_to_log(error_message):
    error_message = str(error_message)
    with open("db/errors.txt", "a") as el:
        el.write(str(error_message)+"\nError time: "+str(datetime.datetime.now())+"\n\n")


def download_file(video_link: str, client_dirname: str):
    try:
        video_name = get_random_string()
        audio_name = get_random_string()

        
        
        if video_link.find("http") == -1:
            return {"status":"Error","msg":"متن ارسال شده صحیح نمی باشد\nباید لینک باشد"}

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": f"database/{client_dirname}/{video_name}.%(ext)s",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_link])
        
        for root, dirs, files in os.walk(f"database/{client_dirname}"):
            for f in files:
                if f.find(video_name) != -1:
                    video_name = f
                    break
            else:
                return {"status":"Error","msg":"خطا در دریافت ویدیو"}
                    
        
        audio = ffmpeg.input(f"database/{client_dirname}/{video_name}")
        audio = ffmpeg.output(audio, f"database/{client_dirname}/{audio_name}.mp3")
        ffmpeg.run(audio)

        return {
            "status":"Successful",
            "video":
            {
                "name": video_name,
                "path": f"database/{client_dirname}/{video_name}"
            },
            "audio":
            {
                "name": audio_name + ".mp3",
                "path": f"database/{client_dirname}/{audio_name}.mp3"
            }
        }

    except Exception:
        error = traceback.format_exc()
        save_error_to_log(error)
        return {"status":"Error","msg": str(error)}


def start(bot, context):
    chat_id = context.message.chat_id

    keyboard = [["🧡 Donate"], ["Ⓜ️ Studio Bahram", "Report ❗️"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=False, resize_keyboard=True)
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="هاومیا، رباتی برای دانلود صدای ویدیو های یوتیوب و دیگر سایت ها\nلینک ویدیو یوتیوب مدنظر  خود را ارسال نمونه و فایل ان را دریافت کنید به سادگی",
                     reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

@run_async
def send_file(bot, context):
    chat_id = context.message.chat_id
    try:
        if not os.path.exists(f"database/{chat_id}"):
            os.makedirs(f"database/{chat_id}")

        vurl = context.message.text

        bot.send_chat_action(chat_id, ChatAction.TYPING)
        msg = bot.send_message(chat_id=chat_id, text="درحال دانلود موسیقی مدنظر شما\nلطفا کمی صبر کنید")
        data_files = download_file(video_link=vurl,client_dirname=str(chat_id))

        if data_files["status"] == "Error":
            error = data_files["msg"]
            bot.send_message(chat_id=chat_id, text=f"Error:\n\n{error}")
        else:
            bot.send_chat_action(chat_id, ChatAction.TYPING)
            msg = bot.edit_message_text(chat_id=chat_id, text="درحال اپلود موسیقی مورد نظر شما", message_id=msg.message_id)
            
            if os.path.getsize(data_files["audio"]["path"]) < 50000000:
                bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)
                bot.send_audio(chat_id=chat_id, audio=open(data_files["audio"]["path"], "rb"), timeout=1000)
            else:
                bot.send_message(chat_id=chat_id, text="فایل بسیار بزرگ است")

            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)

            if os.path.exists(data_files["video"]["path"]):
                os.remove(data_files["video"]["path"])
            
            if os.path.exists(data_files["audio"]["path"]):
                os.remove(data_files["audio"]["path"])

    except Exception as err:
        save_error_to_log(traceback.format_exc())
        bot.send_message(chat_id=chat_id, text=str(err))


def stb(bot, context):
    chat_id = context.message.chat_id
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    keyboard = [
                [
                    InlineKeyboardButton("سایت", "https://StudioBahram.ir"),
                    InlineKeyboardButton(
                        "گیت هاب", "https://github.com/Studio-Bahram")
                ],
                [
                    InlineKeyboardButton(
                        "تلگرام", "https://T.me/Studio_Bahram"),
                    InlineKeyboardButton(
                        "دیسکورد", "https://discord.gg/ZmGWTtZ"),
                    InlineKeyboardButton(
                        "اینستاگرام", "https://instagram.com/Studio_Bahram.ir")
                ]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=chat_id, text="تو که تا اینجا اومدی 😑\nمنم که مجبورت نکردم عضو بشی ولی خب اگه تو یکی از اینا عضو بشی حمایت بزرگی به من و استودیو بهرام کردی\nسپاس با قلب برای تو ❤️", reply_markup=reply_markup)


def donate(bot, context):
    chat_id = context.message.chat_id
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    text = "پول بهترین دلگرمی و حمایت نیست\n اما با این کار شما من را حمایت می کنید در تولید محصولاتی بهتر و باکیفیت بیشتر \n اگر توان حمایت مالی ندارید اصلا مهم نیست \n همین که در کنار ما هستید بزرگ ترین حمایت است \n لینک حمایت مالی : https://idpay.ir/i007c"
    bot.send_message(chat_id=chat_id, text=text)


def reporterr(bot, context):
    chat_id = context.message.chat_id
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="شما می توانید مشکلات و باگ های ربات را به ما گزارش دهید :) \n @i007x")


def main():
    token = json.load(open("db/sec.json", "r"))["token"]
    updater = Updater(token, use_context=False)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text(
        ["/start", "/Start", "Start", "/update"]), start))

    dp.add_handler(MessageHandler(Filters.text(
        ["Ⓜ️ Studio Bahram", "Studio Bahram", "استودیو بهرام", "بهرام", "استودیو", "سازنده", "/STUB"]), stb))
    dp.add_handler(MessageHandler(Filters.text(
        ["/report", "Report ❗️", "report", "Report"]), reporterr))
    dp.add_handler(MessageHandler(Filters.text(
        ["🧡 Donate", "حمایت", "donate", "/donate", "Donate"]), donate))
    dp.add_handler(MessageHandler(Filters.all, send_file))


    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    if not os.path.exists("database"):
        os.makedirs("database")
    
    if not os.path.exists("db"):
        os.makedirs("db")

    main()