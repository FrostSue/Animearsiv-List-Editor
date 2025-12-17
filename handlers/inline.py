from aiogram import Router, types, html
from database.db import db
import hashlib

router = Router()

@router.inline_query()
async def inline_search_handler(query: types.InlineQuery):
    text = query.query.lower().strip()
    
    if text:
        db.increment_stat("inline_count")

    data = db.load()
    anime_list = data.get("anime_list", [])
    
    results = []
    for anime in anime_list:
        if text in anime["title"].lower():
            result_id = hashlib.md5(anime["url"].encode()).hexdigest()
            escaped_title = html.quote(anime["title"])
            escaped_url = html.quote(anime["url"])
            
            content = f"📺 <b>{escaped_title}</b>\n🔗 {escaped_url}"
            
            results.append(
                types.InlineQueryResultArticle(
                    id=result_id,
                    title=anime["title"],
                    input_message_content=types.InputTextMessageContent(
                        message_text=content,
                        parse_mode="HTML",
                        disable_web_page_preview=False
                    ),
                    description=anime["url"]
                )
            )
            if len(results) >= 50:
                break
    
    await query.answer(results, cache_time=60, is_personal=True)