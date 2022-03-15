from config import Config
from pyrogram import filters
from pyrogram.types import Message
from pyrogram import Client as Bot
import regex
import traceback
import os


FLAGGED_MESSAGES=[]

@Bot.on_message(filters.command(["start"]))
async def start(bot: Bot, message: Message):
    await message.reply(text="بات زندس", quote=True)


@Bot.on_message(filters.chat([-1001444385906]) & filters.forwarded)
async def vnc_gp_hook(bot: Bot, message: Message):
    # await message.reply(text="بات زندس", quote=True)
    pass

@Bot.on_message(filters.chat(["vanitas_no_shuki"]) & filters.forwarded)
async def flag_tab_messages(bot: Bot, message: Message):
    msg_chat = message.forward_from_chat
    channel_msg_id = message.forward_from_message_id
    msg_author = message.author_signature
    print(message)
    if(msg_author in ["×kyo×", "⤷Kyo.˖","Darkido"] or msg_chat.title in ["Kyo bnr"]):
        FLAGGED_MESSAGES.append(channel_msg_id)
        print("hey it is added")
        await bot.send_message("killingDarkness","hey it triggered")


@Bot.on_message(filters.chat([-1001444385906]) & filters.forwarded)
async def vnc_gp_hook(bot: Bot, message: Message):
    channel_msg_id = message.forward_from_message_id
    if(channel_msg_id in FLAGGED_MESSAGES):
        await message.delete()
        FLAGGED_MESSAGES.remove(channel_msg_id)
        return "I'm done"

    msg_chat = message.forward_from_chat
    channel_msg = await bot.get_messages("vanitas_no_shuki", channel_msg_id)
    msg_author = channel_msg.author_signature
    if(msg_author in ["×kyo×", "⤷Kyo.˖"] or msg_chat.title in ["Kyo bnr"]):
        await bot.send_message("killingDarkness","heh you were wrong")
        await message.delete()


# forward_from_message_id
@Bot.on_message(filters.command(["check_post"]))
async def check_post(bot: Bot, message: Message):
    try:
        cmd = message.command[1:]
        tg_toks = regex.search(
            "https://t.me/c?\/?([a-zA-Z0-9_]*)/([0-9]+)", "".join(cmd))
        if not tg_toks:
            return
        tg_toks= tg_toks.groups()
        tg_post = int(tg_toks[1])
        tg_post_chat = tg_toks[0]
        if(tg_post_chat[:4] != "-100" and tg_post_chat[1:].isdigit()):
            tg_post_chat = int(f"-100{tg_post_chat}")
        msg = await bot.get_messages(tg_post_chat, tg_post)
        print(msg)
        msg_id = message.message_id
        os.mkdir(f"{msg_id}")
        with open(f"{msg_id}/messageData.json","w") as f:
            f.write(msg.__str__())
        await message.reply_document(f"{msg_id}/messageData.json")
        await message.reply("checked successfully")
    except Exception as e:
        await bot.send_message(Config.LOGGER_GP, traceback.format_exc())
