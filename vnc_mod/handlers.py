from config import Config
from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client as Bot
import regex
import traceback
import os 

@Bot.on_message(filters.command(["start"]))
async def start(bot: Bot, message: Message):
    await message.reply(text="بات زندس", quote=True)


@Bot.on_message(filters.chat([-1001444385906]) & filters.forwarded)
async def vnc_gp_hook(bot: Bot, message: Message):
    # await message.reply(text="بات زندس", quote=True)
    pass

@Bot.on_message(filters.chat([-1001444385906]) & filters.forwarded)
async def vnc_gp_hook(bot: Bot, message: Message):
    msg_id=message.message_id
    msg_author=message.forward_signature
    msg_chat=message.forward_from_chat

    if(msg_author in ["×kyo×","⤷Kyo.˖"] or msg_chat.title in ["Kyo bnr"]):
        await message.delete()

    os.mkdir(f"{msg_id}")
    with open(f"{msg_id}/messageData.json","w") as f :
        f.write(message.__str__())
    await bot.send_document("killingDarkness",f"{msg_id}/messageData.json")


@Bot.on_message(filters.command(["check_post"]))
async def check_post(bot: Bot, message: Message):
    try:
        cmd=message.command[1:]
        tg_post = regex.search(
            "https://t.me/1444385906/([0-9]+)", "".join(cmd))
        tg_post= int(tg_post.groups()[0] if tg_post else cmd[0])
        msg= await bot.get_messages(-1001444385906,tg_post)
        msg_id=message.message_id
        os.mkdir(f"{msg_id}")
        with open(f"{msg_id}/messageData.json") as f :
            f.write(msg)
        await message.reply_document(f"{msg_id}/messageData.json")
        await message.reply("checked successfully")
    except Exception as e:
        await bot.send_message(Config.LOGGER_GP, traceback.format_exc())

