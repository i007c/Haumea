#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Programmer 007

import telegram
from telegram import ChatAction, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
import logging
import time
import json
import requests
import os
import youtube_dl
import utube_search
import wget
import random
import string


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


ydl_opts = {'format': 'bestaudio/best', 'postprocessors': [
    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}


def get_info_audio(fild_search: str):
    global ydl_opts
    try:
        if fild_search.find("youtube.com") != -1 or fild_search.find("youtu.be") != -1:
            link_video = fild_search
        else:
            link_video = utube_search.search_on_utube(fild_search)[
                                                      0]["video_link"]

        ydl = youtube_dl.YoutubeDL(ydl_opts)
        result = ydl.extract_info(link_video, download=False)
        if 'entries' in result:
            video = result['entries'][0]
        else:
            video = result
        i1 = len(video["formats"]) - 1
        mp4_link = video["formats"][i1]["url"]
        title_video = video["title"]

        return {"mp4_link": mp4_link, "title_video": title_video}
    except Exception as err:
        print(err)
        return 0


def start(bot, context):
    chat_id = context.message.chat_id

    keyboard = [["🆘 help", "🧡 Donate"], ["Ⓜ️ Studio Bahram", "Report ❗️"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=False, resize_keyboard=True)
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    bot.send_message(chat_id=chat_id, text="درووود بر تو ای شخصی که اومده اهنگ دانلود کنه 😂\nشوخی کردم 😶\nخلاصه که اگه کمک می خوای بزن روی این  /help\nاگه هم بلدی که هیچی دیگه😑",
                     reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


def help(bot, context):
    try:
        chat_id = context.message.chat_id
        bot.send_chat_action(chat_id, ChatAction.TYPING)
        bot.send_message(chat_id=chat_id, text="اصل مطلب 👇🏻👇🏻\n\n1⃣ برای یافتن ویدیو ها این کار رو بکن:\n<code>/search name_music </code>\nبجای name_music اسم اهنگ یا ویدیو رو بنویس\n\n2⃣ حالا برای دانلود اهنگ ( فایل صوتی ویدیو ) :\nفقط کافیه اسمش یا لینک یوتوبش رو ارسال کنی 😶\n\n3️⃣ یه قابلیت هم هست که می توانی لینک مستقیم اهنگ رو بدی و من اونو برات آپلود کنم توی تلگرام \n اینطوری \n <code> /upload (link.mp3) </code>\n به‌ همین راحتی\n\nراستی یه سری به استودیو بهرام هم بزن 🤗\n/STUB\n@Studio_Bahram", parse_mode="HTML")
    except Exception as err:
        bot.send_chat_action(chat_id, ChatAction.TYPING)
        bot.send_message(chat_id=chat_id, text=str(err))


@run_async
def send_music(bot, context):
    chat_id = context.message.chat_id
    try:
        name_music = context.message.text

        bot.send_chat_action(chat_id, ChatAction.TYPING)
        msg = bot.send_message(
            chat_id=chat_id, text="دارم دنبال اهنگ میگردم یه کوچولو صبر کن")
        bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)
        info_video = get_info_audio(name_music)
        if info_video == 0:
            bot.send_message(
                chat_id=chat_id, text="خیلی شرمنده 😔 من نتونستم برات اهنگ رو دانلود کنم ")
        else:
            url = info_video["mp4_link"]
            title = info_video["title_video"]
            namefile = "".join(random.choices(
                string.ascii_lowercase + string.ascii_uppercase, k=27))

            bot.send_chat_action(chat_id, ChatAction.TYPING)
            msg = bot.edit_message_text(
                chat_id=chat_id, text="دارم اهنگ رو دانلود میکنم 😀\nیه کوچولو صبر کنی برات فرستادمش😅", message_id=msg.message_id)
            # Dowmload file mp4
            bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)
            wget.download(url, f"db/{namefile}.mp4")

            bot.send_chat_action(chat_id, ChatAction.TYPING)
            msg = bot.edit_message_text(
                text="خب داریم به جاهای خوبش میرسیم 😋\nاهنگ دانلود شد فقط باید تبدیلش کنم به فایل mp3 و برات بفرستمش زیاد طول نمیکشه بهت قول میدم\nاحتمالا الان که داری این خط رو می خونی دیگه برات فرستادمش 😂😂", chat_id=chat_id, message_id=msg.message_id)
            bot.send_chat_action(chat_id, ChatAction.UPLOAD_AUDIO)
            # Cover mp4 to mp3
            os.system(f"ffmpeg -i db/{namefile}.mp4 db/music-{namefile}.mp3")
            # delete file mp4
            os.system(f"rm db/{namefile}.mp4")
            # upload to telegram
            bot.send_audio(chat_id=chat_id, audio=open(
                f"db/music-{namefile}.mp3", "rb"), timeout=1000, title=title)
            # delete file mp3
            os.system(f"rm db/music-{namefile}.mp3")
            bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except Exception as err:
        bot.send_chat_action(chat_id, ChatAction.TYPING)
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
                chat_id=chat_id, text="دنبال اینی {} صب کن الان برات میفرستم".format(fild_search))
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
        bot.send_chat_action(chat_id, ChatAction.TYPING)
        bot.send_message(chat_id=chat_id, text=str(err))


@run_async
def upload_from_web(bot, context, args):
    chat_id = context.message.chat_id
    try:
        if len(args) < 0:
            bot.send_message(
                chat_id=chat_id, text="بعد از این دستور باید لینک دانلودتم بدی \nمثل این:\n\n <code>/upload (link.mp3) </code>", parse_mode="HTML")
        else:
            link_download = args[0]
            if link_download[len(link_download)-4:] == ".mp3":
                msg = bot.send_message(
                    chat_id=chat_id, text="الان برات میفرستمش")
                bot.send_audio(chat_id=chat_id, audio=link_download,
                               timeout=100, title="Your Music :)")
                bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            else:
                bot.send_message(chat_id=chat_id, text="فقط لینک های .mp3")
    except Exception as err:
        bot.send_chat_action(chat_id, ChatAction.TYPING)
        bot.edit_message_text(chat_id=chat_id, text=str(
            err), message_id=msg.message_id)


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
    bot.send_message(chat_id=chat_id, text="داداش یا ابجی 😶\nاینو دیگه نمی تونم تشخیص بدم خب 😑\nخلاصه که مرسی از اینکه می خوای حمایت کنی\n\nولی من دنبال حمایت مالی نیستم 😶\nهمین که به یکی از دوستاتم استودیو بهرام رو معرفی کنی بزرگترین حمایت رو به من و استودیو کردی\n\nSite : StudioBahram.ir\nTelegram : T.me/Studio_Bahram\nInstagram : instagram.com/Studio_Bahram.ir\nGitHub : github.com/Studio-Bahram\nDiscord : discord.gg/ZmGWTtZ")


def reporterr(bot, context):
    chat_id = context.message.chat_id
    bot.send_chat_action(chat_id, ChatAction.TYPING)
    bot.send_message(
        chat_id=chat_id, text="هرمشکلی بود فقط به خودم بگو 😁😅\nاینم ایدیمه\n@SSBahramBot")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    token = json.load(open("db/sec.json", "r"))["token"]
    updater = Updater(token, use_context=False)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text(
        ["/start", "/Start", "Start", "شروع", "آغاز", "/update"]), start))
    dp.add_handler(MessageHandler(Filters.text(
        ["راهنما", "کمک", "help", "/help", "کمکم کن", "🆘 help"]), help))
    dp.add_handler(CommandHandler(
        "search", search_on_youtube, pass_args=True))
    dp.add_handler(CommandHandler(
        "upload", upload_from_web, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text(
        ["Ⓜ️ Studio Bahram", "Studio Bahram", "استودیو بهرام", "بهرام", "استودیو", "سازنده", "/STUB"]), stb))
    dp.add_handler(MessageHandler(Filters.text(
        ["گزارش", "/report", "Report ❗️", "report", "Report"]), reporterr))
    dp.add_handler(MessageHandler(Filters.text(
        ["🧡 Donate", "حمایت", "donate", "/donate", "Donate"]), donate))
    dp.add_handler(MessageHandler(Filters.all, send_music))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
