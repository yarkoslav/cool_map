"""
This module provide some functions to build cool map
"""
from math import sqrt, sin, cos, asin, pi
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable
import folium


def read_data(year: str) -> list:
    """
    Read data from locations.list file and return it as the list of tuples,
    where each tuple gas following appearance:
    (name_of_film, location)

    >>> len(read_data('2020'))
    103
    """
    films = []
    with open("locations.list", "r", encoding = 'latin-1') as file:
        contents = file.readlines()
        index = 14
        while index < len(contents) - 1:
            line = contents[index].strip().split('\t')
            num_bad_pos = line[0].find('{')
            if num_bad_pos != -1:
                line[0] = line[0][:num_bad_pos-1]
            film_year = line[0][-5:-1]
            name = line[0][:-6]
            count = 1
            while line[count] == '':
                count += 1
            location = line[count]
            index += 1
            if film_year == year:
                films.append((name, location))
            if len(films) >= 150:
                break
    return films


def distance(point1: list, point2: list) -> float:
    """
    Calculate the conventional distance between two points on sphere
    (so, we suppose that radius of sphere is equal to 1)

    >>> distance([0, 0], [0, 0])
    0.0
    >>> distance([0, 0], [0, 180])
    3.141592653589793
    """
    to_radian = lambda degree: (degree*pi)/180
    lat_1, long_1 = list(map(to_radian, point1))
    lat_2, long_2 = list(map(to_radian, point2))
    under_sqrt = sin((lat_2-lat_1)/2)**2 + cos(lat_1)*cos(lat_2)*(sin((long_2-long_1)/2)**2)
    dist = 2 * asin(sqrt(under_sqrt))
    return dist


def ten_nearest_films(films: list, location: list) -> list:
    """
    Return the list of ten nearest films to our location in appearance of list,
    where each component of list is tuple:
    (name_of_film, location_of_film)
    location_of_film is list with latitude and longitude

    >>> ten_nearest_films(read_data('2020'), [0.0, 0.0])
    [('Escape from Biafra ', [-1.3031689499999999, 36.826061224105075]),\
 ('Deceptive Exit ', [39.3260685, -4.8379791]), ('"The Nordic Odyssey" '\
, [48.8566969, 2.3514616]), ('If ', [48.1371079, 11.5753822]), ('Bread in\
 Heaven ', [36.9936175, 35.3258349]), ('Elzï¿½nak Szeretettel ', [46.1753793,\
 21.3196342]), ('Wild Thing ', [34.6401861, 39.0494106]), ('Elzï¿½nak\
 Szeretettel ', [47.48138955, 19.14607278448202]), ('Escape from Biafra ', \
[51.5073219, -0.1276474]), ('If ', [51.5073219, -0.1276474])]
    """
    new_appearance = []
    geolocator = Nominatim(user_agent="map_generator.py")
    for film in films:
        name, film_loc = film
        try:
            std_loc = geolocator.geocode(film_loc)
            if std_loc is not None:
                new_appearance.append((name, [std_loc.latitude, std_loc.longitude]))
        except GeocoderUnavailable:
            pass
    new_appearance.sort(key=lambda film: distance(film[1], location))
    return new_appearance[:10]


def creating_map(year: str, location: list):
    """
    Creates web map, on which we have 3 balls:
    first - default
    second - ten_nearest_films
    third - filling countries with different colors by population
    """
    mp = folium.Map(location=location)
    fg_tnf = folium.FeatureGroup(name="Ten nearest films")
    for film in ten_nearest_films(read_data(year), location):
        fg_tnf.add_child(folium.Marker(location=film[1],
                                       popup=film[0],
                                       icon=folium.Icon()))
    fg_pp = folium.FeatureGroup(name="The furthest film")
    fg_pp.add_child(folium.GeoJson(data=open('world.json', 'r',
                        encoding='utf-8-sig').read(),
                        style_function=lambda x: {'fillColor':'green'
        if x['properties']['POP2005'] < 10000000
        else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000
        else 'red'}))
    mp.add_child(fg_tnf)
    mp.add_child(fg_pp)
    mp.add_child(folium.LayerControl())
    mp.save('cool_map.html')
