# nostromo-cli

MU-TH-UR 6000 Terminal Interface - An Aliens-themed CLI chatbot with full-screen TUI.

## Installation

```bash
# With Anthropic (recommended)
pip install "nostromo-cli[anthropic]"

# With OpenAI
pip install "nostromo-cli[openai]"

# All providers
pip install "nostromo-cli[all]"
```

## Quick Start

```bash
# First run - configure your API keys
nostromo configure

# Launch the interface
nostromo

# Check status
nostromo status
```

## Features

- 🖥️ Full-screen terminal interface (like k9s)
- 💚 Authentic 1979 CRT aesthetic with phosphor green
- ⌨️ Typing effect for responses
- 🔐 Encrypted API key storage with master password
- ⚙️ Separate LLM and user configuration files
- 📜 Configurable chat history persistence
