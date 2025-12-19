"""Telegram bot powered by PraisonAI."""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from telegram_praisonai_bot.client import PraisonAIClient

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class PraisonAITelegramBot:
    """Telegram bot that integrates with PraisonAI multi-agent framework."""

    def __init__(
        self,
        token: str,
        api_url: str = "http://localhost:8080",
        timeout: int = 300,
    ) -> None:
        self.token = token
        self.api_url = api_url
        self.timeout = timeout
        self.praisonai = PraisonAIClient(api_url=api_url, timeout=timeout)
        self.application = Application.builder().token(token).build()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register command and message handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("ask", self.ask_command))
        self.application.add_handler(CommandHandler("agent", self.agent_command))
        self.application.add_handler(CommandHandler("agents", self.agents_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        welcome_message = (
            "🤖 *Welcome to PraisonAI Bot!*\n\n"
            "I'm powered by PraisonAI multi-agent framework.\n\n"
            "*Commands:*\n"
            "/ask <query> - Ask PraisonAI agents\n"
            "/agent <name> <query> - Ask a specific agent\n"
            "/agents - List available agents\n"
            "/help - Show this help message\n\n"
            "Or just send me a message and I'll process it!"
        )
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_message = (
            "*PraisonAI Bot Commands:*\n\n"
            "/ask <query> - Ask PraisonAI agents a question\n"
            "/agent <name> <query> - Ask a specific agent\n"
            "/agents - List all available agents\n"
            "/help - Show this help message\n\n"
            "*Examples:*\n"
            "`/ask What are the latest AI trends?`\n"
            "`/agent researcher Research quantum computing`\n\n"
            f"*API URL:* `{self.api_url}`"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')

    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /ask command."""
        if not context.args:
            await update.message.reply_text("Usage: /ask <your question>")
            return

        query = " ".join(context.args)
        await update.message.reply_text("🔄 Processing your request...")

        try:
            response = await self.praisonai.run_workflow(query)
            await self._send_long_message(update, response)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def agent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /agent command."""
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /agent <agent_name> <your question>")
            return

        agent = context.args[0]
        query = " ".join(context.args[1:])
        await update.message.reply_text(f"🔄 Asking {agent} agent...")

        try:
            response = await self.praisonai.run_agent(query, agent)
            await self._send_long_message(update, response)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def agents_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /agents command."""
        try:
            response = await self.praisonai.list_agents()
            await update.message.reply_text(response, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages."""
        query = update.message.text
        await update.message.reply_text("🔄 Processing your request...")

        try:
            response = await self.praisonai.run_workflow(query)
            await self._send_long_message(update, response)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def _send_long_message(self, update: Update, text: str) -> None:
        """Send a long message, splitting if necessary."""
        if not text:
            await update.message.reply_text("No response received.")
            return

        # Telegram has a 4096 character limit
        max_length = 4000
        if len(text) <= max_length:
            await update.message.reply_text(text)
        else:
            # Split into chunks
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            for chunk in chunks:
                await update.message.reply_text(chunk)

    def run(self) -> None:
        """Run the bot."""
        logger.info("Starting PraisonAI Telegram Bot...")
        logger.info(f"Connected to PraisonAI at {self.api_url}")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point for the bot."""
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_url = os.getenv("PRAISONAI_API_URL", "http://localhost:8080")
    timeout = int(os.getenv("PRAISONAI_TIMEOUT", "300"))

    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable is required")
        print("Get your token from @BotFather on Telegram")
        print("Set it in .env file or environment:")
        print("  export TELEGRAM_BOT_TOKEN=your_token_here")
        return

    bot = PraisonAITelegramBot(token=token, api_url=api_url, timeout=timeout)
    bot.run()


if __name__ == "__main__":
    main()
