# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['Interfaz_Carga.pyw'],
             pathex=[],
             binaries=[],
             datas=[("Carga_electronica_ui.py","."),("Elementos_propios.py","."),("Funciones_Carga.py","."),("ComSerial.py","."),("Ventana_advertencia_ui.py","."),("Icono_4.png","."),("Icono_4.ico",".")],
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
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='Interfaz_Carga',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon="Icono_4.ico")

