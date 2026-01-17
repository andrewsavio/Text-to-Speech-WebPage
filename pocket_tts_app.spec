# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, copy_metadata

block_cipher = None

# Collect hidden imports for complex libraries
hidden_imports = [
    'uvicorn',
    'fastapi',
    'scipy',
    'scipy.io.wavfile', # Explicitly needed sometimes
    'torch',
    'pocket_tts',
    'engineio.async_drivers.threading', # Common uvicorn issue
    'beartype',
    'safetensors',
    'einops',
    'typer',
    'sentencepiece',
]
hidden_imports += collect_submodules('pocket_tts')
hidden_imports += collect_submodules('beartype')

# Collect data files
datas = []
datas += collect_data_files('pocket_tts')
datas += [('backend/static', 'static')] # Frontend
datas += [('frontend/public/andrew.png', '.')] # Splash image

# pocket-tts relies on some safe tensors or config files in its package
# We ensure the whole package source is available if collect_data_files missed anything
# But usually collect_data_files('pocket_tts') is enough if the package is installed
# Since we are using local source in sys.path in backend/main.py, we might need to manually include it if it's not installed in site-packages
# Wait, my backend/main.py ADDS local path. PyInstaller won't see that dynamic add easily.
# We should include the 'pocket-tts-main/pocket-tts-main/pocket_tts' folder into 'pocket_tts' in the bundle.
datas += [('pocket-tts-main/pocket-tts-main/pocket_tts', 'pocket_tts')]


a = Analysis(
    ['desktop_main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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

# Splash screen configuration
splash = Splash(
    'frontend/public/andrew.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(10, 50),
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash, # Include splash
    [],
    exclude_binaries=True,
    name='AndrewsTTS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Windowed mode (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='frontend/public/andrew.png', # Use the logo as icon too if it's compatible (might need .ico conversion, PyInstaller might warn)
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AndrewsTTS',
)
