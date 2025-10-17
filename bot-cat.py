import discord
from discord.ext import commands, tasks
from datetime import datetime
import os

# -----------------------------
# CONFIGURAÇÕES BÁSICAS
# -----------------------------
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))
CATALOG_CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# CORES DAS CATEGORIAS
# -----------------------------
CORES = {
    "▸ DESTAQUES": 0xFF8C42,     # Laranja
    "▸ EQUIPAMENTOS": 0x2ECCFF,  # Azul claro
    "▸ OUTROS": 0x0A3D62,        # Azul escuro
    "▸ SOMBRIOS": 0xA9A9A9,      # Cinza
    "▸ VISUAIS": 0x800080        # Roxo
}

# -----------------------------
# CRIA EMBEDS DO CATÁLOGO
# -----------------------------
def criar_embeds(automatico=False):
    rodape = "📅 Postagem automática (a cada 25 dias)" if automatico else "🪶 Postagem manual"
    embeds = []

    embeds.append(discord.Embed(
        title="▸ DESTAQUES",
        description="⚔️ Itens mais recentes e populares disponíveis no catálogo.",
        color=CORES["▸ DESTAQUES"]
    ).set_footer(text=rodape))

    embeds.append(discord.Embed(
        title="▸ EQUIPAMENTOS",
        description="🛡️ Armas, armaduras e acessórios lendários para os guerreiros de elite.",
        color=CORES["▸ EQUIPAMENTOS"]
    ).set_footer(text=rodape))

    embeds.append(discord.Embed(
        title="▸ OUTROS",
        description="📦 Itens diversos, utilidades raras e colecionáveis únicos.",
        color=CORES["▸ OUTROS"]
    ).set_footer(text=rodape))

    embeds.append(discord.Embed(
        title="▸ SOMBRIOS",
        description="🌑 Artefatos amaldiçoados e equipamentos das trevas. Somente para os destemidos.",
        color=CORES["▸ SOMBRIOS"]
    ).set_footer(text=rodape))

    embeds.append(discord.Embed(
        title="▸ VISUAIS",
        description="🎭 Aparências e visuais exclusivos para personalizar o seu estilo.",
        color=CORES["▸ VISUAIS"]
    ).set_footer(text=rodape))

    return embeds


# -----------------------------
# COMANDO MANUAL
# -----------------------------
@bot.tree.command(name="catalogo", description="Mostra o catálogo de itens disponíveis.")
async def catalogo(interaction: discord.Interaction):
    embeds = criar_embeds(automatico=False)
    await interaction.response.send_message(embeds=embeds)


# -----------------------------
# LOOP AUTOMÁTICO (a cada 25 dias)
# -----------------------------
@tasks.loop(hours=600)  # 25 dias = 600 horas
async def postar_catalogo():
    canal = bot.get_channel(CATALOG_CHANNEL_ID)
    if canal:
        embeds = criar_embeds(automatico=True)
        await canal.send(embeds=embeds)
        print(f"[{datetime.now()}] Catálogo postado automaticamente.")


# -----------------------------
# EVENTO DE INICIALIZAÇÃO
# -----------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot online como {bot.user}")
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Comandos slash sincronizados no servidor {GUILD_ID}.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")

    postar_catalogo.start()


# -----------------------------
# EXECUÇÃO DO BOT
# -----------------------------
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERRO: Variável DISCORD_TOKEN não encontrada.")
