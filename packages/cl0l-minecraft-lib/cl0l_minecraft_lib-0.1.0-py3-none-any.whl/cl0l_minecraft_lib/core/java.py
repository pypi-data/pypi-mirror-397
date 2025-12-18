import shutil
import subprocess

def find_java(version_json):
    # Простейший поиск системной java
    java_exec = shutil.which("java")
    if java_exec:
        return java_exec
    raise RuntimeError("Java not found! Install Java 8+ for Minecraft.")
