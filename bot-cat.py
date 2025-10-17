import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
import traceback
import asyncio

# -----------------------------
# CONFIGURAÇÃO
# -----------------------------
TOKEN = os.environ.get("DISCORD_TOKEN")  # Token armazenado como variável secreta no Replit
GUILD_ID = int(os.environ.get("GUILD_ID"))  # ID do servidor
CANAL_ID = int(os.environ.get("CANAL_ID"))  # ID do canal para envio automático

ITEMS_FILE = "itens.json"

# Cria arquivo JSON caso não exista
if not os.path.exists(ITEMS_FILE):
    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# -----------------------------
# FUNÇÕES AUXILIARES
# -----------------------------
def carregar_itens():
    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Erro ao carregar itens:", e)
        return []

def salvar_itens(itens):
    try:
        with open(ITEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(itens, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Erro ao salvar itens:", e)

# -----------------------------
# CONFIGURAÇÃO DO BOT
# -----------------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
guild = discord.Object(id=GUILD_ID)

# -----------------------------
# EVENTO ON_READY
# -----------------------------
@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")
    try:
        await bot.tree.sync(guild=guild)
        print("Comandos slash sincronizados no servidor.")
    except Exception as e:
        print(e)
    # Inicia a tarefa de envio automático
    enviar_catalogo_periodicamente.start()

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

        for grupo in itens:  # Cada grupo é uma categoria/subtítulo
            embed = discord.Embed(title=grupo["categoria"], color=grupo.get("cor", discord.Color.light_grey()))
            for item in grupo["itens"]:
                embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)
            await interaction.response.send_message(embed=embed)

    except Exception:
        print("Erro no comando /catalogo:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao carregar o catálogo.", ephemeral=True)

# -----------------------------
# TAREFA AUTOMÁTICA PARA ENVIAR CATALOGO
# -----------------------------
@tasks.loop(hours=1)  # A cada hora ele verifica, mas só envia quando atingir o intervalo de 25 dias
async def enviar_catalogo_periodicamente():
    await bot.wait_until_ready()
    # Calcula 25 dias em segundos
    tempo_espera = 25 * 24 * 60 * 60
    await asyncio.sleep(tempo_espera)  # Espera 25 dias
    canal = bot.get_channel(CANAL_ID)
    if canal:
        for grupo in carregar_itens():
            embed = discord.Embed(title=grupo["categoria"], color=grupo.get("cor", discord.Color.light_grey()))
            for item in grupo["itens"]:
                embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)
            await canal.send(embed=embed)
    else:
        print(f"Canal {CANAL_ID} não encontrado.")

# -----------------------------
# RODA O BOT
# -----------------------------
bot.run(TOKEN)
