from PIL import Image

im_rgb = Image.open('abomination.webp')

im_rgba = im_rgb.copy()
im_rgba.putalpha(50)
im_rgba.save('t_abomination.webp')