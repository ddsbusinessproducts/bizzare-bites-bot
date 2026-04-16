import discord
from discord.ext import commands
from discord import app_commands

import os
TOKEN = os.getenv("TOKEN")STAFF_ROLE_NAME = "Staff"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(e)


# ---------------- TICKET BUTTONS ----------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🍔 Open Order Ticket", style=discord.ButtonStyle.green)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )

        channel = await guild.create_text_channel(
            name=f"order-{user.name}", overwrites=overwrites
        )

        embed = discord.Embed(
            title="🍟 Bizzare Bites Order Ticket",
            description="Send your food order here.",
            color=0x9B59B6,
        )
        embed.add_field(
            name="💳 Payment Methods",
            value="PayPal • Apple Pay • Zelle",
            inline=False,
        )
        embed.add_field(
            name="🚗 Tracking",
            value="Staff will send your delivery tracking link here.",
            inline=False,
        )

        await channel.send(content=user.mention, embed=embed, view=StaffControls())
        await interaction.response.send_message(
            f"Ticket created: {channel.mention}", ephemeral=True
        )


class StaffControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Claim Order", style=discord.ButtonStyle.blurple)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"{interaction.user.mention} claimed this order."
        )

    @discord.ui.button(label="❌ Close Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()


# ---------------- COMMANDS ----------------

@bot.tree.command(name="setup", description="Post order panel")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🍕 Bizzare Bites",
        description="Welcome to Bizzare Bites.\nClick below to place an order.",
        color=0xE67E22,
    )
    embed.add_field(
        name="Payments",
        value="PayPal • Apple Pay • Zelle",
        inline=False,
    )

    await interaction.response.send_message(embed=embed, view=TicketView())


@bot.tree.command(name="menu", description="Show the menu")
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🍽️ Bizzare Bites Menu",
        description="Choose your favorites",
        color=0xF1C40F,
    )

    embed.add_field(name="🍔 Burgers", value="$8 - $12", inline=False)
    embed.add_field(name="🍕 Pizza", value="$10 - $18", inline=False)
    embed.add_field(name="🍟 Sides", value="$3 - $6", inline=False)
    embed.add_field(name="🥤 Drinks", value="$2 - $4", inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="tracking", description="Send tracking link")
@app_commands.describe(link="Tracking URL")
async def tracking(interaction: discord.Interaction, link: str):
    embed = discord.Embed(
        title="🚗 Delivery Tracking",
        description=f"Track your order:\n{link}",
        color=0x2ECC71,
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="eta", description="Estimated delivery time")
@app_commands.describe(minutes="Minutes until arrival")
async def eta(interaction: discord.Interaction, minutes: int):
    await interaction.response.send_message(
        f"🚗 Estimated arrival time: {minutes} minutes."
    )


@bot.tree.command(name="vouch", description="Leave a review")
@app_commands.describe(message="Your review")
async def vouch(interaction: discord.Interaction, message: str):
    embed = discord.Embed(
        title="⭐ Customer Review",
        description=message,
        color=0x3498DB,
    )
    embed.set_footer(text=f"Thanks {interaction.user}")
    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)