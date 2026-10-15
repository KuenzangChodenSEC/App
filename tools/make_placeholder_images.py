"""
make_placeholder_images.py - creates one illustrated landscape picture per place.

These are only STAND-INS so every place looks different until you add real
photos. To use a real photo, save it as  assets/places/<slug>.jpg  (replace the
placeholder). For extra photos on the details page use <slug>_2.jpg and
<slug>_3.jpg.

Run from the project folder:   python tools/make_placeholder_images.py
(Existing files are never overwritten unless you pass --force.)
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.places_data import PLACES, slugify   # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'places')
SIZE = (1200, 675)

# (sky top, sky bottom, ridge colours from far to near) for each category.
THEMES = {
    'Nature & Hiking': ((120, 180, 215), (225, 240, 230), [(120, 160, 150), (70, 125, 95), (35, 90, 60)]),
    'Cultural Sites':  ((235, 160, 110), (250, 225, 175), [(150, 120, 120), (105, 85, 85), (60, 50, 55)]),
    'Mountains':       ((90, 130, 190), (205, 225, 245), [(170, 185, 210), (110, 130, 165), (60, 75, 105)]),
    'Cities':          ((150, 190, 225), (245, 235, 210), [(150, 165, 150), (100, 130, 105), (60, 95, 70)]),
}


def blend(a, b, t):
    """Mix two RGB colours (t = 0 gives a, t = 1 gives b)."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_ridge(draw, rng, colour, base_y, amplitude):
    """Draw one jagged mountain ridge filled down to the bottom of the picture."""
    width, height = SIZE
    points = [(0, height)]
    x, y = 0, base_y
    while x <= width + 80:
        points.append((x, y))
        x += rng.randint(60, 140)
        y = base_y + rng.randint(-amplitude, amplitude)
    points.append((width, height))
    draw.polygon(points, fill=colour)


def make_picture(place, path):
    """Create and save the placeholder for a single place."""
    rng = random.Random(place['name'])               # same place -> same picture every time
    sky_top, sky_bottom, ridges = THEMES.get(place['type'], THEMES['Nature & Hiking'])
    image = Image.new('RGB', SIZE)
    draw = ImageDraw.Draw(image)

    for y in range(SIZE[1]):                          # sky gradient
        draw.line([(0, y), (SIZE[0], y)], fill=blend(sky_top, sky_bottom, y / SIZE[1]))
    sun_x, sun_y = rng.randint(200, 1000), rng.randint(110, 230)   # soft sun
    draw.ellipse([sun_x - 60, sun_y - 60, sun_x + 60, sun_y + 60], fill=(255, 245, 220))

    for index, colour in enumerate(ridges):           # three layered ridges
        draw_ridge(draw, rng, colour, 330 + index * 100, 70 - index * 12)

    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    try:
        title_font = ImageFont.truetype(font_path, 54)
        small_font = ImageFont.truetype(font_path, 28)
    except OSError:
        title_font = small_font = ImageFont.load_default()
    draw.text((50, SIZE[1] - 120), place['name'], font=title_font, fill='white')
    draw.text((52, SIZE[1] - 55), place['location'] + ', Bhutan', font=small_font, fill=(235, 245, 238))
    image.save(path, quality=88)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    force = '--force' in sys.argv
    for place in PLACES:
        path = os.path.join(OUT_DIR, slugify(place['name']) + '.jpg')
        if os.path.exists(path) and not force:
            print('keep   ', os.path.basename(path))
            continue
        make_picture(place, path)
        print('created', os.path.basename(path))


if __name__ == '__main__':
    main()
