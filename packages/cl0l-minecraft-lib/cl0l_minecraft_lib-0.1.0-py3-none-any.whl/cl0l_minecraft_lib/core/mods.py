import os
import shutil

class ModManager:
    def __init__(self, game_dir):
        self.mods_dir = os.path.join(game_dir, "mods")
        os.makedirs(self.mods_dir, exist_ok=True)

    def install_mod(self, mod_file_path):
        if not os.path.exists(mod_file_path):
            raise FileNotFoundError(f"Мод не найден: {mod_file_path}")
        shutil.copy(mod_file_path, self.mods_dir)
        print(f"Мод установлен: {os.path.basename(mod_file_path)}")

    def remove_mod(self, mod_name):
        path = os.path.join(self.mods_dir, mod_name)
        if os.path.exists(path):
            os.remove(path)
            print(f"Мод удалён: {mod_name}")
        else:
            print(f"Мод не найден: {mod_name}")

    def list_mods(self):
        return [f for f in os.listdir(self.mods_dir) if f.endswith(".jar")]
