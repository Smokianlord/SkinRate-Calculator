# -*- mode: python ; coding: utf-8 -*-

# Fast-launch build: creates a folder app in dist/.
# This launches faster than --onefile because Windows does not need to unpack the app every time.

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
    [],
    exclude_binaries=True,
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

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SkinRate Calculator',
)
