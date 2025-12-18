import os
from .downloader import Downloader

def download_libraries(version_json, game_dir):
    for lib in version_json["libraries"]:
        if "downloads" in lib and "artifact" in lib["downloads"]:
            art = lib["downloads"]["artifact"]
            path = os.path.join(game_dir, "libraries", art["path"])
            Downloader.download(art["url"], path, art.get("sha1"))
