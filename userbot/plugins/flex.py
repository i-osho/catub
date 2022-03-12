from userbot import catub

plugin_category = "extra"


@catub.cat_cmd(
    pattern="flex($)",
    command=("flex", plugin_category),
    info={
        "header": "Flex your years of knowledge...",
        "usage": ["{tr}flex"],
    },
)
async def respect(event):
    if event.fwd_from:
        return
    Cat = await reply_id(event)
    bot = "@AniFluidBot"
    results = await event.client.inline_query(bot, f".flex")
    await results[0].click(event.chat_id, reply_to=Cat)
    await event.delete()
