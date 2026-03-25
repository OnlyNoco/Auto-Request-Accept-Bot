import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    RPCError,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
)

from bot import Bot
from config import API_ID, API_HASH, OWNER_ID
from database.database import get_user_session, set_user_session, set_user_setting


SESSION_STRING_MIN_LEN = 300


@Client.on_message(filters.command(["login"]) & filters.private)
async def login_cmd(bot: Bot, message: Message):
    if not getattr(bot, "allow_all_users", True) and message.from_user.id != OWNER_ID:
        await message.reply_text("ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ɴᴏᴛ ᴇɴᴀʙʟᴇᴅ ꜰᴏʀ ᴘᴜʙʟɪᴄ ʟᴏɢɪɴꜱ.")
        return

    user_id = int(message.from_user.id)
    existing = await get_user_session(user_id)
    if existing:
        await message.reply_text("ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ʟᴏɢɢᴇᴅ ɪɴ. ᴜꜱᴇ /logout ꜰɪʀꜱᴛ.")
        return

    phone_msg = await bot.ask(
        chat_id=user_id,
        text=(
            "<b>ꜱᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ.</b>\n"
            "<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>+13124562345</code>\n\n"
            ""
        ),
        filters=filters.text,
        timeout=600,
    )
    if not phone_msg.text or phone_msg.text.strip() == "/cancel":
        await phone_msg.reply_text("<b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
        return

    phone_number = phone_msg.text.strip()

    login_client = Client(
        name=f"login_{user_id}",
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=True,
        workers=1,
    )

    await login_client.connect()
    try:
        await phone_msg.reply_text("ꜱᴇɴᴅɪɴɢ ᴏᴛᴘ...")
        try:
            sent = await login_client.send_code(phone_number)
        except PhoneNumberInvalid:
            await phone_msg.reply_text("ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ.")
            return

        code_msg = await bot.ask(
            chat_id=user_id,
            text=(
                "ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘᴘ ꜰᴏʀ ᴛʜᴇ ᴏᴛᴘ.\n\n"
                "ɪꜰ ᴏᴛᴘ ɪꜱ <code>12345</code>, ꜱᴇɴᴅ ɪᴛ ᴀꜱ: <code>1 2 3 4 5</code>\n\n"
                "ᴛɪᴍᴇᴏᴜᴛ: 10ᴍɪɴ , ꜱᴇɴᴅ /cancel ᴛᴏ ꜱᴛᴏᴘ."
            ),
            filters=filters.text,
            timeout=600,
        )
        if not code_msg.text or code_msg.text.strip() == "/cancel":
            await code_msg.reply_text("<b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
            return

        phone_code = code_msg.text.replace(" ", "").strip()
        try:
            await login_client.sign_in(phone_number, sent.phone_code_hash, phone_code)
        except PhoneCodeInvalid:
            await code_msg.reply_text("ɪɴᴠᴀʟɪᴅ ᴏᴛᴘ.")
            return
        except PhoneCodeExpired:
            await code_msg.reply_text("ᴏᴛᴘ ᴇxᴘɪʀᴇᴅ. ᴛʀʏ /ʟᴏɢɪɴ ᴀɢᴀɪɴ.")
            return
        except SessionPasswordNeeded:
            pwd_msg = await bot.ask(
                chat_id=user_id,
                text=(
                    "ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴛᴡᴏ ꜱᴛᴇᴘ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴄᴏᴅᴇ: \n"
                    "ᴛɪᴍᴇᴏᴜᴛ: 10ᴍɪɴ , ꜱᴇɴᴅ /cancel ᴛᴏ ꜱᴛᴏᴘ."
                ),
                filters=filters.text,
                timeout=600,
            )
            if not pwd_msg.text or pwd_msg.text.strip() == "/cancel":
                await pwd_msg.reply_text("<b>ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>")
                return
            try:
                await login_client.check_password(password=pwd_msg.text)
            except PasswordHashInvalid:
                await pwd_msg.reply_text("ɪɴᴠᴀʟɪᴅ ᴛᴡᴏ ꜱᴛᴇᴘ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴄᴏᴅᴇ.")
                return

        session_string = await login_client.export_session_string()
    finally:
        try:
            await login_client.disconnect()
        except Exception:
            pass

    if not session_string or len(session_string) < SESSION_STRING_MIN_LEN:
        await message.reply_text("ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ᴠᴀʟɪᴅ ꜱᴇꜱꜱɪᴏɴ. ᴛʀʏ /ʟᴏɢɪɴ ᴀɢᴀɪɴ.")
        return

    await set_user_session(user_id, session_string, phone=phone_number)
    await set_user_setting(user_id, "auto_accept_enabled", True)

    try:
        await bot.userbots.ensure_running(user_id)
    except Exception as e:
        await message.reply_text(f"ʟᴏɢɪɴ ꜱᴀᴠᴇᴅ, ʙᴜᴛ ᴜꜱᴇʀʙᴏᴛ ꜱᴛᴀʀᴛ ꜰᴀɪʟᴇᴅ: <code>{e}</code>")
        return

    await message.reply_text(
        "<b>ʟᴏɢɪɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ.</b>\n\n"
        "ᴜꜱᴇ /accept_off ᴛᴏ ᴅɪꜱᴀʙʟᴇ ᴀᴜᴛᴏ-ᴀᴄᴄᴇᴘᴛ, ᴏʀ /logout ᴛᴏ ʀᴇᴍᴏᴠᴇ ʏᴏᴜʀ ꜱᴇꜱꜱɪᴏɴ."
    )


@Client.on_message(filters.command(["logout"]) & filters.private)
async def logout_cmd(bot: Bot, message: Message):
    user_id = int(message.from_user.id)
    existing = await get_user_session(user_id)
    if not existing:
        await message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ʟᴏɢɢᴇᴅ ɪɴ.")
        return

    await bot.userbots.stop(user_id)
    await asyncio.sleep(0.2)
    await set_user_session(user_id, None)
    await message.reply_text("<b>ʟᴏɢɢᴇᴅ ᴏᴜᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ.</b>")


@Client.on_message(filters.command(["accept_on"]) & filters.private)
async def accept_on_cmd(bot: Bot, message: Message):
    user_id = int(message.from_user.id)
    existing = await get_user_session(user_id)
    if not existing:
        await message.reply_text("ᴜꜱᴇ /login ꜰɪʀꜱᴛ.")
        return

    await set_user_setting(user_id, "auto_accept_enabled", True)
    await bot.userbots.ensure_running(user_id)
    await message.reply_text("<b>ᴀᴜᴛᴏ-ᴀᴄᴄᴇᴘᴛ ᴇɴᴀʙʟᴇᴅ.</b>")


@Client.on_message(filters.command(["accept_off"]) & filters.private)
async def accept_off_cmd(bot: Bot, message: Message):
    user_id = int(message.from_user.id)
    existing = await get_user_session(user_id)
    if not existing:
        await message.reply_text("ᴜꜱᴇ /login ꜰɪʀꜱᴛ.")
        return

    await set_user_setting(user_id, "auto_accept_enabled", False)
    await message.reply_text("<b>ᴀᴜᴛᴏ-ᴀᴄᴄᴇᴘᴛ ᴅɪꜱᴀʙʟᴇᴅ.</b>")


@Client.on_message(filters.command(["accept"]) & filters.private)
async def accept_pending_cmd(bot: Bot, message: Message):
    """
    Approve all currently pending join requests for a specific chat using the logged-in user session.
    Usage: /accept <chat_id or @username>
    """
    if len(message.command) < 2:
        if message.reply_to_message and message.reply_to_message.forward_from_chat:
            raw_chat = str(message.reply_to_message.forward_from_chat.id)
        else:
            await message.reply_text(
                "Usage: <code>/accept &lt;chat_id or @username&gt;</code>\n"
            )
            return
    else:
        raw_chat = message.command[1]

    user_id = int(message.from_user.id)
    existing = await get_user_session(user_id)
    if not existing:
        await message.reply_text("Use /login first.")
        return

    chat_id = int(raw_chat) if raw_chat.lstrip("-").isdigit() else raw_chat
    status_msg = await message.reply_text("ꜰᴇᴛᴄʜɪɴɢ ᴘᴇɴᴅɪɴɢ ʀᴇQᴜᴇꜱᴛꜱ...")

    try:
        uclient = await bot.userbots.ensure_running(user_id)
    except Exception as e:
        await status_msg.edit_text(f"ᴜꜱᴇʀʙᴏᴛ ɴᴏᴛ ʀᴜɴɴɪɴɢ: <code>{e}</code>")
        return

    # Validate chat resolution early for clearer errors
    try:
        chat = await uclient.get_chat(chat_id)
    except Exception as e:
        await status_msg.edit_text(
            "ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ.\n\n"
            f"<code>{e}</code>\n\n"
            "ꜰɪx:\n"
            "1. ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜ ᴀʀᴇ ᴜꜱɪɴɢ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ &lt;ᴄᴏᴅᴇ&gt;-100...<!--ᴄᴏᴅᴇ--> ᴄʜᴀᴛ ɪᴅ (ᴏʀ &lt;ᴄᴏᴅᴇ&gt;@ᴜꜱᴇʀɴᴀᴍᴇ<!--ᴄᴏᴅᴇ-->).\n"
            "2. ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜʀ ʟᴏɢɢᴇᴅ-ɪɴ ᴀᴄᴄᴏᴜɴᴛ ɪꜱ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ ᴀɴᴅ ɪꜱ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ʀᴇQᴜᴇꜱᴛꜱ.\n"
            "3. ꜰᴏʀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛꜱ: ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴀᴛ ᴄʜᴀᴛ ʜᴇʀᴇ, ʀᴇᴘʟʏ &lt;ᴄᴏᴅᴇ&gt;/ᴀᴄᴄᴇᴘᴛ<!--ᴄᴏᴅᴇ-->."
        )
        return

    try:
        joiners = [j async for j in uclient.get_chat_join_requests(chat.id)]
    except Exception as e:
        await status_msg.edit_text(
            "ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴅ ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛꜱ.\n\n"
            f"ᴄʜᴀᴛ: <code>{chat.title}</code> (<code>{chat.id}</code>)\n"
            f"<code>{e}</code>\n\n"
            "ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛꜱ ᴀʀᴇ ᴇɴᴀʙʟᴇᴅ ꜰᴏʀ ᴛʜɪꜱ ᴄʜᴀᴛ ᴀɴᴅ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ᴛʜᴇᴍ."
        )
        return

    pending = [j for j in joiners if getattr(j, "pending", True)]
    total_users = len(pending)
    if total_users == 0:
        await status_msg.edit_text("ɴᴏ ᴘᴇɴᴅɪɴɢ ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛꜱ ꜰᴏᴜɴᴅ.")
        return

    processed = approved = failed = 0
    start_time = asyncio.get_event_loop().time()

    def progress_bar(done: int, total: int, size: int = 10) -> str:
        filled = int(size * done / total) if total else 0
        return "█" * filled + "░" * (size - filled)

    async def edit_status():
        while processed < total_users:
            try:
                pct = int((processed / total_users) * 100)
                bar = progress_bar(processed, total_users)
                await status_msg.edit_text(
                    f"<b>ᴀᴘᴘʀᴏᴠɪɴɢ ᴘᴇɴᴅɪɴɢ ʀᴇQᴜᴇꜱᴛꜱ...</b>\n\n"
                    f"<code>[{bar}] {pct}%</code>\n"
                    f"ᴛᴏᴛᴀʟ: <code>{total_users}</code>\n"
                    f"ᴀᴘᴘʀᴏᴠᴇᴅ: <code>{approved}</code>\n"
                    f"ꜰᴀɪʟᴇᴅ: <code>{failed}</code>\n"
                    f"ᴘʀᴏɢʀᴇꜱꜱ: <code>{processed}/{total_users}</code>"
                )
            except Exception:
                pass
            await asyncio.sleep(3)

    updater_task = asyncio.create_task(edit_status())

    batch_size = 20
    for i in range(0, total_users, batch_size):
        batch = pending[i:i + batch_size]

        async def approve_one(joiner):
            nonlocal processed, approved, failed
            try:
                await uclient.approve_chat_join_request(chat_id=chat_id, user_id=joiner.user.id)
                approved += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await uclient.approve_chat_join_request(chat_id=chat_id, user_id=joiner.user.id)
                    approved += 1
                except Exception:
                    failed += 1
            except RPCError:
                failed += 1
            except Exception:
                failed += 1
            finally:
                processed += 1

        await asyncio.gather(*[approve_one(j) for j in batch])
        await asyncio.sleep(0.05)

    updater_task.cancel()
    try:
        await updater_task
    except asyncio.CancelledError:
        pass

    duration = round(asyncio.get_event_loop().time() - start_time, 1)
    bar = progress_bar(total_users, total_users)
    await status_msg.edit_text(
        f"<b>ᴅᴏɴᴇ ᴀᴘᴘʀᴏᴠɪɴɢ ʀᴇQᴜᴇꜱᴛꜱ.</b>\n\n"
        f"<code>[{bar}] 100%</code>\n"
        f"ᴛᴏᴛᴀʟ: <code>{total_users}</code>\n"
        f"ᴀᴘᴘʀᴏᴠᴇᴅ: <code>{approved}</code>\n"
        f"ꜰᴀɪʟᴇᴅ: <code>{failed}</code>\n"
        f"ᴅᴜʀᴀᴛɪᴏɴ: <code>{duration}s</code>"
    )
