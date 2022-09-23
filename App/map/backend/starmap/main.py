from astropy import units as u
from PIL import Image
from skyfield.api import N, W, wgs84
from skyfield.api import Star, load
from skyfield.data import hipparcos
import starmap_drawer

map_size_x = 1000
map_size_y = 1000
ts = load.timescale()
t = ts.now()
planets = load('de421.bsp')
earth = planets['earth']


def make_starmap(lat, lon, bortle_val):
    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)
    if bortle_val == 9:
        df = df[df['magnitude'] <= 1.65]  # Pleiades
        df = df[df['dec_degrees'] < 90]
        df = df[df['dec_degrees'] > 50]
    if bortle_val == 8:
        df = df[df['magnitude'] <= 3.0]  # M31
        df = df[df['dec_degrees'] < 90]
        df = df[df['dec_degrees'] > 50]
    if bortle_val == 6:
        df = df[df['magnitude'] <= 3.5]  # M31
    if bortle_val == 5:
        df = df[df['magnitude'] <= 8.5]  # Milky Way
    if bortle_val == 3:
        df = df[df['magnitude'] <= 10]  # M15
    if bortle_val == 2:
        df = df[df['magnitude'] <= 12]
    if bortle_val == 1:
        df = df[df['magnitude'] <= 15]
    choose_seenable_stars(lat, lon, df, bortle_val)
    # print(df.to_string())
    # print(df['magnitude'].to_string())
    starmap_drawer.print_map(bortle_val)
    return 0


def choose_seenable_stars(lat, lon, stars, bortle_val):
    sorted_array = []
    file = open("stars_to_process.txt", 'w')
    location = earth + wgs84.latlon(lat * N, lon * W)
    for i in range(0, len(stars) - 1):
        # print(stars.iat[i, 0])
        star = Star(ra_hours=stars.iat[i, 6], dec_degrees=stars.iat[i, 2])
        astrometric = location.at(t).observe(star)
        alt, az, d = astrometric.apparent().altaz()
        degree = alt.to(u.deg)
        azimuth = az.to(u.deg)
        if bortle_val == 9:
            if 50.0 * u.deg < degree < 90.0 * u.deg:
                sorted_array.append(star)
        if bortle_val == 8:
            if 50.0 * u.deg < degree < 90.0 * u.deg:
                sorted_array.append(star)
        if bortle_val == 6:
            if 35.0 * u.deg < degree < 90.0 * u.deg:
                sorted_array.append(star)
        if bortle_val == 5:
            if 20.0 * u.deg < degree < 90.0 * u.deg:
                sorted_array.append(star)
        if bortle_val == 3:
            if 10.0 * u.deg < degree < 90.0 * u.deg:
                sorted_array.append(star)
        if bortle_val == 2:
            if 10.0 * u.deg < degree < 90.0 * u.deg:
                sorted_array.append(star)
        if bortle_val == 1:
            if 10.0 * u.deg < degree < 90.0 * u.deg:
                sorted_array.append(star)
        # print('{:.8f}'.format(degree.degrees()))
        # print('{:.8f}'.format(az.degrees()))
        # print(degree)
        # print("{:.3}.".format(degree))
        # print('{:.2f}'.format(d.km))
        file.write("{:.3}.".format(degree))
        file.write('\n')
        file.write("{:.3}.".format(azimuth))
        file.write('\n')
        file.write('{:.2f}'.format(d.km))
        file.write('\n')
    file.close()
    return sorted_array


def on_bortle_scale(val):
    in_approximate_visible_magnitude = 6.5 * val + 0.5
    if in_approximate_visible_magnitude < 2:
        return 9
    if in_approximate_visible_magnitude < 4:
        return 8
    if in_approximate_visible_magnitude < 5:
        return 6
    if in_approximate_visible_magnitude < 5.8:
        return 5
    if in_approximate_visible_magnitude < 6.5:
        return 3
    if in_approximate_visible_magnitude < 6.7:
        return 2
    if in_approximate_visible_magnitude < 7:
        return 1
    print("bug in bortle scale")
    return -1


def create_circle_of_map(bortle_val):
    if bortle_val == 2:
        im = Image.new('RGB', (map_size_x, map_size_y), (0, 0, 200))
    im.save('draw-ellipse-rectangle-line.jpg', quality=95)
    return 0


make_starmap(54, 27, 6)