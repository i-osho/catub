# https://t.me/Credits_Not_Needed
import heroku3

from userbot import catub

plugin_category = "tools"

Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
HEROKU_APP_NAME = Config.HEROKU_APP_NAME
HEROKU_API_KEY = Config.HEROKU_API_KEY
app = Heroku.app(Config.HEROKU_APP_NAME)
heroku_var = app.config()


@catub.cat_cmd(
    pattern="branch (.*)",
    command=("branch", plugin_category),
    info={
        "header": "Changes your `UPSTREAM_REPO_BRANCH`",
        "usage": ["{tr}branch <name>"],
    },
)
async def laziii(event):
    "Just for lazy kids"
    if event.fwd_from:
        return
    value = event.pattern_match.group(1)
    await event.edit(f"**Branch changed to ->** `{value}`")
    heroku_var["UPSTREAM_REPO_BRANCH"] = value
