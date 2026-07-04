import discord
from discord import app_commands
from embeds.embed_manager import create_embed
import time

async def setup(bot, context):
    # Catches command errors
    @bot.tree.error
    async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        await context.log_error(interaction, "on_app_commmand_error", 1, error)
        return
    
    # Cmds

    @bot.tree.command(name="configure-verification", description="Configures the verification info.")
    @app_commands.checks.has_role("[CDEV] Chief Developer")
    async def configure_verification(interaction : discord.Interaction, role : discord.Role, roblox_group_id : int):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send("Configuring server...",ephemeral=True)
        
        context.db.set_guild_config(interaction.guild.id, role.id, roblox_group_id)

        await interaction.followup.send("Server configured. :D",ephemeral=True)



    @bot.tree.command(name="update-embed", description="Re-sends the targeted embed.")
    @app_commands.checks.has_role("[CDEV] Chief Developer")
    async def update_embed(interaction : discord.Interaction, channel : discord.TextChannel):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send("Updating embed...",ephemeral=True)

        async for i in channel.history(limit=100):
            if i.author.id == bot.user.id:
                await i.delete()
        
        await create_embed(context, channel)

        await interaction.followup.send("Updated Embed. :D",ephemeral=True)

    @bot.tree.command(name="update-all-embeds", description="Updates all the embeds.")
    @app_commands.checks.has_role("[CDEV] Chief Developer")
    async def update_embed(interaction : discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send("**Updating all embeds...**",ephemeral=True)

        starttime = time.perf_counter()

        guild = interaction.guild
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                await update_embed(interaction=interaction, channel=channel)
        
        endtime = time.perf_counter()

        await interaction.followup.send(f"**All embeds updated. :D** (In {endtime-starttime:.6f}s)",ephemeral=True)

    @bot.tree.command(name="server-stats", description="Provides the stats of the server.")
    @app_commands.checks.has_role("[DEV] Developer")
    async def server_stats(interaction : discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild

        # Online members
        online = sum(
            1 for member in guild.members
            if member.status != discord.Status.offline
        )

        # Humans / Bots
        humans = sum(not m.bot for m in guild.members)
        bots = sum(m.bot for m in guild.members)

        embed = discord.Embed(
            title=f"📊 {guild.name} Statistics",
            colour=discord.Color.gold()
        )

        embed.add_field(name="Server Name", value=guild.name, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Chief Developer", value="<@1462918523616493834>")

        embed.add_field(name="Max Members", value=guild.max_members)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Online", value=online, inline=True)
        embed.add_field(name="Humans / Bots", value=f"{humans} / {bots}", inline=True)

        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)

        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Stickers", value=len(guild.stickers), inline=True)

        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="Verification Level", value=str(guild.verification_level).title(), inline=True)

        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at, "F"), inline=False)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="bot-diagnostics", description="Provides the stats of the bot.")
    @app_commands.checks.has_role("[DEV] Developer")
    async def bot_diagnostics(interaction : discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        me = guild.me

        permissions = me.guild_permissions

        embed = discord.Embed(
            title=f"📊 Bot diagnostics • {guild.name}",
            colour=discord.Color.gold()
        )

        embed.add_field(name="Latency", value=round(bot.latency * 1000), inline=True)
        embed.add_field(name="Highest Role", value=me.top_role.mention, inline=True)
        embed.add_field(name="Role Position", value=me.top_role.position, inline=True)
        embed.add_field(name="Colour", value=me.colour, inline=True)

        embed.add_field(name="Manage Roles", value='✅' if permissions.manage_roles else '❌', inline=True)
        embed.add_field(name="Manage Nicknames", value='✅' if permissions.manage_nicknames else '❌', inline=True)
        embed.add_field(name="Administrator", value='✅' if permissions.administrator else '❌', inline=True)
        embed.add_field(name="View Audit Log", value='✅' if permissions.view_audit_log else '❌', inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.followup.send(embed=embed, ephemeral=True)
    
    '''
    #promote (Lt. Gen+)   ---- also need promotion logs and they cant promote anyone to CSB! for example
    @bot.tree.command(name="bot-diagnostics", description="Provides the stats of the bot.")
    @app_commands.checks.has_role("[CDEV] Chief Developer")
    async def bot_diagnostics(interaction : discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        me = guild.me

        permissions = me.guild_permissions

        embed = discord.Embed(
            title=f"📊 Bot diagnostics • {guild.name}",
            colour=discord.Color.gold()
        )

        embed.add_field(name="Latency", value=round(bot.latency * 1000), inline=True)
        embed.add_field(name="Highest Role", value=me.top_role.mention, inline=True)
        embed.add_field(name="Role Position", value=me.top_role.position, inline=True)
        embed.add_field(name="Colour", value=me.colour, inline=True)

        embed.add_field(name="Manage Roles", value='✅' if permissions.manage_roles else '❌', inline=True)
        embed.add_field(name="Manage Nicknames", value='✅' if permissions.manage_nicknames else '❌', inline=True)
        embed.add_field(name="Administrator", value='✅' if permissions.administrator else '❌', inline=True)
        embed.add_field(name="View Audit Log", value='✅' if permissions.view_audit_log else '❌', inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.followup.send(embed=embed, ephemeral=True)
    '''