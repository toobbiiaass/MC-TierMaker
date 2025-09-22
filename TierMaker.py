import requests
from PIL import Image, ImageDraw, ImageFont
import os
import base64
import json
import time

DELAY_PER_REQUEST = 1

def get_uuid(username):
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        response.raise_for_status()
        return response.json()["id"]
    except requests.RequestException:
        return None

def get_skin(uuid):
    try:
        response = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
        response.raise_for_status()
        data = response.json()
        for prop in data["properties"]:
            if prop["name"] == "textures":
                textures = json.loads(base64.b64decode(prop["value"]).decode("utf-8"))
                return textures["textures"]["SKIN"]["url"]
        return None
    except requests.RequestException:
        return None

def save_player_head_with_name(username, output_dir):
    output_path = os.path.join(output_dir, f"{username}.png")

    uuid = get_uuid(username)
    time.sleep(DELAY_PER_REQUEST)

    if not uuid:
        return False

    skin_url = get_skin(uuid)
    time.sleep(DELAY_PER_REQUEST)

    if not skin_url:
        return False

    try:
        skin_response = requests.get(skin_url)
        skin_response.raise_for_status()
        with open("temp_skin.png", "wb") as f:
            f.write(skin_response.content)
    except requests.RequestException:
        return False

    try:
        skin = Image.open("temp_skin.png")
        
        # layer1
        head_base = skin.crop((8, 8, 16, 16))
        # layer2
        head_overlay = skin.crop((40, 8, 48, 16))
        
        head_base = head_base.resize((128, 128), Image.NEAREST)
        head_overlay = head_overlay.resize((128, 128), Image.NEAREST)
        head_base.paste(head_overlay, (0, 0), head_overlay)
        head = head_base

        draw = ImageDraw.Draw(head)
        try:
            max_font_size = 36
            min_font_size = 12
            name_length = len(username)
            font_size = int(max_font_size - (name_length - 3) * (max_font_size - min_font_size) / 9)
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        text = username
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (128 - text_width) / 2
        y = (128 - text_height) / 4
        draw.text((x, y), text, fill=(255, 0, 255), font=font)

        head.save(output_path)
        print(f"Head of {username} saved at {output_path}.")
        return True
    except Exception as e:
        print(f"Error processing image for {username}: {e}")
        return False
    finally:
        if os.path.exists("temp_skin.png"):
            os.remove("temp_skin.png")

def main():
    print("+-----------------------------------------+")
    print("|            TierMaker by vuacy           |")
    print("+-----------------------------------------+")
    names = input("Enter the names (comma separated): ")
    name_list = [n.strip() for n in names.split(",") if n.strip()]
    skins_folder = "skins"
    os.makedirs(skins_folder, exist_ok=True)

    failed = []

    for name in name_list:
        success = save_player_head_with_name(name, skins_folder)
        if not success:
            failed.append(name)
        time.sleep(DELAY_PER_REQUEST)

    if failed:
        print("\nCould not find skins for the following names:")
        for name in failed:
            print(f" - {name}")
    else:
        print("\nAll skins processed successfully.")

if __name__ == "__main__":
    main()
