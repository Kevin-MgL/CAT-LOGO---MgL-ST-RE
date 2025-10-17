import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import asyncio
import traceback  # Para mostrar erros completos no terminal

# -----------------------------
# CONFIGURAÇÃO
# -----------------------------
TOKEN = os.environ.get("TOKEN")  # Substitua pelo token do bot
GUILD_ID = int(os.environ.get("GUILD_ID", 0))  # Substitua pelo ID do seu servidor
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", 0))  # Canal para postagem automática

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

def salvar_itens(itens):
    try:
        with open(ITEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(itens, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar {ITEMS_FILE}:")
        print(e)

# -----------------------------
# CONFIGURAÇÃO DO BOT
# -----------------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
guild = discord.Object(id=GUILD_ID)  # Apenas para testes no servidor

# -----------------------------
# EVENTO ON_READY
# -----------------------------
@bot.event
async def on_ready():
    print(f"Bot online como {bot.user}")
    try:
        await bot.tree.sync(guild=guild)  # Sincroniza apenas no servidor
        print("Comandos slash sincronizados no servidor.")
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

        categorias = {}
        for item in itens:
            cat = item.get("categoria", "SEM CATEGORIA")
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(item)

        for cat, lista in categorias.items():
            cor = discord.Color.greyple()  # Default
            if "▸DESTAQUES" in cat:
                cor = discord.Color.from_rgb(255, 165, 0)  # Laranja
            elif "▸EQUIPAMENTOS" in cat:
                cor = discord.Color.from_rgb(173, 216, 230)  # Azul Claro
            elif "▸OUTROS" in cat:
                cor = discord.Color.from_rgb(0, 0, 139)  # Azul Escuro
            elif "▸SOMBRIOS" in cat:
                cor = discord.Color.light_grey()  # Cinza
            elif "▸VISUAIS" in cat:
                cor = discord.Color.purple()  # Roxo

            embed = discord.Embed(title=cat, color=cor)
            for item in lista:
                embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)

            await interaction.response.send_message(embed=embed)

    except Exception as e:
        print("Erro no comando /catalogo:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao carregar o catálogo.", ephemeral=True)

# -----------------------------
# COMANDO /additem
# -----------------------------
@bot.tree.command(name="additem", description="Adiciona um item ao catálogo")
@app_commands.describe(nome="Nome do item", preco="Preço do item", categoria="Categoria/Subtítulo")
async def additem(interaction: discord.Interaction, nome: str, preco: str, categoria: str = "SEM CATEGORIA"):
    try:
        itens = carregar_itens()
        # Verifica se já existe
        for item in itens:
            if item["nome"].lower() == nome.lower():
                await interaction.response.send_message(f"Item '{nome}' já existe.", ephemeral=True)
                return
        itens.append({"nome": nome, "preco": preco, "categoria": categoria})
        salvar_itens(itens)
        await interaction.response.send_message(f"Item '{nome}' adicionado com preço '{preco}' na categoria '{categoria}'.")
    except Exception as e:
        print("Erro no comando /additem:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao adicionar o item.", ephemeral=True)

# -----------------------------
# COMANDO /edititem
# -----------------------------
@bot.tree.command(name="edititem", description="Edita um item do catálogo")
@app_commands.describe(nome="Nome do item a ser editado", novo_nome="Novo nome do item", novo_preco="Novo preço do item")
async def edititem(interaction: discord.Interaction, nome: str, novo_nome: str, novo_preco: str):
    try:
        itens = carregar_itens()
        for item in itens:
            if item["nome"].lower() == nome.lower():
                item["nome"] = novo_nome
                item["preco"] = novo_preco
                salvar_itens(itens)
                await interaction.response.send_message(f"Item '{nome}' editado para '{novo_nome}' com preço '{novo_preco}'.")
                return
        await interaction.response.send_message(f"Item '{nome}' não encontrado.", ephemeral=True)
    except Exception as e:
        print("Erro no comando /edititem:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao editar o item.", ephemeral=True)

# -----------------------------
# COMANDO /delitem
# -----------------------------
@bot.tree.command(name="delitem", description="Deleta um item do catálogo")
@app_commands.describe(nome="Nome do item a ser deletado")
async def delitem(interaction: discord.Interaction, nome: str):
    try:
        itens = carregar_itens()
        for item in itens:
            if item["nome"].lower() == nome.lower():
                itens.remove(item)
                salvar_itens(itens)
                await interaction.response.send_message(f"Item '{nome}' removido do catálogo.")
                return
        await interaction.response.send_message(f"Item '{nome}' não encontrado.", ephemeral=True)
    except Exception as e:
        print("Erro no comando /delitem:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao deletar o item.", ephemeral=True)

# -----------------------------
# FUNÇÃO POSTAGEM AUTOMÁTICA
# -----------------------------
async def postar_catalogo_periodicamente():
    await bot.wait_until_ready()
    canal = bot.get_channel(CHANNEL_ID)
    if not canal:
        print("Canal não encontrado. Verifique CHANNEL_ID.")
        return

    while True:
        try:
            itens = carregar_itens()
            if not itens:
                await canal.send("O catálogo está vazio.")
            else:
                # Mensagem de aviso de postagem automática
                await canal.send("**Postagem Automática**")

                categorias = {}
                for item in itens:
                    cat = item.get("categoria", "SEM CATEGORIA")
                    if cat not in categorias:
                        categorias[cat] = []
                    categorias[cat].append(item)

                for cat, lista in categorias.items():
                    cor = discord.Color.greyple()  # Default
                    if "▸DESTAQUES" in cat:
                        cor = discord.Color.from_rgb(255, 165, 0)  # Laranja
                    elif "▸EQUIPAMENTOS" in cat:
                        cor = discord.Color.from_rgb(173, 216, 230)  # Azul Claro
                    elif "▸OUTROS" in cat:
                        cor = discord.Color.from_rgb(0, 0, 139)  # Azul Escuro
                    elif "▸SOMBRIOS" in cat:
                        cor = discord.Color.light_grey()  # Cinza
                    elif "▸VISUAIS" in cat:
                        cor = discord.Color.purple()  # Roxo

                    embed = discord.Embed(title=cat, color=cor)
                    for item in lista:
                        embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)
                    await canal.send(embed=embed)

        except Exception as e:
            print("Erro na postagem automática:")
            traceback.print_exc()

        # Aguarda 25 dias (em segundos)
        await asyncio.sleep(25*24*60*60)

# Inicia a tarefa automática
bot.loop.create_task(postar_catalogo_periodicamente())

# -----------------------------
# RODA O BOT
# -----------------------------
bot.run(TOKEN)
