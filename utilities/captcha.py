from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os

widthbase, heightbase = 400, 200
taillebase = 6


def brouiller(draw, nblignes=10, nbpoints=12500):
    for _ in range(nblignes):
        x1, y1 = random.randint(0, widthbase), random.randint(0, heightbase)
        x2, y2 = random.randint(0, widthbase), random.randint(0, heightbase)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0), width=2)
    for _ in range(nbpoints):
        x, y = random.randint(0, widthbase), random.randint(0, heightbase)
        draw.point((x, y), fill=(0, 0, 0))


def ecrire(draw, code, height):
    fonts = [os.path.join(os.getcwd(), 'fonts', 'arial.ttf'), os.path.join(os.getcwd(), 'fonts', 'arial.ttf'),
             os.path.join(os.getcwd(), 'fonts', 'arial.ttf'),
             os.path.join(os.getcwd(), 'fonts', 'arial.ttf')]
    font_sizes = [28, 30, 32, 34]
    x = 30
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
        x += font_size + random.randint(15, 35)


def creer_captcha(code, width=400, height=200):
    # Créer une image blanche
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    brouiller(draw)

    # Dessiner les caractères du code de captcha
    ecrire(draw, code, height)

    # Appliquer un filtre de flou pour rendre l'image plus difficile à lire
    img = img.filter(ImageFilter.GaussianBlur(radius=0.80))

    # Enregistrer l'image
    img.save('./../img/captcha.png')
    img.close()
    return img


def generer_code(taille=6):
    return ''.join(random.choice('abcdefghijklmnopqrsxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(taille))

creer_captcha("123456", 400, 200)