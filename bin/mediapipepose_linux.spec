# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['mediapipepose.py'],
             pathex=['bin/'],
             binaries=[],
             datas=[('/opt/hostedtoolcache/Python/3.10.8/x64/lib/python3.10/site-packages/mediapipe/modules','mediapipe/modules'),],
             hiddenimports=[],
             hookspath=[],
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
          name='mediapipepose',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mediapipepose')
