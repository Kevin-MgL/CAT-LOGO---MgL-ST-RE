import discord
from discord.ext import tasks, commands
import asyncio

# === CONFIGURAÇÕES ===
TOKEN = "SEU_TOKEN_AQUI"
CANAL_ID = 123456789012345678  # <-- coloque aqui o ID do canal que receberá o catálogo

# === INTENTS ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === EMBEDS DO CATÁLOGO ===

def criar_catalogo_embeds():
    # ▸ DESTAQUES (Laranja)
    destaques = discord.Embed(
        title="▸ DESTAQUES",
        description=(
            "**• Pacote de Moedas (Promoção)** 💰\n"
            "**• Passe de Temporada** ⭐\n"
            "**• Caixa Premium** 🎁"
        ),
        color=discord.Color.orange()
    )
    destaques.set_footer(text="Postagem automática do catálogo oficial • Desenvolvido por MgL")

    # ▸ EQUIPAMENTOS (Azul claro)
    equipamentos = discord.Embed(
        title="▸ EQUIPAMENTOS",
        description=(
            "**• Espada Flamejante** 🔥\n"
            "**• Escudo Congelante** ❄️\n"
            "**• Arco Celestial** 🌠"
        ),
        color=discord.Color.blue()
    )
    equipamentos.set_footer(text="Postagem automática do catálogo oficial • Desenvolvido por MgL")

    # ▸ OUTROS (Azul escuro)
    outros = discord.Embed(
        title="▸ OUTROS",
        description=(
            "**• Poções** 🧪\n"
            "**• Itens de evento** 🎊\n"
            "**• Emotes raros** 😎"
        ),
        color=discord.Color.dark_blue()
    )
    outros.set_footer(text="Postagem automática do catálogo oficial • Desenvolvido por MgL")

    # ▸ SOMBRIOS (Cinza)
    sombrios = discord.Embed(
        title="▸ SOMBRIOS",
        description=(
            "**• Lâmina Abissal** ⚔️\n"
            "**• Armadura Espectral** 🕸️\n"
            "**• Elmo do Vazio** 🌑"
        ),
        color=discord.Color.dark_gray()
    )
    sombrios.set_footer(text="Postagem automática do catálogo oficial • Desenvolvido por MgL")

    # ▸ VISUAIS (Roxo)
    visuais = discord.Embed(
        title="▸ VISUAIS",
        description=(
            "**• Visual Arcano** 💜\n"
            "**• Visual Samurai** 🥋\n"
            "**• Visual Neon** 💡"
        ),
        color=discord.Color.purple()
    )
    visuais.set_footer(text="Postagem automática do catálogo oficial • Desenvolvido por MgL")

    return [destaques, equipamentos, outros, sombrios, visuais]


# === FUNÇÃO PARA ENVIAR O CATÁLOGO ===
@tasks.loop(hours=600)  # 25 dias = 600 horas
async def enviar_catalogo():
    await bot.wait_until_ready()
    canal = bot.get_channel(CANAL_ID)
    if canal is None:
        print("❌ Canal não encontrado. Verifique o ID.")
        return

    embeds = criar_catalogo_embeds()
    for embed in embeds:
        await canal.send(embed=embed)
        await asyncio.sleep(1)  # intervalo curto entre mensagens

    print("✅ Catálogo enviado automaticamente.")


# === COMANDO MANUAL PARA TESTE ===
@bot.command()
async def catalogo(ctx):
    embeds = criar_catalogo_embeds()
    for embed in embeds:
        await ctx.send(embed=embed)
        await asyncio.sleep(1)
    await ctx.send("✅ *Postagem automática do catálogo oficial • Desenvolvido por MgL*")


# === EVENTOS ===
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    if not enviar_catalogo.is_running():
        enviar_catalogo.start()


# === EXECUÇÃO ===
bot.run(TOKEN)
