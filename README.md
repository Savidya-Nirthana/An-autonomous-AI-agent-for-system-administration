<p align="center">
  <img src="https://img.shields.io/badge/python-3.13+-blue?logo=python&logoColor=white" alt="Python 3.13+"/>
  <img src="https://img.shields.io/badge/LangChain-powered-green?logo=langchain" alt="LangChain"/>
  <img src="https://img.shields.io/badge/Qdrant-vector%20db-red?logo=qdrant" alt="Qdrant"/>
  <img src="https://img.shields.io/badge/Docker-ready-blue?logo=docker" alt="Docker"/>
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License"/>
</p>

# 🧠 AdminMind

**An autonomous AI agent for system administration — powered by LLMs, with a beautiful terminal UI.**

AdminMind (ChatOps) is an intelligent, conversational system-admin assistant that lives in your terminal. It understands natural-language requests, routes them to the right specialized agent, and executes real sysadmin tasks — from managing files and monitoring resources to diagnosing network issues — all while maintaining conversational memory via a vector database.

---

## ✨ Features

- 🤖 **Intelligent Request Routing** — A router agent classifies every user request and dispatches it to the most appropriate specialized agent.
- 📂 **File System Management** — Create, list, and delete files/directories with interactive confirmation for destructive operations.
- 🌐 **Network Diagnostics** — Ping, traceroute, IP lookup, default gateway inspection, and TCP port checking.
- 🛡️ **Firewall & Security** — Query firewall status and security posture.
- 📊 **Resource Monitoring** — Real-time CPU, memory, and disk usage reports (basic & detailed views).
- 🧠 **Conversational Memory** — Chat history is embedded and stored in Qdrant, enabling context-aware follow-up conversations.
- 🔐 **Token Guard** — Built-in prompt-size safety mechanism that prevents token-limit overflows before they reach the LLM.
- 🎨 **Rich Terminal UI** — Gorgeous CLI experience built with [Rich](https://github.com/Textualize/rich), featuring ASCII banners, live spinners, styled panels, and formatted tool output.
- ⚙️ **Multi-Provider LLM Support** — Seamlessly switch between OpenRouter, OpenAI, Google Gemini, Groq, Anthropic, and DeepSeek via YAML configuration.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      CLI Interface                      │
│              (Rich terminal UI + login)                 │
└────────────────────────┬────────────────────────────────┘
                         │ user prompt
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Router Agent                         │
│           (Groq LLaMA 3.1 · fast classify)             │
│         Classifies → agent type + reason                │
└────────────────────────┬────────────────────────────────┘
                         │ routing decision
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Agent Client Factory                   │
│         Creates the specialized agent + tools           │
├─────────┬──────────┬──────────┬───────────┬─────────────┤
│Filesystem│ Network │ Admin   │ Firewall  │  Usage      │
│  Agent   │  Agent  │ Agent   │  Agent    │  Monitor    │
└─────────┴──────────┴──────────┴───────────┴─────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌───────────┐ ┌────────────┐
   │ Token Guard│ │  Qdrant   │ │ Tool UI    │
   │ (overflow  │ │ (vector   │ │ (formatted │
   │  safety)   │ │  memory)  │ │  output)   │
   └────────────┘ └───────────┘ └────────────┘
```

---

## 📁 Project Structure

```
ChatOps/
├── main.py                  # Application entry point & main loop
├── pyproject.toml           # Project metadata & dependencies
├── docker-compose.yml       # Qdrant vector database service
│
├── config/
│   ├── param.yaml           # Runtime parameters (provider, LLM, retrieval)
│   └── models.yaml          # Model registry (per-provider, per-tier)
│
├── src/
│   ├── agents/
│   │   ├── agents_client.py # Agent factory — creates specialized agents
│   │   ├── router_agent.py  # Router chain (classify → route)
│   │   ├── tools/           # Tool implementations per domain
│   │   │   ├── filesystem.py
│   │   │   ├── filesystem_delete.py
│   │   │   ├── network.py
│   │   │   ├── firewallandsecurity.py
│   │   │   └── usagemonitoring.py
│   │   └── prompts/         # System prompts for each agent
│   │       ├── admin/
│   │       ├── file_system/
│   │       └── router_agent/
│   │
│   └── infrastructure/
│       ├── config.py         # YAML config loader & provider logic
│       ├── llm/              # LLM client initialization
│       └── db/               # Qdrant vector store client
│
├── cli/
│   ├── cli_functions.py      # Banner, login, prompt loop, theming
│   ├── networking.py         # Network tool UI renderers
│   ├── filesystem.py         # Filesystem tool UI renderers
│   └── resourse_monitoring.py# Resource monitoring UI renderers
│
├── core/
│   ├── tool_parser.py        # Extract structured tool output from messages
│   └── tool_router_ui.py     # Route tool output to the correct UI renderer
│
├── schema/
│   └── routing_schema.py     # Pydantic model for routing decisions
│
├── utils/
│   ├── token_utils.py        # Token counting & prompt overflow guard
│   ├── memory_store.py       # Qdrant-backed chat memory (save/load)
│   ├── execution_log.py      # Execution logging utilities
│   └── delete_state.py       # Stateful delete confirmation tracker
│
└── notebooks/                # Jupyter notebooks for experimentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+**
- **Docker** (for Qdrant vector database)
- **uv** (recommended) or pip for dependency management
- At least one LLM API key (OpenRouter recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/Savidya-Nirthana/An-autonomous-AI-agent-for-system-administration.git
cd An-autonomous-AI-agent-for-system-administration
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Required — at least one provider key
OPENROUTER_API_KEY=your_openrouter_key

# Optional — for direct provider access
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
```

### 3. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 4. Start Qdrant (Vector Database)

```bash
docker compose up -d
```

This launches Qdrant on ports `6333` (HTTP) and `6334` (gRPC).

### 5. Run AdminMind

```bash
python main.py
```

---

## 🎮 Usage

Once launched, you'll see the AdminMind ASCII banner and a login prompt:

```
    _       _           _         __  __ _             _
   / \   __| |_ __ ___ (_)_ __   |  \/  (_)_ __   __ | |
  / _ \ / _` | '_ ` _ \| | '_ \  | |\/| | | '_ \ / _` |
 / ___ \ (_| | | | | | | | | | | | |  | | | | | | (_| |
/_/   \_\__,_|_| |_| |_|_|_| |_| |_|  |_|_|_| |_|\__,_|

Enter Your username (Admin): Admin
Enter Your password: ***
```

After logging in, type natural-language requests:

```
[Admin@Admin-a1b2c3d4]-[D:\projects]
$ show me disk usage

[Admin@Admin-a1b2c3d4]-[D:\projects]
$ ping google.com

[Admin@Admin-a1b2c3d4]-[D:\projects]
$ create a folder called reports in the current directory

[Admin@Admin-a1b2c3d4]-[D:\projects]
$ check firewall status

[Admin@Admin-a1b2c3d4]-[D:\projects]
$ what is my default gateway
```

Type `exit` to quit.

---

## ⚙️ Configuration

All runtime behavior is controlled via two YAML files — **no code changes needed**.

### `config/param.yaml`

| Section     | Key                  | Description                          | Default       |
|-------------|----------------------|--------------------------------------|---------------|
| `provider`  | `default`            | LLM provider to use                  | `openrouter`  |
| `provider`  | `tier`               | Model tier: `general`, `strong`, `reason` | `general` |
| `llm`       | `temperature`        | Sampling temperature                 | `0.0`         |
| `llm`       | `max_tokens`         | Max output tokens                    | `2000`        |
| `embedding` | `tier`               | Embedding tier: `default` or `small` | `small`       |
| `retrieval` | `top_k`              | Number of memory results to retrieve | `5`           |
| `retrieval` | `similarity_threshold`| Min similarity for retrieval        | `0.7`         |

### `config/models.yaml`

Defines available models per provider and tier. Example:

```yaml
openrouter:
  chat:
    general: google/gemini-2.5-flash
    strong:  google/gemini-2.5-pro
  embedding:
    default: openai/text-embedding-3-large
    small:   openai/text-embedding-3-small
```

Supported providers: **OpenRouter**, **OpenAI**, **Google**, **Anthropic**, **Groq**, **DeepSeek**.

---

## 🤖 Specialized Agents

| Agent                | Trigger Examples                              | Tools Available                                              |
|----------------------|-----------------------------------------------|--------------------------------------------------------------|
| **Filesystem**       | "create a folder", "list files", "delete log" | `make_dir`, `create_file`, `list_dir`, `delete_file`, etc.   |
| **Network**          | "ping server", "trace route", "check port"    | `ping`, `traceroute`, `get_ip_address`, `tcp_port_check`     |
| **Admin**            | General admin questions                       | LLM-only (no tools)                                          |
| **Firewall**         | "firewall status", "security check"           | `firewall_status`                                            |
| **Usage Monitoring** | "CPU usage", "memory stats", "disk space"     | `cpu_usage`, `memory_usage`, `disk_usage`                    |
| **Network + File**   | Combined network & file tasks                 | All network + filesystem tools                               |

---

## 🛠️ Tech Stack

| Component        | Technology                                      |
|------------------|-------------------------------------------------|
| Language         | Python 3.13+                                    |
| Agent Framework  | LangChain                                       |
| LLM Providers   | OpenRouter, Google Gemini, OpenAI, Groq, Anthropic, DeepSeek |
| Router Model     | Groq LLaMA 3.1-8B-Instant                      |
| Vector Database  | Qdrant (Docker)                                 |
| Embeddings       | OpenAI text-embedding-3-small / large           |
| Terminal UI      | Rich, PyFiglet                                  |
| Token Counting   | tiktoken                                        |
| System Monitoring| psutil                                          |
| Remote Access    | paramiko (SSH)                                  |
| Package Manager  | uv                                              |

---


