# slack-praisonai-bot

Slack bot powered by [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install slack-praisonai-bot
```

## Quick Start

1. **Create a Slack App**
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Create New App → From scratch
   - Enable Socket Mode and get App Token
   - Add Bot Token Scopes: `app_mentions:read`, `chat:write`, `commands`
   - Install to Workspace and get Bot Token

2. **Start PraisonAI Server**
   ```bash
   pip install praisonai
   praisonai serve agents.yaml --port 8080
   ```

3. **Run the Bot**
   ```bash
   export SLACK_BOT_TOKEN=xoxb-your-bot-token
   export SLACK_APP_TOKEN=xapp-your-app-token
   export PRAISONAI_API_URL=http://localhost:8080
   slack-praisonai-bot
   ```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/ask <query>` | Ask PraisonAI agents |
| `/agent <name> <query>` | Ask a specific agent |
| `/agents` | List available agents |

## App Mentions

Mention the bot in any channel: `@PraisonAI What are the latest AI trends?`

## Configuration

| Environment Variable | Description |
|---------------------|-------------|
| `SLACK_BOT_TOKEN` | Bot token (xoxb-...) |
| `SLACK_APP_TOKEN` | App token (xapp-...) |
| `PRAISONAI_API_URL` | PraisonAI server URL |
| `PRAISONAI_TIMEOUT` | Request timeout (default: 300) |

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [Slack Bolt Documentation](https://slack.dev/bolt-python)

## License

MIT
