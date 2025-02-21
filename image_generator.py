import json
import random
from PIL import Image, ImageDraw, ImageFont

def load_countries():
    """Carica la lista completa dei paesi con bandiere."""
    with open("full_countries.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["countries"]

def add_border(image, border_size=5, border_color="black"):
    """Aggiunge un bordo all'immagine."""
    bordered_image = Image.new("RGB", (image.width + 2 * border_size, image.height + 2 * border_size), border_color)
    bordered_image.paste(image, (border_size, border_size))
    return bordered_image

def generate_match_image(country1, flag1_path, move1, country2, flag2_path, move2, round_num):
    """Genera un'immagine del match con i dettagli delle bandiere e delle mosse."""
    width, height = 1200, 675  # Formato Twitter (16:9)
    background = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(background)
    
    try:
        flag1_img = Image.open(flag1_path).resize((400, 250))
        flag1_img = add_border(flag1_img)
    except Exception as e:
        print(f"Errore caricamento bandiera per {country1}: {e}")
        flag1_img = Image.new("RGB", (410, 260), "gray")
    
    try:
        flag2_img = Image.open(flag2_path).resize((400, 250))
        flag2_img = add_border(flag2_img)
    except Exception as e:
        print(f"Errore caricamento bandiera per {country2}: {e}")
        flag2_img = Image.new("RGB", (410, 260), "gray")
    
    try:
        battle_icon = Image.open("assets/spade_incrociate.png").convert("RGBA").resize((150, 150))
    except Exception as e:
        print(f"Errore caricamento icona di battaglia: {e}")
        battle_icon = Image.new("RGBA", (150, 150), (255, 255, 255, 0))  # Trasparente
    
    x_offset = (width - (flag1_img.width + battle_icon.width + flag2_img.width)) // 2
    y_offset = (height - flag1_img.height) // 2 + 50
    
    background.paste(flag1_img, (x_offset, y_offset))
    background.paste(battle_icon, (x_offset + flag1_img.width + 20, (height - battle_icon.height) // 2), battle_icon)
    background.paste(flag2_img, (x_offset + flag1_img.width + battle_icon.width + 40, y_offset))
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    round_text = f"Round {round_num}"
    draw.text(((width - draw.textbbox((0, 0), round_text, font=font)[2]) // 2, 20), round_text, font=font, fill="black")
    
    move1_text = f"{move1}"
    move2_text = f"{move2}"
    draw.text((x_offset + (flag1_img.width // 2) - 20, y_offset + flag1_img.height + 10), move1_text, font=font, fill="blue")
    draw.text((x_offset + flag1_img.width + battle_icon.width + 40 + (flag2_img.width // 2) - 20, y_offset + flag2_img.height + 10), move2_text, font=font, fill="red")
    
    img_path = "current_match.png"
    background.save(img_path)
    print(f"✅ Immagine del match salvata come {img_path}.")
    
    return img_path

def test_generate_match_image():
    """Testa la generazione dell'immagine con due paesi casuali."""
    countries = load_countries()
    country1, country2 = random.sample(countries, 2)
    move1, move2 = random.choice(["Rock", "Paper", "Scissors"]), random.choice(["Rock", "Paper", "Scissors"])
    
    generate_match_image(
        country1["name"], country1["flag"], move1,
        country2["name"], country2["flag"], move2,
        round_num=random.randint(1, 10)
    )

if __name__ == "__main__":
    test_generate_match_image()
