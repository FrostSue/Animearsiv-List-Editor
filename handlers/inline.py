from aiogram import Router, types
from database.db import db
import hashlib

router = Router()

@router.inline_query()
async def inline_search_handler(query: types.InlineQuery):
    text = query.query.lower().strip()
    data = db.load()
    anime_list = data.get("anime_list", [])
    
    results = []
    for anime in anime_list:
        if text in anime["title"].lower():
            result_id = hashlib.md5(anime["url"].encode()).hexdigest()
            results.append(
                types.InlineQueryResultArticle(
                    id=result_id,
                    title=anime["title"],
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"📺 **{anime['title']}**\n🔗 {anime['url']}",
                        parse_mode="Markdown"
                    ),
                    description=anime["url"]
                )
            )
            if len(results) >= 50:
                break
    
    await query.answer(results, cache_time=60, is_personal=True)