# Censorate Hermes Plugin

Censorate integration plugin for Hermes. Automatically syncs skills from Censorate to your Hermes agent.

## Installation

```bash
pip install censorate-hermes-plugin
```

## Configuration

### 1. Configure the plugin

```bash
censorate configure --url http://localhost:8216/api/v1 --api-key your-api-key --agent-id your-agent-id
```

This will:
- Store API key securely in `~/.hermes/.env` (0600 permissions)
- Store configuration in `~/.hermes/censorate.json`

### 2. Install the plugin in Hermes

```bash
censorate install
```

This adds the plugin to your Hermes configuration.

## Usage

### Manual Sync

```bash
censorate sync
```

### Automatic Sync

The plugin automatically syncs skills when:
- Hermes session starts
- Before each LLM call (if background sync is enabled)

### Configuration Options

Edit `~/.hermes/censorate.json`:

```json
{
  "censorate_url": "http://localhost:8216/api/v1",
  "agent_id": "your-agent-id",
  "sync_interval": 300,
  "sync_on_startup": true,
  "background_sync": true,
  "skills_dir": "~/.hermes/censorate_skills"
}
```

## How It Works

1. **Plugin Hooks**: The plugin registers `on_session_start` and `pre_llm_call` hooks
2. **Skill Sync**: Fetches skills bound to your agent from Censorate API
3. **Skill Download**: Downloads skill packages and extracts them to the skills directory
4. **Hermes Integration**: Hermes automatically loads skills from the configured directory

## Development

```bash
# Clone the repo
git clone https://github.com/your-org/censorate-hermes-plugin.git
cd censorate-hermes-plugin

# Install in development mode
pip install -e .

# Run tests
pytest
```

## License

MIT
