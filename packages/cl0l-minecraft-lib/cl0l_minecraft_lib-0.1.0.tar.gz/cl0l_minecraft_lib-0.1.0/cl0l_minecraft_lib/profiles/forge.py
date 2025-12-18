from cl0l_minecraft_lib.core.launcher import launch
from cl0l_minecraft_lib.auth.offline import OfflineAuth
from cl0l_minecraft_lib.core.mods import ModManager

class ForgeProfile:
    def __init__(self, game_dir, version_json, java_path="java"):
        self.game_dir = game_dir
        self.version_json = version_json
        self.java_path = java_path
        self.auth = OfflineAuth()
        self.mods = ModManager(game_dir)

    def install_mod(self, mod_file_path):
        self.mods.install_mod(mod_file_path)

    def launch(self, memory="2G"):
        launch(
            self.version_json,
            self.java_path,
            self.game_dir,
            self.auth.get_args(),
            memory=memory
        )
