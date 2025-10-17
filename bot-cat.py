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
intents.message_content = True  # necessário para ler conteúdo de mensagens
bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# CORES DAS EMBEDS
# -----------------------------
CORES = {
    "▸DESTAQUES": 0xFF8C42,    # Laranja
    "▸EQUIPAMENTOS": 0xADD8E6, # Azul Claro
    "▸OUTROS": 0x0A3D62,       # Azul Escuro
    "▸SOMBRIOS": 0xA9A9A9,     # Cinza
    "▸VISUAIS": 0x800080       # Roxo
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
# FUNÇÃO PARA CRIAR EMBEDS
# -----------------------------
def criar_embeds(itens, automatico=True):
    embeds = []
    tipo_postagem = "*Postagem Automática*" if automatico else "*Postagem Manual*"
    for categoria in itens:
        nome_categoria = categoria.get("categoria", "")
        cor = CORES.get(nome_categoria, 0xFFFFFF)
        embed = discord.Embed(
            title=f"🛒 Catálogo de Itens - {nome_categoria}",
            color=cor,
            description=tipo_postagem
        )
        itens_categoria = categoria.get("itens", [])
        if itens_categoria:
            embed.add_field(
                name="Itens",
                value="\n".join([f"{item['nome']} - {item['preco']}" for item in itens_categoria]),
                inline=False
            )
        embeds.append(embed)
    return embeds

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

        embeds = criar_embeds(itens, automatico=False)
        for embed in embeds:
            await interaction.response.send_message(embed=embed)

    except Exception as e:
        print("Erro no comando /catalogo:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao carregar o catálogo.", ephemeral=True)

# -----------------------------
# POSTAGEM AUTOMÁTICA
# -----------------------------
@tasks.loop(seconds=60*60*24*25)  # 25 dias em segundos
async def postar_catalogo():
    try:
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            guild = await bot.fetch_guild(GUILD_ID)
        canal = guild.get_channel(CHANNEL_ID)
        if not canal:
            canal = await guild.fetch_channel(CHANNEL_ID)

        itens = carregar_itens()
        if not itens:
            await canal.send("O catálogo está vazio.")
            return

        embeds = criar_embeds(itens, automatico=True)
        for embed in embeds:
            await canal.send(embed=embed)

    except Exception as e:
        print("Erro ao postar catálogo automaticamente:")
        traceback.print_exc()

# -----------------------------
# RODA O BOT
# -----------------------------
bot.run(TOKEN)
