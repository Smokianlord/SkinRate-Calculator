# -*- mode: python ; coding: utf-8 -*-

# SkinRate Calculator Pro - Single EXE Standalone Build Spec
# Portable zero-install single executable

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets')],
    hiddenimports=[
        'skinrate',
        'skinrate.engine',
        'skinrate.config',
        'skinrate.theme',
        'skinrate.widgets',
        'skinrate.dialogs',
        'skinrate.views',
        'skinrate.views.standard_view',
        'skinrate.views.reverse_view',
        'skinrate.views.steam_view',
        'skinrate.views.matrix_view',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'argparse', 'doctest', 'email', 'html', 'http', 'pydoc',
        'sqlite3', 'ssl', 'unittest', 'urllib', 'xml', 'xmlrpc',
        'bz2', 'lzma', 'multiprocessing', 'distutils', 'test',
        'asyncio', 'concurrent', 'ctypes.test'
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
    version='version_info.txt',
)
