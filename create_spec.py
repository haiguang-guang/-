import PyInstaller.config 
from PyInstaller.__main__ import run 
PyInstaller.config.CONF['workpath'] = 'build' 
PyInstaller.config.CONF['distpath'] = 'dist' 
run(['-n', 'ToolsApp', --icon=ui\icons\favicon.ico, '--windowed', '--noconfirm', '--specpath=.', '--add-data=ui/icons;ui/icons', '--hidden-import=PyQt6.QtSvg', '--hidden-import=PyQt6.QtCore', '--hidden-import=PyQt6.QtGui', '--hidden-import=PyQt6.QtWidgets', 'main.py']) 
