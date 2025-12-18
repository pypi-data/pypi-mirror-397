import requests

MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest.json"

class ManifestManager:
    def __init__(self):
        self.manifest = None

    def fetch(self):
        """Скачать version_manifest.json"""
        r = requests.get(MANIFEST_URL)
        r.raise_for_status()
        self.manifest = r.json()
        return self.manifest

    def list_versions(self, kind=None):
        """Вернуть список версий: release, snapshot, old_alpha, old_beta"""
        if not self.manifest:
            self.fetch()
        return [v for v in self.manifest["versions"] if kind is None or v["type"] == kind]

    def get_version_json(self, version_id):
        """Скачать version.json конкретной версии"""
        if not self.manifest:
            self.fetch()
        for v in self.manifest["versions"]:
            if v["id"] == version_id:
                r = requests.get(v["url"])
                r.raise_for_status()
                return r.json()
        raise ValueError(f"Version {version_id} not found")
