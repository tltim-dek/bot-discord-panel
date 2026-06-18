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
        return "N/A"
    return "\n".join(elements)


def mention_role(role):
    return role.mention if role else ""


def signature():
    return (
        "Cordialement,\n"
        "Le Service des Ressources Humaines\n"
        "Service Departemental de l'Ariege"
    )


def creer_notification(titre, description, couleur=discord.Color.blue()):
    embed = discord.Embed(
        title=titre,
        description=description,
        color=couleur
    )
    embed.set_footer(text="Service Departemental de l'Ariege")
    return embed


async def envoyer_notification(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    role: discord.Role,
    embed: discord.Embed
):
    await interaction.response.defer(ephemeral=True)

    await salon.send(
        content=mention_role(role),
        embed=embed,
        allowed_mentions=discord.AllowedMentions(roles=True)
    )

    await interaction.followup.send(
        f"Notification envoyee dans {salon.mention}.",
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


@bot.tree.command(name="service", description="Envoyer une notification de service")
@app_commands.describe(
    salon="Salon ou envoyer la notification",
    message="Message de service",
    role="Role a mentionner, optionnel"
)
async def service(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    message: str,
    role: discord.Role = None
):
    description = (
        "Le Service Departemental de l'Ariege vous communique une information de service.\n\n"
        f"{message}\n\n"
        "Pour toute question ou demande d'information complementaire, le service reste a votre disposition.\n\n"
        f"{signature()}"
    )

    embed = creer_notification(
        "Notification Service - Service Departemental de l'Ariege",
        description,
        discord.Color.blue()
    )

    await envoyer_notification(interaction, salon, role, embed)


@bot.tree.command(name="formation", description="Envoyer une notification de formation")
@app_commands.describe(
    salon="Salon ou envoyer la notification",
    message="Message de formation",
    role="Role a mentionner, optionnel"
)
async def formation(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    message: str,
    role: discord.Role = None
):
    description = (
        "Le Service Departemental de l'Ariege vous communique une information relative a une formation.\n\n"
        f"{message}\n\n"
        "Les personnes concernees sont invitees a prendre connaissance des informations transmises.\n\n"
        f"{signature()}"
    )

    embed = creer_notification(
        "Notification Formation - Service Departemental de l'Ariege",
        description,
        discord.Color.green()
    )

    await envoyer_notification(interaction, salon, role, embed)


@bot.tree.command(name="reunion", description="Envoyer une notification de reunion")
@app_commands.describe(
    salon="Salon ou envoyer la notification",
    message="Message de reunion",
    role="Role a mentionner, optionnel"
)
async def reunion(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    message: str,
    role: discord.Role = None
):
    description = (
        "Le Service Departemental de l'Ariege vous informe de la tenue d'une reunion.\n\n"
        f"{message}\n\n"
        "Les personnes concernees sont priees de se rendre disponibles aux horaires indiques.\n\n"
        f"{signature()}"
    )

    embed = creer_notification(
        "Notification Reunion - Service Departemental de l'Ariege",
        description,
        discord.Color.purple()
    )

    await envoyer_notification(interaction, salon, role, embed)


@bot.tree.command(name="entretien", description="Creer une notification d'entretien")
@app_commands.describe(
    salon="Salon ou envoyer l'entretien",
    date="Date de l'entretien, exemple : 25/06/2026",
    heure="Heure de l'entretien, exemple : 18:00",
    assistant="Assistant present a l'entretien, optionnel",
    role="Role a mentionner, optionnel"
)
async def entretien(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    date: str,
    heure: str,
    assistant: discord.Member = None,
    role: discord.Role = None
):
    assistant_texte = assistant.mention if assistant else "Aucun assistant prevu"

    description = (
        "Le Service Departemental de l'Ariege vous informe de la creation d'une session d'entretien.\n\n"
        f"**Date :** {date}\n"
        f"**Heure :** {heure}\n"
        f"**Assistant :** {assistant_texte}\n\n"
        "La personne concernee est invitee a se presenter a l'heure indiquee.\n\n"
        f"{signature()}"
    )

    embed = creer_notification(
        "Notification Entretien - Service Departemental de l'Ariege",
        description,
        discord.Color.blue()
    )

    await envoyer_notification(interaction, salon, role, embed)


@bot.tree.command(name="resultat", description="Publier les resultats d'une formation")
@app_commands.describe(
    salon="Salon ou envoyer les resultats",
    date="Date des resultats, exemple : 18/06/2026",
    heure="Heure des resultats, exemple : 20h00",
    formation="Nom de la formation",
    admis="Personnes admises, separees par des virgules",
    non_admis="Personnes non admises, separees par des virgules",
    notes="Notes, exemple : Jean 16/20, Lucas 9/20",
    role="Role a mentionner, optionnel"
)
async def resultat(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    date: str,
    heure: str,
    formation: str,
    admis: str,
    non_admis: str,
    notes: str,
    role: discord.Role = None
):
    description = (
        "Le Service Departemental de l'Ariege a l'honneur de vous communiquer les resultats des candidatures.\n\n"
        "Apres etude des dossiers, les decisions suivantes ont ete prises.\n\n"
        f"**Date :** {date}\n"
        f"**Heure :** {heure}\n"
        f"**Formation :** {formation}\n\n"
        "*Candidat admis*\n"
        f"{liste_texte(admis)}\n\n"
        "*Candidat non admis*\n"
        f"{liste_texte(non_admis)}\n\n"
        "**Notes**\n"
        f"{liste_texte(notes)}\n\n"
        "Pour toute question ou demande d'information complementaire, le service reste a votre disposition.\n"
        "Nous vous remercions pour l'interet porte a notre structure et vous souhaitons une bonne journee.\n\n"
        f"{signature()}"
    )

    embed = creer_notification(
        "Notification Resultats - Service Departemental de l'Ariege",
        description,
        discord.Color.green()
    )

    await envoyer_notification(interaction, salon, role, embed)


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
