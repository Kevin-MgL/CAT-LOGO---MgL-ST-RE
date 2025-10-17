import discord
from discord.ext import tasks
from discord import Embed
import asyncio
import os

# ================= CONFIGURAÇÃO =================
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
GUILD_ID = int(os.environ.get("GUILD_ID"))
# =================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = discord.Client(intents=intents)

# Cores dos embeds
CORES = {
    "DESTAQUES": 0xFFA500,      # Laranja
    "EQUIPAMENTOS": 0x0077FF,   # Azul normal
    "OUTROS": 0x0055AA,         # Azul mais escuro
    "SOMBRIOS": 0x808080,       # Cinza
    "VISUAIS": 0x800080         # Roxo
}

# Conteúdo dos embeds (exemplo, substitua pelo seu)
CATEGORIAS = {
    "DESTAQUES": ["Item destaque 1", "Item destaque 2"],
    "EQUIPAMENTOS": ["Equipamento 1", "Equipamento 2"],
    "OUTROS": ["Outro 1", "Outro 2"],
    "SOMBRIOS": ["Sombrio 1", "Sombrio 2"],
    "VISUAIS": ["Visual 1", "Visual 2"]
}

async def postar_catalogo():
    try:
        canal = await bot.fetch_channel(CHANNEL_ID)
    except discord.errors.NotFound:
        print(f"[ERRO] Canal com ID {CHANNEL_ID} não encontrado ou bot não tem acesso.")
        return
    except discord.errors.Forbidden:
        print(f"[ERRO] Sem permissão para acessar o canal {CHANNEL_ID}.")
        return

    embed = Embed(title="📚 Catálogo de Itens", description="Atualização automática do catálogo", color=0xFFFFFF)
    for categoria, itens in CATEGORIAS.items():
        descricao = "\n".join(f"• {item}" for item in itens)
        embed.add_field(name=f"▸{categoria}", value=descricao or "Sem itens", inline=False)
        embed.color = CORES[categoria]

    await canal.send(embed=embed)
    print("[INFO] Catálogo enviado com sucesso.")

# Loop diário usando segundos
@tasks.loop(seconds=86400)
async def loop_catalogo():
    await postar_catalogo()

@bot.event
async def on_ready():
    print(f"[INFO] Bot conectado como {bot.user}")
    loop_catalogo.start()

bot.run(TOKEN)

