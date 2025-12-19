"""Discord bot powered by PraisonAI."""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from discord_praisonai_bot.client import PraisonAIClient


class PraisonAIBot(commands.Bot):
    """Discord bot that integrates with PraisonAI multi-agent framework.

    Example:
        ```python
        bot = PraisonAIBot(
            token="YOUR_DISCORD_TOKEN",
            api_url="http://localhost:8080"
        )
        bot.run_bot()
        ```
    """

    def __init__(
        self,
        token: str,
        api_url: str = "http://localhost:8080",
        timeout: int = 300,
        **kwargs,
    ) -> None:
        """Initialize the PraisonAI Discord bot.

        Args:
            token: Discord bot token.
            api_url: PraisonAI API server URL.
            timeout: Request timeout in seconds.
        """
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            **kwargs,
        )

        self.token = token
        self.api_url = api_url
        self.timeout = timeout
        self.praisonai = PraisonAIClient(api_url=api_url, timeout=timeout)

        # Register commands
        self._register_commands()

    def _register_commands(self) -> None:
        """Register slash commands."""

        @self.slash_command(name="ask", description="Ask PraisonAI agents a question")
        async def ask(ctx: discord.ApplicationContext, query: str, agent: str = None):
            """Ask PraisonAI agents a question.

            Args:
                ctx: Discord application context.
                query: The question or task.
                agent: Optional specific agent to use.
            """
            await ctx.defer()

            try:
                if agent:
                    response = await self.praisonai.run_agent(query, agent)
                else:
                    response = await self.praisonai.run_workflow(query)

                # Discord has a 2000 character limit
                if len(response) > 1900:
                    # Split into chunks
                    chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await ctx.followup.send(chunk)
                        else:
                            await ctx.send(chunk)
                else:
                    await ctx.followup.send(response or "No response received.")

            except Exception as e:
                await ctx.followup.send(f"❌ Error: {str(e)}")

        @self.slash_command(name="agents", description="List available PraisonAI agents")
        async def agents(ctx: discord.ApplicationContext):
            """List available PraisonAI agents."""
            await ctx.defer()

            try:
                response = await self.praisonai.list_agents()
                await ctx.followup.send(response)
            except Exception as e:
                await ctx.followup.send(f"❌ Error: {str(e)}")

        @self.slash_command(name="praisonai", description="Get PraisonAI bot info")
        async def praisonai_info(ctx: discord.ApplicationContext):
            """Show PraisonAI bot information."""
            embed = discord.Embed(
                title="🤖 PraisonAI Bot",
                description="Multi-agent AI assistant powered by PraisonAI",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Commands",
                value=(
                    "`/ask <query>` - Ask PraisonAI agents\n"
                    "`/ask <query> <agent>` - Ask a specific agent\n"
                    "`/agents` - List available agents\n"
                    "`/praisonai` - Show this info"
                ),
                inline=False
            )
            embed.add_field(
                name="API URL",
                value=f"`{self.api_url}`",
                inline=True
            )
            embed.add_field(
                name="Links",
                value=(
                    "[PraisonAI Docs](https://docs.praison.ai) | "
                    "[GitHub](https://github.com/MervinPraison/PraisonAI)"
                ),
                inline=False
            )
            await ctx.respond(embed=embed)

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        print(f"✅ {self.user} is online!")
        print(f"📡 Connected to PraisonAI at {self.api_url}")

    def run_bot(self) -> None:
        """Run the bot."""
        self.run(self.token)


def main():
    """Main entry point for the bot."""
    load_dotenv()

    token = os.getenv("DISCORD_TOKEN")
    api_url = os.getenv("PRAISONAI_API_URL", "http://localhost:8080")
    timeout = int(os.getenv("PRAISONAI_TIMEOUT", "300"))

    if not token:
        print("❌ Error: DISCORD_TOKEN environment variable is required")
        print("Set it in .env file or environment:")
        print("  export DISCORD_TOKEN=your_token_here")
        return

    bot = PraisonAIBot(token=token, api_url=api_url, timeout=timeout)
    bot.run_bot()


if __name__ == "__main__":
    main()
