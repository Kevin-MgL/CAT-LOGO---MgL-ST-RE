import os
import asyncio
import discord
from discord.ext import commands, tasks
from aiohttp import web

# Variáveis de ambiente
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --------- Função de postar catálogo ----------
async def postar_catalogo():
    canal = bot.get_channel(CHANNEL_ID)
    if not canal:
        print(f"Canal {CHANNEL_ID} não encontrado.")
        return

    # Exemplo de embed
    embed = discord.Embed(
        title="▸EQUIPAMENTOS",
        description="Lista de equipamentos do catálogo",
        color=discord.Color.blue()  # Azul normal
    )

    # Adicionar campos de exemplo
    embed.add_field(name="Espada", value="100 moedas", inline=True)
    embed.add_field(name="Escudo", value="150 moedas", inline=True)
    
    await canal.send(embed=embed)
    print("Catálogo postado com sucesso!")

# --------- Loop diário ----------
@tasks.loop(hours=24)
async def loop_diario():
    await postar_catalogo()

@loop_diario.before_loop
async def before_loop():
    await bot.wait_until_ready()

# --------- Servidor HTTP mínimo para Render ----------
async def handle(request):
    return web.Response(text="Bot rodando")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)  # Porta aberta para Render
    await site.start()
    print("Webserver iniciado na porta 10000")

# --------- Evento on_ready ----------
@bot.event
async def on_ready():
    print(f"Bot logado como {bot.user}")
    if not loop_diario.is_running():
        loop_diario.start()
    # Inicia o servidor HTTP em paralelo
    asyncio.create_task(start_webserver())

bot.run(TOKEN)
