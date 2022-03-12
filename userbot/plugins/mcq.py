import random

from userbot import catub

from ..core.managers import edit_delete
from ..helpers.utils import reply_id

plugin_category = "extra"


@catub.cat_cmd(
    pattern="mcq ?(.*)",
    command=("mcq", plugin_category),
    info={
        "header": "Chooses a random item in the given options, give a comma ',' to add multiple option",
        "usage": ["{tr}mcq <options>", "{tr}mcq a,b,c,d", "{tr}mcq cat,dog,life,death"],
    },
)
async def Gay(event):
    "Tukka bazi"
    if event.fwd_from:
        return
    inp = event.pattern_match.group(1)
    await reply_id(event)
    if not inp:
        return await edit_delete(event, "`What to choose from`", 15)
    options = inp.split(",")
    await event.edit(f"**Input :** `{inp}`\n**Result :** `{random.choice(options)}`")
