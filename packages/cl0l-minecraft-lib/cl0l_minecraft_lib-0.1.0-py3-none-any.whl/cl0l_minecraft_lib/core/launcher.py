import os
import subprocess
from .resolver import RuleResolver, extract_natives
from .downloader import Downloader
from .libraries import download_libraries
from .assets import download_assets
from ..profiles.mods import ModsManager

def build_classpath(version_json, game_dir, include_mods=True):
    """
    Собирает classpath из всех библиотек, client.jar и модов (если include_mods=True)
    """
    cp = []
    # библиотеки
    for lib in version_json.get("libraries", []):
        if not RuleResolver.allowed(lib.get("rules")):
            continue
        if "downloads" in lib and "artifact" in lib["downloads"]:
            path = os.path.join(game_dir, "libraries", lib["downloads"]["artifact"]["path"])
            cp.append(path)

    # client.jar
    cp.append(os.path.join(game_dir, "versions", version_json["id"], f"{version_json['id']}.jar"))

    # моды
    if include_mods:
        mods_dir = os.path.join(game_dir, "mods")
        if os.path.exists(mods_dir):
            for jar in os.listdir(mods_dir):
                if jar.endswith(".jar"):
                    cp.append(os.path.join(mods_dir, jar))

    return os.pathsep.join(cp)

def launch(version_json, java_path, game_dir, auth_args, memory="2G", include_mods=True):
    """
    Запуск Minecraft с:
    - Classpath (библиотеки + client.jar + моды)
    - JVM аргументами
    - Game аргументами
    - Natives
    """
    # Распаковка natives
    natives_dir = os.path.join(game_dir, "natives", version_json["id"])
    os.makedirs(natives_dir, exist_ok=True)
    extract_natives(version_json, natives_dir)

    # Скачиваем библиотеки
    download_libraries(version_json, game_dir)

    # Скачиваем ассеты
    if "assetIndex" in version_json:
        assets_dir = os.path.join(game_dir, "assets")
        download_assets(version_json["assetIndex"]["url"], assets_dir)

    # Classpath
    cp = build_classpath(version_json, game_dir, include_mods=include_mods)

    # Основной класс
    main_class = version_json["mainClass"]

    # JVM args
    jvm_args = [
        java_path,
        f"-Xmx{memory}",
        f"-Xms{memory}",
        "-Djava.library.path=" + natives_dir,
        "-cp", cp,
        main_class
    ]

    # Game args
    game_args = []
    if "arguments" in version_json and "game" in version_json["arguments"]:
        for arg in version_json["arguments"]["game"]:
            if isinstance(arg, str):
                val = arg.replace("${auth_player_name}", auth_args["auth_player_name"])
                val = val.replace("${auth_uuid}", auth_args["auth_uuid"])
                val = val.replace("${auth_access_token}", auth_args["auth_access_token"])
                val = val.replace("${game_directory}", game_dir)
                game_args.append(val)

    # Запуск Minecraft
    subprocess.Popen(jvm_args + game_args, cwd=game_dir)
