import os 
from dotenv import load_dotenv
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
import logging

load_dotenv('secrets/.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FashionBot:
    def __init__(self):
        self.bot = Client(
            name="FashionIcon",
            api_id=os.environ.get("API_ID"),
            api_hash=os.environ.get("API_HASH"),
            bot_token=os.environ.get("BOT_TOKEN")
        )
        self.user_starts = set()
        self.rates = {
            'MLC': 275,
            'USD': 330,
            'EUR': 345
        }
        self.user_state = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.on_message(filters.command("start") & filters.private)
        async def start(client: Client, message: Message):
            user_id = message.from_user.id
            user_name = message.from_user.first_name
            logger.info(f"User {user_name} (ID: {user_id}) started the bot")
            
            if user_id in self.user_starts:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"MLC: {self.rates['MLC']}", callback_data="change_mlc"),
                     InlineKeyboardButton(f"USD: {self.rates['USD']}", callback_data="change_usd"),
                     InlineKeyboardButton(f"EUR: {self.rates['EUR']}", callback_data="change_eur")],
                    [InlineKeyboardButton("📚 Ver Comandos", callback_data="show_commands")],
                ])
                await message.reply_text(
                    f"¡Hola de nuevo, {user_name}!\n\n"
                    f"Tasas de cambio actuales:\n"
                    f"MLC: {self.rates['MLC']}\n"
                    f"USD: {self.rates['USD']}\n"
                    f"EUR: {self.rates['EUR']}\n\n"
                    "Haz clic en cualquier moneda para cambiar su valor.",
                    reply_markup=keyboard
                )
            else:
                self.user_starts.add(user_id)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📚 Ver Comandos", callback_data="show_commands")],
                ])
                await message.reply_text(
                    f"👋 ¡Bienvenido, {user_name}!\n\n"
                    "Soy tu asistente personal para el rastreo y manejo de paquetes, estoy aquí para ayudarte. "
                    "Puedo ayudarte a añadir pedidos, editar existentes, recibir totales, gráficos de ventas con respecto al mes anterior y mucho más.\n\n"
                    "¿Qué te gustaría hacer hoy?",
                    reply_markup=keyboard
                )

        @self.bot.on_message(filters.command("rates") & filters.private)
        async def rates_command(client: Client, message: Message):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"MLC: {self.rates['MLC']}", callback_data="change_mlc"),
                 InlineKeyboardButton(f"USD: {self.rates['USD']}", callback_data="change_usd"),
                 InlineKeyboardButton(f"EUR: {self.rates['EUR']}", callback_data="change_eur")],
            ])
            await message.reply_text(
                "Tasas de cambio actuales:\n"
                f"MLC: {self.rates['MLC']}\n"
                f"USD: {self.rates['USD']}\n"
                f"EUR: {self.rates['EUR']}\n\n"
                "Haz clic en cualquier moneda para cambiar su valor.",
                reply_markup=keyboard
            )

        @self.bot.on_message(filters.command("help") & filters.private)
        async def help_command(client: Client, message: Message):
            logger.info(f"User {message.from_user.first_name} (ID: {message.from_user.id}) requested help")
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Volver al Inicio", callback_data="back_to_start")],
            ])
            await message.reply_text(
                "🌟 **Comandos Disponibles:**\n\n"
                "🔹 /start - Muestra el mensaje de bienvenida\n"
                "🔹 /help - Muestra este mensaje de ayuda\n"
                "🔹 /rates - Muestra y permite cambiar las tasas\n"
                "🔹 /outfit - Recibe recomendaciones de outfits\n"
                "🔹 /trends - Descubre las últimas tendencias\n\n"
                "¿Necesitas más ayuda? ¡No dudes en preguntarme!",
                reply_markup=keyboard
            )

        @self.bot.on_message(filters.text & filters.private)
        async def handle_rate_change(client: Client, message: Message):
            user_id = message.from_user.id
            if user_id in self.user_state:
                currency = self.user_state[user_id]
                try:
                    new_rate = int(message.text)
                    self.rates[currency] = new_rate
                    del self.user_state[user_id]
                    await message.reply_text(f"✅ El valor de {currency} ha sido actualizado a {new_rate}")
                except ValueError:
                    await message.reply_text("❌ Por favor, envía un valor numérico entero válido.")
            
        @self.bot.on_callback_query()
        async def handle_callback(client: Client, callback_query):
            if callback_query.data == "show_commands":
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Volver al Inicio", callback_data="back_to_start")],
                ])
                await callback_query.message.edit_text(
                    "🌟 **Comandos Disponibles:**\n\n"
                    "🔹 /start - Muestra el mensaje de bienvenida\n"
                    "🔹 /help - Muestra este mensaje de ayuda\n"
                    "🔹 /rates - Muestra y permite cambiar las tasas\n"
                    "🔹 /outfit - Recibe recomendaciones de outfits\n"
                    "🔹 /trends - Descubre las últimas tendencias\n\n"
                    "¿Necesitas más ayuda? ¡No dudes en preguntarme!",
                    reply_markup=keyboard
                )
            elif callback_query.data == "back_to_start":
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📚 Ver Comandos", callback_data="show_commands")],
                ])
                await callback_query.message.edit_text(
                    f"👋 ¡Bienvenido, {callback_query.from_user.first_name}!\n\n"
                    "Soy tu asistente personal para el rastreo y manejo de paquetes, estoy aquí para ayudarte. "
                    "Puedo ayudarte a añadir pedidos, editar existentes, recibir totales, gráficos de ventas con respecto al mes anterior y mucho más.\n\n"
                    "¿Qué te gustaría hacer hoy?",
                    reply_markup=keyboard
                )
            elif callback_query.data.startswith("change_"):
                currency = callback_query.data.split("_")[1].upper()
                self.user_state[callback_query.from_user.id] = currency
                await callback_query.message.reply_text(
                    f"Por favor, envía el nuevo valor para {currency}:"
                )
            await callback_query.answer()

    def run(self):
        self.bot.run()


if __name__ == "__main__":
    bot = FashionBot()
    bot.run()