import os, random
from config import START_PIC, START_MSG, ABOUT_MSG, CMD_MSG, SETTINGS_MSG, OWNER_ID
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton 
from pyrogram.enums import ParseMode, ChatAction
from bot import Bot
from database.database import add_user, set_settings


#-- 🫆 start command --#
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    # chat action
    await client.send_chat_action(message.chat.id, ChatAction.PLAYING)
    
    # save user id to mongodb
    await add_user(message.from_user.id) 
    
    bot = await client.get_me() # obj
    bot_username = bot.username # username
    # buttons 
    buttons = []

    if message.from_user.id == OWNER_ID:
        buttons.append([
            InlineKeyboardButton("ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")
        ])
    buttons.append([
        InlineKeyboardButton("✏️ Aʙᴏᴜᴛ", callback_data="about"),
        InlineKeyboardButton("💨 Cᴏᴍᴍᴀɴᴅs", callback_data="cmd")
    ])
    reply_btns = InlineKeyboardMarkup(buttons)

    photo = random.choice(START_PIC)
    
    # send a photo with msg 
    await message.reply_photo(
        photo = photo,
        caption = START_MSG.format(
        mention = message.from_user.mention),
        reply_markup = reply_btns
    )
  
#-- added to group or channel --#
@Client.on_message(filters.new_chat_members) 
async def new_chat_addded(client: Client, message: Message):
  for member in message.new_chat_members:
    if member.id == (await client.get_me()).id:
      try:
        chat = message.chat 
        perms = await client.get_chat_member(chat.id, member.id) 
        if perms.status in ['administrator', 'member']:
          await client.send_message(
            message.from_user.id,
            f"ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ɪɴ <b>{chat.title}</b>\n"
            f"sᴛᴀᴛᴜs ◉ perms.status",
            parse_mode=ParseMode.HTML
          )
        else:
          await client.send_message(
            message.from_user.id,
            f"⎚ ᴀᴅᴅᴇᴅ ʙᴜᴛ ᴡɪᴛʜ ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ",
            parse_mode=ParseMode.HTML
          )
      except Exception as e:
        await client.send_message(
          message.from_user.id,
          f"Cʜᴇᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ ғᴀɪʟᴇᴅ ғᴏʀ <b>{message.chat.title}</b>\n\n <code>{e}</code>",
          parse_mode=ParseMode.HTML
        )
    


@Client.on_callback_query(filters.regex(r"^toggle:(.+)") & filters.user(OWNER_ID))
async def toggle_handler(client: Bot, query: CallbackQuery):
    key = query.data.split(":")[1]

    current = getattr(client, key)
    new = not current

    # update db and attr
    setattr(client, key, new)
    await set_settings(key, new)

    # update settings message
    await query.message.edit_text(
        text = SETTINGS_MSG.format(
            mention=query.from_user.mention, 
            allow_all_users='Eɴᴀʙʟᴇᴅ' if client.allow_all_users else 'Dɪsᴀʙʟᴇᴅ'
        ),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=get_settings_buttons(client)
    )

def get_settings_buttons(client):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"ᴀʟʟᴏᴡ ᴀʟʟ ᴜꜱᴇʀꜱ: {'🔘' if client.allow_all_users else '✖️'}",
                callback_data="toggle:allow_all_users"
            ),
            InlineKeyboardButton("🖇️ ʙᴀᴄᴋ", callback_data="back")
        ],
    ])


@Client.on_callback_query(filters.regex("^settings$") & filters.user(OWNER_ID))
async def settings_handler(client: Bot, query: CallbackQuery):
   await query.message.edit_text(
            text = SETTINGS_MSG.format(mention=query.from_user.mention, allow_all_users='Eɴᴀʙʟᴇᴅ' if client.allow_all_users else 'Dɪsᴀʙʟᴇᴅ'),
            disable_web_page_preview = True, 
            parse_mode = ParseMode.HTML,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(f"ᴀʟʟᴏᴡ ᴀʟʟ ᴜꜱᴇʀꜱ: {'🔘' if client.allow_all_users else '✖️'}", callback_data="toggle:allow_all_users"),
                        InlineKeyboardButton("🖇️ ʙᴀᴄᴋ", callback_data="back")
                    ]
                ]
            )
        )

  
#-- Callback Queries --#
@Client.on_callback_query()
async def callback_queries(client: Bot, query: CallbackQuery):

    if query.data.startswith("toggle:"):
        await toggle_handler(client, query)
        return
        

    #-- About --#
    if query.data == "about":
        await query.message.edit_text(
            text = ABOUT_MSG.format(mention=query.from_user.mention),
            disable_web_page_preview = True, 
            parse_mode = ParseMode.HTML,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")
                    ],
                    [
                        InlineKeyboardButton("🖇️ ʙᴀᴄᴋ", callback_data="back"),
                        InlineKeyboardButton("💨 Cᴏᴍᴍᴀɴᴅs", callback_data="cmd")
                    ]
                ]
            )
        )
    
    #-- Commands --#
    elif query.data == "cmd":
        await query.message.edit_text(
            text = CMD_MSG.format(mention=query.from_user.mention),
            disable_web_page_preview = True, 
            parse_mode = ParseMode.HTML,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")
                    ],
                    [
                        InlineKeyboardButton("✏️ Aʙᴏᴜᴛ", callback_data="about"),
                        InlineKeyboardButton("🖇️ ʙᴀᴄᴋ", callback_data="back")
                    ]
                ]
            )
        )
    
    #-- Back Callback --#
    elif query.data == "back":
        await query.message.edit_text(
            text = START_MSG.format(mention=query.from_user.mention),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings")
                    ],
                    [
                        InlineKeyboardButton("✏️ Aʙᴏᴜᴛ", callback_data="about"),
                        InlineKeyboardButton("💨 Cᴏᴍᴍᴀɴᴅs", callback_data="cmd")
                    ]
                ]
            )
        )