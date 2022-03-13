import os
from datetime import datetime
from pathlib import Path

from ..Config import Config
from ..utils import load_module, remove_plugin
from . import (
    CMD_HELP,
    CMD_LIST,
    SUDO_LIST,
    catub,
    edit_delete,
    edit_or_reply,
    hmention,
    reply_id,
)

plugin_category = "tools"

DELETE_TIMEOUT = 5
thumb_image_path = os.path.join(
    Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")


@catub.cat_cmd(
    pattern="i$",
    command=("i", plugin_category),
    info={
        "header": "To intall an external plugin.",
    },
)
async def install(event):
    "To install an external plugin."
    if event.reply_to_msg_id:
        try:
            downloaded_file_name = await event.client.download_media(
                await event.get_reply_message(),
                "userbot/plugins/",
            )
            if "(" not in downloaded_file_name:
                path1 = Path(downloaded_file_name)
                shortname = path1.stem
                load_module(shortname.replace(".py", ""))
                await edit_delete(
                    event,
                    f"Installed Plugin `{os.path.basename(downloaded_file_name)}`",
                    10,
                )
            else:
                path1 = Path(downloaded_file_name)
                shortname = path1.stem
                try:
                    remove_plugin(shortname)
                    await edit_or_reply(event, f"Uninstalled {shortname}")
                except Exception as e:
                    await edit_or_reply(event, f"Uninstalled {shortname}\n{e}")
                load_module(shortname.replace(".py", ""))
                await edit_delete(
                    event,
                    f"Installed Plugin `{os.path.basename(downloaded_file_name)}`",
                    10,
                )
        except Exception as e:
            await edit_delete(event, f"**Error:**\n`{e}`", 10)
            os.remove(downloaded_file_name)


@catub.cat_cmd(
    pattern="send ([\s\S]*)",
    command=("send", plugin_category),
    info={
        "header": "To upload a plugin file to telegram chat",
        "usage": "{tr}send <plugin name>",
        "examples": "{tr}send markdown",
    },
)
async def send(event):
    "To uplaod a plugin file to telegram chat"
    reply_to_id = await reply_id(event)
    thumb = thumb_image_path if os.path.exists(thumb_image_path) else None
    input_str = event.pattern_match.group(1)
    the_plugin_file = f"./userbot/plugins/{input_str}.py"
    repo_link = os.environ.get("UPSTREAM_REPO")
    if repo_link == "goodcat":
        repo_link = "https://github.com/sandy1709/catuserbot"
    if repo_link == "badcat":
        repo_link = "https://github.com/i-osho/catub"
    repo_branch = os.environ.get("UPSTREAM_REPO_BRANCH") or "master"
    git_link = f"<a href= {repo_link}/blob/{repo_branch}/userbot/plugins/{input_str}.py>GitHub</a>"
    raw_link = (
        f"<a href= {repo_link}/raw/{repo_branch}/userbot/plugins/{input_str}.py>Raw</a>"
    )
    if os.path.exists(the_plugin_file):
        start = datetime.now()
        caat = await event.client.send_file(
            event.chat_id,
            the_plugin_file,
            force_document=True,
            allow_cache=False,
            reply_to=reply_to_id,
            thumb=thumb,
        )
        end = datetime.now()
        (end - start).seconds
        await event.delete()
        await caat.edit(
            f"<b>〣File • {input_str}</b>\n<b>〣Link • {git_link} | {raw_link}</b>\n<b>〣By • {hmention}</b>",
            parse_mode="html",
        )
    else:
        await edit_or_reply(event, "404: File Not Found")


@catub.cat_cmd(
    pattern="uninstall ([\s\S]*)",
    command=("uninstall", plugin_category),
    info={
        "header": "To uninstall a plugin temporarily.",
        "description": "To stop functioning of that plugin and remove that plugin from bot.",
        "note": "To unload a plugin permanently from bot set NO_LOAD var in heroku with that plugin name, give space between plugin names if more than 1.",
        "usage": "{tr}uninstall <plugin name>",
        "examples": "{tr}uninstall markdown",
    },
)
async def unload(event):
    "To uninstall a plugin."
    shortname = event.pattern_match.group(1)
    path = Path(f"userbot/plugins/{shortname}.py")
    if not os.path.exists(path):
        return await edit_delete(
            event, f"There is no plugin with path {path} to uninstall it"
        )
    os.remove(path)
    if shortname in CMD_LIST:
        CMD_LIST.pop(shortname)
    if shortname in SUDO_LIST:
        SUDO_LIST.pop(shortname)
    if shortname in CMD_HELP:
        CMD_HELP.pop(shortname)
    try:
        remove_plugin(shortname)
        await edit_or_reply(event, f"{shortname} is Uninstalled successfully")
    except Exception as e:
        await edit_or_reply(event, f"Successfully uninstalled {shortname}\n{e}")
