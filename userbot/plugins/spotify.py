import asyncio
import os
import re
import time
import urllib.request

import lyricsgenius
import requests
import ujson
from PIL import Image, ImageEnhance, ImageFilter
from telethon import events
from telethon.errors import AboutTooLongError, FloodWaitError
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.custom import Button
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.functions.users import GetFullUserRequest
from validators.url import url

from userbot.core.logger import logging

from ..sql_helper.globals import gvarstatus
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions.functions import (
    delete_conv,
    ellipse_create,
    ellipse_layout_create,
    make_inline,
    text_draw,
)
from ..helpers.tools import post_to_telegraph
from ..sql_helper import global_collectionjson as glob_db
from . import BOTLOG, BOTLOG_CHATID, Config, catub, reply_id

SPOTIFY_CLIENT_ID = gvarstatus("S_ID")
SPOTIFY_CLIENT_SECRET = gvarstatus("S_S")


LOGS = logging.getLogger(__name__)


plugin_category = "misc"


SP_DATABASE = None  # Main DB (Class Database)
# Saves Auth data cuz heroku doesn't have persistent storage
try:
    SPOTIFY_DB = glob_db.get_collection("SP_DATA").json
except AttributeError:
    SPOTIFY_DB = None


USER_INITIAL_BIO = {}  # Saves Users Original Bio
PATH = "userbot/cache/spotify_database.json"

# [---------------------------] Constants [------------------------------]
KEY = "🎶"
BIOS = [
    KEY + " Vibing : {interpret} - {title}",
    KEY + " : {interpret} - {title}",
    KEY + " Vibing : {title}",
    KEY + " : {title}",
]
OFFSET = 1
# reduce the OFFSET from our actual 70 character limit
LIMIT = 70 - OFFSET
# [----------------------------------------------------------------------]

class Database:
    def __init__(self):
        if not os.path.exists(PATH):
            if SPOTIFY_DB is None:
                return
            if db_ := SPOTIFY_DB.get("data"):
                access_token = db_.get("access_token")
                refresh_token = db_.get("refresh_token")
                to_create = {
                    "bio": "",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "telegram_spam": False,
                    "spotify_spam": False,
                }
                with open(PATH, "w") as outfile:
                    ujson.dump(to_create, outfile, indent=4)
        with open(PATH) as f:
            self.db = ujson.load(f)
        self.SPOTIFY_MODE = False

    def save_token(self, token):
        self.db["access_token"] = token
        self.save()

    def save_refresh(self, token):
        self.db["refresh_token"] = token
        self.save()

    def save_bio(self, bio):
        self.db["bio"] = bio
        self.save()

    def save_spam(self, which, what):
        self.db[f"{which}_spam"] = what

    def return_token(self):
        return self.db["access_token"]

    def return_refresh(self):
        return self.db["refresh_token"]

    def return_bio(self):
        return self.db["bio"]

    def return_spam(self, which):
        return self.db[f"{which}_spam"]

    def save(self):
        with open(PATH, "w") as outfile:
            ujson.dump(self.db, outfile, indent=4, sort_keys=True)


SP_DATABASE = Database()


def ms_converter(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    if str(seconds) == "0":
        seconds = "00"
    if len(str(seconds)) == 1:
        seconds = f"0{str(seconds)}"
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    return f"{minutes}:{str(seconds)}"


@catub.cat_cmd(
    pattern="spsetup$",
    command=("spsetup", plugin_category),
    info={
        "header": "Setup for Spotify Auth",
        "description": "Login in your spotify account before doing this\nIn BOT Logger Group do .spsetup then follow the instruction.",
        "usage": "{tr}spsetup",
    },
)
async def spotify_setup(event):
    """Setup Spotify Creds"""
    global SP_DATABASE
    if not BOTLOG:
        return await edit_delete(
            event,
            "For authencation you need to set `PRIVATE_GROUP_BOT_API_ID` in heroku",
            7,
        )
    if event.chat_id != BOTLOG_CHATID:
        return await edit_delete(
            event, "CHAT INVALID :: Do this in your Log Channel", 7
        )
    authurl = (
        "https://accounts.spotify.com/authorize?client_id={}&response_type=code&redirect_uri="
        "https%3A%2F%2Fexample.com%2Fcallback&scope=user-read-playback-state%20user-read-currently"
        "-playing+user-follow-read+user-read-recently-played+user-top-read+playlist-read-private+playlist"
        "-modify-private+user-follow-modify+user-read-private"
    )
    async with event.client.conversation(BOTLOG_CHATID) as conv:
        msg = await conv.send_message(
            "Go to the following link in "
            f"your browser: {authurl.format(SPOTIFY_CLIENT_ID)} and reply this msg with the Page Url you got after giving authencation."
        )
        res = conv.wait_event(events.NewMessage(outgoing=True, chats=BOTLOG_CHATID))
        res = await res
        await msg.edit("`Processing ...`")
        initial_token = res.text.strip()
    if "code=" in initial_token:
        initial_token = (initial_token.split("code=", 1))[1]
    body = {
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": "https://example.com/callback",
        "code": initial_token,
    }
    r = requests.post("https://accounts.spotify.com/api/token", data=body)
    save = r.json()
    access_token = save.get("access_token")
    refresh_token = save.get("refresh_token")
    if not (access_token and refresh_token):
        return await edit_delete(
            msg,
            "Auth. Unsuccessful !\ndo .spsetup again and provide a valid URL in reply",
            10,
        )
    to_create = {
        "bio": "",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "telegram_spam": False,
        "spotify_spam": False,
    }
    with open(PATH, "w") as outfile:
        ujson.dump(to_create, outfile, indent=4)
    await edit_delete(msg, "Done! Setup Successfull", 5)
    glob_db.add_collection(
        "SP_DATA",
        {"data": {"access_token": access_token, "refresh_token": refresh_token}},
    )
    SP_DATABASE = Database()


async def sp_var_check(event):
    return True

def title_fetch(title):
    pattern = re.compile(r"([^(-]+) [(-].*")
    if "-E-" in title or "- E -" in title:
        pattern = re.compile(
            r"([a-zA-Z0-9]+(?: ?[a-zA-Z0-9]+)+(?: - \w - \w+)?(?:-\w-\w+)?).*"
        )
    regx = pattern.search(title)
    if regx:
        return regx.group(1)
    return title


async def telegraph_lyrics(tittle, artist, title_img):
    GENIUS = Config.GENIUS_API_TOKEN
    symbol = "❌"
    if GENIUS is None:
        result = "<h1>Set GENIUS_API_TOKEN in heroku vars for functioning of this command.<br>‌‌‎ <br>Check out this <a href = https://telegra.ph/How-to-get-Genius-API-Token-04-26>Tutorial</a></h1>"
    else:
        genius = lyricsgenius.Genius(GENIUS)
        try:
            songs = genius.search_song(tittle, artist)
            content = songs.lyrics
            content = (
                content.replace("\n", "<br>")
                .replace("<br><br>", "<br>‌‌‎ <br>")
                .replace("[", "<b>[")
                .replace("]", "]</b>")
            )
            result = f"<img src='{title_img}'/><h4>{tittle}</h4><br><b>by {artist}</b><br>‌‌‎ <br>{content}"
            symbol = "𝄞"
        except (TypeError, AttributeError):
            result = "<h4>Lyrics Not found!</h4>"
            symbol = "❌"
    try:
        response = await post_to_telegraph("Lyrics", result)
    except Exception as e:
        symbol = "❌"
        response = await post_to_telegraph("Lyrics", f"<h4>{e}</h4>")
    return response, symbol


def sp_data(API):
    oauth = {"Authorization": "Bearer " + SP_DATABASE.return_token()}
    spdata = requests.get(API, headers=oauth)
    if spdata.status_code == 401:
        data = {
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": SP_DATABASE.return_refresh(),
        }
        r = requests.post("https://accounts.spotify.com/api/token", data=data)
        received = r.json()
        # if a new refresh is token as well, we save it here
        try:
            SP_DATABASE.save_refresh(received["refresh_token"])
        except KeyError:
            pass
        SP_DATABASE.save_token(received["access_token"])
        glob_db.add_collection(
            "SP_DATA",
            {
                "data": {
                    "access_token": SP_DATABASE.return_token(),
                    "refresh_token": SP_DATABASE.return_refresh(),
                }
            },
        )
        oauth2 = {"Authorization": "Bearer " + SP_DATABASE.return_token()}
        spdata = requests.get(API, headers=oauth2)
    return spdata


@catub.cat_cmd(
    pattern="sprecent$",
    command=("sprecent", plugin_category),
    info={
        "header": "To fetch list of recently played songs",
        "description": "Shows 15 recently played songs form spotify",
        "usage": "{tr}sprecent",
    },
)
async def spotify_now(event):
    "Spotify recently played songs"
    if not await sp_var_check(event):
        return
    x = sp_data("https://api.spotify.com/v1/me/player/recently-played?limit=15")
    if x.status_code == 200:
        song = "__**Spotify last played songs :-**__\n\n"
        songs = x.json()
        for i in songs["items"]:
            title = title_fetch(i["track"]["name"])
            song += f"**◉ [{title} - {i['track']['artists'][0]['name']}]({i['track']['external_urls']['spotify']})**\n"
    await edit_or_reply(event, song)


@catub.cat_cmd(
    pattern="(i|)now(?:\s|$)([\s\S]*)",
    command=("now", plugin_category),
    info={
        "header": "To get song from spotify",
        "description": "Send the currently playing song of spotify or song from a spotify link.",
        "usage": [
            "{tr}now",
            "{tr}now <Spotify/Deezer link>",
        ],
        "flags": {
            "i": "To send song song link as button",
        },
        "usage": [
            "{tr}now",
            "{tr}inow",
            "{tr}now <Spotify/Deezer link>",
            "{tr}inow <Spotify/Deezer link>",
        ],
    },
)
async def spotify_now(event):
    "Send spotify song"
    chat = "@DeezerMusicBot"
    msg_id = await reply_id(event)
    cmd = event.pattern_match.group(1).lower()
    link = event.pattern_match.group(2)
    catevent = await edit_or_reply(event, "🎶 `Fetching...`")
    if link:
        if not url(link) and "spotify" not in link:
            return await edit_delete(catevent, "**Give me a correct link...**")
        idrgx = re.search(r"(?:/track/)((?:\w|-){22})", link)
        if not idrgx:
            return await edit_delete(catevent, "\n**Error!! Invalid spotify url ;)**")
        song_id = idrgx.group(1)
        received = sp_data(f"https://api.spotify.com/v1/tracks/{song_id}").json()
        title = received["album"]["name"]
        artist = received["album"]["artists"][0]["name"]
        thumb = received["album"]["images"][1]["url"]
        link = f"https://open.spotify.com/track/{song_id}"
    else:
        if not await sp_var_check(event):
            return
        r = sp_data("https://api.spotify.com/v1/me/player/currently-playing")
        if r.status_code == 204:
            return await edit_delete(
                catevent, "\n**I'm not listening anything right now  ;)**"
            )
        received = r.json()
        if received["currently_playing_type"] == "track":
            title = received["item"]["name"]
            link = received["item"]["external_urls"]["spotify"]
            artist = received["item"]["artists"][0]["name"]
            thumb = received["item"]["album"]["images"][1]["url"]
    async with event.client.conversation(chat) as conv:
        try:
            purgeflag = await conv.send_message("/start")
        except YouBlockedUserError:
            await catub(unblock("DeezerMusicBot"))
            purgeflag = await conv.send_message("/start")
        await conv.get_response()
        await event.client.send_read_acknowledge(conv.chat_id)
        await conv.send_message(link)
        song = await conv.get_response()
        await event.client.send_read_acknowledge(conv.chat_id)
        await catevent.delete()
        if cmd == "i":
            title = title_fetch(title)
            lyrics, symbol = await telegraph_lyrics(title, artist, thumb)
            songg = await catub.send_file(BOTLOG_CHATID, song)
            fetch_songg = await catub.tgbot.get_messages(BOTLOG_CHATID, ids=songg.id)
            btn_song = await catub.tgbot.send_file(
                BOTLOG_CHATID,
                fetch_songg,
                buttons=[
                    Button.url("🎧 Spotify", link),
                    Button.url(f"{symbol} Lyrics", lyrics),
                ],
            )
            fetch_btn_song = await catub.get_messages(BOTLOG_CHATID, ids=btn_song.id)
            await event.client.forward_messages(event.chat_id, fetch_btn_song)
            await songg.delete()
            await btn_song.delete()
        else:
            await event.client.send_file(
                event.chat_id,
                song,
                caption=f"<b>Spotify :- <a href = {link}>{title}</a></b>",
                parse_mode="html",
                reply_to=msg_id,
            )
        await delete_conv(event, chat, purgeflag)
