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

def save_error_to_log(error_message):
    error_message = str(error_message)
    with open("db/errors.txt", "a") as el:
        el.write(str(error_message)+"\nError time: "+str(datetime.datetime.now())+"\n\n")


def download_mp3(fild_search: str):
    try:
        if os.path.exists("database/audio.mp3"):
            os.remove("database/audio.mp3")
        
        if os.path.exists("database/video.mp4"):
            os.remove("database/video.mp4")

        if fild_search.find("youtube.com") != -1 or fild_search.find("youtu.be") != -1:
            link_video = fild_search
        else:
            link_video = utube_search.search_on_utube(fild_search)[0]["video_link"]

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": "database/video.mkv",
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mkv",
            }]
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link_video])
        
        audio = ffmpeg.input("database/video.mkv")
        audio = ffmpeg.output(audio, "database/audio.mp3")
        ffmpeg.run(audio)
        return {"audio_path": "database/audio.mp3", "audio_name": "audio.mp3"}

    except Exception:
        save_error_to_log(traceback.format_exc())
        return False


def start(bot, context):
    chat_id = context.message.chat_id

    keyboard = [["🆘 help", "🧡 Donate"], ["Ⓜ️ Studio Bahram", "Report ❗️"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=False, resize_keyboard=True)
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="درووود بر تو ای شخصی که اومده اهنگ دانلود کنه 😂\nشوخی کردم 😶\nخلاصه که اگه کمک می خوای بزن روی این  /help\nاگه هم بلدی که هیچی دیگه😑",
                     reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


def help(bot, context):
    chat_id = context.message.chat_id
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="اصل مطلب 👇🏻👇🏻\n\n1⃣ برای یافتن ویدیو ها این کار رو بکن:\n<code>/search name_music </code>\nبجای name_music اسم اهنگ یا ویدیو رو بنویس\n\n2⃣ حالا برای دانلود اهنگ ( فایل صوتی ویدیو ) :\nفقط کافیه اسمش یا لینک یوتوبش رو ارسال کنی 😶\n\n3️⃣ یه قابلیت هم هست که می توانی لینک مستقیم اهنگ رو بدی و من اونو برات آپلود کنم توی تلگرام \n اینطوری \n <code> /upload (link.mp3) </code>\n به‌ همین راحتی\n\nراستی یه سری به استودیو بهرام هم بزن 🤗\n/STUB\n@Studio_Bahram", parse_mode="HTML")


@run_async
def send_music(bot, context):
    chat_id = context.message.chat_id
    try:
        name_music = context.message.text

        bot.send_chat_action(chat_id, ChatAction.TYPING)
        msg = bot.send_message(chat_id=chat_id, text="درحال دانلود موسیقی مدنظر شما\nلطفا کمی صبر کنید")
        audio_data = download_mp3(name_music)

        if not audio_data:
            bot.send_message(
                chat_id=chat_id, text="خیلی شرمنده 😔 من نتونستم برات اهنگ رو دانلود کنم ")
        else:
            bot.send_chat_action(chat_id, ChatAction.TYPING)
            msg = bot.edit_message_text(chat_id=chat_id, text="درحال اپلود موسیقی مورد نظر شما", message_id=msg.message_id)
            
            bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)

            bot.send_audio(chat_id=chat_id, audio=open(audio_data["audio_path"], "rb"), timeout=1000)

            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except Exception as err:
        save_error_to_log(traceback.format_exc())
        bot.send_message(chat_id=chat_id, text=str(err))


@run_async
def search_on_youtube(bot, context, args):
    try:
        chat_id = context.message.chat_id
        if len(args) > 0:
            fild_search = ""
            for n in args:
                fild_search += n + " "

            msg = bot.send_message(
                chat_id=chat_id, text="متن جستوجوی شما: {}".format(fild_search))
            list_search = utube_search.search_on_utube(fild_search, 10)
            if list_search == None:
                bot.edit_message_text(
                    chat_id=chat_id, text="فک‌ کنم داری اشتباه میزنیا 😶\nمن که چیزی پیدا نکردم 🤐\n\nیه چیز دیگه رو تست کن", message_id=msg.message_id)
            else:
                textsend = ""
                nm = 1
                for item in list_search:
                    video_time = item["video_time"]
                    video_title = item["video_title"][:31]
                    video_link = item["video_link"]
                    textsend += f"{nm})  <a href='{video_link}' >{video_title}</a>  {video_time}\n------------------------------------------------------------\n"
                    nm += 1

                bot.edit_message_text(
                    chat_id=chat_id, text=textsend, parse_mode="HTML", message_id=msg.message_id)
        else:
            bot.send_message(
                chat_id=chat_id, text="حس میکنم داری اشتباه میزنی 😑😐 \n\n<code> /search اسم اهنگ </code>\n\n اینطوریه", parse_mode="HTML")
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
    updater = Updater(token) # , use_context=False

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text(
        ["/start", "/Start", "Start", "/update"]), start))
    dp.add_handler(MessageHandler(Filters.text(
        ["راهنما", "help", "/help", "🆘 help"]), help))
    dp.add_handler(CommandHandler(
        "search", search_on_youtube, pass_args=True))

    dp.add_handler(MessageHandler(Filters.text(
        ["Ⓜ️ Studio Bahram", "Studio Bahram", "استودیو بهرام", "بهرام", "استودیو", "سازنده", "/STUB"]), stb))
    dp.add_handler(MessageHandler(Filters.text(
        ["/report", "Report ❗️", "report", "Report"]), reporterr))
    dp.add_handler(MessageHandler(Filters.text(
        ["🧡 Donate", "حمایت", "donate", "/donate", "Donate"]), donate))
    dp.add_handler(MessageHandler(Filters.all, send_music))


    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    if not os.path.exists("database"):
        os.makedirs("database")
    
    if not os.path.exists("db"):
        os.makedirs("db")

    main()