import os
import asyncio

from Script import script
from asyncio import TimeoutError
from MadxMoviez.bot import StreamBot
from MadxMoviez.utils.database import Database
from MadxMoviez.utils.human_readable import humanbytes
from MadxMoviez.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from shortzy import Shortzy

from MadxMoviez.utils.file_properties import get_name, get_hash, get_media_file_size

db = Database(Var.DATABASE_URL, Var.name)


MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")


class temp(object):
    U_NAME = None
    B_NAME = None


@StreamBot.on_message(filters.group & filters.command("set_caption"))
async def add_caption(c: Client, m: Message):
    if len(m.command) == 1:
        buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
        return await m.reply_text(
            "**ʜᴇʏ 👋\n\n<u>ɢɪᴠᴇ ᴛʜᴇ ᴄᴀᴩᴛɪᴏɴ</u>\n\nᴇxᴀᴍᴩʟᴇ:- `/set_caption <b>{file_name}\n\nSize : {file_size}\n\n➠ Fast Download Link :\n{download_link}\n\n➠ watch Download Link : {watch_link}</b>`**",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    caption = m.text.split(" ", 1)[1]
    await db.set_caption(m.from_user.id, caption=caption)
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    await m.reply_text(
        "<b>ʜᴇʏ {}\n\n✅ sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴀᴅᴅ ʏᴏᴜʀ ᴄᴀᴩᴛɪᴏɴ ᴀɴᴅ sᴀᴠᴇᴅ</b>".format(
            m.from_user.mention, temp.U_NAME, temp.B_NAME
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@StreamBot.on_message(filters.group & filters.command("del_caption"))
async def delete_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if not caption:
        return await m.reply_text("__**😔 Yᴏᴜ Dᴏɴ'ᴛ Hᴀᴠᴇ Aɴy Cᴀᴩᴛɪᴏɴ**__")
    await db.set_caption(m.from_user.id, caption=None)
    buttons = [[InlineKeyboardButton("⇇ ᴄʟᴏsᴇ ⇉", callback_data="close")]]
    await m.reply_text(
        "<b>ʜᴇʏ {}\n\n✅ sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ʏᴏᴜʀ ᴄᴀᴩᴛɪᴏɴ</b>".format(
            m.from_user.mention, temp.U_NAME, temp.B_NAME
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@StreamBot.on_message(filters.group & filters.command(["see_caption", "view_caption"]))
async def see_caption(c: Client, m: Message):
    caption = await db.get_caption(m.from_user.id)
    if caption:
        await m.reply_text(f"**ʏᴏᴜ'ʀᴇ ᴄᴀᴩᴛɪᴏɴ:-**\n\n`{caption}`")
    else:
        await m.reply_text("__**😔 ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴄᴀᴩᴛɪᴏɴ**__")


@StreamBot.on_message(
    (filters.group)
    & (filters.document | filters.video | filters.audio | filters.photo),
    group=4,
)
async def private_receive_handler(c: Client, m: Message):
    if str(m.chat.id).startswith("-100") and m.chat.id not in Var.GROUP_ID:
        return
    elif m.chat.id not in Var.GROUP_ID:
        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id)
            await c.send_message(
                Var.BIN_CHANNEL,
                f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!",
            )
            return
    media = m.document or m.video or m.audio

    if m.document or m.video or m.audio:
        if m.caption:
            file_name = f"{m.caption}"
        else:
            file_name = ""
    file_name = file_name.replace(".mkv", "")
    file_name = file_name.replace("HEVC", "#HEVC")
    file_name = file_name.replace("Sample video.", "#SampleVideo")
    # return

    try:
        user = await db.get_user(m.from_user.id)
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)

        hs_stream_link = f"{Var.URL}exclusive/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?MadxMoviez={get_hash(log_msg)}"
        stream_link = await short_link(hs_stream_link, user)

        hs_online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?MadxMoviez={get_hash(log_msg)}"
        online_link = await short_link(hs_online_link, user)

        msg_text ="""<b>📂 ғɪʟᴇ ɴᴀᴍᴇ : {file_name}\n\n📦 ғɪʟᴇ ꜱɪᴢᴇ : {file_size}\n\n📥 ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ :\n{download_link}\n\n🖥 ᴡᴀᴛᴄʜ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ  :\n{watch_link}</b>"""

        await log_msg.reply_text(
            text=f"**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`\n**Stream ʟɪɴᴋ :** {stream_link}",
            disable_web_page_preview=True,
            quote=True,
        )
        c_caption = await db.get_caption(m.from_user.id)
        if c_caption:
            try:
                caption = c_caption.format(
                    file_name="" if file_name is None else file_name,
                    file_size=humanbytes(get_media_file_size(m)),
                    download_link=online_link,
                    watch_link=stream_link,
                )
            except Exception as e:
                return
            else:
                caption = caption.format(
                    file_name="" if file_name is None else file_name,
                    file_size=humanbytes(get_media_file_size(m)),
                    download_link=online_link,
                    watch_link=stream_link,
                )
        await c.send_cached_media(
            caption=caption, chat_id=m.chat.id, file_id=media.file_id
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`",
            disable_web_page_preview=True,
        )


async def short_link(link, user=None):
    if not user:
        return link

    api_key = user.get("shortner_api")
    base_site = user.get("shortner_url")

    if bool(api_key and base_site) and Var.USERS_CAN_USE:
        shortzy = Shortzy(api_key, base_site)
        link = await shortzy.convert(link)

    return link


 await c.send_cached_media(
            caption=caption,
            chat_id=-1002205204150,
            file_id=media.file_id
        )


async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link

@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1,)
async def channel_receive_handler(bot, broadcast):
    try:
        message_id = broadcast.id
        chat_id = broadcast.chat.id
        media = broadcast.document or broadcast.video or broadcast.audio

        file_name = (
            broadcast.caption
            if (broadcast.document or broadcast.video or broadcast.audio)
            else ""
        )

        replacements = {
            ".mkv": "",
            "〽️ Uploaded by @MadxMoviez": "",
            "HEVC": "#HEVC",
            "Sample video.": "#SampleVideo",
        }

        for old, new in replacements.items():
            file_name = file_name.replace(old, new)

        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)

        hs_stream_link = (
            f"{Var.URL}exclusive/{str(log_msg.id)}/?MadxMoviez={get_hash(log_msg)}"
        )
        stream_link = await get_shortlink(
            Var.SHORTLINK_URL2, Var.SHORTLINK_API2, hs_stream_link
        )

        hs_online_link = f"{Var.URL}{str(log_msg.id)}/?MadxMoviez={get_hash(log_msg)}"
        online_link = await get_shortlink(
            Var.SHORTLINK_URL2, Var.SHORTLINK_API2, hs_online_link
        )

        caption = (
            f"<b>{file_name}"
            f"🗳 Fast Stream Link : <a href='{stream_link}'>DOWNLOAD 🚀</a>\n\n"
            f"〽️ Uploaded by @MadxMoviez</b>"
        )

        await bot.send_cached_media(
            caption=caption, chat_id=chat_id, file_id=media.file_id
        )
        await broadcast.delete()

    except Exception as e:
        print(f"Error : {e}")
        print(f"Original message ID: {message_id}")
        print(f"Chat ID: {chat_id}")
        print(f"Forwarded message ID: {log_msg.id}")
        print(f"hs_stream_link: {hs_stream_link}")
        print(f"stream_link: {stream_link}")
        print(f"hs_online_link: {hs_online_link}")
        print(f"online_link: {online_link}")
