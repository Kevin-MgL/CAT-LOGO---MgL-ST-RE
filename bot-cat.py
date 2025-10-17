import discord
from discord.ext import commands, tasks
import asyncio
import os
import json
import traceback

# -----------------------------
# CONFIGURAÇÃO DE VARIÁVEIS
# -----------------------------
TOKEN = os.environ.get("TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID", 0))
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", 0))
ITEMS_FILE = "itens.json"

# -----------------------------
# FUNÇÕES AUXILIARES
# -----------------------------
def carregar_itens():
    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {ITEMS_FILE} não encontrado.")
        return []
    except json.JSONDecodeError as e:
        print(f"Erro ao ler {ITEMS_FILE}: JSON inválido.")
        print(e)
        return []
    except Exception as e:
        print(f"Erro inesperado ao carregar {ITEMS_FILE}:")
        print(e)
        return []

# -----------------------------
# CONFIGURAÇÃO DO BOT
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# CORES DAS EMBEDS
# -----------------------------
CORES = {
    "▸**DESTAQUES**": 0xFF8C42,    # Laranja
    "▸**EQUIPAMENTOS**": 0xADD8E6, # Azul Claro
    "▸**OUTROS**": 0x0A3D62,       # Azul Escuro
    "▸**SOMBRIOS**": 0xA9A9A9,     # Cinza
    "▸**VISUAIS**": 0x800080       # Roxo
}

# -----------------------------
# EVENTO ON_READY
# -----------------------------
@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")
    try:
        await bot.tree.sync()
        print("Comandos slash sincronizados no servidor.")
        postar_catalogo.start()
    except Exception as e:
        print(e)

# -----------------------------
# COMANDO /catalogo
# -----------------------------
@bot.tree.command(name="catalogo", description="Mostra o catálogo de itens disponíveis")
async def catalogo(interaction: discord.Interaction):
    try:
        itens = carregar_itens()
        if not itens:
            await interaction.response.send_message("O catálogo está vazio.", ephemeral=True)
            return

        embed_msg = []
        for categoria in itens:
            nome_categoria = categoria.get("categoria", "")
            embed = discord.Embed(
                title=f"🛒 {nome_categoria}",
                description="*Postagem Manual*",
                color=CORES.get(nome_categoria, discord.Color.dark_gray())
            )
            embed.add_field(
                name="\u200b",
                value="\n".join([f"{item['nome']} - {item['preco']}" for item in categoria.get("itens", [])]),
                inline=False
            )
            embed_msg.append(embed)

        for e in embed_msg:
            await interaction.response.send_message(embed=e)

    except Exception as e:
        print("Erro no comando /catalogo:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao carregar o catálogo.", ephemeral=True)

# -----------------------------
# POSTAGEM AUTOMÁTICA
# -----------------------------
@tasks.loop(hours=24)  # Loop diário
async def postar_catalogo():
    try:
        canal = bot.get_channel(CHANNEL_ID)
        if canal is None:
            canal = await bot.fetch_channel(CHANNEL_ID)

        itens = carregar_itens()
        if not itens:
            await canal.send("O catálogo está vazio.")
            return

        embed_msg = []
        for categoria in itens:
            nome_categoria = categoria.get("categoria", "")
            embed = discord.Embed(
                title=f"🛒 {nome_categoria}",
                description="*Postagem Automática*",
                color=CORES.get(nome_categoria, discord.Color.dark_gray())
            )
            embed.add_field(
                name="\u200b",
                value="\n".join([f"{item['nome']} - {item['preco']}" for item in categoria.get("itens", [])]),
                inline=False
            )
            embed_msg.append(embed)

        for e in embed_msg:
            await canal.send(embed=e)

    except Exception as e:
        print("Erro ao postar catálogo automaticamente:")
        traceback.print_exc()

# -----------------------------
# RODA O BOT
# -----------------------------
bot.run(TOKEN)
