from captcha.image import ImageCaptcha
import random
import os

global_fonts = [os.path.join(os.getcwd(), 'fonts', 'arial.ttf'), os.path.join(os.getcwd(), 'fonts', 'cour.ttf'),
                os.path.join(os.getcwd(), 'fonts', 'times.ttf'),
                os.path.join(os.getcwd(), 'fonts', 'verdana.ttf')]

font_sizes = (80, 82, 84, 86, 88, 90)


def generer_image(code: str = "123456"):
    fonts = global_fonts
    image = ImageCaptcha(fonts=fonts, width=250, height=100, font_sizes=font_sizes)
    image.write(code, os.path.join(os.getcwd(), 'img', 'captcha.png'))


def generer_code(taille: int = 6):
    return ''.join(random.choice('abcdefghijklmnopqrsxyz0123456789') for _ in range(taille))
