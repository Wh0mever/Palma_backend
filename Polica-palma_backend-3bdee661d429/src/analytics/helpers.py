import random

COLORS = [
    '#FF6384',
    '#F4CA16',
    '#004242',
    '#50C878',
    '#CC397B',
    '#9457EB',
    '#318CE7',
    '#E7201D',
    '#36E7DB',
    '#E782AF',
    '#65E736',
    '#E76400',
    '#89E7C3',
]


def generate_random_rgb():
    min = 0
    max = 255
    red = random.randint(min, max)
    green = random.randint(min, max)
    blue = random.randint(min, max)
    return red, green, blue


def get_random_background_color():
    r, g, b = generate_random_rgb()
    return f"rgba({r}, {g}, {b}, 0.2)"


def get_random_border_color():
    r, g, b = generate_random_rgb()
    return f"rgba({r}, {g}, {b}, 1)"
