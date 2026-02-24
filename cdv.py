import discord
from discord.ext import commands, tasks
import json
import random
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ========================
# CARREGAR TEMAS
# ========================
arquivos = ["temas.json", "temas2.json", "temas3.json", "temas4.json"]
temas = {}

for arquivo in arquivos:
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            data = json.load(f)
            temas.update(data)
    except:
        print(f"Erro ao carregar {arquivo}")

# ========================
# VARIÁVEIS
# ========================
quiz_ativo = False
tema_atual = None
pergunta_atual = None
resposta_atual = None
tempo_restante = 0
canal_quiz = None
pontuacao = {}

# ========================
# FUNÇÕES
# ========================

def get_pergunta(tema):
    lista = temas.get(tema.lower())
    if not lista:
        return None
    return random.choice(lista)

async def iniciar_pergunta(ctx):
    global pergunta_atual, resposta_atual, tempo_restante

    q = get_pergunta(tema_atual)
    if not q:
        await ctx.send("❌ Tema não encontrado.")
        return

    pergunta_atual = q["pergunta"]
    resposta_atual = q["resposta"].lower()
    tempo_restante = 20

    embed = discord.Embed(
        title=f"📚 Tema: {tema_atual}",
        description=f"❓ {pergunta_atual}",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

    while tempo_restante > 0:
        await ctx.send(f"⏳ {tempo_restante}...")
        await asyncio.sleep(1)
        tempo_restante -= 1

        if not quiz_ativo:
            return

        if resposta_atual is None:
            return

    await ctx.send("❌ Ninguém acertou!")
    reset_pergunta()

def reset_pergunta():
    global pergunta_atual, resposta_atual
    pergunta_atual = None
    resposta_atual = None

# ========================
# COMANDOS
# ========================

@bot.command()
async def iniciar(ctx, *, tema: str):
    global quiz_ativo, tema_atual, canal_quiz

    if quiz_ativo:
        await ctx.send("⚠️ Já existe um quiz rolando.")
        return

    if tema.lower() not in temas:
        await ctx.send("❌ Tema inválido.")
        return

    quiz_ativo = True
    tema_atual = tema
    canal_quiz = ctx.channel

    await ctx.send(f"🚀 Quiz iniciado no tema **{tema}**!")

    await iniciar_pergunta(ctx)

@bot.command()
async def next(ctx):
    global quiz_ativo

    if not quiz_ativo:
        await ctx.send("❌ Nenhum quiz ativo.")
        return

    await ctx.send("➡️ Próxima pergunta!")
    await iniciar_pergunta(ctx)

@bot.command()
async def stop(ctx):
    global quiz_ativo

    if not quiz_ativo:
        await ctx.send("❌ Nenhum quiz ativo.")
        return

    quiz_ativo = False
    await ctx.send("🛑 Quiz encerrado!")

@bot.command()
async def top(ctx):
    if not pontuacao:
        await ctx.send("📉 Ninguém pontuou ainda.")
        return

    ranking = sorted(pontuacao.items(), key=lambda x: x[1], reverse=True)[:3]

    desc = ""
    for i, (user, pts) in enumerate(ranking, start=1):
        desc += f"**{i}º** - {user} : {pts} pontos\n"

    embed = discord.Embed(
        title="🏆 Top 3",
        description=desc,
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, msg):
    respostas = [
        "Eaiii 😎",
        "Tô por aqui 👀",
        "Fala comigo 🔥",
        "Hmm interessante...",
        "KKKK boa",
        "Entendi 🤔"
    ]

    await ctx.send(f"**Lumo:** {random.choice(respostas)}")

# ========================
# EVENTO DE RESPOSTA
# ========================

@bot.event
async def on_message(message):
    global resposta_atual

    if message.author.bot:
        return

    if quiz_ativo and resposta_atual and message.channel == canal_quiz:
        if message.content.lower() == resposta_atual:
            user = str(message.author)

            pontuacao[user] = pontuacao.get(user, 0) + 1

            embed = discord.Embed(
                title="🎉 Acertou!",
                description=f"{message.author.mention} acertou!\n\nResposta: **{resposta_atual}**",
                color=discord.Color.yellow()
            )

            await message.channel.send(embed=embed)

            resposta_atual = None

    await bot.process_commands(message)

# ========================
# RUN
# ========================

bot.run(os.getenv("DISCORD_TOKEN"))
