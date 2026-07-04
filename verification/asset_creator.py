import discord
import time
import asyncio
import db
from utils.logger import log_error
import verification.roblox_api as roblox_api
import random
import string
import verification.sync_accounts as sync_accounts

BUTTON_COOLDOWN = 4 # in seconds
EXPIRY_TIME = 600 #(10 minutes = 600 seconds)

def generate_code_six() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

roblox_cache = {}
user_cooldowns = {}
role_lock = asyncio.Lock()

def check_cooldown(user_id: int, cooldown: int = 10):
    now = time.time()

    if user_id in user_cooldowns:
        if now - user_cooldowns[user_id] < cooldown:
            return False

    user_cooldowns[user_id] = now
    return True

def cache_roblox(username: str, roblox_id: int):
    roblox_cache[username.lower()] = roblox_id

def get_cached_roblox( username: str):
    return roblox_cache.get(username.lower())

def create_verification_embed() -> discord.Embed:
    return discord.Embed(
        title="- Roblox Verification -",
        description="1. Click the 'Start Verification' button below.\n"
        "2. Enter your Roblox Username.\n"
        "3. Click the 'Complete Verification' button once you have attached the code to your profile.\n\n"
        "> If you are already Verified click 'Update' to update your server roles.",
        color=discord.Color(0xffd739)
    )

# Gets the guild config but returns it as a dict
def get_guild_config(guild_id : int) -> dict | None:
    config = db.get_guild_config(guild_id)
    if not config:
        return None
    try:
        role_id, group_id = config
        return {
            "role_id" : role_id,
            "group_id" : group_id
        }
    except Exception as e:
        log_error(None, "get_guild_config", 1, e)
        return None



async def ensure_role_sync(interaction, roblox_id, group_id, role_id, roblox_username):
    # Sync roblox & discord roles
    try:
        async with role_lock:
            
            result = await sync_accounts.sync_discord_and_roblox_roles(
                interaction.user, 
                interaction, 
                roblox_id,
                int(group_id),
                roblox_username
            )
            

        if result:
            role = interaction.guild.get_role(role_id)

            if role:
                await interaction.user.add_roles(role) # adds verified role

            db.delete_pending(interaction.user.id)
            db.save_verify(interaction.user.id, roblox_id)  
            
            base_roles = result[2] or []

            roles_list = base_roles + ([role] if role else [])

            await output_roles(result[0], result[1], roles_list)

            await interaction.followup.send("✅ Verified!", ephemeral=True)

        else:
            await interaction.followup.send("❌ Verification Failed.", ephemeral=True)
            return
        
    except Exception as e:
        await log_error(interaction, "ensure_role_sync", 1, e)

# Gives a resulting output to the user
async def output_roles(member, interaction : discord.Interaction, roles: list):
    new_roles = []

    for role in roles:
        if isinstance(role, discord.Role):
            new_roles.append(role.name)
        elif role is not None:
            new_roles.append(str(role))

    outputEmbed = discord.Embed(
        description="## You have been given the roles:\n\n> " + "\n> ".join(new_roles), #----------------------------------------------------------------
        color=discord.Color(0xffd739)
    )

    await interaction.followup.send(embed=outputEmbed, ephemeral=True)

    try:
        await member.send(
            f"You have been ranked in the {interaction.guild.name} Discord Server."
        )
    except discord.Forbidden:
        pass



# Creates a modal to get a players username and begin the verification process
class UsernameModal(discord.ui.Modal, title="Enter Roblox Username"):
    username_ = discord.ui.TextInput(label="Roblox Username")

    async def on_submit(self, interaction : discord.Interaction):
        username = self.username_.value.strip()
        
        roblox_id = get_cached_roblox(username)

        if roblox_id is None:
            roblox_id = await roblox_api.get_roblox_id(username)
            cache_roblox(username, roblox_id)

        if roblox_id is None:
            await interaction.response.send_message(
                "Username not found. Try again.", 
                ephemeral=True,
            )
            return
        
        code = generate_code_six()
        db.save_pending(
            discord_id=interaction.user.id, 
            roblox_id=roblox_id, 
            code=code, 
            created_at=int(time.time())
        )

        await interaction.response.send_message(
            f"Put this code into your Roblox bio:\n\n**{code}**\n\nThen press **Complete Verification**",
            ephemeral=True,
        )



# Creates a button that is used to begin verify users and connect to the modal.
class StartVerificationButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Start Verification",
            style=discord.ButtonStyle.blurple,
            custom_id="persistent_start_verification"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            # General checks

            if not check_cooldown(interaction.user.id, BUTTON_COOLDOWN):
                await interaction.response.send_message(
                    f"⏳ Please wait {BUTTON_COOLDOWN} seconds before trying again.",
                    ephemeral=True
                )
                return

            # Send username modal to get username

            await interaction.response.send_modal(UsernameModal())

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "An unexpected error occurred.",
                    ephemeral=True
                )
            await log_error(interaction, "StartVerificationButton", 2, e)



# Creates a button that is used to complete the verificiation process and save users data to the database (db), and finally auto-update their roles using services/role_sync.py.
class CompleteVerificationButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Complete Verification",
            style=discord.ButtonStyle.green,
            custom_id="persistent_complete_verification"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            # Account and general checks

            if not check_cooldown(interaction.user.id, BUTTON_COOLDOWN):
                await interaction.response.send_message(
                    f"⏳ Please wait {BUTTON_COOLDOWN} seconds before trying again.",
                    ephemeral=True
                )
                return

            await interaction.response.defer(ephemeral=True)

            pending = db.get_pending(interaction.user.id)
            if not pending:
                await interaction.followup.send("❌ Start Verification first.", ephemeral=True)
                return
            roblox_id, code, created_at = pending

            # Expiry check 
            if time.time() - created_at > EXPIRY_TIME:
                db.delete_pending(interaction.user.id)
                await interaction.followup.send("❌ Verification expired. Start again.", ephemeral=True)
                return
            
            config = get_guild_config(interaction.guild.id)
            if not config:
                await log_error(interaction, "CompleteVerificationButton", 1, "Guild not configured")
                return

            player_data = await roblox_api.get_roblox_player_data(roblox_id)
            if player_data == None:
                await log_error(interaction, "CompleteVerificationButton", 2, f"Error when getting player data of id: {roblox_id}")
            elif player_data['isBanned'] == True:
                interaction.followup.send(f"Player of id: {roblox_id} is banned, cannot verify.", ephemeral=True)
            
            description = player_data['description']
            if not description or code not in description:
                await interaction.followup.send("❌ Code not in bio.", ephemeral=True)
                return
            
            if interaction.user.id == 1434931977571668113:
                await interaction.followup.send("(-.-) Eagle, I'll give it go, no promises...", ephemeral=True)

            await asyncio.sleep(0.5)
            
            await ensure_role_sync(
                interaction, 
                roblox_id, 
                config['group_id'],
                config['role_id'],
                player_data["name"]
            )

        except Exception as e:
            await log_error(interaction, "CompleteVerificationButton", 3, e)
        
        

# Creates a button that is used to update verified users' roles using services/role_sync.py.
class UpdateButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Update",
            style=discord.ButtonStyle.green,
            custom_id="persistent_update_verification",
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            # General checks

            if not check_cooldown(interaction.user.id, BUTTON_COOLDOWN):
                await interaction.response.send_message(
                    f"⏳ Please wait {BUTTON_COOLDOWN} seconds before trying again.",
                    ephemeral=True
                )
                return
            
            await interaction.response.defer(ephemeral=True)

            roblox_id = db.get_roblox_id(interaction.user.id)
            if not roblox_id or roblox_id is None:
                await interaction.followup.send("❌ Your account is not verified.", ephemeral=True)
                return
            
            player_data = await roblox_api.get_roblox_player_data(roblox_id)
            if player_data == None:
                await log_error(interaction, "UpdateButton", 2, f"Error when getting player data of id: {roblox_id}")
            elif player_data['isBanned'] == True:
                interaction.followup.send(f"Player of id: {roblox_id} is banned, cannot update.", ephemeral=True)
            
            config = get_guild_config(interaction.guild.id)
            if not config:
                await log_error(interaction, "UpdateButton", 1, "Guild not configured")
                return

            await asyncio.sleep(0.5)
            
            await ensure_role_sync(
                interaction, 
                roblox_id, 
                config['group_id'],
                config['role_id'],
                player_data["name"]
            )
            
        except Exception as e:
            await log_error(interaction, "UpdateButton", 2, e)


# Persistent view that keeps buttons active across restarts (requires bot.add_view on startup). 
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent
        self.add_item(StartVerificationButton())
        self.add_item(CompleteVerificationButton())
        self.add_item(UpdateButton())