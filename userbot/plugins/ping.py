# ==================================================================================================
# Made by https://t.me/o_s_h_o_r_a_j
# It is simillar to my other plugin 'pping' (ping with media)
# This randomly chooses from the given media links, i.e 'multi-pping', in short 'mping'
# Now with PING_TEMPLATE
import asyncio
import random
from datetime import datetime

from userbot import catub

from ..core.managers import edit_or_reply
from ..sql_helper.globals import gvarstatus
from . import catub, mention, reply_id

plugin_category = "tools"

# ===============================================
normaltext = "1234567890."
pingfont = [
    "𝟏",
    "𝟐",
    "𝟑",
    "𝟒",
    "𝟓",
    "𝟔",
    "𝟕",
    "𝟖",
    "𝟗",
    "𝟎",
    "•",
]

# ===============================================


@catub.cat_cmd(
    pattern="ping( -a|$)",
    command=("ping", plugin_category),
    info={
        "header": "check how long it takes to ping your userbot",
        "flags": {"-a": "average ping"},
        "option": "change ping design using `PING_TEMPLATE` (dv)",
        "usage": ["{tr}ping", "{tr}ping -a"],
    },
)
async def _(event):
    "To check ping"
    flag = event.pattern_match.group(1)
    start = datetime.now()
    catevent = await edit_or_reply(event, f"`Checking`")
    end = datetime.now()
    ms = str((end - start).microseconds / 1000)
    for normal in ms:
        if normal in normaltext:
            pingchars = pingfont[normaltext.index(normal)]
            ms = ms.replace(normal, pingchars)
    my = f"𝔑𝔬𝔴, 𝔏𝔢𝔱 𝔗𝔥𝔢 𝔊𝔞𝔪𝔢 𝔅𝔢𝔤𝔦𝔫!!\n`{ms}` 𝔪𝔰\nℜ𝔲𝔩𝔢𝔰 𝔅𝔶 **{mention}**"
    ping_caption = gvarstatus("PING_TEMPLATE") or my

    if flag == " -a":
        catevent = await edit_or_reply(event, "`!....`")
        await asyncio.sleep(0.3)
        await catevent.edit("`..!..`")
        await asyncio.sleep(0.3)
        await catevent.edit("`....!`")
        end = datetime.now()
        tms = (end - start).microseconds / 1000
        ms = str(round((tms - 0.6) / 3, 3))
        for normal in ms:
            if normal in normaltext:
                pingchars = pingfont[normaltext.index(normal)]
                ms = ms.replace(normal, pingchars)
        await catevent.edit(
            f"<b>☞ Average Pong!<b>\n➥ <code>{ms} ms<code>",
            parse_mode="html",
        )
    else:
        ping_caption = gvarstatus("PING_TEMPLATE") or my
        caption = ping_caption.format(ping=ms, mention=mention)
        await catevent.edit(caption)


# ===============================================


@catub.cat_cmd(
    pattern="mping$",
    command=("mping", plugin_category),
    info={
        "header": "Checks the latency of userbot from the server, with a media",
        "option": "change ping design using `PING_TEMPLATE` (dv)",
        "usage": "{tr}mping",
    },
)
async def _(event):
    "Shows ping with a given random media"
    if event.fwd_from:
        return
    reply_to_id = await reply_id(event)
    # add space b/w each telegraph link
    PING_PICS = (
        gvarstatus("PING_PICS")
        or "https://telegra.ph/file/1328d62db93ad22b69ba2.jpg https://telegra.ph/file/b2da6e4c55dd29600e4ed.jpg"
    )
    PING_PICS = PING_PICS.rsplit(" ")
    start = datetime.now()
    await edit_or_reply(event, f"`Checking`")
    end = datetime.now()
    ms = str((end - start).microseconds / 1000)
    for normal in ms:
        if normal in normaltext:
            pingchars = pingfont[normaltext.index(normal)]
            ms = ms.replace(normal, pingchars)
    my = f"𝔑𝔬𝔴, 𝔏𝔢𝔱 𝔗𝔥𝔢 𝔊𝔞𝔪𝔢 𝔅𝔢𝔤𝔦𝔫!!\n`{ms}` 𝔪𝔰\nℜ𝔲𝔩𝔢𝔰 𝔅𝔶 **{mention}**"
    ping_caption = gvarstatus("PING_TEMPLATE") or my
    caption = ping_caption.format(ping=ms, mention=mention)
    PING_PIC = random.choice(PING_PICS)
    if PING_PIC:
        while PING_PIC == "":
            try:
                PING_PIC = random.choice(PING_PICS)
            except IndexError:
                pass
        await event.delete()
        await event.client.send_file(
            event.chat_id,
            PING_PIC,
            caption=caption,
            reply_to=reply_to_id,
            link_preview=False,
            allow_cache=True,
        )


# ==================================================================================================
