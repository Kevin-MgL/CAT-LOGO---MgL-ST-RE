import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
import traceback
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURAÇÃO
# -----------------------------
TOKEN = "SEU_TOKEN_AQUI"  # Substitua pelo token do bot
GUILD_ID = 1428479253997162548  # Substitua pelo ID do seu servidor
CHANNEL_ID = 1428479568808771605  # Canal onde o catálogo será postado

ITEMS_FILE = "itens.json"
LAST_POST_FILE = "ultima_postagem.txt"

# Cria arquivos caso não existam
if not os.path.exists(ITEMS_FILE):
    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

if not os.path.exists(LAST_POST_FILE):
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write("0")

# -----------------------------
# FUNÇÕES AUXILIARES
# -----------------------------
def carregar_itens():
    try:
        with open(ITEMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler {ITEMS_FILE}: {e}")
        return []

def salvar_ultima_postagem(timestamp):
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write(str(timestamp))

def ler_ultima_postagem():
    try:
        with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
            return float(f.read())
    except:
        return 0

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
    post_catalogo_auto.start()

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

        embeds = []

        # Monta cada embed por categoria
        for categoria in itens:
            embed = discord.Embed(
                title=categoria["categoria"],
                color=discord.Color(int(categoria.get("cor", "0x808080"), 16))
            )
            for item in categoria["itens"]:
                embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)
            embeds.append(embed)

        await interaction.response.send_message(embeds=embeds)

    except Exception as e:
        print("Erro no comando /catalogo:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao carregar o catálogo.", ephemeral=True)

# -----------------------------
# POSTAGEM AUTOMÁTICA A CADA 25 DIAS
# -----------------------------
@tasks.loop(hours=24)
async def post_catalogo_auto():
    try:
        ultima = ler_ultima_postagem()
        agora = datetime.utcnow().timestamp()
        # 25 dias em segundos
        if agora - ultima >= 25*24*60*60:
            canal = bot.get_channel(CHANNEL_ID)
            if canal:
                itens = carregar_itens()
                if itens:
                    mensagem = "📦 Postagem Automática\n\n"
                    embeds = []
                    for categoria in itens:
                        embed = discord.Embed(
                            title=categoria["categoria"],
                            color=discord.Color(int(categoria.get("cor", "0x808080"), 16))
                        )
                        for item in categoria["itens"]:
                            embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)
                        embeds.append(embed)
                    await canal.send(content=mensagem, embeds=embeds)
                    salvar_ultima_postagem(agora)
    except Exception as e:
        print("Erro na postagem automática:")
        traceback.print_exc()

# -----------------------------
# RODA O BOT
# -----------------------------
bot.run(TOKEN)
