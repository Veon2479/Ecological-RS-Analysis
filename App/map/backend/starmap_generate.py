from config import get_all_data
import os


# working with html page
def map_generate(lat, lon):
    # images_path = make_star_map(lat, lon)
    images_path = './map/static/starmap/img/'
    list_of_images = os.listdir(images_path)

    # Item template
    itcss_item = "<div class=\"itcss__item\"><img class=\"img-fluid\" src=\"{img_path}\" " \
                 "width=\"100%\" height=\"100%\" alt=\"Your advertisement could be here\"></div>\n"

    slider_items = "{% load static %}"

    # Generate template
    for img in list_of_images:
        slider_items += itcss_item.format(img_path="{% static '/starmap/img/" + img + "' %}")

    # Save template to the file
    f = open('./map/templates/starmap/slider_items.html', 'w')
    f.write(slider_items)
    f.close()

    return 0




# this method loads image with starmap template, changes and saves it and returns path to new map
# image would be in the /static/starmap folder, path is starting from the /starmap folder
def make_star_map(lat, lon):

    data = get_all_data(lat, lon, 5)

    return 0
