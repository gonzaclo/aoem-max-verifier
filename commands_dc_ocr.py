import discord
import json
import io
import pytesseract
from PIL import Image, ImageEnhance
from deep_translator import GoogleTranslator

async def on_message(message):
    # Load config
    with open("config.json") as f:
        config = json.load(f)

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

        # Download image
        image_bytes = await attachment.read()
        image = Image.open(io.BytesIO(image_bytes)).convert(
            "L")  # Convert to grayscale
        image = ImageEnhance.Contrast(image).enhance(2.0)
        image = ImageEnhance.Sharpness(image).enhance(2.0)

        ocr_data = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DATAFRAME)

        # Clean up the data
        ocr_data = ocr_data[ocr_data.conf != -1].reset_index(drop=True)

        # Find the row with the word "Alliance"
        ocr_data['text_trl'] = ocr_data['text'].apply(
            lambda x: GoogleTranslator(source='auto', target='en').translate(x)
            if isinstance(x, str) and x.strip() else x)

        print(ocr_data['text_trl'])
        alliance_row = ocr_data[ocr_data['text_trl'].str.lower() == "alliance"]
        print(alliance_row)

        if not alliance_row.empty:
            # Get the line number of "Alliance"
            line_num = alliance_row.iloc[0]['line_num']
            block_num = alliance_row.iloc[0]['block_num']
            par_num = alliance_row.iloc[0]['par_num']

            # Find the text in the line immediately below "Alliance"
            next_line = ocr_data[(ocr_data['block_num'] == block_num)
                                 & (ocr_data['par_num'] == par_num) &
                                 (ocr_data['line_num'] == line_num + 1) &
                                 (ocr_data['text'].str.contains(']'))]

            print(next_line)

            text_below = ' '.join(next_line['text'].tolist()).replace(
                '[', '').replace(']', '')
            print("Text below 'Alliance':", text_below)

        else:
            print("'Alliance' not found in OCR output.")

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
                    await message.channel.send(f"Role '{role_name}' assigned.")
                except discord.Forbidden:
                    await message.channel.send(
                        "Missing permission to assign roles.")
            else:
                await message.channel.send(
                    f"Role '{role_name}' not found on server.")
        else:
            await message.channel.send(
                f"No role mapping found for alliance tag: [{alliance_tag}].")