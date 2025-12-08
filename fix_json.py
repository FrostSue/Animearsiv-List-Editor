import json
import os

def clean_database():
    db_path = "database/data.json"
    
    if not os.path.exists(db_path):
        print("❌ Veritabanı dosyası bulunamadı!")
        return

    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_count = len(data["anime_list"])
    cleaned_list = []

    for anime in data["anime_list"]:
        if anime["url"] == "https://t.me/animearsiv/5659" or not anime["title"].strip():
            print(f"🗑️ Silindi: {anime['url']}")
            continue

        title = anime["title"]

        if "[" in title or "]" in title:
            old_title = title
            title = title.replace("[", "(").replace("]", ")")
            print(f"🔧 Düzeltildi (Parantez): {old_title} -> {title}")

        if "\n" in title or "\r" in title:
            old_title = title
            title = title.replace("\n", " ").replace("\r", " ").strip()
            if title.endswith("-"):
                title = title[:-1].strip()
            print(f"🔧 Düzeltildi (Satır): {old_title} -> {title}")

        anime["title"] = title
        cleaned_list.append(anime)

    data["anime_list"] = cleaned_list
    
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Temizlik Tamamlandı!")
    print(f"Önceki Kayıt: {original_count} -> Şimdiki Kayıt: {len(cleaned_list)}")

if __name__ == "__main__":
    clean_database()