# Inline Ping by t.me/i_osho
import re
from datetime import datetime

from telethon.events import CallbackQuery

from ..Config import Config
from . import BOTLOG_CHATID, catub, reply_id

plugin_category = "tools"


@catub.cat_cmd(
    pattern="iping$",
    command=("iping", plugin_category),
    info={
        "header": "Checks bot ping via inline mode",
        "options": "Brah, why do dis exists",
        "usage": [
            "{tr}iping",
        ],
    },
)
async def edit_and_u_gay(osho):
    "Inline Ping"
    reply_to_id = await reply_id(osho)
    results = await osho.client.inline_query(Config.TG_BOT_USERNAME, "ping")
    await results[0].click(osho.chat_id, reply_to=reply_to_id, hide_via=True)
    await osho.delete()


@catub.tgbot.on(CallbackQuery(data=re.compile(b"ping")))
async def ping(event):
    start = datetime.now()
    life = await event.client.send_message(BOTLOG_CHATID, "Just For Ping")
    await life.delete()
    end = datetime.now()
    ms = str((end - start).microseconds / 1000)
    ping_data = f"「 𝗣𝗶𝗻𝗴 」 {ms}ms"
    await event.answer(ping_data, cache_time=0, alert=True)
