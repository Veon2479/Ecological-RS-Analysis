import math

from PIL import Image, ImageDraw

map_size_x = 1000
map_size_y = 1000


def print_map(bortle_val):
    r, g, b = 0, 0, 0
    if bortle_val == 1:
        r = 12
        g = 16
        b = 28
    if bortle_val == 2:
        r = 13
        g = 16
        b = 31
    if bortle_val == 3:
        r = 15
        g = 18
        b = 35
    if bortle_val == 5:
        r = 24
        g = 26
        b = 39
    if bortle_val == 6:
        r = 31
        g = 29
        b = 42
    if bortle_val == 8:
        r = 43
        g = 36
        b = 43
    if bortle_val == 9:
        r = 50
        g = 39
        b = 43
    im = Image.new('RGB', (map_size_x, map_size_y), (r, g, b))
    draw = ImageDraw.Draw(im)
    file = open("stars_to_process.txt", 'r')
    line = file.readline()
    while len(line) != 0:
        if line[1] != 'e':
            if line[2] != 'e':
                if line[3] != 'e':
                    if line[4] != 'e':
                        phi = float(line[0:4])
                    else:
                        phi = float(line[0:3])
                else:
                    phi = float(line[0:2])
            else:
                phi = float(line[0:1])
        else:
            phi = float(line[0:1])
        line = file.readline()
        if line[1] != 'e':
            if line[2] != 'e':
                if line[3] != 'e':
                    psi = float(line[0:3])
                else:
                    psi = float(line[0:3])
            else:
                psi = float(line[0:2])
        else:
            psi = float(line[0:1])
        line = file.readline()
        r = float(line[15:22])
        line = file.readline()
        x = ((r * math.sin(90 - phi) * math.cos(psi)) / 7000) + 600
        y = ((r * math.sin(90 - phi) * math.sin(psi)) / 7000) + 600
        # print(x)
        # print(y)
        if math.sqrt((x-500) * (x-500) + (y-500) * (y-500)) < 500:
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill='white', outline=(0, 0, 0))

    file.close()
    draw.ellipse((0, 0, 999, 999))
    im.save('draw-ellipse-rectangle-line.jpg', quality=95)
    return 0
