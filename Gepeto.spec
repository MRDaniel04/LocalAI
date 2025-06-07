# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],  # Tu script principal
    pathex=[],   # PyInstaller usualmente detecta bien la ruta del proyecto. Si no, añádela aquí.
                 # Ejemplo: ['/ruta/completa/a/tu/proyecto/gemini_local_chat']
    binaries=[], # Si tuvieras binarios externos que empaquetar
    datas=[
        ('templates', 'templates'),  # Incluye la carpeta 'templates' y la pone como 'templates' en el paquete
        ('static', 'static')         # Incluye la carpeta 'static' y la pone como 'static' en el paquete
    ],
    hiddenimports=[
        'google.api_core.bidi', # A veces necesario para google-cloud o librerías relacionadas
        'google.auth.compute_engine', # Puede ser necesario dependiendo de cómo google-auth resuelva credenciales
        'pkg_resources.py2_warn' # A veces PyInstaller lo necesita
        # Añade aquí otros módulos si PyInstaller se queja de no encontrarlos en tiempo de ejecución
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Gepeto',  # El nombre de tu ejecutable
    debug=False,          # Poner True para más output de depuración del bootloader de PyInstaller
    bootloader_ignore_signals=False,
    strip=False,          # Poner True puede reducir tamaño, pero a veces causa problemas
    upx=True,             # Usa UPX para comprimir el ejecutable (necesitas UPX instalado y en el PATH)
                          # Si da problemas o la compilación es lenta, ponlo en False.
    console=True,        # True para mostrar una ventana de consola (útil para depurar)
                          # False para una aplicación "sin ventana" (como --windowed)
    icon='images\Logo.ico'  # Opcional: ruta a tu archivo .ico (Windows) o .icns (macOS)
                                # Ejemplo: 'static/img/app_icon.ico' (si lo tienes ahí)
                                # Si no tienes icono, comenta o elimina esta línea.
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Gepeto'  # El nombre de la carpeta si no usas --onefile (no aplica aquí si EXE es tu objetivo principal)
)

# Si quieres un solo archivo ejecutable (como --onefile), la sección EXE es la principal.
# La sección COLLECT se usa más cuando construyes un directorio.
# Para un --onefile efectivo, la configuración en EXE es la más importante.
# PyInstaller con un .spec y la opción --onefile se maneja al construir:
# pyinstaller --onefile GeminiChatApp.spec