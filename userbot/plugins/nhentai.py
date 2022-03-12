# By @FeelDeD
import asyncio
import re

from hentai import Hentai, Utils
from natsort import natsorted
from telethon.errors.rpcerrorlist import (
    UserAlreadyParticipantError,
    YouBlockedUserError,
)
from telethon.tl.functions.messages import ImportChatInviteRequest

from userbot import catub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import post_to_telegraph
from ..helpers.utils import reply_id

plugin_category = "useless"


@catub.cat_cmd(
    pattern="nhentai(?: |$)(.*)",
    command=("nhentai", plugin_category),
    info={
        "header": "To read nHentai inside Telegram using telegraph",
        "examples": "{tr}nhentai 369835",
        "usage": [
            "{tr}nhentai <link or code>",
            "{tr}nhentai random",
        ],
    },
)
async def _(event):
    "nHentai as telegraph"
    if event.fwd_from:
        return
    await edit_or_reply(event, "`Processing ...`")
    input_str = event.pattern_match.group(1)
    code = input_str
    if "nhentai" in input_str:
        link_regex = r"(?:https?://)?(?:www\.)?nhentai\.net/g/(\d+)"
        match = re.match(link_regex, input_str)
        code = match.group(1)
    if input_str == "random":
        code = Utils.get_random_id()
    try:
        doujin = Hentai(code)
    except BaseException as n_e:
        if "404" in str(n_e):
            return await edit_delete(
                event, f"Nothing found for `{code}`. You shouldn't use nhentai"
            )
        return await edit_delete(event, f"**ERROR :** `{n_e}`")
    msg = ""
    imgs = "".join(f"<img src='{url}'/>" for url in doujin.image_urls)
    imgs = f"&#8205; {imgs}"
    title = doujin.title()
    graph_link = await post_to_telegraph(title, imgs)
    msg += f"[{title}]({graph_link})"
    msg += f"\n**Source:**\n[{code}]({doujin.url})"
    if doujin.parody:
        msg += "\n**Parodies:**"
        parodies = [
            "#" + parody.name.replace(" ", "_").replace("-", "_")
            for parody in doujin.parody
        ]

        msg += "\n" + " ".join(natsorted(parodies))
    if doujin.character:
        msg += "\n**Characters:**"
        charas = [
            "#" + chara.name.replace(" ", "_").replace("-", "_")
            for chara in doujin.character
        ]

        msg += "\n" + " ".join(natsorted(charas))
    if doujin.tag:
        msg += "\n**Tags:**"
        tags = [
            "#" + tag.name.replace(" ", "_").replace("-", "_") for tag in doujin.tag
        ]

        msg += "\n" + " ".join(natsorted(tags))
    if doujin.artist:
        msg += "\n**Artists:**"
        artists = [
            "#" + artist.name.replace(" ", "_").replace("-", "_")
            for artist in doujin.artist
        ]

        msg += "\n" + " ".join(natsorted(artists))
    if doujin.language:
        msg += "\n**Languages:**"
        languages = [
            "#" + language.name.replace(" ", "_").replace("-", "_")
            for language in doujin.language
        ]

        msg += "\n" + " ".join(natsorted(languages))
    if doujin.category:
        msg += "\n**Categories:**"
        categories = [
            "#" + category.name.replace(" ", "_").replace("-", "_")
            for category in doujin.category
        ]

        msg += "\n" + " ".join(natsorted(categories))
    msg += f"\n**Pages:**\n {doujin.num_pages}"
    await edit_or_reply(event, msg, link_preview=True)


@catub.cat_cmd(
    pattern="inhentai",
    command=("inhentai", plugin_category),
    info={
        "header": "nHentai as telegraph via bot",
        "examples": "{tr}inhentai 369835",
        "usage": [
            "{tr}inhentai <code>",
        ],
    },
)
async def _(event):
    "nHentai as telegraph via bot"
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    reply_to_id = await reply_id(event)
    await event.edit("`Processing ...`")
    reply_message = await event.get_reply_message()
    if not input_str and not reply_message:
        await edit_delete(
            event,
            "Give me a nHentai code or reply",
        )

    chat = "@Nhentairead_bot"
    async with event.client.conversation(chat) as conv:
        try:
            try:
                await event.client(ImportChatInviteRequest("AAAAAFZPuYvdW1A8mrT8Pg"))
            except UserAlreadyParticipantError:
                await asyncio.sleep(0.00000069420)
            await conv.send_message(
                f"https://nhentai.net/g/{input_str or reply_message}"
            )
            message = await conv.get_response(1)
            await event.client.send_message(
                event.chat_id, message, reply_to=reply_to_id
            )
            await event.delete()
        except YouBlockedUserError:
            await edit_delete("**Error:**\nUnblock @Nhentairead_bot and try again")
