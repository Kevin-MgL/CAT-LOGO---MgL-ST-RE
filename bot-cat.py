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
TOKEN = os.environ['TOKEN']            # Token do bot
GUILD_ID = int(os.environ['GUILD_ID']) # ID do servidor
CANAL_ID = int(os.environ['CANAL_ID']) # ID do canal onde postar o catálogo

ITEMS_FILE = "itens.json"

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

def salvar_itens(itens):
    try:
        with open(ITEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(itens, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar {ITEMS_FILE}: {e}")

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
    # Inicia a tarefa automática
    enviar_catalogo_automatico.start()

# -----------------------------
# FUNÇÃO PARA ENVIAR CATÁLOGO
# -----------------------------
async def enviar_catalogo(canale_id):
    itens = carregar_itens()
    if not itens:
        print("O catálogo está vazio.")
        return
    try:
        canal = bot.get_channel(canale_id)
        if canal is None:
            canal = await bot.fetch_channel(canale_id)

        # Cria Embeds por categoria
        for grupo in itens:
            embed = discord.Embed(
                title=grupo["categoria"],
                color=int(grupo["cor"],16)
            )
            for item in grupo["itens"]:
                embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)
            await canal.send(embed=embed)
        print("Catálogo enviado automaticamente.")
    except Exception as e:
        print("Erro ao enviar catálogo automaticamente:")
        traceback.print_exc()

# -----------------------------
# TASK AUTOMÁTICA (a cada 25 dias)
# -----------------------------
@tasks.loop(hours=25*24)
async def enviar_catalogo_automatico():
    await bot.wait_until_ready()
    await enviar_catalogo(CANAL_ID)

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
        for grupo in itens:
            embed = discord.Embed(
                title=grupo["categoria"],
                color=int(grupo["cor"],16)
            )
            for item in grupo["itens"]:
                embed.add_field(name=item["nome"], value=f"Preço: {item['preco']}", inline=False)
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        print("Erro no comando /catalogo:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao carregar o catálogo.", ephemeral=True)

# -----------------------------
# COMANDOS /additem, /edititem e /delitem
# -----------------------------
@bot.tree.command(name="additem", description="Adiciona um item ao catálogo")
@app_commands.describe(categoria="Categoria do item", nome="Nome do item", preco="Preço do item")
async def additem(interaction: discord.Interaction, categoria: str, nome: str, preco: str):
    try:
        itens = carregar_itens()
        # Procura o grupo
        grupo = next((g for g in itens if g["categoria"].lower() == categoria.lower()), None)
        if not grupo:
            await interaction.response.send_message(f"Categoria '{categoria}' não encontrada.", ephemeral=True)
            return
        # Verifica se item já existe
        if any(i["nome"].lower() == nome.lower() for i in grupo["itens"]):
            await interaction.response.send_message(f"Item '{nome}' já existe.", ephemeral=True)
            return
        grupo["itens"].append({"nome": nome, "preco": preco})
        salvar_itens(itens)
        await interaction.response.send_message(f"Item '{nome}' adicionado em '{categoria}'.")
    except Exception as e:
        print("Erro no comando /additem:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao adicionar o item.", ephemeral=True)

@bot.tree.command(name="edititem", description="Edita um item do catálogo")
@app_commands.describe(categoria="Categoria do item", nome="Nome atual", novo_nome="Novo nome", novo_preco="Novo preço")
async def edititem(interaction: discord.Interaction, categoria: str, nome: str, novo_nome: str, novo_preco: str):
    try:
        itens = carregar_itens()
        grupo = next((g for g in itens if g["categoria"].lower() == categoria.lower()), None)
        if not grupo:
            await interaction.response.send_message(f"Categoria '{categoria}' não encontrada.", ephemeral=True)
            return
        for item in grupo["itens"]:
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

@bot.tree.command(name="delitem", description="Deleta um item do catálogo")
@app_commands.describe(categoria="Categoria do item", nome="Nome do item")
async def delitem(interaction: discord.Interaction, categoria: str, nome: str):
    try:
        itens = carregar_itens()
        grupo = next((g for g in itens if g["categoria"].lower() == categoria.lower()), None)
        if not grupo:
            await interaction.response.send_message(f"Categoria '{categoria}' não encontrada.", ephemeral=True)
            return
        for item in grupo["itens"]:
            if item["nome"].lower() == nome.lower():
                grupo["itens"].remove(item)
                salvar_itens(itens)
                await interaction.response.send_message(f"Item '{nome}' removido de '{categoria}'.")
                return
        await interaction.response.send_message(f"Item '{nome}' não encontrado.", ephemeral=True)
    except Exception as e:
        print("Erro no comando /delitem:")
        traceback.print_exc()
        await interaction.response.send_message("Ocorreu um erro ao deletar o item.", ephemeral=True)

# -----------------------------
# RODA O BOT
# -----------------------------
bot.run(TOKEN)