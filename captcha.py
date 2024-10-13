from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import random


def brouiller(draw, width, height, nblignes=10, nbpoints=17500):
    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0), width=2)
    for _ in range(17500):
        x, y = random.randint(0, width), random.randint(0, height)
        draw.point((x, y), fill=(0, 0, 0))

def ecrire(draw,code,height):
    fonts = ['arial.ttf', 'times.ttf', 'cour.ttf', 'verdana.ttf']
    font_sizes = [28, 30, 32, 34]
    x = 50
    for char in code:
        font_name = random.choice(fonts)
        font_size = random.choice(font_sizes)
        font = ImageFont.truetype(font_name, font_size)
        y = random.randint(10, height - font_size - 10)
        draw.text((x, y), char, font=font, fill=(0, 0, 0))
        # Mettre la lettre en italique avec une certaine probabilité
        if random.random() < 0.5:
            angle = random.uniform(-10, 10)
            draw.text((x, y), char, font=font, fill=(0, 0, 0), angle=angle)
        # Ajouter un espace suffisant pour éviter les chevauchements
        x += font_size + random.randint(15, 30)

def creer_captcha(code, width=400, height=200):
    # Créer une image blanche
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    brouiller(draw, width, height)

    # Dessiner les caractères du code de captcha
    ecrire(draw, code, height)

    # Appliquer un filtre de flou pour rendre l'image plus difficile à lire
    img = img.filter(ImageFilter.GaussianBlur(radius=0.80))

    # Enregistrer l'image
    img.save('captcha.png')
    img.close()
    return img


def generer_code(taille=6):
    return ''.join(random.choice('abcdefghijklmnopqrsxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(taille))

creer_captcha("123456")