import os
import requests

def download_assets(version_json, game_dir):
    """Скачать ассеты"""
    assets_index = version_json["assetIndex"]
    url = assets_index["url"]
    r = requests.get(url)
    r.raise_for_status()
    index = r.json()

    for name, obj in index["objects"].items():
        h = obj["hash"]
        sub = h[:2]
        path = os.path.join(game_dir, "assets", "objects", sub, h)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            r2 = requests.get(f"https://resources.download.minecraft.net/{sub}/{h}")
            r2.raise_for_status()
            with open(path, "wb") as f:
                f.write(r2.content)
