# -*- mode: python ; coding: utf-8 -*-

# Single EXE build. Easier to share, but startup is usually slower than the folder build.

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/skinrate.ico', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'argparse', 'doctest', 'email', 'html', 'http', 'pydoc',
        'sqlite3', 'ssl', 'unittest', 'urllib', 'xml', 'xmlrpc'
    ],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SkinRate Calculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/skinrate.ico',
)
