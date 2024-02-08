import xml.etree.ElementTree as ET
from math import floor
import os
import sys

def init():
    folder_paths = ["POLY", "GEO", "FREETEXT"]
    for folder_path in folder_paths:
        # Check if the folder exists
        if os.path.exists(folder_path):
            # If the folder exists, empty it
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
        else:
            os.makedirs(folder_path)

def dekachra(kml_file):
    try:
        tree = ET.parse(kml_file)
        root = tree.getroot()

        ns = {'ns0': 'http://www.opengis.net/kml/2.2'}  # Define the namespace prefix

        for placemark in root.findall('.//ns0:Placemark', ns):  # Use namespace prefix in XPath
            name_tag = placemark.find('ns0:name', ns)  # Use namespace prefix
            description_tag = placemark.find('ns0:description', ns)  # Use namespace prefix
            styleUrl_tag = placemark.find('ns0:styleUrl', ns)
            
            if name_tag is not None and description_tag is not None:
                description = description_tag.text
                color = styleUrl_tag.text
                name_tag.text = "COLOR_"+description
                placemark.remove(description_tag)

        
        tree.write("output.kml", encoding="utf-8", xml_declaration=True)

    except ET.ParseError as e:
        print("System phat gaya: ", e)

def splitter(kml_file):
    s

def convert_to_degrees_minutes_seconds(latitude, longitude):
    def convert_to_degrees(value, is_longitude=False):
        direction = 'E' if is_longitude else 'N' if value >= 0 else 'S'
        value = abs(value)
        degrees = int(value)
        value = (value - degrees) * 60
        minutes = int(value)
        seconds = (value - minutes) * 60
        return f"{direction}{degrees:03}.{minutes:02}.{seconds:06.3f}"

    latitude_str = convert_to_degrees(latitude)
    longitude_str = convert_to_degrees(longitude, is_longitude=True)
    return f"{latitude_str}:{longitude_str}"

def extract_coordinates(kml_file):
    with open("FREETEXT.txt", "w") as output_file:
        tree = ET.parse(kml_file)
        root = tree.getroot()

        # Define the namespace prefix
        ns = {'ns0': 'http://www.opengis.net/kml/2.2'}

        # Find all folders with a 4-letter name that starts with "V"
        for folder in root.findall('.//ns0:Folder', ns):
            folder_name_element = folder.find('ns0:name', ns)
            if folder_name_element is not None:
                folder_name = folder_name_element.text.strip()
                if len(folder_name) == 4 and folder_name.startswith("V"):
                    airport_code = folder_name

                    # Find all placemarks within this folder
                    for placemark in folder.findall('.//ns0:Placemark', ns):
                        placemark_name = placemark.find('ns0:name', ns).text
                        coordinates = placemark.find('.//ns0:coordinates', ns).text.strip()

                        # Extract latitude, longitude, and altitude from coordinates
                        longitude, latitude, altitude = map(float, coordinates.split(','))

                        ese_coords = convert_to_degrees_minutes_seconds(latitude, longitude)
                        output_file.write(f"{ese_coords}:{airport_code}:{placemark_name}\n")






def main():
    try:
        kml_file = sys.argv[1]
    except IndexError:
        sys.exit("Skill issue")

    dekachra(kml_file)
    # GEO
    # POLYGONS
    # FRETEXT
    #init()   #IT WORKS DONT FORGET TO UNCOMMENT


if __name__ == "__main__":
    main()