import numpy as np

from map.backend.config import get_all_data
from map.backend.meteodata import get_param
# from vec3 import Vec3
# from helper import Ray, Atmosphere
import cv2

# atmosphere = Atmosphere()


def generate_overlay(radius_px, lat, lon, radius_search):
    # data = get_all_data(lat, lon, radius_search)
    # origin = Vec3(0., atmosphere.radiusEarth + 1., 0.)

    # this is temp data!!!
    data = dict.fromkeys(['night_overview', 'fog', 'dust', 'cloudtop'])
    data['night_overview'] = np.array([1.0, 0.95, 0.9, 0.7, 0.3, 0.15, 0.1])
    data['fog'] = np.array([0.0])
    data['dust'] = np.array([[1.0, 1.0, 0.7, 0.5],
                             [0.9, 0.8, 0.4, 0.1],
                             [0.5, 0.6, 0.4, 0.1],
                             [0.5, 0.8, 0.1, 0.2]])
    data['cloudtop'] = np.array([0.0])

    # this is data interpolation for whole view
    # todo replace INTER_LINEAR to INTER_CUBIC when amount of data more than 4 for each axis
    light = cv2.resize(data['night_overview'],
               dsize=(radius_px, radius_px),
               interpolation=cv2.INTER_LINEAR)
    fog = cv2.resize(data['fog'],
                       dsize=(radius_px, radius_px),
                       interpolation=cv2.INTER_LINEAR)
    dust = cv2.resize(data['dust'],
                     dsize=(radius_px, radius_px),
                     interpolation=cv2.INTER_CUBIC)
    cloudtop = cv2.resize(data['cloudtop'],
                     dsize=(radius_px, radius_px),
                     interpolation=cv2.INTER_LINEAR)

    blank_image = np.zeros((radius_px, radius_px, 3), np.uint8)

    for j in np.arange(radius_px):
        y = (j + 0.5) * 2. / (radius_px - 1.) - 1.  # generate cords in the cartesian sys

        for i in np.arange(radius_px):
            x = (i + 0.5) * 2. / (radius_px - 1.) - 1.
            z2 = x * x + y * y

            if z2 <= 1.:
                # phi = np.arctan2(y, x) + 90  # convert cords to cylindrical
                # theta = np.arccos(1. - z2)

                transparency = 0.995 - (fog[i, j] + dust[i, j] + cloudtop[i, j]) / 4

                # how the stars are obscured?
                rel_atm_density = 1 / (1. - z2)
                v = 1 - pow(transparency, rel_atm_density)
                # M is proportional rel_atm_density
                # pixel color lost is proportional to v
                # pixel lightness (yelowness) proportional to light[i, j] * v

                value = 255. * v
                value_b = value * (1. - light[i, j]*0.8)

                blank_image[j, i] = [value_b, value, value]

                # variant 2
                # vr = (1 - pow(1 - 0.12, rel_atm_density)) * 255
                # vg = (1 - pow(1 - 0.20, rel_atm_density)) * 255
                # vb = (1 - pow(1 - 0.7, rel_atm_density)) * 255
                #
                # blank_image[j, i] = [vb, vg, vr]

                # direction = Vec3(np.sin(theta) * np.cos(phi),
                #                  np.cos(theta),
                #                  np.sin(theta) * np.sin(phi))

                # ray = Ray(origin, direction)
                # flux = atmosphere.compute_incident_light(ray)
    cv2.imwrite('test.tif', blank_image)


if __name__ == '__main__':
    # get_param('night_overview')
    # get_param('fog')
    # get_param('dust')
    # get_param('cloudtop')

    print('got data')

    generate_overlay(100, 52.441176, 30.987846, 4)
