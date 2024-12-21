from captcha.image import ImageCaptcha
import random
import os

global_fonts = [os.path.join(os.getcwd(), 'fonts', 'arial.ttf'), os.path.join(os.getcwd(), 'fonts', 'cour.ttf'),
             os.path.join(os.getcwd(), 'fonts', 'times.ttf'),
             os.path.join(os.getcwd(), 'fonts', 'verdana.ttf')]

def generer_image(code = "123456"):
    fonts = global_fonts
    image = ImageCaptcha(fonts=fonts)
    image.write(code,os.path.join(os.getcwd(),'img','captcha.png'))

def generer_code(taille=6):
    return ''.join(random.choice('abcdefghijklmnopqrsxyz0123456789') for _ in range(taille))
