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
        "Le Service Departemental de l'Ariege souhaite porter a votre connaissance une information de service importante.\n\n"
        "Cette communication a pour objectif de transmettre clairement les consignes, informations ou rappels necessaires "
        "au bon fonctionnement de l'organisation interne. Les personnes concernees sont invitees a lire attentivement "
        "le contenu de cette notification et a appliquer les indications qui y sont mentionnees.\n\n"
        "**Information communiquee**\n"
        f"{message}\n\n"
        "Il est demande a chacun de prendre en compte cette information dans les meilleurs delais. En cas de doute, "
        "de question ou de besoin de precision supplementaire, vous pouvez vous rapprocher d'un responsable afin "
        "d'obtenir les renseignements necessaires.\n\n"
        "Nous vous remercions pour votre attention, votre serieux et votre cooperation dans le respect des consignes transmises.\n\n"
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
        "Le Service Departemental de l'Ariege vous informe de la publication d'une communication relative a une formation.\n\n"
        "Cette notification concerne l'organisation, le suivi ou le deroulement d'un module de formation. Les agents concernes "
        "sont invites a prendre connaissance des informations transmises afin de se preparer dans les meilleures conditions "
        "et de respecter les attentes fixees par l'equipe encadrante.\n\n"
        "**Information de formation**\n"
        f"{message}\n\n"
        "La formation constitue une etape importante dans la progression de chaque agent. Il est donc attendu que les personnes "
        "concernees fassent preuve d'assiduite, de serieux et d'implication tout au long du processus. Toute absence, retard "
        "ou difficulte particuliere doit etre signalee rapidement a un responsable.\n\n"
        "Nous vous remercions pour votre engagement et vous invitons a suivre attentivement les indications communiquees.\n\n"
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
        "Le Service Departemental de l'Ariege vous informe de la tenue d'une reunion ou d'un point d'organisation.\n\n"
        "Cette reunion a pour objectif de rassembler les personnes concernees afin d'echanger sur les informations importantes, "
        "les consignes a appliquer, les decisions a prendre ou les elements necessaires au bon fonctionnement du service.\n\n"
        "**Informations relatives a la reunion**\n"
        f"{message}\n\n"
        "Les personnes mentionnees ou concernees par cette notification sont priees de se rendre disponibles et de se presenter "
        "dans de bonnes conditions. La ponctualite, l'ecoute et le respect des consignes donnees sont attendus afin de permettre "
        "un deroulement clair, efficace et organise.\n\n"
        "En cas d'indisponibilite, il est demande de prevenir rapidement un responsable afin que l'information puisse etre prise en compte.\n\n"
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
        "Cet entretien a pour objectif d'echanger avec la personne concernee, d'evaluer sa situation, sa motivation, "
        "son comportement ou son avancement selon le cadre prevu par le service. Il s'agit d'une etape importante "
        "dans le suivi administratif et humain du candidat ou de l'agent concerne.\n\n"
        "**Informations de convocation**\n"
        f"**Date :** {date}\n"
        f"**Heure :** {heure}\n"
        f"**Assistant :** {assistant_texte}\n\n"
        "La personne convoquee est invitee a se presenter a l'heure indiquee, dans de bonnes conditions et avec le serieux attendu. "
        "Il est demande de respecter l'horaire fixe afin de garantir le bon deroulement de la session et de ne pas perturber "
        "l'organisation prevue par les responsables.\n\n"
        "En cas d'indisponibilite ou de difficulte particuliere, la personne concernee doit se rapprocher rapidement d'un responsable "
        "afin que la situation puisse etre etudiee.\n\n"
        f"{signature()}"
    )

    embed = creer_notification(
        "Notification Entretien - Service Departemental de l'Ariege",
        description,
        discord.Color.blue()
    )

    await envoyer_notification(interaction, salon, role, embed)


@bot.tree.command(name="examen", description="Envoyer une convocation a un examen")
@app_commands.describe(
    salon="Salon ou envoyer la convocation",
    candidat="Candidat a convoquer",
    date="Date de l'examen, exemple : 25/06/2026",
    heure="Heure de l'examen, exemple : 18:00",
    module="Module ou formation concernee",
    role="Role a mentionner en plus, optionnel"
)
async def examen(
    interaction: discord.Interaction,
    salon: discord.TextChannel,
    candidat: discord.Member,
    date: str,
    heure: str,
    module: str,
    role: discord.Role = None
):
    await interaction.response.defer(ephemeral=True)

    role_texte = f" {role.mention}" if role else ""

    description = (
        "Le Service Departemental de l'Ariege vous informe qu'une convocation a un examen a ete emise.\n\n"
        f"**Candidat convoque :** {candidat.mention}\n"
        f"**Module concerne :** {module}\n"
        f"**Date :** {date}\n"
        f"**Heure :** {heure}\n\n"
        "Votre progression dans le module de formation concerne ayant ete jugee suffisante par l'equipe encadrante, "
        "vous etes officiellement convoque afin de proceder au passage de votre examen.\n\n"
        "Cette convocation marque l'etape finale de votre parcours de formation pour le module indique ci-dessus. "
        "Il vous est donc demande de vous rendre disponible a la date et a l'heure prevues, et de vous presenter "
        "dans de bonnes conditions afin de realiser votre evaluation.\n\n"
        "L'examen permettra d'evaluer vos connaissances, votre comprehension du module ainsi que votre capacite a appliquer "
        "les consignes et procedures vues durant la formation. Il est attendu de votre part une attitude serieuse, respectueuse "
        "et conforme aux exigences du service.\n\n"
        "En cas d'indisponibilite ou de difficulte particuliere, vous etes invite a vous rapprocher rapidement d'un responsable "
        "afin que la situation puisse etre prise en compte avant la date prevue.\n\n"
        f"{signature()}"
    )

    embed = creer_notification(
        "Convocation Examen - Service Departemental de l'Ariege",
        description,
        discord.Color.gold()
    )

    await salon.send(
        content=f"{candidat.mention}{role_texte}",
        embed=embed,
        allowed_mentions=discord.AllowedMentions(users=True, roles=True)
    )

    await interaction.followup.send(
        f"Convocation envoyee dans {salon.mention}.",
        ephemeral=True
    )


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
        "Apres etude des dossiers, analyse des evaluations et prise en compte des elements transmis par l'equipe encadrante, "
        "les decisions suivantes ont ete prises concernant le module ou la formation indiquee ci-dessous.\n\n"
        f"**Date :** {date}\n"
        f"**Heure :** {heure}\n"
        f"**Formation :** {formation}\n\n"
        "**Candidat admis**\n"
        f"{liste_texte(admis)}\n\n"
        "**Candidat non admis**\n"
        f"{liste_texte(non_admis)}\n\n"
        "**Notes**\n"
        f"{liste_texte(notes)}\n\n"
        "Les candidats admis sont felicites pour leur travail, leur implication et les efforts fournis durant le parcours de formation. "
        "Ils sont invites a poursuivre leur engagement avec le meme serieux dans les prochaines etapes qui leur seront communiquees.\n\n"
        "Les candidats non admis sont encourages a poursuivre leurs efforts. Une non-admission ne constitue pas une fin definitive, "
        "mais une indication qu'un travail supplementaire, un accompagnement ou une nouvelle evaluation peut etre necessaire selon "
        "les decisions prises par les responsables.\n\n"
        "Pour toute question ou demande d'information complementaire, le service reste a votre disposition. Nous vous remercions "
        "pour l'interet porte a notre structure et vous souhaitons une bonne continuation.\n\n"
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
