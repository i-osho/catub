import io
import os
import urllib

import requests
from PIL import Image
from telethon import events

HAREM = os.environ.get("HAREM", False)


opener = urllib.request.build_opener()
useragent = "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36"
opener.addheaders = [("User-agent", useragent)]

if HAREM:

    @catub.on(events.NewMessage, outgoing=False, from_users=792028928)
    async def waifus_are_eternal(event):
        if event.is_private:
            return
        if event.media:
            borg = event.client
            if "Add" in event.raw_text:
                logger.info("OwO! A Waifu.")
                waifu_moment = io.BytesIO()
                await borg.download_media(event.media, waifu_moment)
                try:
                    image = Image.open(waifu_moment)
                except OSError:
                    return
                name = "waifu.png"
                image.save(name, "PNG")
                image.close()
                searchUrl = "https://www.google.com/searchbyimage/upload"
                file_img = {
                    "encoded_image": (name, open(name, "rb")),
                    "image_content": "",
                }
                response = requests.post(
                    searchUrl, files=file_img, allow_redirects=False
                )
                os.remove(name)
                if response.status_code == 400:
                    return
                fetchUrl = response.headers["Location"]
                match = await ParseSauce(fetchUrl + "&preferences?hl=en&fg=1#languages")
                guessp = match["best_guess"]
                if not guessp:
                    return
                guess = guessp.replace("Results for", "").replace(" ", "")
                await borg.send_message(event.chat_id, f"/protecc {guess}")
