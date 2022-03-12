# By @FeelDeD
from userbot import catub

from ..helpers.utils import _catutils

plugin_category = "tools"


@catub.cat_cmd(
    pattern="pip(.*)",
    command=("pip", plugin_category),
    info={
        "header": "Run pip",
        "examples": "{tr}pip show telethon",
        "usage": [
            "{tr}pip <code>",
        ],
    },
)
async def movie(event):
    "Run pip"
    await event.edit("`Processing ...`")
    code = event.pattern_match.group(1)
    cmd = f"pip {code}"
    run = (await _catutils.runcmd(cmd))[0]
    await event.edit(f"<b>Results:</b>\n\n<code>{run}</code>", parse_mode="html")
