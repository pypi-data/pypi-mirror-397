import os
from ..core.downloader import Downloader

class FabricInstaller:
    FABRIC_META = "https://meta.fabricmc.net/v2/versions/loader/{mc_version}/latest.json"

    def install(self, mc_version, game_dir):
        r = Downloader.download(self.FABRIC_META.format(mc_version=mc_version),
                                os.path.join(game_dir, "fabric_meta.json"))
        meta = json.load(open(os.path.join(game_dir, "fabric_meta.json")))
        # Скачиваем installer и запускаем его
        installer_url = meta["loader"]["url"]
        installer_path = os.path.join(game_dir, "fabric_installer.jar")
        Downloader.download(installer_url, installer_path)
        # Запуск через Java
        os.system(f'java -jar "{installer_path}" client -dir "{game_dir}" -noprofile')
