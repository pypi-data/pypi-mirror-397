# telegram-praisonai-bot

Telegram bot powered by [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install telegram-praisonai-bot
```

## Quick Start

1. **Create a Telegram Bot**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the bot token

2. **Start PraisonAI Server**
   ```bash
   pip install praisonai
   praisonai serve agents.yaml --port 8080
   ```

3. **Run the Bot**
   ```bash
   export TELEGRAM_BOT_TOKEN=your_telegram_token
   export PRAISONAI_API_URL=http://localhost:8080
   telegram-praisonai-bot
   ```

   Or create a `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_token
   PRAISONAI_API_URL=http://localhost:8080
   PRAISONAI_TIMEOUT=300
   ```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show welcome message |
| `/help` | Show help message |
| `/ask <query>` | Ask PraisonAI agents a question |
| `/agent <name> <query>` | Ask a specific agent |
| `/agents` | List available PraisonAI agents |

You can also just send a message directly and the bot will process it.

## Usage Examples

```
/ask What are the latest trends in AI?
/agent researcher Research quantum computing
/agents
```

## Programmatic Usage

```python
from telegram_praisonai_bot.bot import PraisonAITelegramBot

bot = PraisonAITelegramBot(
    token="YOUR_TELEGRAM_TOKEN",
    api_url="http://localhost:8080",
    timeout=300
)
bot.run()
```

## Using the Client Directly

```python
import asyncio
from telegram_praisonai_bot import PraisonAIClient

async def main():
    client = PraisonAIClient(api_url="http://localhost:8080")
    
    # Run workflow
    result = await client.run_workflow("Research AI trends")
    print(result)
    
    # Run specific agent
    result = await client.run_agent("Write an article", "writer")
    print(result)
    
    # List agents
    agents = await client.list_agents()
    print(agents)

asyncio.run(main())
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | (required) | Telegram bot token from @BotFather |
| `PRAISONAI_API_URL` | `http://localhost:8080` | PraisonAI server URL |
| `PRAISONAI_TIMEOUT` | `300` | Request timeout in seconds |

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [PraisonAI GitHub](https://github.com/MervinPraison/PraisonAI)
- [python-telegram-bot Documentation](https://python-telegram-bot.org)

## License

MIT
