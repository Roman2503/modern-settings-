#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборщик пакета .mtmod и автоматический установщик мода Modern Settings для «Мира танков».

Что делает скрипт:
1. Создаёт корректный файл meta.xml и структуру ресурсов внутри пакета:
   - res/scripts/client/gui/mods/mod_modern_settings.py
   - res/gui/gameface/mods/modern_settings/index.html
   - res/gui/gameface/mods/modern_settings/bridge.js
2. Упаковывает все файлы БЕЗ СЖАТИЯ (ZIP_STORED) в пакет `modern_settings.mtmod`
   (обязательное требование движка BigWorld / Мир танков для пакетов модификаций).
3. При запуске на ПК с установленной игрой автоматически ищет папку клиента «Мир танков»
   и копирует `modern_settings.mtmod` в актуальную версионную папку `mods/<версия_патча>/`.
"""

import os
import re
import shutil
import sys
import zipfile


MOD_ID = 'ru.mirtankov.modern_settings'
MOD_NAME = 'Modern Settings (Современное окно настроек)'
MOD_VERSION = '2.2.0'
MOD_DESCRIPTION = 'Современный интерфейс настроек игры на базе Gameface для клиента Мир танков.'
PACKAGE_FILENAME = 'modern_settings.mtmod'

META_XML = """<root>
    <id>{mod_id}</id>
    <version>{version}</version>
    <name>{name}</name>
    <description>{desc}</description>
</root>
""".format(
    mod_id=MOD_ID,
    version=MOD_VERSION,
    name=MOD_NAME,
    desc=MOD_DESCRIPTION,
)


def build_mtmod_package(base_dir, output_path=None):
    """Собирает пакет modern_settings.mtmod со способом хранения ZIP_STORED (без сжатия)."""
    py_path = os.path.join(base_dir, 'mod_modern_settings.py')
    html_path = os.path.join(base_dir, 'index.html')
    js_path = os.path.join(base_dir, 'bridge.js')

    for req_file in (py_path, html_path, js_path):
        if not os.path.isfile(req_file):
            raise FileNotFoundError('Не найден обязательный файл мода: %s' % req_file)

    if output_path is None:
        output_path = os.path.join(base_dir, PACKAGE_FILENAME)

    with zipfile.ZipFile(output_path, mode='w', compression=zipfile.ZIP_STORED) as zf:
        zf.writestr('meta.xml', META_XML.encode('utf-8'))
        zf.write(
            py_path,
            arcname='res/scripts/client/gui/mods/mod_modern_settings.py',
            compress_type=zipfile.ZIP_STORED,
        )
        zf.write(
            html_path,
            arcname='res/gui/gameface/mods/modern_settings/index.html',
            compress_type=zipfile.ZIP_STORED,
        )
        zf.write(
            js_path,
            arcname='res/gui/gameface/mods/modern_settings/bridge.js',
            compress_type=zipfile.ZIP_STORED,
        )

    print('[OK] Собран пакет модификации: %s (%d байт)' % (output_path, os.path.getsize(output_path)))
    return output_path


def find_mir_tankov_dir():
    """Пытается автоматически обнаружить установленный клиент «Мир танков» на Windows."""
    candidates = [
        r'C:\Games\Mir_Tankov',
        r'D:\Games\Mir_Tankov',
        r'E:\Games\Mir_Tankov',
        r'C:\Games\Tanki',
        r'D:\Games\Tanki',
        r'C:\Games\World_of_Tanks_RU',
        r'D:\Games\World_of_Tanks_RU',
    ]
    for path in candidates:
        if os.path.isdir(os.path.join(path, 'mods')):
            return path
    return None


def find_latest_patch_mods_folder(game_dir):
    """Находит самую свежую версионную папку внутри <game_dir>/mods/<версия>."""
    mods_root = os.path.join(game_dir, 'mods')
    if not os.path.isdir(mods_root):
        return None

    version_dirs = []
    for entry in os.listdir(mods_root):
        full = os.path.join(mods_root, entry)
        if os.path.isdir(full) and re.match(r'^\d+\.\d+', entry):
            parts = [int(x) for x in re.findall(r'\d+', entry)]
            version_dirs.append((parts, full))

    if not version_dirs:
        return None

    version_dirs.sort(key=lambda item: item[0], reverse=True)
    return version_dirs[0][1]


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pkg_path = build_mtmod_package(script_dir)

    target_game_dir = sys.argv[1] if len(sys.argv) > 1 else find_mir_tankov_dir()
    if target_game_dir and os.path.isdir(target_game_dir):
        patch_folder = find_latest_patch_mods_folder(target_game_dir)
        if patch_folder:
            dest_file = os.path.join(patch_folder, PACKAGE_FILENAME)
            shutil.copy2(pkg_path, dest_file)
            print('[OK] Мод автоматически установлен в клиент игры: %s' % dest_file)
        else:
            print('[INFO] Не удалось определить версионную папку в %s\\mods' % target_game_dir)
    else:
        print(
            '[INFO] Скопируйте созданный файл %s в папку Вашей игры: '
            '<Папка_Мир_Танков>/mods/<текущая_версия_игры>/' % PACKAGE_FILENAME
        )


if __name__ == '__main__':
    main()