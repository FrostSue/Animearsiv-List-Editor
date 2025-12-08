import validators

def chunk_message(anime_list, max_lines=500, char_limit=4000):
    chunks = []
    current_chunk = ""
    line_count = 0
    header = "📜 **Anime Listesi**\n\n"
    current_chunk += header

    for anime in anime_list:
        line = f"• [{anime['title']}]({anime['url']})\n"
        if line_count >= max_lines or len(current_chunk) + len(line) > char_limit:
            chunks.append(current_chunk)
            current_chunk = line
            line_count = 1
        else:
            current_chunk += line
            line_count += 1
            
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def extract_animes_from_message(text, entities):
    extracted = []
    if not entities:
        return extracted

    for entity in entities:
        if entity.type == "text_link":
            url = entity.url
            start = entity.offset
            end = start + entity.length
            title = text[start:end]
            if validators.url(url):
                extracted.append({"title": title.strip(), "url": url})
    return extracted