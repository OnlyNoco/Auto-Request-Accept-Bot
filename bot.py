from aiohttp import web
from plugins import web_server

from pyrogram import Client
from pyrogram.enums import ParseMode
import sys 
import os
import asyncio
from datetime import datetime
from database.database import (
    get_settings,
    get_user_session,
    get_user_settings,
)
import pyrogram.utils
pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

from pyrogram.types import ChatJoinRequest
from pyrogram.errors import FloodWait, RPCError

from config import API_HASH, API_ID, BOT_TOKEN, WORKER, PORT , LOGGER, ALLOW_ALL_USERS

logger = LOGGER(__name__)


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if os.path.exists(os.path.join(ROOT, "config.py")):
    pass 
elif os.path.exists(os.path.join(ROOT, "sample_config.py")):
    LOGGER(__name__).error("config.py not found! Rename <sample_config.py> to <config.py> and set your credentials.") 
    sys.exit(1) 
else:
    LOGGER(__name__).error("Neither config.py nor sample_config.py found.")
    sys.exit(1)
        

class UserbotManager:
    def __init__(self, bot: "Bot"):
        self._bot = bot
        self._clients: dict[int, Client] = {}
        self._locks: dict[int, asyncio.Lock] = {}

    def is_running(self, user_id: int) -> bool:
        return user_id in self._clients

    async def ensure_running(self, user_id: int) -> Client:
        if self.is_running(user_id):
            return self._clients[user_id]

        lock = self._locks.get(user_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[user_id] = lock

        async with lock:
            if self.is_running(user_id):
                return self._clients[user_id]

            session = await get_user_session(user_id)
            if not session:
                raise RuntimeError("No session found. Use /login first.")

            user_client = Client(
                name=f"userbot_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=session,
                in_memory=True,
                workers=2,
            )

            @user_client.on_chat_join_request()
            async def _auto_accept_join_request(client: Client, message: ChatJoinRequest):
                settings = await get_user_settings(user_id)
                if not settings.get("auto_accept_enabled", True):
                    return
                if not message.from_user:
                    return

                try:
                    await client.approve_chat_join_request(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id,
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.approve_chat_join_request(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id,
                    )
                except RPCError as e:
                    # Ignore already approved/already participant cases and similar non-fatal errors
                    if "USER_ALREADY_PARTICIPANT" in str(e):
                        return
                    raise

            await user_client.start()
            self._clients[user_id] = user_client
            return user_client

    async def stop(self, user_id: int):
        client = self._clients.pop(user_id, None)
        if client is None:
            return
        try:
            await client.stop()
        finally:
            self._locks.pop(user_id, None)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={
                "root": "plugins"
            },
            workers=WORKER,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER
        self.userbots = UserbotManager(self)

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.allow_all_users = ALLOW_ALL_USERS

        try:
            data = await get_settings()

            if not data or len(data.keys()) <= 1:  # only _id
                logger.warning("⚠️ Settings empty in MongoDB. Using defaults.")
            else:
                self.allow_all_users = data.get("allow_all_users", self.allow_all_users)
                

            logger.info(
                f"🟢 Settings loaded:\n allow_all_users={self.allow_all_users}"
            )

        except Exception as e:
            logger.error(f"🔴 Failed loading settings: {e}")
        
        try:
            self.set_parse_mode(ParseMode.HTML)
            # here is the vars 
            bot_name = usr_bot_me.first_name or "Name Not Defined!"
            bot_username = usr_bot_me.username or "Username Not Defined!"
            self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/OnlyNoco")
            self.LOGGER(__name__).info("Bot Detailes: \n\n")
            self.LOGGER(__name__).info(f"Bot Name: {bot_name}")
            self.LOGGER(__name__).info(f"Bot Username: {bot_username}")
            
        except Exception as e:
            self.LOGGER(__name__).warning(f"Error during bot startup: {e}")
            sys.exit()

        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
