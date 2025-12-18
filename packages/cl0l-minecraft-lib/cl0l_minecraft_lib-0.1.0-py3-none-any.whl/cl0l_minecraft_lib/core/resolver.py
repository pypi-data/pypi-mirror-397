import os
import zipfile

class RuleResolver:
    @staticmethod
    def allowed(rules):
        # Простейшая проверка правил (можно расширить)
        if not rules:
            return True
        for rule in rules:
            if rule.get("action") == "disallow":
                return False
        return True

def extract_natives(version_json, natives_dir):
    for lib in version_json.get("libraries", []):
        if lib.get("natives"):
            # Здесь распаковка natives (например zip) в natives_dir
            # Пока заглушка
            pass
