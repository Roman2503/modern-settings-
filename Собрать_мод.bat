@echo off
chcp 65001 > nul
title Сборка мода Modern Settings для Мира танков

echo ===================================================
echo   Сборка пакета modern_settings.mtmod
echo ===================================================
echo.

python build_and_install_mtmod.py

echo.
echo ===================================================
echo Если у вас установлен Python, пакет modern_settings.mtmod
echo создан прямо в этой папке!
echo.
echo Для установки в игру скопируйте:
echo   1. modern_settings.mtmod
echo   2. net.openwg.gameface_1.2.2.mtmod
echo в папку вашей игры:
echo   <Папка_Мир_Танков>\mods\<номер_текущей_версии>\
echo ===================================================
echo.
pause
