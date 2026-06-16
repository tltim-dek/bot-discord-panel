import os
import threading
import discord
from discord.ext import commands
from flask import Flask, jsonify, request

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
PANEL_API_KEY = os.getenv("PANEL_API_KEY", "")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

@bot.event
async def on_ready():
    print(f"Bot connecte : {bot.user}")

@app.get("/")
def home():
    return "Bot panel API actif"

@app.get("/panel/member/<discord_id>")
def panel_member(discord_id):
    if request.args.get("key") != PANEL_API_KEY:
        return jsonify({"error": "Acces refuse"}), 403

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return jsonify({"error": "Serveur introuvable"}), 404

    member = guild.get_member(int(discord_id))
    if member is None:
        return jsonify({"error": "Membre introuvable"}), 404

    roles = [
        {
            "id": str(role.id),
            "name": role.name,
            "color": str(role.color)
        }
        for role in sorted(member.roles, key=lambda r: r.position, reverse=True)
        if role.name != "@everyone"
    ]

    return jsonify({
        "id": str(member.id),
        "username": member.name,
        "displayName": member.display_name,
        "avatar": str(member.display_avatar.url),
        "joinedAt": member.joined_at.isoformat() if member.joined_at else None,
        "roles": roles
    })

def run_panel_api():
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_panel_api, daemon=True).start()

bot.run(TOKEN)
