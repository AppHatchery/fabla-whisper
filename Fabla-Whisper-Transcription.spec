# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['transcribe-whisper-gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'whisper',
        'numpy',
        'pandas',
        'tkinter',
        'torch',
        'tiktoken',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Fabla-Whisper-Transcription',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
)

app = BUNDLE(
    exe,
    name='Fabla-Whisper-Transcription.app',
    icon=None,
    bundle_identifier='com.fabla.whisper',
    version=None,
    info_plist={
        'LSMinimumSystemVersion': '10.13',  # macOS High Sierra minimum
        'NSHighResolutionCapable': 'True',
    },
)
