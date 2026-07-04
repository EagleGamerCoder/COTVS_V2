import discord
import verification.asset_creator as asset_creator

async def send_VerificationUi(ctx, channel : discord.TextChannel):
    await channel.send(f"# Welcome to the {channel.guild.name} discord server!")

    verification_embed = asset_creator.create_verification_embed()
    await channel.send(embed=verification_embed, view=ctx.VerifyView())