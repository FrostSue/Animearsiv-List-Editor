from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import db
from utils.helper import extract_animes_from_message, chunk_message
from utils.keyboards import confirm_keyboard
import os
from dotenv import load_dotenv

load_dotenv()

router = Router()
OWNER_ID = int(os.getenv("OWNER_ID", 0))

class AnimeStates(StatesGroup):
    waiting_for_overwrite = State()

def is_admin(user_id):
    return user_id == OWNER_ID or user_id in db.get_admins()

def is_owner(user_id):
    return user_id == OWNER_ID

@router.message(Command("addadmin"))
async def cmd_add_admin(message: types.Message):
    if not is_owner(message.from_user.id): return
    try:
        new_admin_id = int(message.text.split()[1])
        if db.add_admin(new_admin_id):
            await message.answer(f"✅ Admin eklendi: `{new_admin_id}`")
        else:
            await message.answer("⚠️ Bu kullanıcı zaten admin.")
    except (IndexError, ValueError):
        await message.answer("⚠️ Kullanım: `/addadmin <user_id>`")

@router.message(Command("deladmin"))
async def cmd_del_admin(message: types.Message):
    if not is_owner(message.from_user.id): return
    try:
        target_id = int(message.text.split()[1])
        if db.remove_admin(target_id):
            await message.answer(f"✅ Admin silindi: `{target_id}`")
        else:
            await message.answer("⚠️ Kullanıcı admin listesinde bulunamadı.")
    except (IndexError, ValueError):
        await message.answer("⚠️ Kullanım: `/deladmin <user_id>`")

@router.message(Command("yedekle"))
async def cmd_backup(message: types.Message):
    if not is_admin(message.from_user.id): return
    filename = db.create_backup()
    await message.answer(f"✅ Yedek oluşturuldu: `{filename}`")

@router.message(Command("ekle"))
async def cmd_add(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id): return

    args = message.text.split(" ", 1)
    if len(args) < 2 or "|" not in args[1]:
        await message.answer("⚠️ Format hatalı!\nKullanım: `/ekle Anime Adı | https://link`", parse_mode="Markdown")
        return

    content = args[1].split("|", 1)
    title = content[0].strip()
    url = content[1].strip()

    success, result = db.add_anime(title, url, message.from_user.id)
    
    if success:
        await message.answer(f"✅ **{title}** listeye eklendi!")
        await refresh_list(message)
    else:
        await state.update_data(title=title, url=url)
        await state.set_state(AnimeStates.waiting_for_overwrite)
        await message.answer(
            f"⚠️ **{title}** zaten listede var!\nÜzerine yazmak istiyor musunuz?",
            reply_markup=confirm_keyboard(message.from_user.id)
        )

@router.message(F.text.lower() == "import", F.reply_to_message)
async def import_list(message: types.Message):
    if not is_admin(message.from_user.id): return
    
    target_msg = message.reply_to_message
    if not target_msg.entities and not target_msg.text:
        await message.answer("⚠️ Yanıtlanan mesajda link bulunamadı.")
        return

    extracted = extract_animes_from_message(target_msg.text, target_msg.entities)
    count = 0
    for item in extracted:
        success, _ = db.add_anime(item['title'], item['url'], message.from_user.id)
        if success: count += 1
    
    await message.answer(f"✅ Toplam **{len(extracted)}** link bulundu, **{count}** yeni anime eklendi.")
    await refresh_list(message)

async def refresh_list(message: types.Message):
    data = db.load()
    chunks = chunk_message(data["anime_list"], max_lines=data["settings"]["max_lines"])
    old_ids = data["settings"].get("message_ids", [])

    for mid in old_ids:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=mid)
        except:
            pass

    new_ids = []
    for chunk in chunks:
        sent = await message.answer(chunk, parse_mode="Markdown", disable_web_page_preview=True)
        new_ids.append(sent.message_id)
    
    db.update_message_ids(new_ids)