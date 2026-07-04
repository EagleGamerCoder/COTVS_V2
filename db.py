'''

Module: db.py
Author: EagleGamerCoder
Most recent update version: V 0.6.5
Description:
    Handles all database quieries including checking, getting 
    and saving.

Usage:
    verify_view.py
    reactions.py
    discord_roblox_role_sync.py

Components:
    Functions:
        init_database()
        set_guild_config(guild_id, channel_id, role_id, group_id, sub_group_id_one, sub_group_id_two, sub_group_id_three)
        get_guild_config(guild_id)
        save_pending(discord_id, roblox_id, code, created_at)
        get_pending(discord_id)
        delete_pending(discord_id)
        save_verify(discord_id, roblox_id)
        get_roblox_id(discord_id)
        save_server_rules_ids(guild_id, channel_id, message_id)
        get_server_rules_ids(guild_id)
        save_accepted_rules(guild_id, user_id)
        has_accepted_rules(guild_id, user_id)
        remove_accepted_rules(guild_id, user_id)

    Classes:
        _

''''''

import psycopg2
import os


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_database():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS guild_config (
        guild_id BIGINT PRIMARY KEY,
        channel_id BIGINT,
        role_id BIGINT,
        group_id BIGINT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS pending_verifications (
        discord_id BIGINT PRIMARY KEY,
        roblox_id BIGINT,
        code TEXT,
        created_at BIGINT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS verified (
        discord_id BIGINT PRIMARY KEY,
        roblox_id BIGINT
    )
    """)

    conn.commit()
    conn.close()

# ------------------------------------------------------------ GUILD CONFIG ------------------------------------------------------------

def set_guild_config(guild_id, channel_id, role_id, group_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO guild_config VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (guild_id) DO UPDATE SET
        channel_id = EXCLUDED.channel_id,
        role_id = EXCLUDED.role_id,
        group_id = EXCLUDED.group_id
    """, (guild_id, channel_id, role_id, group_id))

    conn.commit()
    conn.close()

def get_guild_config(guild_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT channel_id, role_id, group_id
    FROM guild_config WHERE guild_id = %s
    """, (guild_id,))

    data = c.fetchone()
    conn.close()
    return data

# ------------------------------------------------------------ PENDING ------------------------------------------------------------

def save_pending(discord_id, roblox_id, code, created_at):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO pending_verifications VALUES (%s, %s, %s, %s)
    ON CONFLICT (discord_id) DO UPDATE SET
        roblox_id = EXCLUDED.roblox_id,
        code = EXCLUDED.code,
        created_at = EXCLUDED.created_at
    """, (discord_id, roblox_id, code, created_at))

    conn.commit()
    conn.close()

def get_pending(discord_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT roblox_id, code, created_at
    FROM pending_verifications WHERE discord_id = %s
    """, (discord_id,))

    data = c.fetchone()
    conn.close()
    return data

def delete_pending(discord_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    DELETE FROM pending_verifications WHERE discord_id = %s
    """, (discord_id,))

    conn.commit()
    conn.close()

# ------------------------------------------------------------ VERIFIED ------------------------------------------------------------

def save_verify(discord_id, roblox_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO verified VALUES (%s, %s)
    ON CONFLICT (discord_id) DO UPDATE SET
        roblox_id = EXCLUDED.roblox_id
    """, (discord_id, roblox_id))

    conn.commit()
    conn.close()

def get_roblox_id(discord_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT roblox_id FROM verified WHERE discord_id = %s
    """, (discord_id,))

    data = c.fetchone()
    conn.close()
    return data[0] if data else None  
'''

import sqlite3

DB_NAME = "database.db"


def get_conn():
    return sqlite3.connect(DB_NAME)


def init_database():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS guild_config (
        guild_id INTEGER PRIMARY KEY,
        role_id INTEGER,
        group_id INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS pending_verifications (
        discord_id INTEGER PRIMARY KEY,
        roblox_id INTEGER,
        code TEXT,
        created_at INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS verified (
        discord_id INTEGER PRIMARY KEY,
        roblox_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# GUILD CONFIG
# ------------------------------------------------------------

def set_guild_config(guild_id, role_id, group_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO guild_config (guild_id, role_id, group_id)
    VALUES (?, ?, ?)
    ON CONFLICT(guild_id) DO UPDATE SET
        role_id = excluded.role_id,
        group_id = excluded.group_id
    """, (guild_id, role_id, group_id))

    conn.commit()
    conn.close()


def get_guild_config(guild_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT role_id, group_id
    FROM guild_config
    WHERE guild_id = ?
    """, (guild_id,))

    data = c.fetchone()
    conn.close()
    return data


# ------------------------------------------------------------
# PENDING VERIFICATIONS
# ------------------------------------------------------------

def save_pending(discord_id, roblox_id, code, created_at):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO pending_verifications
    (discord_id, roblox_id, code, created_at)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(discord_id) DO UPDATE SET
        roblox_id = excluded.roblox_id,
        code = excluded.code,
        created_at = excluded.created_at
    """, (discord_id, roblox_id, code, created_at))

    conn.commit()
    conn.close()


def get_pending(discord_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT roblox_id, code, created_at
    FROM pending_verifications
    WHERE discord_id = ?
    """, (discord_id,))

    data = c.fetchone()
    conn.close()
    return data


def delete_pending(discord_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    DELETE FROM pending_verifications
    WHERE discord_id = ?
    """, (discord_id,))

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# VERIFIED
# ------------------------------------------------------------

def save_verify(discord_id, roblox_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO verified (discord_id, roblox_id)
    VALUES (?, ?)
    ON CONFLICT(discord_id) DO UPDATE SET
        roblox_id = excluded.roblox_id
    """, (discord_id, roblox_id))

    conn.commit()
    conn.close()


def get_roblox_id(discord_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT roblox_id
    FROM verified
    WHERE discord_id = ?
    """, (discord_id,))

    data = c.fetchone()
    conn.close()

    return data[0] if data else None