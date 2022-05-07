#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from plugins.responses import Response
import time
import math
import sys

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join(["█" for i in range(math.floor(percentage / 5))]),
            ''.join(["░" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(text=f"{ud_type}\n {tmp}")
        except:
            exc_info = sys.exc_info()
            print(exc_info)


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]



async def download_file(message,real_msg,formats=None):
    try:
        filename = message.document.file_name.replace("_", " ")
    except:
        filename = message.video.file_name.replace("_", " ")

    print(filename)
    if(formats!=None):
        if(filename[-3:] not in formats):
            return(None,"error")
    msg = await real_msg.reply(text=f"Received {filename}", quote=True)
    if(not os.path.exists(filename)):
        start_time = time.time()
        path = await message.download(file_name=filename, progress=progress_for_pyrogram,
                                    progress_args=(f"Downloading {filename}",  msg, start_time))

        if(path==None):
            await msg.edit(Response.DOWNLOAD_FAILED)
            return
        os.system(f"mv \"{path}\" .")
    return (filename,msg)





