import os
from ..core.downloader import Downloader

class ModsManager:
    def __init__(self, game_dir):
        self.mods_dir = os.path.join(game_dir, "mods")
        os.makedirs(self.mods_dir, exist_ok=True)

    def install_mod(self, url, filename=None):
        if not filename:
            filename = url.split("/")[-1]
        path = os.path.join(self.mods_dir, filename)
        Downloader.download(url, path)
        return path

    def list_mods(self):
        return [f for f in os.listdir(self.mods_dir) if f.endswith(".jar")]
