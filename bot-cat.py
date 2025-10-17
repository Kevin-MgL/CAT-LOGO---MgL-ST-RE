import discord
from discord.ext import tasks
import asyncio
import traceback
import os

# Variáveis essenciais
TOKEN = os.environ.get("TOKEN")       # Token do bot
GUILD_ID = 123456789012345678        # ID do servidor
CHANNEL_ID = 987654321098765432      # ID do canal onde o catálogo será postado

# Cores das categorias
CORES = {
    "▸DESTAQUES": discord.Color.orange(),
    "▸EQUIPAMENTOS": discord.Color.blue(),  # azul padrão, mais escuro que antes
    "▸OUTROS": discord.Color.dark_blue(),
    "▸SOMBRIOS": discord.Color.dark_grey(),
    "▸VISUAIS": discord.Color.purple(),
}

# Estrutura de itens do catálogo
CATALOGO = [
    {
        "categoria": "▸DESTAQUES",
        "itens": [{"nome": "Item A", "preco": "100"}, {"nome": "Item B", "preco": "150"}]
    },
    {
        "categoria": "▸EQUIPAMENTOS",
        "itens": [{"nome": "Espada", "preco": "250"}, {"nome": "Escudo", "preco": "200"}]
    },
    {
        "categoria": "▸OUTROS",
        "itens": [{"nome": "Poção", "preco": "50"}, {"nome": "Chave", "preco": "75"}]
    },
    {
        "categoria": "▸SOMBRIOS",
        "itens": [{"nome": "Capa Sombria", "preco": "300"}]
    },
    {
        "categoria": "▸VISUAIS",
        "itens": [{"nome": "Chapéu Roxo", "preco": "120"}]
    }
]

# Criação do bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Função que cria os embeds e envia em uma única mensagem
async def postar_catalogo():
    try:
        canal = bot.get_channel(CHANNEL_ID)
        if canal is None:
            canal = await bot.fetch_channel(CHANNEL_ID)

        embed_msg = []
        for categoria in CATALOGO:
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

        # envia todos os embeds em uma única mensagem (até 10 por limite do Discord)
        await canal.send(embeds=embed_msg[:10])

        print("Catálogo postado com sucesso!")

    except Exception as e:
        print("Erro ao postar catálogo automaticamente:")
        traceback.print_exc()

# Loop diário para postar catálogo
@tasks.loop(hours=24)
async def loop_diario():
    await bot.wait_until_ready()
    await postar_catalogo()

# Inicia o loop quando o bot está pronto
@bot.event
async def on_ready():
    print(f"Bot logado como {bot.user}")
    if not loop_diario.is_running():
        loop_diario.start()

# Roda o bot
bot.run(TOKEN)
