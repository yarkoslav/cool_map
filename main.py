"""
This module provides the main.py function, which is the main
part of project
"""
from map_generator import creating_map


def main():
    """
    Running the hole project
    """
    year = input('Please enter a year you would like to have a map for: ')
    location=list(map(float, input('Please enter your location (format: lat, long): ').split(',')))
    creating_map(year, location)
    print('Finished. Please have look at the map cool_map.html')


if __name__ == "__main__":
    main()
