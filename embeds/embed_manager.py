import discord
from utils.data_loader import load_data
from verification.verification_manager import send_VerificationUi

async def create_embed(ctx, channel : discord.TextChannel):
    if channel.name == "verification":
        await send_VerificationUi(ctx, channel)
        return

    data = await load_data("embeds/embed_info.json")
    embed_data = data[channel.name]

    if embed_data:
        try:
            # English heading
            await channel.send(f"# __**{embed_data["eng"]["title"]}**__ (English)")
            
            # English embeds
            for i, data_catgeory in embed_data["eng"]["embeds"].items():
                embed = discord.Embed(
                    description=data_catgeory.get("desc", ""),
                    color=discord.Color(0xffd739)
                )

                if "title" in data_catgeory:
                    embed.title = f"__{data_catgeory['title']}__"

                await channel.send(embed=embed)

            # Spanish Heading
            await channel.send(f"# __**{embed_data["spa"]["title"]}**__ (Español)")
            
            # Spanish embeds
            for i, data_catgeory in embed_data["spa"]["embeds"].items():
                embed = discord.Embed(
                    description=data_catgeory.get("desc", ""),
                    color=discord.Color(0xffd739)
                )

                if "title" in data_catgeory:
                    embed.title = f"__{data_catgeory['title']}__"

                await channel.send(embed=embed)
        
        except Exception as e:
            await ctx.log_error(None, "create_embed", 1, e)
