from bot import Bot 
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatJoinRequest 
from pyrogram.errors import FloodWait, RPCError
from config import LOGGER, OWNER_ID
logger = LOGGER("auto_accept.py")
import asyncio
from database.database import *



@Client.on_chat_join_request()
async def auto_accept(client: Bot, message: ChatJoinRequest):
    chat, user = message.chat, message.from_user

    if not user:
        logger.warning(f"Join request without from_user in chat_id={chat.id}")
        return
    
    # remove those two when public the repo
    logger.info(f"{'@' + user.username if user.username else user.id} Joined {chat.title} in {chat.id} with id: {user.id}")

    approved = False
    approve_error = None
    try:
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        approved = True
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
            approved = True
        except Exception as e2:
            approve_error = f"{type(e2).__name__}: {e2}"
            logger.exception(f"Failed to approve join request after FloodWait chat_id={chat.id} user_id={user.id}")
    except RPCError as e:
        approve_error = f"{type(e).__name__}: {e}"
        if "USER_ALREADY_PARTICIPANT" in str(e):
            approved = True
        else:
            logger.error(f"Failed to approve join request chat_id={chat.id} user_id={user.id}: {e}")
    except Exception as e:
        approve_error = f"{type(e).__name__}: {e}"
        logger.exception(f"Unexpected error approving join request chat_id={chat.id} user_id={user.id}")

    try:
        status = "ACCEPTED" if approved else "FAILED"
        await client.send_message(
            chat_id=OWNER_ID,
            text=(
                f"{status}: {user.mention}!\n\n"
                f"Joined {chat.title}\nChat ID:{chat.id}\nUser ID:{user.id}"
                + (f"\nError: {approve_error}" if (not approved and approve_error) else "")
            ),
        )
    except Exception:
        logger.exception(f"Failed to notify owner about join request chat_id={chat.id} user_id={user.id}")

    if not approved:
        return

    # save user id to mongodb
    try:
        await add_user(user.id)
    except Exception:
        logger.exception(f"Failed to save user to DB user_id={user.id}")
    
    # generate invite link 
    try:
      invite_link = await client.export_chat_invite_link(chat.id) 
    except Exception:
      invite_link = f"https://t.me/{chat.username}" if chat.username else None
    
    
    
    # channel buttons
    buttons = InlineKeyboardMarkup([
      [
        InlineKeyboardButton("🧭 Vɪsɪᴛ Cʜᴀɴɴᴇʟ", url=invite_link)
      ]
    ]) if invite_link else None
    
    
    try:
        await client.send_message(
      chat_id=user.id,
      text=f"Wᴇʟᴄᴏᴍᴇ, {user.mention}!\n\nYᴏᴜʀ ʀʀᴇsᴘᴇᴄᴛᴇᴅ ʀᴇǫᴜᴇsᴛ ᴏғ ᴊᴏɪɴɪɴɢ {chat.title} ʜᴀs ʙᴇᴇɴ ᴀʟʀᴇᴀᴅʏ ᴀᴄᴄᴇᴘᴛᴇᴅ.",
      reply_markup=buttons,
        )
    except Exception:
        pass
