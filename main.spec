# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

def get_hidden_imports() -> list:
    dirs = [Path("cmds"), Path('core')]
    hiddenimports = []

    # find all .py
    for dir in dirs:
        for path in dir.rglob("*.py"):
            # 轉換路徑
            module_name = ".".join(path.with_suffix("").parts)
            hiddenimports.append(module_name)

    hiddenimports.extend([
        'montydb.storage.sqlite',
        '_cffi_backend',
    ])

    return hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('cmds', 'cmds'), 
        ('assets', 'assets'), 
        ('core/locales', 'core/locales'),
        ('.env.example', '.env.example'),
    ] + collect_data_files('fakeredis'),
    hiddenimports=get_hidden_imports(),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
