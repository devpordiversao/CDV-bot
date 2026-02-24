import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import asyncio
import random

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ====== CARREGAR TEMAS ======
arquivos = ["temas.json", "temas2.json", "temas3.json", "temas4.json"]
temas = {}

for arquivo in arquivos:
    with open(arquivo, "r", encoding="utf-8") as f:
        data = json.load(f)
        temas.update(data)

# ====== ESTADO DO QUIZ ======
quiz_ativo = False
tema_atual = None
pergunta_atual = None
resposta_atual = None
pontuacao = {}
canal_quiz = None


# ====== FUNÇÃO PERGUNTA ======
async def nova_pergunta():
    global pergunta_atual, resposta_atual

    pergunta = random.choice(temas[tema_atual])
    pergunta_atual = pergunta["pergunta"]
    resposta_atual = pergunta["resposta"].lower()

    embed = discord.Embed(
        title=f"📚 Tema: {tema_atual}",
        description=f"❓ {pergunta_atual}",
        color=discord.Color.blue()
    )

    await canal_quiz.send(embed=embed)

    # Timer
    for i in range(20, 0, -1):
        await canal_quiz.send(f"⏳ {i}...")
        await asyncio.sleep(1)

        if resposta_atual is None:
            return

    await canal_quiz.send("❌ Ninguém acertou!")
    await canal_quiz.send("👉 Digite `/next` para próxima pergunta")


# ====== COMANDO /iniciar ======
@bot.tree.command(name="iniciar", description="Iniciar quiz")
@app_commands.describe(tema="Nome do tema")
async def iniciar(interaction: discord.Interaction, tema: str):
    global quiz_ativo, tema_atual, canal_quiz, pontuacao

    if tema not in temas:
        await interaction.response.send_message("❌ Tema não existe")
        return

    quiz_ativo = True
    tema_atual = tema
    canal_quiz = interaction.channel
    pontuacao = {}

    await interaction.response.send_message(f"✅ Quiz iniciado no tema **{tema}**")

    await nova_pergunta()


# ====== COMANDO /next ======
@bot.tree.command(name="next", description="Próxima pergunta")
async def next_pergunta(interaction: discord.Interaction):
    if not quiz_ativo:
        await interaction.response.send_message("❌ Nenhum quiz ativo")
        return

    await interaction.response.send_message("➡️ Próxima pergunta...")
    await nova_pergunta()


# ====== COMANDO /stop ======
@bot.tree.command(name="stop", description="Parar quiz")
async def stop(interaction: discord.Interaction):
    global quiz_ativo

    if not quiz_ativo:
        await interaction.response.send_message("❌ Nenhum quiz ativo")
        return

    quiz_ativo = False

    # Top 3
    top = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)[:3]

    desc = ""
    for i, (user, pontos) in enumerate(top, start=1):
        desc += f"{i}º - <@{user}> ({pontos} pts)\n"

    embed = discord.Embed(
        title="🏆 Top 3",
        description=desc if desc else "Ninguém pontuou",
        color=discord.Color.gold()
    )

    await interaction.response.send_message("🛑 Quiz encerrado!")
    await canal_quiz.send(embed=embed)


# ====== DETECTAR RESPOSTAS ======
@bot.event
async def on_message(message):
    global resposta_atual

    if message.author.bot:
        return

    if quiz_ativo and resposta_atual:
        if message.content.lower() == resposta_atual:
            resposta_atual = None

            pontuacao[message.author.id] = pontuacao.get(message.author.id, 0) + 1

            embed = discord.Embed(
                title="✅ Acertou!",
                description=f"{message.author.mention} acertou!\nResposta: **{resposta_atual}**",
                color=discord.Color.green()
            )

            await canal_quiz.send(embed=embed)
            await canal_quiz.send("👉 Digite `/next` para continuar")

    await bot.process_commands(message)


# ====== READY ======
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logado como {bot.user}")


# ====== TOKEN ======
bot.run("MTQ2ODAwNTQ0NjU4ODU2MzUyOA.GdVIg9.CyPewbzcdgYiv4LqVOjko02FIsNYC8HZVV5Rks")
