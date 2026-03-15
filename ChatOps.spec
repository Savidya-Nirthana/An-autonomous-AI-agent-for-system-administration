# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\ai\\ChatOps\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\ai\\ChatOps\\config', 'config'), ('D:\\ai\\ChatOps\\src', 'src'), ('D:\\ai\\ChatOps\\cli', 'cli'), ('D:\\ai\\ChatOps\\core', 'core'), ('D:\\ai\\ChatOps\\paths.py', '.')],
    hiddenimports=['yaml', 'tiktoken', 'tiktoken_ext', 'tiktoken_ext.openai_public', 'langchain', 'langchain.chains', 'langchain_core', 'langchain_core.messages', 'langchain_core.tools', 'langchain_openai', 'langchain_groq', 'langchain_community', 'langgraph', 'langgraph.graph', 'qdrant_client', 'qdrant_client.http', 'qdrant_client.http.models', 'qdrant_client.models', 'pyfiglet', 'rich', 'rich.console', 'rich.panel', 'rich.prompt', 'rich.text', 'rich.live', 'prompt_toolkit', 'prompt_toolkit.completion', 'prompt_toolkit.formatted_text', 'prompt_toolkit.styles', 'paramiko', 'psutil', 'dotenv', 'python_dotenv', 'openai', 'uuid', 'uuid6'],
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
    name='ChatOps',
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
