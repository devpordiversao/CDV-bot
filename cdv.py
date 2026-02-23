import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
import threading
import discord
from discord.ext import commands

# --------------------------
# CONFIGURAÇÃO DO BOT
# --------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --------------------------
# LOGS
# --------------------------
public_logs = []
private_logs = []

MAX_LOGS = 500  # máximo de logs em memória

def add_log(log_list, entry):
    log_list.append(entry)
    if len(log_list) > MAX_LOGS:
        log_list.pop(0)

# --------------------------
# EVENTOS DO BOT
# --------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    log_entry = {
        "id": str(datetime.utcnow().timestamp()),
        "timestamp": datetime.utcnow().isoformat(),
        "guild": message.guild.name if message.guild else "DM",
        "guild_id": message.guild.id if message.guild else None,
        "channel": message.channel.name if hasattr(message.channel, "name") else "DM",
        "channel_id": message.channel.id if hasattr(message.channel, "id") else None,
        "user": str(message.author),
        "user_id": message.author.id,
        "content": message.content
    }

    if message.guild:
        everyone = message.guild.default_role
        perms = message.channel.permissions_for(everyone)
        if perms.view_channel:
            add_log(public_logs, log_entry)
            print(f"[PUBLIC] {log_entry['guild']} #{log_entry['channel']} {log_entry['user']}: {log_entry['content']}")
        else:
            add_log(private_logs, log_entry)
            print(f"[PRIVATE] {log_entry['guild']} #{log_entry['channel']} {log_entry['user']}: {log_entry['content']}")
    else:
        add_log(private_logs, log_entry)
        print(f"[DM] {log_entry['user']}: {log_entry['content']}")

    await bot.process_commands(message)

# --------------------------
# FLASK API
# --------------------------
app = Flask(__name__)

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Retorna todos os logs (públicos + privados)"""
    logs = public_logs + private_logs
    logs_sorted = sorted(logs, key=lambda x: x['timestamp'], reverse=True)
    return jsonify(logs_sorted)

@app.route("/api/logs/public", methods=["GET"])
def get_public_logs():
    return jsonify(list(reversed(public_logs)))

@app.route("/api/logs/private", methods=["GET"])
def get_private_logs():
    return jsonify(list(reversed(private_logs)))

@app.route("/api/send-dm", methods=["POST"])
def send_dm():
    data = request.json
    user_id = data.get("user_id")
    content = data.get("message")
    if not user_id or not content:
        return jsonify({"error": "user_id e message obrigatórios"}), 400

    user = bot.get_user(int(user_id))
    if not user:
        return jsonify({"error": "usuário não encontrado"}), 404

    async def dm_user():
        try:
            await user.send(content)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    fut = bot.loop.create_task(dm_user())
    bot.loop.run_until_complete(fut)
    return fut.result()

# --------------------------
# RODA FLASK EM THREAD PARA NÃO BLOQUEAR O BOT
# --------------------------
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

threading.Thread(target=run_flask).start()

# --------------------------
# RODA O BOT
# --------------------------
bot.run(os.environ.get("BOT_TOKEN"))
