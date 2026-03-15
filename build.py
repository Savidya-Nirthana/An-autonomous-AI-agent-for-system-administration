"""
Build script for ChatOps using PyInstaller.
Compiles the application into a single executable file.
"""

import PyInstaller.__main__
from pathlib import Path

# Paths
project_root = Path(__file__).parent.absolute()
main_script = project_root / "main.py"

# Folders to bundle (read-only data shipped inside the EXE)
config_dir = project_root / "config"
src_dir = project_root / "src"
cli_dir = project_root / "cli"
core_dir = project_root / "core"
paths_file = project_root / "paths.py"

# Hidden imports that PyInstaller cannot auto-detect
hidden_imports = [
    # YAML config loading
    "yaml",
    # Tokenizer
    "tiktoken",
    "tiktoken_ext",
    "tiktoken_ext.openai_public",
    # LangChain ecosystem
    "langchain",
    "langchain.chains",
    "langchain_core",
    "langchain_core.messages",
    "langchain_core.tools",
    "langchain_openai",
    "langchain_groq",
    "langchain_community",
    "langgraph",
    "langgraph.graph",
    # Qdrant vector DB
    "qdrant_client",
    "qdrant_client.http",
    "qdrant_client.http.models",
    "qdrant_client.models",
    # CLI / UI
    "pyfiglet",
    "rich",
    "rich.console",
    "rich.panel",
    "rich.prompt",
    "rich.text",
    "rich.live",
    "prompt_toolkit",
    "prompt_toolkit.completion",
    "prompt_toolkit.formatted_text",
    "prompt_toolkit.styles",
    # System tools
    "paramiko",
    "psutil",
    # Env
    "dotenv",
    "python_dotenv",
    # OpenAI
    "openai",
    # UUID
    "uuid",
    "uuid6",
]

# PyInstaller Arguments
args = [
    str(main_script),                   # The main script
    '--name=ChatOps',                   # Executable name
    '--onefile',                        # Package as a single executable file
    '--console',                        # Ensure terminal shows up (CLI app)
    '--clean',                          # Clean PyInstaller cache
    # Add data folders (source;destination)  — Windows uses ;
    f'--add-data={config_dir};config',
    f'--add-data={src_dir};src',
    f'--add-data={cli_dir};cli',
    f'--add-data={core_dir};core',
    f'--add-data={paths_file};.',       # Bundle paths.py at top level
]

# Append hidden imports
for imp in hidden_imports:
    args.append(f'--hidden-import={imp}')

print("Starting PyInstaller Build process...")
print(f"Building from: {project_root}")
print(f"Hidden imports: {len(hidden_imports)}")

# Run the build
try:
    PyInstaller.__main__.run(args)
    print("\nBuild Successful! Check the 'dist' folder for ChatOps.exe.")
except Exception as e:
    print(f"\nBuild Failed: {e}")
