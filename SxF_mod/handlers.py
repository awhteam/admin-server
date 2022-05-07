from config import Config
from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client as Bot
import regex
import traceback
import os

WATCH_MESSAGES=[]


@Bot.on_message(filters.command(["start"]))
async def start(bot: Bot, message: Message):
    await message.reply(text="بات زندس", quote=True)



@Bot.on_message(filters.command(["watch"]))
async def watch_command(bot: Bot, message: Message):
    chat="Latest_Ongoing_Airing_Anime"
    postId= int(message.command[1].split("Latest_Ongoing_Airing_Anime/")[-1])
    await message.reply(text=postId, quote=True)
    WATCH_MESSAGES.append(postId)

