"""
Video + Music Stream Telegram Bot
Copyright (c) 2022-present levina=lab <https://github.com/levina-lab>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/licenses.html>
"""


import re
import asyncio

from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, Message

from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.exceptions import NoAudioSourceFound, NoActiveGroupCall, GroupCallNotFound

from program import LOGS
from program.utils.inline import stream_markup
from driver.design.thumbnail import thumb
from driver.design.chatname import CHAT_TITLE
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.core import calls, user, me_user
from driver.utils import bash, remove_if_exists, from_tg_get_msg
from driver.database.dbqueue import add_active_chat, remove_active_chat, music_on
from driver.decorators import require_admin, check_blacklist

from config import BOT_USERNAME, IMG_1, IMG_2, IMG_5
from asyncio.exceptions import TimeoutError
from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = data["thumbnails"][0]["url"]
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0

async def ytdl(link: str):
    stdout, stderr = await bash(
        f'yt-dlp --geo-bypass -g -f "[height<=?720][width<=?1280]" {link}'
    )
    if stdout:
        return 1, stdout
    return 0, stderr

def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)






Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
async def ytplay(_, message: Message):
   keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("༎⃝✨𝐌𝐄𝐍𝐔༎⃝➤", url=f"https://t.me/SAB_KAA_KATEGA"),
                InlineKeyboardButton("༎⃝💔𝐂𝐋𝐎𝐒𝐄༎⃝➤", url=f"https://t.me/SAB_KAA_KATEGA"),
            ],
            [InlineKeyboardButton("༎⃝🥀𝐔𝐏𝐃𝐀𝐓𝐄𝐒༎⃝➤", url=f"https://t.me/YUKKI_X_UPDATES")],
        ]
    )
  
    nofound = "😕 **couldn't find song you requested**\n\n» **please provide the correct song name or include the artist's name as well**"
    
    global que
    if message.chat.id in DISABLED_GROUPS:
        return
    lel = await message.reply("**༎⃝🔥𝐀𝐋𝐄𝐗𝐀 𝐌𝐔𝐒𝐈𝐂 𝐎𝐍 𝐅𝐈𝐑𝐄༎⃝🔥**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "music assistant"
    usar = user
    wew = usar.id
    try:
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"💡 **please add the userbot to your channel first**",
                    )
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+","https://t.me/joinchat/")
                except:
                    await lel.edit(
                        "💡 **To use me, I need to be an Administrator with the permissions:\n\n» ❌ __Delete messages__\n» ❌ __Ban users__\n» ❌ __Add users__\n» ❌ __Manage voice chat__\n\n**Then type /reload**",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await lel.edit(
                        f"✅ **userbot succesfully entered chat**",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"🔴 **Flood Wait Error** 🔴 \n\n**userbot can't join this group due to many join requests for userbot.**"
                        f"\n\n**or add @{ASSISTANT_NAME} to this group manually then try again.**",
                    )
    try:
        await USER.get_chat(chid)
    except:
        await lel.edit(
            f"» **userbot not in this chat or is banned in this group !**\n\n**unban @{ASSISTANT_NAME} and add to this group again manually, or type /reload then try again.**"
        )
        return

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    await lel.edit("**༎⃝💔𝐂𝐎𝐍𝐍𝐄𝐂𝐓𝐈𝐍𝐆 𝐓𝐎 𝐀𝐋𝐄𝐗𝐀 𝐒𝐄𝐑𝐕𝐄𝐑𝐒༎⃝➤**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:70]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        ctitle = message.chat.title
        ctitle = await CHAT_TITLE(ctitle)
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        results[0]["url_suffix"]

    except Exception as e:
        await lel.delete()
        await message.reply_photo(
            photo=f"{CMD_IMG}",
            caption=nofound,
            reply_markup=bttn,
        )
        print(str(e))
        return
    try:
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
            await lel.edit(
                f"❌ **music with duration more than** `{DURATION_LIMIT}` **minutes, can't play !**"
            )
            return
    except:
        pass
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("༎⃝✨𝐌𝐄𝐍𝐔༎⃝➤", url=f"https://t.me/SAB_KAA_KATEGA"),
                InlineKeyboardButton("༎⃝💔𝐂𝐋𝐎𝐒𝐄༎⃝➤", url=f"https://t.me/SAB_KAA_KATEGA"),
            ],
            [InlineKeyboardButton("༎⃝🥀𝐔𝐏𝐃𝐀𝐓𝐄𝐒༎⃝➤", url=f"https://t.me/YUKKI_X_UPDATES")],
        ]
    )
    await generate_cover(title, thumbnail, ctitle)
    file_path = await converter.convert(youtube.download(url))
   
    ACTV_CALLS = []
    chat_id = message.chat.id
    for x in callsmusic.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))
    if int(message.chat.id) in ACTV_CALLS:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await lel.delete()
        await message.reply_photo(
            photo="final.png",
            caption=f"💡 **𝚃𝚁𝙰𝙲𝙺 𝙰𝙳𝙳𝙴𝙳 𝚃𝙾 𝚀𝚄𝙴𝚄𝙴 »** `{position}`\n\n🏷 **𝙽𝙰𝙼𝙴 ✘** [{title[:35]}...]({url})\n⏱ **𝙳𝚄𝚁𝙰𝚃𝙸𝙾𝙽 ✘** `{duration}`\n🎧 **𝚁𝙴𝚀𝚄𝙴𝚂𝚃 𝙱𝚈 ✘** {message.from_user.mention}",
            reply_markup=keyboard,
        )
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            await callsmusic.pytgcalls.join_group_call(
                chat_id, 
                InputStream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            )
        except:
            await lel.edit(
                "😕 **voice chat not found**\n\n» please turn on the voice chat first"
            )
            return
        await lel.delete()
        await message.reply_photo(
            photo="final.png",
            caption=f"🏷 **𝙽𝙰𝙼𝙴 ✘** [{title[:70]}]({url})\n⏱ **𝙳𝚄𝚁𝙰𝚃𝙸𝙾𝙽 ✘** `{duration}`\n💡 **𝚂𝚃𝙰𝚃𝚄𝚂** `𝙿𝙻𝙰𝚈𝙸𝙽𝙶`\n"
            + f"🎧 **𝚁𝙴𝚀𝚄𝙴𝚂𝚃 𝙱𝚈 ✘** {message.from_user.mention}",
            reply_markup=keyboard,
        )
        os.remove("final.png")
