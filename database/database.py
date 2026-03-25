from config import DB_URL, DB_NAME, LOGGER
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime


# clients setup 
logger = LOGGER(__name__)

_client = AsyncIOMotorClient(DB_URL)

def _resolve_db_name(desired: str) -> str:
  """
  MongoDB doesn't allow databases that differ only by case (e.g. Test vs test).
  If the DB already exists with different case, reuse the existing name.
  """
  try:
    existing = _client.delegate.list_database_names()
  except Exception as e:
    logger.warning(f"Could not list database names to resolve casing: {e}")
    return desired

  desired_fold = desired.casefold()
  for name in existing:
    if name.casefold() == desired_fold:
      return name

  return desired

_db = _client[_resolve_db_name(DB_NAME)]
_users = _db.users # collection name "users"
_collection = _db.settings #  collection for setings logic
_sessions = _db.user_sessions  # per-user Pyrogram session strings
_user_settings = _db.user_settings  # per-user feature toggles

# save id 
async def add_user(user_id: int):
  await _users.update_one(
    {"_id": user_id}, {"$setOnInsert": {"_id": user_id}}, upsert=True
  )
  
# get all users 
async def get_all_users() -> list[int]:
  curser = _users.find({}, {"_id": 1}) 
  return [doc["_id"] async for doc in curser] 
  
# delete users [bot blocked or deactivated account cleanup] 
async def del_user(user_id: int):
  await _users.delete_one({"_id": user_id}) 


# settings 
async def set_settings(key, value):
  await _collection.update_one(
    {"_id": "bot_settings"},
    {"$set": {key: value}},
    upsert=True
  )
  

async def get_settings():
  data = await _collection.find_one({"_id": "bot_settings"})
  return data or {}


# -----------------------------
# User sessions (userbot)
# -----------------------------
async def get_user_session(user_id: int) -> str | None:
  doc = await _sessions.find_one({"_id": user_id}, {"session": 1})
  if not doc:
    return None
  return doc.get("session")


async def set_user_session(user_id: int, session: str | None, phone: str | None = None):
  now = datetime.utcnow()
  if not session:
    await _sessions.delete_one({"_id": user_id})
    return

  payload = {"session": session, "updated_at": now}
  if phone is not None:
    payload["phone"] = phone

  await _sessions.update_one(
    {"_id": user_id},
    {"$set": payload, "$setOnInsert": {"created_at": now}},
    upsert=True,
  )


async def get_all_user_sessions() -> list[dict]:
  cursor = _sessions.find({}, {"_id": 1, "session": 1})
  return [doc async for doc in cursor]


# -----------------------------
# Per-user settings (userbot)
# -----------------------------
async def get_user_settings(user_id: int) -> dict:
  doc = await _user_settings.find_one({"_id": user_id})
  return doc or {"_id": user_id, "auto_accept_enabled": True}


async def set_user_setting(user_id: int, key: str, value):
  await _user_settings.update_one(
    {"_id": user_id},
    {"$set": {key: value}},
    upsert=True,
  )
