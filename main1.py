import asyncio
import requests
import pandas as pd

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD

# =========================================
# CONFIGURACION
# =========================================

TOKEN = "8821914120:AAHrxlzxCpLfYd1Ux3u5QDa27x1gTnP72kU"

# ID DEL GRUPO VIP
VIP_GROUP_ID = -1003801482151

# ID DEL CANAL FREE
FREE_CHANNEL_ID = -1003972519997

# TU ID DE TELEGRAM
ADMIN_ID = 8507166595

# =========================================
# FUNCION ANALISIS
# =========================================

def analizar(par):

    url = f"https://api.binance.com/api/v3/klines?symbol={par}&interval=5m&limit=100"

    data = requests.get(url).json()

    cierres = [float(x[4]) for x in data]

    df = pd.DataFrame(cierres, columns=["close"])

    # RSI
    rsi = RSIIndicator(df["close"], window=14)
    df["rsi"] = rsi.rsi()

    # EMA
    ema = EMAIndicator(df["close"], window=20)
    df["ema"] = ema.ema_indicator()

    # MACD
    macd = MACD(df["close"])

    df["macd"] = macd.macd()
    df["signal"] = macd.macd_signal()

    precio = df["close"].iloc[-1]
    ultimo_rsi = df["rsi"].iloc[-1]
    ultima_ema = df["ema"].iloc[-1]
    ultimo_macd = df["macd"].iloc[-1]
    ultima_signal = df["signal"].iloc[-1]

    señal = "🟡 MERCADO NEUTRAL"

    # COMPRA
    if (
        ultimo_rsi < 35
        and precio > ultima_ema
        and ultimo_macd > ultima_signal
    ):

        señal = "🟢 POSIBLE COMPRA"

    # VENTA
    elif (
        ultimo_rsi > 65
        and precio < ultima_ema
        and ultimo_macd < ultima_signal
    ):

        señal = "🔴 POSIBLE VENTA"

    mensaje = f"""
🚀 CryptoPulse AI

💎 PAR: {par}

💰 Precio: {round(precio,2)}

📈 RSI: {round(ultimo_rsi,2)}
📊 EMA20: {round(ultima_ema,2)}
⚡ MACD: {round(ultimo_macd,2)}

📡 Señal:
{señal}
"""

    return mensaje

# =========================================
# COMANDOS
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = """
🚀 Bienvenido a CryptoPulse AI

Comandos disponibles:

/btc → análisis BTC
/eth → análisis ETH
/sol → análisis SOL
/vip → acceso premium
/id → ver tu ID
/help → ayuda
"""

    await update.message.reply_text(texto)

# =========================================

async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = analizar("BTCUSDT")

    await update.message.reply_text(mensaje)

# =========================================

async def eth(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = analizar("ETHUSDT")

    await update.message.reply_text(mensaje)

# =========================================

async def sol(update: Update, context: ContextTypes.DEFAULT_TYPE):

    mensaje = analizar("SOLUSDT")

    await update.message.reply_text(mensaje)

# =========================================

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = """
💎 VIP PREMIUM

Beneficios:

✅ Señales privadas
✅ Más precisión
✅ Alertas rápidas
✅ Más monedas
✅ Estrategias avanzadas

📩 Contacta al administrador.
"""

    await update.message.reply_text(texto)

# =========================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = """
📚 AYUDA

Usa:

/btc
/eth
/sol
/vip
/id
"""

    await update.message.reply_text(texto)

# =========================================

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    await update.message.reply_text(
        f"🆔 Tu ID es:\n{user_id}"
    )

# =========================================
# AGREGAR VIP
# =========================================

async def agregarvip(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # SOLO ADMIN
    if update.effective_user.id != ADMIN_ID:
        return

    try:

        user_id = int(context.args[0])

        invite = await context.bot.create_chat_invite_link(
            chat_id=VIP_GROUP_ID,
            member_limit=1
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
🔥 ACCESO VIP APROBADO

Únete aquí:
{invite.invite_link}
"""
        )

        await update.message.reply_text(
            "✅ Usuario agregado correctamente"
        )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            "❌ Uso correcto:\n/agregarvip ID"
        )

# =========================================
# SEÑALES AUTOMATICAS
# =========================================

async def señales_automaticas(app):

    while True:

        try:

            pares = [
                "BTCUSDT",
                "ETHUSDT",
                "SOLUSDT"
            ]

            for par in pares:

                mensaje = analizar(par)

                # VIP
                await app.bot.send_message(
                    chat_id=VIP_GROUP_ID,
                    text=f"💎 VIP SIGNAL\n{mensaje}"
                )

                # FREE
                await app.bot.send_message(
                    chat_id=FREE_CHANNEL_ID,
                    text=f"🆓 FREE SIGNAL\n{mensaje}"
                )

                await asyncio.sleep(5)

        except Exception as e:

            print(f"ERROR: {e}")

        # Espera 5 minutos
        await asyncio.sleep(300)

# =========================================
# APP
# =========================================

app = ApplicationBuilder().token(TOKEN).build()

# COMANDOS
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("btc", btc))
app.add_handler(CommandHandler("eth", eth))
app.add_handler(CommandHandler("sol", sol))
app.add_handler(CommandHandler("vip", vip))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("id", id_command))
app.add_handler(CommandHandler("agregarvip", agregarvip))

# =========================================
# INICIAR BOT
# =========================================

print("🚀 BOT ONLINE")

loop = asyncio.get_event_loop()

loop.create_task(
    señales_automaticas(app)
)

app.run_polling()