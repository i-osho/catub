# By @feelded
import requests

from userbot import catub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions import yt_search

plugin_category = "useless"


@catub.cat_cmd(
    pattern="lyric ?(.*)",
    command=("lyric", plugin_category),
    info={
        "header": "Song lyrics searcher",
        "description": "if you want to provide artist name with song name, Will be better (Loser - Neoni)",
        "usage": [
            "{tr}lyric <song name>",
        ],
        "examples": [
            "{tr}lyric death bed",
        ],
    },
)
async def lyrics(odi):
    "To get song lyrics"
    songname = odi.pattern_match.group(1)
    if not songname:
        await edit_delete(odi, "`Give me a song name`", 6)
    else:
        await edit_or_reply(odi, f"`Searching lyrics for {songname} ...`")
        x = requests.get(f"https://apis.xditya.me/lyrics?song={songname}").json()
        artist = lyrics = ""
        try:
            name = x["name"]
            lyrics = x["lyrics"]
        except Exception:
            await edit_delete(odi, f"`No result found for {songname}.`", 6)

        yt = await yt_search(str(name))
        await edit_or_reply(
            odi, f"**[{name}]({yt}):**\n\n`{lyrics}`", link_preview=False
        )
