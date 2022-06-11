from config import Config
from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client as Bot
import regex
import traceback
import os
from SxF_mod.utils import download_file
from glob import glob
WATCH_MESSAGES = []
FINISHED_FILES = []


@Bot.on_message(filters.command(["start"]))
async def start(bot: Bot, message: Message):
    await message.reply(text="بات زندس", quote=True)


@Bot.on_message(filters.command(["watch"]))
async def watch_command(bot: Bot, message: Message):
    chat = "Latest_Ongoing_Airing_Anime"
    postId = int(message.command[1].split("Latest_Ongoing_Airing_Anime/")[-1])
    await message.reply(text=postId, quote=True)
    WATCH_MESSAGES.append(postId)


@Bot.on_message(filters.command(["gdown"]))
async def gdown_command(bot: Bot, message: Message):
    unique_id = f"{message.chat.id}_{message.message_id}"
    folder = f"gdown_{unique_id}"
    os.system(f"mkdir {folder}")
    cmd = " ".join(message.command[1:])
    toks = cmd.split('|')
    url = toks[0].strip()
    filename = toks[1].strip()
    gid = None
    if("/file/d/" in url):
        gid = url.split("/file/d/")[1].split("/")[0]
    elif("id=" in url):
        gid = url.split("id=")[1].split("/")[0].split("&")[0]
    os.system(f'cd {folder} && gdown --id "{gid}"')
    for file in glob(f"{folder}/*.mkv"):
        os.system(f'mv "{file}" "{filename}"')
        await message.reply_document(filename)


@Bot.on_message(filters.command(["rename"]))
async def rename_command(bot: Bot, message: Message):
    unique_id = f"{message.chat.id}_{message.message_id}"
    folder = f"rename_{unique_id}"
    os.system(f"mkdir {folder}")
    new_filename = " ".join(message.command[1:]).strip()
    filename, msg2 = await download_file(message.reply_to_message, message)
    os.system(
        f'mv "{filename}" "{new_filename}" && mv "{new_filename}" {folder} ')
    await message.reply_document(f"{folder}/{new_filename}")


file_names = {
    "WebDL": "[SpyxFamilyChannel] Spy x Family - 0{0} ({q} web-dl)"
}


@Bot.on_message(filters.command(["dl"]))
async def dl_command(bot: Bot, message: Message):
    toks = message.command[1].split("/")
    chat = toks[-2]
    postId = int(toks[-1])
    msg = await bot.get_messages(chat, postId)
    filename, msg2 = await download_file(msg, message)
    anime_name = filename.split("]")[1].strip()
    anime_name = anime_name.replace("[", "(").replace("]", ")")
    await message.reply(text=f"Got it {filename}", quote=True)
    ver = " "
    if("WebDL" in chat):
        ver = " web-dl"
    new_filename = f'[SpyxFamilyChannel] {anime_name.split(")")[0]}{ver}).mkv'
    await message.reply(text=f"Changing it to {new_filename}", quote=True)
    os.system(f'mv "{filename}" "{new_filename}"')
    await message.reply_document(f"{new_filename}")
    await msg2.delete()




@Bot.on_message(filters.chat([-1001225416353]) & filters.document,group=1)
async def airing_anime_hook(bot: Bot, message: Message):
    cap=message.caption
    toks=cap.split("(")[0].strip().split("-")
    epi=toks[1].strip()
    q= regex.search("\(([0-9xp ]*)[^)]*\)",cap).groups()[0]
    new_filename = f'[SpyxFamilyChannel] Spy x Family - {epi} ({q}).mkv'
    msg= await message.reply(f"Changing to {new_filename}")
    cap=f"[[SpyxFamilyChannel](https://t.me/SpyXFamilyChannel)] Spy x Family - {epi} ({q})\n#Ep{epi} #Season01 #{q.replace(' ',' #')}"
    filename, msg2 = await download_file(message, msg)
    os.system(f'mv "{filename}" "{new_filename}"')
    await msg.reply_document(f"{new_filename}",caption=cap)
    await msg2.delete()
    await msg.delete()

    
