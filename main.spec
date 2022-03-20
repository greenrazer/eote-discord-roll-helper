# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None
spec_root = os.path.abspath(SPECPATH)


a = Analysis(['main.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[
              ('requirements.txt','.'), 
              ('config_template.json','.'),
              ('default.json','.'),
              ('templates/*','templates'),
            ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')


# hacky code
os.mkdir('dist/main/saved')
os.rename('dist/main/config_template.json', 'dist/main/config.json')
