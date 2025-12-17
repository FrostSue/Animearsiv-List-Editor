import json
import os
import shutil
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

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
        
        default_user = os.getenv("DEFAULT_WEB_USER", "admin")
        default_pass = os.getenv("DEFAULT_WEB_PASS", "admin")
        
        if not os.path.exists(self.db_file):
            default_data = {
                "anime_list": [],
                "admins": [],
                "web_admins": {}, 
                "settings": {"max_lines": 500, "message_ids": []},
                "stats": {"search_count": 0, "inline_count": 0}
            }
            if default_user and default_pass:
                default_data["web_admins"][default_user] = generate_password_hash(default_pass)
            
            self.save(default_data)
        
        else:
            data = self.load()
            changed = False
            
            if "web_admins" not in data:
                data["web_admins"] = {}
                changed = True
            
            if "stats" not in data:
                data["stats"] = {"search_count": 0, "inline_count": 0}
                changed = True

            if not data["web_admins"] and default_user and default_pass:
                data["web_admins"][default_user] = generate_password_hash(default_pass)
                changed = True
            
            if changed:
                self.save(data)

    def load(self):
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            backups = sorted(os.listdir(self.backup_dir))
            if backups:
                shutil.copy(os.path.join(self.backup_dir, backups[-1]), self.db_file)
                return self.load()
            return {
                "anime_list": [], 
                "admins": [], 
                "web_admins": {}, 
                "settings": {"max_lines": 500, "message_ids": []},
                "stats": {"search_count": 0, "inline_count": 0}
            }

    def save(self, data):
        if "anime_list" in data:
            data["anime_list"].sort(key=lambda x: x["title"].lower())
            
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _sanitize_title(self, title):
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

    def update_anime(self, old_title, new_title, new_url):
        data = self.load()
        new_title = self._sanitize_title(new_title)
        found = False
        for anime in data["anime_list"]:
            if anime["title"] == old_title:
                anime["title"] = new_title
                anime["url"] = new_url
                found = True
                break
        if found:
            self.save(data)
        return found

    def delete_anime(self, title):
        data = self.load()
        original_len = len(data["anime_list"])
        data["anime_list"] = [a for a in data["anime_list"] if a["title"] != title]
        if len(data["anime_list"]) != original_len:
            self.save(data)
            return True
        return False

    def check_web_login(self, username, password):
        data = self.load()
        web_admins = data.get("web_admins", {})
        if username in web_admins:
            return check_password_hash(web_admins[username], password)
        return False

    def add_web_admin(self, username, password):
        data = self.load()
        if "web_admins" not in data: data["web_admins"] = {}
        
        if username in data["web_admins"]:
            return False
        
        data["web_admins"][username] = generate_password_hash(password)
        self.save(data)
        return True

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

    def get_stats(self):
        data = self.load()
        return data.get("stats", {"search_count": 0, "inline_count": 0})

    def increment_stat(self, key):
        data = self.load()
        if "stats" not in data:
            data["stats"] = {"search_count": 0, "inline_count": 0}
        
        current = data["stats"].get(key, 0)
        data["stats"][key] = current + 1
        self.save(data)

db = Database()