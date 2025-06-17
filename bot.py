import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from commands_dc import remove_role_map,set_channel,show_mapping,add_role_map,get_config
import io
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import requests
import asyncio
from only_letters import only_letters
load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load config
with open("config.json") as f:
    config = json.load(f)

FIREBASE_URL = os.getenv("FIREBASE_URL") 
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    await bot.tree.sync()


@bot.event
async def on_message(message):
    # print('Message received!')
    guild_id = message.guild.id
    res = requests.get(f'{FIREBASE_URL}config/{guild_id}.json')
    config = res.json()

    TARGET_CHANNEL_ID = config.get("target_channel_id", "")

    if message.author.bot or not message.attachments:
        return
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    for attachment in message.attachments:
        if not attachment.filename.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp")):
            await message.channel.send(
                "Please upload a .jpg, .jpeg, or .png file.")
            return
        
        # React thinking to the message
        await message.add_reaction('⏳')

        # Download image
        image_bytes = await attachment.read()
        image = Image.open(io.BytesIO(image_bytes)).convert(
            "L")  # Convert to grayscale
        image = ImageOps.invert(image)
        # Crop the image
        wd, hg = image.size
        rect_crop = (
            int(wd * 0.65), int(hg * 0.15),
            int(wd * 0.85), int(hg * 0.30)
        )
        image = image.crop(rect_crop)

        # Turn into red letters and white background
        image = only_letters(image_in=image, threshold=160)

        # Change contrast
        # image = ImageEnhance.Contrast(image).enhance(2.0)
        # image = ImageEnhance.Sharpness(image).enhance(2.0)
        image = image.resize((image.width * 5, image.height * 5))
        # image.show()

        custom_config = r'--oem 3 --psm 6'

        ocr_data = pytesseract.image_to_data(
            image, config=custom_config, lang='eng+spa+tur+ind',
            output_type=pytesseract.Output.DATAFRAME)

        # Clean up the data
        ocr_data = ocr_data[ocr_data.conf != -1].reset_index(drop=True)

        # # Find the row with the word "Alliance"
        # ocr_data['text_trl'] = ocr_data['text'].apply(
        #     lambda x: GoogleTranslator(source='auto', target='en').translate(x)
        #     if isinstance(x, str) and x.strip() else x)

        print(ocr_data)
        # alliance_row = ocr_data[ocr_data['text_trl'].str.lower() == "alliance"]
        # print(alliance_row)

        # Find the text in the line immediately below "Alliance"
        word = ocr_data['text'].dropna().tolist()

        if not len(word) == 0:
            print(word)
            text_below = ''.join(word).strip()
            print(text_below)
            start = text_below.find("[")
            text_below = text_below[start:start+5]
            text_below = text_below.replace("[","").replace("]","")
            print("Alliance name:", text_below)

        else:
            print("'Alliance' not found in OCR output. Try another screenshot.")
            await message.add_reaction('❌')
            await message.channel.send("❌ Alliance not found in OCR output. Try another screenshot.")
            return

        try:
            alliance_tag = config["role_map"][text_below]
        except KeyError:
            alliance_tag = config["role_map"]["OTHER"]

        print(alliance_tag)

        # Assign role
        role_name = alliance_tag
        if role_name:
            role = discord.utils.get(message.guild.roles, name=role_name)
            if role:
                try:
                    await message.author.add_roles(role)
                    await message.clear_reactions()
                    if role_name != 'Other Server'
                        await message.add_reaction('✅')
                        await message.channel.send(f"✅ Role '{role_name}' assigned to {message.author.mention}.")
                    else:
                        await message.add_reaction('❓')
                        await message.channel.send(f"❓ The '{role_name}' role was assigned to {message.author.mention}. If you think it is wrong, try sending a complete screenshot of your profile. You don't have to crop it.")
                except discord.Forbidden:
                    await message.clear_reactions()
                    await message.add_reaction('❌')
                    await message.channel.send(
                        "❌ Missing permission to assign roles.")
            else:
                await message.clear_reactions()
                await message.add_reaction('❌')
                await message.channel.send(
                    f"❌ Role '{role_name}' not found on server.")
        else:
            await message.clear_reactions()
            await message.add_reaction('❌')
            await message.channel.send(
                f"❌ No role mapping found for alliance tag: [{alliance_tag}].")
        # Delete picture
        try:
            print('done')
            #await asyncio.sleep(60)
            #await message.delete()
        except discord.Forbidden:
            print("❌ Bot lacks permission to delete messages.")
        except discord.HTTPException as e:
            print(f"❌ Failed to delete message: {e}")

@bot.tree.command(name="add_role_map",
                  description="Add a new role mapping to config.json")
async def wrapped_add_role_map(interaction: discord.Interaction, tag: str,
                       role_name: str):
    await add_role_map(interaction,tag,role_name, FIREBASE_URL, interaction.guild.id)


@bot.tree.command(name="remove_role_map",
                  description="Remove a role mapping to config.json")
async def wrapped_remove_role_map(interaction: discord.Interaction, tag: str):
    await remove_role_map(interaction,tag, FIREBASE_URL, interaction.guild.id)


@bot.tree.command(name="show_mapping", description="Show role mapping")
async def wrapped_show_mapping(interaction: discord.Interaction):
    await show_mapping(interaction, FIREBASE_URL, interaction.guild.id)


@bot.tree.command(name="set_channel", description="Set the listening channel")
async def wrapped_set_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await set_channel(interaction, channel, FIREBASE_URL, interaction.guild.id)

@bot.tree.command(name='get_config', description='Get the config file')
async def wrapped_get_config(interaction: discord.Interaction):
    await get_config(interaction, str(interaction.guild.id), FIREBASE_URL)

bot.run(TOKEN)
### Created by GONZA ###
