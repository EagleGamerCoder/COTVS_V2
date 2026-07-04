import discord
from discord import app_commands
from embeds.embed_manager import create_embed

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