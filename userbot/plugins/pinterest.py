# Pinterest Downloaded by t.me/i_osho
import asyncio

from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot import catub

from ..core.managers import edit_delete


@catub.cat_cmd(
    pattern="pint(?:\s|$)([\s\S]*)",
    command=("pint", "extra"),
    info={
        "header": "To download posts from Pinterest",
        "usage": "{tr}pint <link>",
        "examples": [
            "{tr}pint https://pin.it/6BE5KZu",
            "{tr}pint https://www.pinterest.com.mx/pin/1096274734264533981/",
        ],
    },
)
async def IfUSawDisUGay(event):
    "Download Pinterest Posts"
    reply_to_id = await reply_id(event)
    chat = "@pinterest_downloaderbot"
    if event.pattern_match.group(1):
        link = event.pattern_match.group(1)
    else:
        return await edit_delete(event, "`What I am Supposed to download`", 30)
    await event.edit("Downloading yout post!")
    async with event.client.conversation(chat) as conv:
        try:
            s = await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(link)
            pic = await conv.get_response()
        except YouBlockedUserError:
            await edit_delete(
                event, "Please unblock **@pinterest_downloaderbot** and try again", 30
            )
            return

    if not pic.media:
        await edit_delete(
            event,
            f"**[Error 404]**\n\nNo post found for the link `{link}`",
            20,
        )
    else:
        await event.delete()
        await event.client.send_file(
            event.chat.id,
            caption=f"• <a href={link}>Pin Link</a> •",
            file=pic,
            reply_to=reply_to_id,
            parse_mode="html",
        )
    asyncio.sleep(1.5)
    msgs = []
    for _ in range(s.id, pic.id + 2):
        msgs.append(_)
    await event.client.delete_messages(1162418064, msgs)
