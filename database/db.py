import json
import os
import shutil
from datetime import datetime

class Database:
    def __init__(self, db_file="database/data.json"):
        self.db_file = db_file
        self.backup_dir = "backups"
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists("database"):
            os.makedirs("database")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        if not os.path.exists(self.db_file):
            default_data = {
                "anime_list": [],
                "admins": [],
                "settings": {"max_lines": 500, "message_ids": []}
            }
            self.save(default_data)

    def load(self):
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            backups = sorted(os.listdir(self.backup_dir))
            if backups:
                shutil.copy(os.path.join(self.backup_dir, backups[-1]), self.db_file)
                return self.load()
            return {"anime_list": [], "admins": [], "settings": {"max_lines": 500, "message_ids": []}}

    def save(self, data):
        if "anime_list" in data:
            data["anime_list"].sort(key=lambda x: x["title"].lower())
            
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _sanitize_title(self, title):
        """Başlıktaki markdown bozan karakterleri ve yeni satırları temizler."""
        if not title: return ""
        title = title.replace("\n", " ").replace("\r", " ").strip()
        title = title.replace("[", "(").replace("]", ")")
        return title

    def add_anime(self, title, url, user_id):
        title = self._sanitize_title(title)
        
        data = self.load()
        for anime in data["anime_list"]:
            if anime["title"].lower() == title.lower() or anime["url"] == url:
                return False, anime
        
        new_entry = {
            "title": title,
            "url": url,
            "added_by": user_id,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["anime_list"].append(new_entry)
        self.save(data)
        return True, new_entry

    def force_add_anime(self, title, url, user_id):
        title = self._sanitize_title(title)
        
        data = self.load()
        data["anime_list"] = [a for a in data["anime_list"] if a["title"].lower() != title.lower()]
        new_entry = {
            "title": title,
            "url": url,
            "added_by": user_id,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data["anime_list"].append(new_entry)
        self.save(data)

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backup_{timestamp}.json"
        shutil.copy(self.db_file, os.path.join(self.backup_dir, filename))
        return filename

    def get_settings(self):
        return self.load().get("settings", {"max_lines": 500})
    
    def update_message_ids(self, ids):
        data = self.load()
        if "settings" not in data: data["settings"] = {}
        data["settings"]["message_ids"] = ids
        self.save(data)

    def get_admins(self):
        return self.load().get("admins", [])

    def add_admin(self, user_id):
        data = self.load()
        if user_id not in data["admins"]:
            data["admins"].append(user_id)
            self.save(data)
            return True
        return False

    def remove_admin(self, user_id):
        data = self.load()
        if user_id in data["admins"]:
            data["admins"].remove(user_id)
            self.save(data)
            return True
        return False

db = Database()