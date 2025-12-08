import subprocess
import re
import time
import threading
import logging

class TunnelManager:
    def __init__(self, port=5000):
        self.port = port
        self.process = None
        self.url = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        if self.process:
            return

        command = ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{self.port}"]
        
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        threading.Thread(target=self._monitor_output, daemon=True).start()

    def _monitor_output(self):
        url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
        
        while self.process:
            line = self.process.stderr.readline()
            if not line:
                break
            
            match = url_pattern.search(line)
            if match:
                self.url = match.group(0)
                print(f"🌍 Tünel Açıldı: {self.url}")

    def get_url(self):
        return self.url

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
            self.url = None

tunnel_manager = TunnelManager()