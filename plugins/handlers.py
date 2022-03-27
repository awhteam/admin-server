#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from config import Config
from plugins.responses import Response
from pyrogram import filters
from pyrogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client as Bot
import regex
from database.models import AnimeV2
from database.database import SessionLocal
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified
import traceback
from services.anime import update_files



@Bot.on_message(filters.command(["start"]))
async def start(bot: Bot, message: Message):
    await message.reply(text="بات زندس", quote=True)


@Bot.on_message(filters.command(["chat_id"]))
async def get_chatid(bot: Bot, message: Message):
    await message.reply(text=message.chat.id, quote=True)


@Bot.on_message(filters.command(["msg_id"]))
async def get_message_id(bot: Bot, message: Message):
    await message.reply(text=message.reply_to_message.message_id, quote=True)


@Bot.on_message(filters.command(["batch_update"]))
async def manual_batch_update(bot: Bot, message: Message):
    try:
        cmd=message.command[1:]
        tg_post = regex.search(
            "https://t.me/animworlddl/([0-9]+)", "".join(cmd))
        tg_post= int(tg_post.groups()[0] if tg_post else cmd[0])
        messages= await bot.get_messages("animworlddl",range(tg_post,tg_post+200))
        for msg in messages:
            await channel_hook(bot,msg)
        await message.reply("updated successfully")
    except Exception as e:
        await bot.send_message(Config.LOGGER_GP, traceback.format_exc())




@Bot.on_message(filters.command(["update_post"]))
async def manual_update(bot: Bot, message: Message):
    try:
        cmd=message.command[1:]
        tg_post = regex.search(
            "https://t.me/animworlddl/([0-9]+)", "".join(cmd))
        tg_post= int(tg_post.groups()[0] if tg_post else cmd[0])
        msg= await bot.get_messages("animworlddl",tg_post)
        await channel_hook(bot,msg)
        await message.reply("updated successfully")
    except Exception as e:
        await bot.send_message(Config.LOGGER_GP, traceback.format_exc())


@Bot.on_message(filters.chat(["animworlddl"]) & ~filters.edited)
async def channel_hook(bot: Bot, message: Message):
    try:
        if(not message.caption):
            return
        post_text = str(message.caption)
        post_urls = [x.url for x in message.caption_entities if x.url]
        malId = regex.search(
            "https://myanimelist.net/anime/([0-9]+)/", "\n".join(post_urls))
        if(malId):
            malId = int(malId.groups()[0])
            await update_files(malId,message)
        else:
            name, year = extract_name(post_text)
            name_q = name.split(" ")[0]
            query = AnimeV2.query.filter(AnimeV2.title.english.ilike(
                f'%{name_q}%') | AnimeV2.title.romaji.ilike(f'%{name_q}%'), AnimeV2.year == year)
            animeHa = query.all()
            print(animeHa)
            nw_msg = f"**NEW UPDATE**\nAnime: {name} {year}\nTelegram post: https://t.me/{message.chat.username}/{message.message_id}"
            await bot.send_message(
                Config.UPDATES_CHANNEL, nw_msg,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(
                            f"{anime.title.romaji} {anime.year}", callback_data=f"new_update {anime.mal_id}")]
                        for anime in animeHa
                    ]))
    except Exception as e:
        await bot.send_message(Config.LOGGER_GP, traceback.format_exc())

@Bot.on_callback_query(filters.regex("new_update"))
async def answer_new_update_queries(bot: Bot, query: CallbackQuery):
    anime_id = query.data.split()[1]
    post = regex.search(
        "https://t.me/([A-Za-z0-9_]+)/([0-9]+)", query.message.text).groups()
    post_msg = await bot.get_messages(post[0], int(post[1]))
    await update_files(anime_id,post_msg)
    await query.message.delete()

def extract_name(text):
    name = regex.search("🔥\s*([^🍁🍀☀️❄️☘️☘☀*]*)", text).groups()[0].split(
        "\n")[0].split("[")[0].split("(")[0].replace("Movie", "").strip()
    year = regex.search(
        "(🍁|🍀|☀️|❄️|☘️|☘|☀)\s*[^0-9]*([0-9]+)", text).groups()[1]
    print(f"{name} {year}")
    return (name, year)

