# discord-praisonai-bot

Discord bot powered by [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install discord-praisonai-bot
```

## Quick Start

1. **Create a Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to Bot → Add Bot
   - Copy the token
   - Enable "Message Content Intent" under Privileged Gateway Intents

2. **Invite Bot to Server**
   - Go to OAuth2 → URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Use Slash Commands`
   - Copy and open the generated URL

3. **Start PraisonAI Server**
   ```bash
   pip install praisonai
   praisonai serve agents.yaml --port 8080
   ```

4. **Run the Bot**
   ```bash
   export DISCORD_TOKEN=your_discord_token
   export PRAISONAI_API_URL=http://localhost:8080
   discord-praisonai-bot
   ```

   Or create a `.env` file:
   ```env
   DISCORD_TOKEN=your_discord_token
   PRAISONAI_API_URL=http://localhost:8080
   PRAISONAI_TIMEOUT=300
   ```

## Commands

| Command | Description |
|---------|-------------|
| `/ask <query>` | Ask PraisonAI agents a question |
| `/ask <query> <agent>` | Ask a specific agent (e.g., researcher) |
| `/agents` | List available PraisonAI agents |
| `/praisonai` | Show bot information |

## Usage Examples

```
/ask What are the latest trends in AI?
/ask Research quantum computing researcher
/agents
```

## Programmatic Usage

```python
from discord_praisonai_bot import PraisonAIBot

bot = PraisonAIBot(
    token="YOUR_DISCORD_TOKEN",
    api_url="http://localhost:8080",
    timeout=300
)
bot.run_bot()
```

## Using the Client Directly

```python
import asyncio
from discord_praisonai_bot import PraisonAIClient

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
| `DISCORD_TOKEN` | (required) | Discord bot token |
| `PRAISONAI_API_URL` | `http://localhost:8080` | PraisonAI server URL |
| `PRAISONAI_TIMEOUT` | `300` | Request timeout in seconds |

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [PraisonAI GitHub](https://github.com/MervinPraison/PraisonAI)
- [Discord.py Documentation](https://docs.pycord.dev)

## License

MIT
