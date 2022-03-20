# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None
spec_root = os.path.abspath(SPECPATH)

exe_name = 'EOTE-HELPER'

a = Analysis(['main.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[
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
          name=exe_name,
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
               name=exe_name)


# hacky code
os.mkdir(f'dist/{exe_name}/saved')
os.rename(f'dist/{exe_name}/config_template.json', f'dist/{exe_name}/config.json')
