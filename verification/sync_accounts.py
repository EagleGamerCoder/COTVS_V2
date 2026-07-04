'''

Module: discord_roblox_role_sync.py
Author: EagleGamerCoder
Most recent update version: V 0.6.5
Description:
    Manages adding roblox group roles and nicknames to 
    discord.

Usage:
    verify_view.py

Components:
    Functions:
        remove_leading_bracket(string : str) -> str
        normalize(name: str) -> str
        set_prefix_nickname(member, role_name: str)
        get_roblox_multi_group_role(member : discord.member, interaction : discord.Interaction, group_id : int, sub_one : int, sub_two : int, sub_three : int)
        get_category_role_name(interaction, clean_name, subgroup_name) -> str
        add_roles_to_user(interaction : discord.Interaction, member : discord.member, *args)
        remove_roles_to_user(interaction : discord.Interaction, member : discord.member, *args)
        sync_discord_and_roblox_roles(member: discord.member, interaction : discord.Interaction, group_id : int, sub_one : int, sub_two : int, sub_three : int) -> int | None

    Classes:
        _

'''

# ------------------------------------------------------------ IMPORTS ------------------------------------------------------------

# Standard Imports
import discord
import asyncio
import re 

# Modules
import db
from config import main_guild_id
from utils.logger import log_error
import verification.roblox_api as roblox_api

# ------------------------------------------------------------ VARIABLES ------------------------------------------------------------
'''
# Category role names in the guild
CATEGORY_ROLE_NAMES = {
    "ENLISTED": "Enlisted",
    "OFFICER": "Officer",
    "CHIEF_OF_STAFF_BOARD": "👑 Chief of Staff Board",
    "DEVELOPER": "[DEV] Developer",
}

# Prefix groups (normalized)
ENLISTED_PREFIX = ("[OR-",)
OFFICER_PREFIX = ("[OF-",)
CSB_PREFIXES = ("[CDS", "[VCD", "[SEA", "[CAS", "[VCA", "[ASM")
DEV_PREFIX = ("[DEV",)
'''


# ------------------------------------------------------------ FUNCTIONS ------------------------------------------------------------

# Removes the leading bracket and all content before it
def remove_leading_bracket(string : str) -> str:
    return re.sub(r'^\[.*?\]\s*','',string)



# normalises a string -> uppercase and without spaces
def normalize(name: str) -> str:
    if name is None:
        return ""
    return name.strip().upper()



# Sets a discord users nickname as their roblox role's prefix
async def set_prefix_nickname(member, role_name: str, roblox_username : str):
    try: 
        match = re.match(r'^\[[^\]]+\]', role_name)
        prefix = match.group(0) if match else ""

        try:
            await member.edit(nick=f"{prefix} {roblox_username}")

        except discord.Forbidden:
            await log_error(None, "set_prefix_nickname", 1, "Missing Permissions - Possible Eagle infiltration")
            return
        except discord.HTTPException as e:
            await log_error(None, "set_prefix_nickname", 2, e)
            return
            
    except Exception as e:
        await log_error(None, "set_prefix_nickname", 3, e)
        return



# returns the group role and sub group name for the specified discord member and guild info
async def get_roblox_multi_group_role(roblox_id : int, interaction : discord.Interaction, group_id : int):
    try:
        # Get main group role safely
        group_data = await roblox_api.get_roblox_player_group_data(roblox_id, group_id)
        if not isinstance(group_data, dict):
            return None

        group_role = group_data.get("role")

        if not isinstance(group_role, dict):
            return None

    except Exception as e:
        await log_error(interaction, "get_roblox_multi_group_role", 1, e)
        return None

    return group_role


'''
# Determins the category role for the new roblox role to be added
async def get_category_role_name(interaction, clean_name, subgroup_name) -> str:    
    new_category_name = None
    if subgroup_name:
        new_category_name = subgroup_name
    else:
        if interaction.guild.id == main_guild_id or any(clean_name.startswith(p) for p in CSB_PREFIXES):
            if any(clean_name.startswith(p) for p in ENLISTED_PREFIX):
                new_category_name = CATEGORY_ROLE_NAMES["ENLISTED"]
            elif any(clean_name.startswith(p) for p in OFFICER_PREFIX):
                new_category_name = CATEGORY_ROLE_NAMES["OFFICER"]
            elif any(clean_name.startswith(p) for p in CSB_PREFIXES):
                new_category_name = CATEGORY_ROLE_NAMES["CHIEF_OF_STAFF_BOARD"]
            elif any(clean_name.startswith(p) for p in DEV_PREFIX):
                new_category_name = CATEGORY_ROLE_NAMES["DEVELOPER"]
        else:
            new_category_name = "HQ"

    return new_category_name
'''

async def add_roles_to_user(interaction, member, *roles):
    for role in roles:
        if role is None:
            continue
        await member.add_roles(role, reason="Syncing Roblox rank")

async def remove_roles_to_user(interaction, member, *roles):
    for role in roles:
        if role is None:
            continue
        await member.remove_roles(role, reason="Syncing Roblox rank")
    
'''
# returns a tuple if successful, syncs the user's discord roles with the users roblox group roles
async def sync_discord_and_roblox_roles(member: discord.Member, interaction : discord.Interaction, group_id : int) -> tuple[discord.Member, discord.Interaction, list[discord.Role | None]] | None:
    
    # Bot permission checks
    
    bot_member = interaction.guild.me

    if not bot_member.guild_permissions.manage_roles:
        await log_error(interaction, "sync_discord_roles", 1, "Missing Manage roles permission")
        return

    if not bot_member.guild_permissions.manage_nicknames:
        await log_error(interaction, "sync_discord_roles", 2, "Missing Change nicknames permission")
        return
    
    # Fetch roblox group role and sub group name

    group_role = await get_roblox_multi_group_role(member, interaction, group_id)

    if group_role is None:
        await log_error(interaction, "sync_discord_roles", 3, "Roblox API returned None (possible rate limit or failure)")
        return member, interaction, None



    if not isinstance(group_role, dict):
        # User has no group role -> they are a CIV
        # Remove all non-exempt roles 
        default_role = interaction.guild.default_role
        roles_to_strip = [
            r for r in member.roles
            if (
                r.name not in ["Roblox Verified", default_role.name]
                and not r.managed
                and r < interaction.guild.me.top_role
            )
        ]
        if roles_to_strip:
            try:
                await member.remove_roles(*roles_to_strip, reason="User not in Roblox group")
            except discord.HTTPException as e:
                await log_error(interaction, "sync_discord_roles", 4, f"Failed to strip roles for {member.id}. Error Msg: {e}")

        civilian_role = discord.utils.get(interaction.guild.roles, name="[CIV] Civilian")
        if civilian_role and civilian_role not in member.roles:
            try:
                await member.add_roles(civilian_role, reason="Assign civilian role")
            except discord.Forbidden:
                await log_error(interaction, "sync_discord_roles", 5, f"Permission denied when adding civilian role to {member.id}")
            except discord.HTTPException as e:
                await log_error(interaction, "sync_discord_roles", 6, f"Failed to add civilian role to {member.id}. Error Msg: {e}")
        
        # Nickname update
        try:
            await set_prefix_nickname(member, "[CIV] Civilian")
        except Exception as e:
            await log_error(interaction, "sync_discord_roles", 7, f"Failed to set nickname for {member.id}. Error Msg: {e}")

        return member, interaction, [civilian_role]

    # Regular role logic
    role_name = group_role.get("name") if group_role else "Unknown"
    clean_name = normalize(role_name)

    keep_role_names = {interaction.guild.default_role.name, "Roblox Verified"}

    # Find the exact discord role that matches the Roblox role name
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role:
        keep_role_names.add(role.name)

    if not role:
        # Try a normalized lookup (in case of spacing/casing differences)
        role = discord.utils.find(
            lambda r: r.name.lower() == role_name.lower(),
            interaction.guild.roles
        )

    if not role:
        await log_error(interaction, "sync_discord_roles", 8, f"The {role_name} discord role does not exist.")
        return

    # Resolve category role object (may be None if not configured)

    new_category_name = await get_category_role_name(interaction, clean_name, sub_group_name)

    category_role = None
    if new_category_name:
        try:
            category_role = discord.utils.get(interaction.guild.roles, name=new_category_name)
        except Exception as e:
            await log_error(interaction, "sync_discord_roles", 9, f"The {new_category_name} discord role does not exist. Error Msg: {e}")
            return

    # ----- ROLE ORGANISATION (Start)

    default_role = interaction.guild.default_role
    
    # Keep the main rank role and the new category role (if present)
    keep_role_names.add(role.name)
    if category_role:
        keep_role_names.add(category_role.name)

    # Identify current category roles on the member (so we can remove ones that don't match)
    current_category_roles = [
        r for r in member.roles
        if r.name in set(CATEGORY_ROLE_NAMES.values())
    ]

    # Roles to remove:
    # - Any role that is not @everyone, not Roblox Verified, not managed,  not above the bot, and not in keep_role_names.
    to_remove = [
        r for r in member.roles
        if (
            r != default_role
            and r.name not in keep_role_names
            and not r.managed
            and r < interaction.guild.me.top_role
        )
    ]

    # Additionally, remove category roles that conflict with the new category.
    # Example: moving from Officer -> Chief of Staff Board should remove Officer role.
    conflicting_category_roles = [
        r for r in current_category_roles
        if r.name not in keep_role_names  # remove category roles that are not the new one
        and r < interaction.guild.me.top_role
    ]

    # Merge lists and deduplicate
    remove_set = {r for r in to_remove + conflicting_category_roles}

    # Perform removals (if any)
    if remove_set:
        await remove_roles_to_user(interaction, member, *remove_set)

    # Add the main role if missing
    if role not in member.roles:
        await add_roles_to_user(interaction, member, role)
        
    # Ensure category role is correct: remove other category roles (defensive) then add the new one
    # Remove any remaining category roles that are not the desired one
    remaining_conflicting = [
        r for r in member.roles
        if r.name in set(CATEGORY_ROLE_NAMES.values())
        and r.name != (category_role.name if category_role else None)
        and r < interaction.guild.me.top_role
    ]
    if remaining_conflicting:
        await remove_roles_to_user(interaction, member, *remaining_conflicting)

    # Add the category role if applicable and missing
    if category_role and category_role not in member.roles:
        await add_roles_to_user(interaction, member, category_role)

    # ----- ROLE ORGANISATION (End)

    # Nickname update
    try:
        await set_prefix_nickname(member, role_name)
    except Exception as e:
        await log_error(interaction, "sync_discord_roles", 10, f"Failed to set nickname for {member.id}. Error Msg: {e}")

    return member, interaction, [role, category_role]
'''


async def sync_discord_and_roblox_roles(member: discord.Member, interaction : discord.Interaction, roblox_id : int, group_id : int, roblox_username : str) -> tuple[discord.Member, discord.Interaction, list[discord.Role | None]] | None:
    
    # Bot permission checks
    added_roles = []
    removed_roles = []

    bot_member = interaction.guild.me

    if not bot_member.guild_permissions.manage_roles:
        await log_error(interaction, "sync_discord_roles", 1, "Missing Manage roles permission")
        return

    if not bot_member.guild_permissions.manage_nicknames:
        await log_error(interaction, "sync_discord_roles", 2, "Missing Change nicknames permission")
        return
    
    # Add format roles if the user doesn't already have them
    CATEGORY_ROLES = ["▬▬▬▬▬ RANKS ▬▬▬▬▬", "▬▬▬▬▬ PERMISSIONS ▬▬▬▬▬", "▬▬▬▬▬ AWARDS ▬▬▬▬▬", "▬▬▬▬▬ OTHER ▬▬▬▬▬"]

    for category_role_name in CATEGORY_ROLES:
        category_role = discord.utils.get(interaction.guild.roles, name=category_role_name)
        if category_role and category_role not in member.roles:
            await add_roles_to_user(interaction, member, category_role)
            added_roles.append(category_role)

    # add CIV to eevry verified user if they are in the group or not
    CIV = "[CIV] Civilian"
    civ = discord.utils.get(interaction.guild.roles, name=CIV)
    if civ not in member.roles:
        await add_roles_to_user(interaction, member, civ)
        added_roles.append(civ)

    # Fetch roblox group role
    group_role = await get_roblox_multi_group_role(roblox_id, interaction, group_id)

    if group_role is None:
        await log_error(interaction, "sync_discord_roles", 3, "Roblox API returned None (possible rate limit or failure)")
        return member, interaction, None
    
    SKIP_ROLES=["▬▬▬▬▬ RANKS ▬▬▬▬▬","▬▬▬▬▬ PERMISSIONS ▬▬▬▬▬", "▬▬▬▬▬ AWARDS ▬▬▬▬▬","▬▬▬▬▬ OTHER ▬▬▬▬▬","[CIV] Civilian","[DEV] Developer","[CDEV] Chief Developer","Admin?","Moderator","Trial Moderator","Army Standard Training Staff","Airborne Wings","EU","EST","AEST","Content Ping","Random Ping","Teaser Ping","Development Ping","Media Ping"]

    main_role = discord.utils.get(interaction.guild.roles, name=group_role.get("name"))

    if main_role not in member.roles:
        user_roles = member.roles
        for role in user_roles:
            if role.name in SKIP_ROLES:
                continue
            removed_roles.append(role)
    
    added_roles.append(main_role)

    # Other organisational roles

    OFFICER_PREFIX = ("[OF-")
    CSB_PREFIXES = ("[CDS", "[VCD", "[SEA", "[CAS", "[VCA", "[ASM")

    if any(group_role.get("name", "").startswith(p) for p in OFFICER_PREFIX):
        rank_category = discord.utils.get(interaction.guild.roles, name="Officer")
        added_roles.append(rank_category)
    elif any(group_role.get("name", "").startswith(p) for p in CSB_PREFIXES):
        rank_category = discord.utils.get(interaction.guild.roles, name="Chief of Staff Board")
        rank_category = discord.utils.get(interaction.guild.roles, name="Officer")
        added_roles.append(rank_category)

    await remove_roles_to_user(interaction, member, *removed_roles)
    await add_roles_to_user(interaction, member, *added_roles)

    # Nickname update
    try:
        await set_prefix_nickname(member, main_role.name, roblox_username)
    except Exception as e:
        await log_error(interaction, "sync_discord_roles", 4, f"Failed to set nickname for {member.id}. Error Msg: {e}")

    return member, interaction, added_roles