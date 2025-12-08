from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import db
from utils.helper import extract_animes_from_message, chunk_message
from utils.keyboards import confirm_keyboard
from utils.tunnel import tunnel_manager
import os
import re
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

@router.message(Command("site"))
async def cmd_get_site(message: types.Message):
    if not is_admin(message.from_user.id): return
    
    url = tunnel_manager.get_url()
    
    if url:
        await message.answer(f"🌐 **Web Yönetim Paneli**\n\n🔗 Link: {url}\n\n⚠️ Bu link bot yeniden başlatılana kadar geçerlidir.")
    else:
        await message.answer("⏳ Tünel oluşturuluyor, lütfen 10-15 saniye sonra tekrar deneyin.")

@router.message(Command("siteadmin"))
async def cmd_add_site_admin(message: types.Message):
    if not is_owner(message.from_user.id): return
    
    try:
        args = message.text.split()
        if len(args) != 3:
            raise ValueError
            
        username = args[1]
        password = args[2]
        
        if db.add_web_admin(username, password):
            await message.answer(f"✅ Web Admin Eklendi:\n👤 Kullanıcı: `{username}`\n🔑 Şifre: `{password}`")
        else:
            await message.answer("⚠️ Bu kullanıcı adı zaten mevcut.")
            
    except ValueError:
        await message.answer("⚠️ Kullanım: `/siteadmin <kullanıcı_adı> <şifre>`")

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

@router.message(Command("yayinla"))
async def cmd_publish(message: types.Message):
    if not is_admin(message.from_user.id): return
    await message.answer("🚀 Liste yayınlanıyor...")
    await refresh_list(message)
    await message.answer("✅ Liste başarıyla güncellendi.")

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
        await message.answer(f"✅ **{title}** veritabanına eklendi!\nYayınlamak için /yayinla komutunu kullanın.")
    else:
        await state.update_data(title=title, url=url)
        await state.set_state(AnimeStates.waiting_for_overwrite)
        await message.answer(
            f"⚠️ **{title}** zaten listede var!\nÜzerine yazmak istiyor musunuz?",
            reply_markup=confirm_keyboard(message.from_user.id)
        )

@router.message(Command("import"))
async def cmd_import_link(message: types.Message, bot: Bot):
    if not is_admin(message.from_user.id): return
    
    args = message.text.split()
    target_msg = None

    if message.reply_to_message:
        target_msg = message.reply_to_message
    
    elif len(args) > 1:
        link = args[1]
        pattern = r"t\.me\/(?:c\/)?(\d+|[\w\d_]+)\/(\d+)"
        match = re.search(pattern, link)
        
        if match:
            chat_identifier = match.group(1)
            message_id = int(match.group(2))
            
            if chat_identifier.isdigit():
                chat_id = int(f"-100{chat_identifier}")
            else:
                chat_id = f"@{chat_identifier}"
            
            try:
                target_msg = await bot.forward_message(
                    chat_id=message.chat.id,
                    from_chat_id=chat_id,
                    message_id=message_id
                )
                await target_msg.delete() 
            except Exception as e:
                await message.answer(f"⚠️ Mesaj alınamadı. Botun o kanalda/grupta olduğundan emin olun.\nHata: {str(e)}")
                return

    if not target_msg or (not target_msg.entities and not target_msg.text):
        await message.answer("⚠️ İşlenecek mesaj bulunamadı.")
        return

    extracted = extract_animes_from_message(target_msg.text, target_msg.entities)
    count = 0
    for item in extracted:
        success, _ = db.add_anime(item['title'], item['url'], message.from_user.id)
        if success: count += 1
    
    await message.answer(f"✅ **{count}** yeni anime eklendi.\n/yayinla ile paylaşabilirsiniz.")

@router.message((F.text | F.caption) & (F.forward_origin | F.forward_date))
async def smart_import_handler(message: types.Message):
    if not is_admin(message.from_user.id): return
    if message.chat.type != "private": return
    
    if message.text and message.text.startswith("/"): return
    
    extracted = extract_animes_from_message(message.text or message.caption, message.entities or message.caption_entities)
    
    if not extracted: return

    count = 0
    duplicates = 0
    
    for item in extracted:
        success, _ = db.add_anime(item['title'], item['url'], message.from_user.id)
        if success: 
            count += 1
        else:
            duplicates += 1
    
    response = f"📥 **İçe Aktarma Raporu**\n\n✅ {count} yeni anime eklendi."
    if duplicates > 0:
        response += f"\n⚠️ {duplicates} anime zaten mevcuttu (Atlandı)."
    
    response += "\n\n📢 Listeyi güncellemek için /yayinla yazın."
    
    await message.reply(response)

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