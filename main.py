import os
import threading
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask, jsonify, request

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
PANEL_API_KEY = os.getenv("PANEL_API_KEY", "")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)


def liste_texte(valeur):
    elements = [item.strip() for item in valeur.split(",") if item.strip()]
    if not elements:
        return "Aucun"
    return "\n".join(f"- {item}" for item in elements)


async def envoyer_message_simple(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    titre: str,
    message: str
):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title=titre,
        description=message,
        color=discord.Color.green()
    )

    embed.set_footer(text="Service Départemental de l'Ariège")

    await salon.send(embed=embed)

    await interaction.followup.send(
        f"Message envoyé dans {salon.mention}.",
        ephemeral=True
    )


@bot.event
async def on_ready():
    print(f"Bot connecte : {bot.user}")

    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"{len(synced)} commandes slash synchronisees.")
    except Exception as error:
        print(f"Erreur sync commandes slash : {error}")


@bot.tree.command(name="service", description="Envoyer un message de service dans un salon choisi")
@app_commands.describe(
    salon="Salon ou envoyer le message",
    message="Message a envoyer"
)
async def service(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    message: str
):
    await envoyer_message_simple(interaction, salon, "Service", message)


@bot.tree.command(name="formation", description="Envoyer un message de formation dans un salon choisi")
@app_commands.describe(
    salon="Salon ou envoyer le message",
    message="Message a envoyer"
)
async def formation(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    message: str
):
    await envoyer_message_simple(interaction, salon, "Formation", message)


@bot.tree.command(name="reunion", description="Envoyer un message de reunion dans un salon choisi")
@app_commands.describe(
    salon="Salon ou envoyer le message",
    message="Message a envoyer"
)
async def reunion(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    message: str
):
    await envoyer_message_simple(interaction, salon, "Reunion", message)


@bot.tree.command(name="entretien", description="Creer une session d'entretien")
@app_commands.describe(
    salon="Salon ou envoyer l'entretien",
    date="Date de l'entretien, exemple : 25/06/2026",
    heure="Heure de l'entretien, exemple : 18:00",
    assistant="Assistant present a l'entretien, optionnel"
)
async def entretien(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    date: str,
    heure: str,
    assistant: discord.Member = None
):
    await interaction.response.defer(ephemeral=True)

    assistant_texte = assistant.mention if assistant else "Aucun assistant prevu"

    embed = discord.Embed(
        title="Creation d'une session d'entretien",
        description=(
            f"**Date :** {date}\n"
            f"**Heure :** {heure}\n"
            f"**Assistant :** {assistant_texte}"
        ),
        color=discord.Color.blue()
    )

    embed.set_footer(text="Service Departemental de l'Ariege")

    await salon.send(embed=embed)

    await interaction.followup.send(
        f"Session d'entretien envoyee dans {salon.mention}.",
        ephemeral=True
    )


@bot.tree.command(name="resultat", description="Envoyer un message de resultats dans un salon choisi")
@app_commands.describe(
    salon="Salon ou envoyer les resultats",
    date="Date des resultats, exemple : 18/06/2026",
    heure="Heure des resultats, exemple : 20h00",
    formation="Nom de la formation",
    admis="Personnes admises, separees par des virgules",
    non_admis="Personnes non admises, separees par des virgules",
    notes="Notes, exemple : Jean 16/20, Lucas 9/20"
)
async def resultat(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    date: str,
    heure: str,
    formation: str,
    admis: str,
    non_admis: str,
    notes: str
):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="Resultats de formation",
        color=discord.Color.green()
    )

    embed.add_field(name="Date", value=date, inline=True)
    embed.add_field(name="Heure", value=heure, inline=True)
    embed.add_field(name="Formation", value=formation, inline=False)
    embed.add_field(name="Admis", value=liste_texte(admis), inline=False)
    embed.add_field(name="Non admis", value=liste_texte(non_admis), inline=False)
    embed.add_field(name="Notes", value=liste_texte(notes), inline=False)

    embed.set_footer(text="Service Departemental de l'Ariege")

    await salon.send(embed=embed)

    await interaction.followup.send(
        f"Resultats envoyes dans {salon.mention}.",
        ephemeral=True
    )


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
