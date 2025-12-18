import os
import requests
import hashlib

class Downloader:
    @staticmethod
    def download(url, path, sha1=None):
        """Скачать файл с проверкой SHA1"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            if sha1:
                if Downloader.check_sha1(path, sha1):
                    return path  # Уже скачан
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        if sha1 and not Downloader.check_sha1(path, sha1):
            raise ValueError(f"SHA1 mismatch for {path}")
        return path

    @staticmethod
    def check_sha1(path, sha1):
        import hashlib
        h = hashlib.sha1()
        with open(path, "rb") as f:
            while True:
                data = f.read(8192)
                if not data:
                    break
                h.update(data)
        return h.hexdigest() == sha1
