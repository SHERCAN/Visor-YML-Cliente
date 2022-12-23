import PyInstaller.__main__
PyInstaller.__main__.run([
    'main.py',
    '--hidden-import=app',
    '--add-data=static;static.',
    '--add-data=templates;templates.',
    '--onefile',
    '-y'])