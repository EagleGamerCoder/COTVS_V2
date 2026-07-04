import discord
from utils.data_loader import load_data
from verification.verification_manager import send_VerificationUi

'''
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
'''

def make_embeds(channel_data: dict, language: str) -> list[discord.Embed]:
    embeds = []

    lang_data = channel_data.get(language)

    if not lang_data:
        return embeds

    for embed_data in lang_data["embeds"].values():

        embed = discord.Embed(
            colour=discord.Color(0xffd739),
            description=embed_data.get("desc", "")
        )

        if embed_data.get("title"):
            embed.title = f"__{embed_data['title']}__"

        embeds.append(embed)

    return embeds

class LanguageDropdown(discord.ui.Select):

    def __init__(self, channel_name: str, languages: dict):

        self.channel_name = channel_name

        options = []

        emoji_lookup = {
            "eng": "🇬🇧",
            "spa": "🇪🇸",
            "fra": "🇫🇷",
            "deu": "🇩🇪",
            "ita": "🇮🇹",
            "por": "🇵🇹",
            "pol": "🇵🇱",
            "jpn": "🇯🇵",
            "kor": "🇰🇷",
            "zho": "🇨🇳",
            "rus": "🇷🇺"
        }

        name_lookup = {
            "eng": "English",
            "spa": "Español",
            "fra": "Français",
            "deu": "Deutsch",
            "ita": "Italiano",
            "por": "Português",
            "pol": "Polski",
            "jpn": "日本語",
            "kor": "한국어",
            "zho": "中文",
            "rus": "Русский"
        }

        for lang in languages.keys():

            options.append(
                discord.SelectOption(
                    label=name_lookup.get(lang, lang.upper()),
                    value=lang,
                    emoji=emoji_lookup.get(lang)
                )
            )

        super().__init__(
            placeholder="🌍 Select your language",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        data = await load_data("embeds/embed_info.json")

        channel_data = data[self.channel_name]

        embeds = make_embeds(channel_data, self.values[0])

        await interaction.response.send_message(
            embeds=embeds,
            ephemeral=True
        )

class LanguageView(discord.ui.View):

    def __init__(self, channel_name: str, languages: dict):
        super().__init__(timeout=None)

        self.add_item(LanguageDropdown(channel_name, languages))

async def create_embed(ctx, channel: discord.TextChannel):

    if channel.name == "verification":
        await send_VerificationUi(ctx, channel)
        return

    try:

        data = await load_data("embeds/embed_info.json")

        if channel.name not in data:
            return

        channel_data = data[channel.name]

        embed = discord.Embed(
            title="🌐 Language Selection",
            description=(
                "Choose your preferred language using the dropdown below.\n "
            ),
            colour=discord.Color(0xffd739)
        )

        embed.set_footer(
            text="The translated information will only be visible to **you**."
        )

        await channel.send(
            embed=embed,
            view=LanguageView(
                channel.name,
                channel_data
            )
        )

    except Exception as e:
        await ctx.log_error(
            None,
            "create_embed",
            1,
            e
        )