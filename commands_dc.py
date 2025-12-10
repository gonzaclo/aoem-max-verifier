import json
import discord
import requests

async def set_channel(interaction: discord.Interaction, channel: discord.TextChannel, firebase_url: str, server_id: str):
    responded = False
    try:
        try:
            await interaction.response.defer(ephemeral=True)
            responded = True
        except discord.HTTPException:
            responded = True

        res = requests.get(f'{firebase_url}config/{server_id}.json')
        config = res.json()
        print(config)

        config["target_channel_id"] = channel.id

        res = requests.patch(f'{firebase_url}config/{server_id}.json', json=config)

        await interaction.followup.send(f"✅ Channel set to: {channel.mention}", ephemeral=True)

    except Exception as e:
        if not responded:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
        else:
            try:
                await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
            except discord.HTTPException:
                pass

async def show_mapping(interaction: discord.Interaction, firebase_url: str, server_id: str):
    try:
        # Load current config
        res = requests.get(f'{firebase_url}config/{server_id}.json')
        config = res.json()

        # Show mapping
        role_map = config.get("role_map", {})
        message = ''
        for role in role_map:
            message = message + f'{role} → {role_map[role]} \n'
        await interaction.response.send_message(f"`{message}`",
                                                ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}",
                                                ephemeral=True)
        
async def remove_role_map(interaction: discord.Interaction, tag: str, firebase_url: str, server_id: str):
    try:
        # Load current config
        res = requests.get(f'{firebase_url}config/{server_id}.json')
        config = res.json()

        # Remove the role
        role_map = config.get("role_map", {})
        removed = role_map.pop(tag, None)
        if removed is None:
            await interaction.response.send_message(
                f"❌ No mapping found for tag: {tag}", ephemeral=True)
            return
        config["role_map"] = role_map

        # Save the updated config
        res = requests.patch(f'{firebase_url}config/{server_id}.json', json=config)

        await interaction.response.send_message(
            f"✅ Removed mapping for tag: `{tag}`", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}",
                                                ephemeral=True)
        
async def add_role_map(interaction: discord.Interaction, tag: str,
                       role_name: discord.Role,
                       firebase_url: str,
                       server_id: str):
    try:
        # Load current config
        res = requests.get(f'{firebase_url}config/{server_id}.json')
        config = res.json()

        # Add or update the role_map
        config.setdefault("role_map", {})[tag] = str(role_name)

        # Save the updated config
        res = requests.patch(f'{firebase_url}config/{server_id}.json', json=config)

        await interaction.response.send_message(
            f"✅ Added mapping: `{tag}` → `{role_name}`",
            ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}",
                                                ephemeral=True)
        
async def set_default_role(interaction: discord.Interaction,
                           set_default: str,
                           firebase_url: str,
                           server_id: str,
                           role_name: str = ''):
    try:
        # Load current config
        res = requests.get(f'{firebase_url}config/{server_id}.json')
        config = res.json() 

        # Add or update the default_role
        if set_default == "yes" and role_name != '-':
            config["default_role"] = str(role_name)
            config["set_default"] = str(set_default)
        else:
            config["default_role"] = ''
            config["set_default"] = 'no'

        # Save the updated config
        res = requests.patch(f'{firebase_url}config/{server_id}.json', json=config)

        if set_default == "yes" and role_name != '-':
            await interaction.response.send_message(
                f"✅ Added default role → `{role_name}`",
                ephemeral=True)
        elif set_default == "yes" and role_name == '-':
            await interaction.response.send_message(
                f"✅ When you use default_role = 'Yes', you must select one Role. The parameter set_default was set as 'No' automatically",
                ephemeral=True)
        else:
            await interaction.response.send_message(
                f"✅ You are not using a default role",
                ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}",
                                                ephemeral=True)
        
async def get_config(interaction: discord.Interaction, server_id: str, firebase_url: str):
    config = requests.get(f'{firebase_url}config/{server_id}.json')
    print(config.json())
    if config.json() is None:
        data = {
            "role_map": {
                "OTHER": "Other Alliance"
            },
            "target_channel_id": ""
        }
        # serv = requests.patch(f'{firebase_url}/config.json', server_id)
        res = requests.patch(f'{firebase_url}config/{server_id}.json', json=data)
        print(data)
        await interaction.response.send_message(
            f"✅ config: `{data}`", ephemeral=True)
    else:
        print(config.json())
        await interaction.response.send_message(
            f"✅ config: `{config.json()}`", ephemeral=True)