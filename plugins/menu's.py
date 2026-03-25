from database.database import del_user, get_all_users, get_user_session
import asyncio
import config 
from config import LOGGER
from pyrogram import Client, filters
from bot import Bot 
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from motor.motor_asyncio import AsyncIOMotorClient 

broadcast_cache = {}

@Client.on_message(filters.incoming & filters.private & ~filters.command(["start", "report", "sendmessage", "users", "login", "logout", "accept", "accept_on", "accept_off"]))
async def broadcast_handler(client: Bot, message): 

    if not client.allow_all_users and message.from_user.id != config.OWNER_ID:
            await message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ, ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ɴᴏᴡ ᴘʀɪᴠᴀᴛᴇ")
            return
    
    broadcast_cache[message.from_user.id] = message 


    buttons = [
        [InlineKeyboardButton("ɢᴇɴᴇʀᴀᴛᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ", callback_data="gen_invitelink")]
    ]

    buttons.append([InlineKeyboardButton("ᴀᴄᴄᴇᴘᴛ ᴀʟʟ ᴘᴇɴᴅɪɴɢ ʀᴇQᴜᴇꜱᴛꜱ", callback_data="accept_pending")])

    if message.from_user.id == config.OWNER_ID:
        buttons += [
            [InlineKeyboardButton("ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="broadcast")],
            [
                InlineKeyboardButton("ᴘɪɴ-ᴄᴀsᴛ", callback_data="pbroadcast"),
                InlineKeyboardButton("ᴅᴇʟ-ᴄᴀsᴛ", callback_data="dbroadcast")
            ]
        ]

    buttons.append([InlineKeyboardButton("ᴄᴀɴᴄᴇʟ", callback_data="cancel")])

    keyboard = InlineKeyboardMarkup(buttons)

    text = f"ꜱᴇʟᴇᴄᴛ ᴏɴᴇ ᴏꜰ ᴛʜᴇᴍ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ ᴡɪᴛʜ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴛʜᴇ ᴍᴇssᴀɢᴇ."

    if message.forward_from_chat:
        chat_id = message.forward_from_chat.id
        text += f"\n\n ᴄʜᴀᴛ ɪᴅ: <code>{chat_id}</code>"

    await message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


# handle confirm or cancel callback 
@Client.on_callback_query(filters.regex("^(broadcast|cancel|pbroadcast|dbroadcast|gen_invitelink|accept_pending)$")) 
async def confirm(client: Bot, query: CallbackQuery):

    msg = broadcast_cache.get(query.from_user.id) 

    if not msg:
        return await query.answer("sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ! ɴᴏ ᴍᴇssᴀɢᴇ ғᴏᴜɴᴅ:(", show_alert=True) 
    
    # ------- gen invite link ------#
    try:
        if query.data == "gen_invitelink":

            # must be forwarded
            if not msg.forward_from_chat:
                await query.answer()
                return await query.message.reply_text(
                    "ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ"
                )
                

            chat_id = msg.forward_from_chat.id

        
            link = await client.create_chat_invite_link(
                chat_id=chat_id,
                creates_join_request=True
            )

            chat = await client.get_chat(chat_id)

            if chat.username:
                await query.message.reply_text(
                    f"'{chat.title}' ɪꜱ ᴀ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴀʟ. ᴀᴜᴛᴏ ʀᴇQᴜᴇꜱᴛ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ."
                )
                await query.answer()
                return


            await query.message.reply_text(
                f"{msg.forward_from_chat.title} ɪɴᴠɪᴛᴇ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ:\n{link.invite_link}",
                disable_web_page_preview=True
            )  

            await query.answer()
            
    except Exception as e:
        # permission error
        if "CHAT_ADMIN_REQUIRED" in str(e) or "CHAT_WRITE_FORBIDDEN" in str(e):

            await query.message.reply_text(
                f"ʙᴏᴛ ɴᴇᴇᴅꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ɪɴ: <i>{msg.forward_from_chat.title}</i> "
                f"• ᴀᴅᴅ ᴍᴇ ᴀꜱ ᴀᴅᴍɪɴ\n"
                f"• ɪɴᴠɪᴛᴇ ᴜꜱᴇʀꜱ ᴠɪᴀ ʟɪɴᴋ",
                parse_mode=ParseMode.HTML
            ) 
            await query.answer()
        else:
            await query.message.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")


    # ------- accept all pending join requests (userbot) ------#
    if query.data == "accept_pending":
        await query.answer()

        if not msg.forward_from_chat:
            return await query.message.reply_text(
                "ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ/ꜱᴜᴘᴇʀɢʀᴏᴜᴘ ꜰɪʀꜱᴛ."
            )

        user_id = int(query.from_user.id)
        session = await get_user_session(user_id)
        if not session:
            return await query.message.reply_text("ʟᴏɢɪɴ ᴡɪᴛʜ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ ꜰɪʀꜱᴛ , ᴜꜱɪɴɢ /login")

        chat_id = msg.forward_from_chat.id
        status_msg = query.message

        try:
            uclient = await client.userbots.ensure_running(user_id)
        except Exception as e:
            return await status_msg.edit_text(f"ᴜꜱᴇʀʙᴏᴛ ɴᴏᴛ ʀᴜɴɴɪɴɢ: \n\n<code>{e}</code>", parse_mode=ParseMode.HTML)

        try:
            chat = await uclient.get_chat(chat_id)
        except Exception as e:
            return await status_msg.edit_text(
                "ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ᴏʀ ɴᴏ ᴀᴄᴄᴇꜱꜱ.\n\n"
                f"<code>{e}</code>\n\n"
                "ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜʀ ʟᴏɢɢᴇᴅ-ɪɴ ᴀᴄᴄᴏᴜɴᴛ ɪꜱ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ ᴀɴᴅ ɪꜱ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ʀᴇQᴜᴇꜱᴛꜱ.",
                parse_mode=ParseMode.HTML,
            )

        try:
            joiners = [j async for j in uclient.get_chat_join_requests(chat.id)]
        except Exception as e:
            return await status_msg.edit_text(
                f"ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴅ ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛꜱ ꜰᴏʀ <b>{chat.title}</b>.\n\n<code>{e}</code>",
                parse_mode=ParseMode.HTML,
            )

        pending = [j for j in joiners if getattr(j, "pending", True)]
        total_users = len(pending)
        if total_users == 0:
            return await status_msg.edit_text(
                f"ɴᴏ ᴘᴇɴᴅɪɴɢ ʀᴇQᴜᴇꜱᴛꜱ ꜰᴏʀ <b>{chat.title}</b>.",
                parse_mode=ParseMode.HTML,
            )

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
                        f"ᴄʜᴀᴛ: <code>{chat.title}</code>\n"
                        f"<code>[{bar}] {pct}%</code>\n"
                        f"ᴛᴏᴛᴀʟ: <code>{total_users}</code>\n"
                        f"ᴀᴘᴘʀᴏᴠᴇᴅ: <code>{approved}</code>\n"
                        f"ꜰᴀɪʟᴇᴅ: <code>{failed}</code>\n"
                        f"ᴘʀᴏɢʀᴇꜱꜱ: <code>{processed}/{total_users}</code>",
                        parse_mode=ParseMode.HTML,
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
                    await uclient.approve_chat_join_request(chat_id=chat.id, user_id=joiner.user.id)
                    approved += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    try:
                        await uclient.approve_chat_join_request(chat_id=chat.id, user_id=joiner.user.id)
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
        return await status_msg.edit_text(
            f"<b>ᴅᴏɴᴇ.</b>\n\n"
            f"ᴄʜᴀᴛ: <code>{chat.title}</code>\n"
            f"<code>[{bar}] 100%</code>\n"
            f"ᴛᴏᴛᴀʟ: <code>{total_users}</code>\n"
            f"ᴀᴘᴘʀᴏᴠᴇᴅ: <code>{approved}</code>\n"
            f"ꜰᴀɪʟᴇᴅ: <code>{failed}</code>\n"
            f"ᴅᴜʀᴀᴛɪᴏɴ: <code>{duration}s</code>",
            parse_mode=ParseMode.HTML,
        )

    # ------ Confirm -------#
    try:
        if query.data == "broadcast":
            await query.answer("ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...", show_alert=False) 

            try:
                await start_broadcast(client, query.message, msg)
            finally:
                broadcast_cache.pop(query.from_user.id, None) 
    except Exception as e:
        await query.message.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")


    
    try:
        # ------ Pin Broadcast --------#
        if query.data == "pbroadcast":
            try:
                await start_broadcast(client, query.message, msg, pin=True)
            finally:
                broadcast_cache.pop(query.from_user.id, None)
        
            #await query.message.reply_text("sᴇɴᴅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ .") 
    except Exception as e:
        await query.message.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")


    try:
        # ------ Delete Broadcast --------#
        if query.data == "dbroadcast":
            try:
                await start_broadcast(client, query.message, msg, delete_after=config.BROADCAST_DELETE_TIME)
            finally:
                broadcast_cache.pop(query.from_user.id, None)
        
            await query.message.reply_text(f"ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ᴀʟʀᴇᴀᴅʏ ꜱᴇɴᴛ, ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ - {config.BROADCAST_DELETE_TIME}") 
    except Exception as e:
        await query.message.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")



    try:
        # ------- Cancel --------#
        if query.data == "cancel":
            broadcast_cache.pop(query.from_user.id, None) 
            try:
                await query.message.delete()
            except Exception:
                pass 
            await query.answer("ᴄᴀɴᴄᴇʟʟᴇᴅ.", show_alert=False)
    except Exception as e:
        await query.message.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {e}")




# ------ Main Broadcast Func (Optimized with async batches) ------- # 
async def start_broadcast(client: Bot, status_msg, broadcast_msg, pin=False, delete_after=None):
    users = [u for u in await get_all_users() if u != config.OWNER_ID] 
    total_users = len(users) 

    total = successful = blocked = deleted = failed = 0 
    start_time = asyncio.get_event_loop().time() 

    # ------ Live Status Update Loop ------- #
    async def edit_status():
        nonlocal total, successful, blocked, deleted, failed
        while total < total_users:
            try:
                await status_msg.edit_text(
                    f"<blockquote><b>ʙʀᴏᴀᴅᴄᴀsᴛ ᴏɴɢᴏɪɴɢ</b></blockquote>\n" 
                    f"ᴛᴏᴛᴀʟ ᴜsᴇʀs: <code>{total_users}</code>\n"
                    f"sᴜᴄᴄᴇssғᴜʟ: <code>{successful}</code>\n"
                    f"ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: <code>{blocked}</code>\n"
                    f"ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: <code>{deleted}</code>\n"
                    f"ᴜɴsᴜᴄᴄᴇssғᴜʟ: <code>{failed}</code>\n"
                    f"ᴏᴜᴛ ᴏғ: <b>{total_users}/{total}</b>\n",
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass 
            await asyncio.sleep(3)

    updater_task = asyncio.create_task(edit_status()) 

    # ------ Send Broadcast in Async Batches ------- #
    batch_size = 20  # number of users to send in parallel
    for i in range(0, total_users, batch_size):
        batch = users[i:i + batch_size]

        async def send_user(user_id):
            nonlocal total, successful, blocked, deleted, failed
            try:
                sent_msg = await broadcast_msg.copy(user_id) 
                if pin:
                    await client.pin_chat_message(
                        chat_id=user_id,
                        message_id=sent_msg.id,
                        both_sides=True
                    )
                if delete_after:
                    asyncio.create_task(delete_later(sent_msg, delete_after))
                successful += 1
            except FloodWait as e: 
                await asyncio.sleep(e.value) 
                try:
                    sent_msg = await broadcast_msg.copy(user_id)
                    if pin:
                        await client.pin_chat_message(
                            chat_id=user_id,
                            message_id=sent_msg.id,
                            both_sides=True
                        )
                    if delete_after:
                        asyncio.create_task(delete_later(sent_msg, delete_after)) 
                    successful += 1 
                except Exception as e:
                    failed += 1
                    LOGGER(__name__).error(f"Failed to send broadcast to {user_id} after FloodWait: {e}")
            except UserIsBlocked:
                await del_user(user_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(user_id)
                deleted += 1 
            except RPCError as e:
                failed += 1 
                LOGGER(__name__).error(f"RPCError while sending broadcast to {user_id}")
            except Exception as e:
                failed += 1 
                LOGGER(__name__).error(f"Unexpected error while sending broadcast to {user_id}: {e}") 
            finally:
                total += 1

        await asyncio.gather(*[send_user(u) for u in batch])
        await asyncio.sleep(0.05)  # small delay between batches
   


    updater_task.cancel()
    try:
        await updater_task
    except asyncio.CancelledError:
        pass

    # ------ Final Summary ------- #
    duration = round(asyncio.get_event_loop().time() - start_time, 1) 

    summery = f"""
    <blockquote><b>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b></blockquote>
    <b>sᴜᴄᴄᴇssғᴜʟ:</b> <code>{successful}</code>
    <b>ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs:</b> <code>{blocked}</code>
    <b>ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs:</b> <code>{deleted}</code>
    <b>ᴜɴsᴜᴄᴄᴇssғᴜʟ:</b> <code>{failed}</code>
    <b>⏱ ᴅᴜʀᴀᴛɪᴏɴ:</b> <code>{duration}</code>
    """ 

    await status_msg.edit_text(summery, parse_mode=ParseMode.HTML) 


async def delete_later(msg, seconds):
    await asyncio.sleep(seconds) 
    try:
        await msg.delete() 
    except Exception as e:
        pass
