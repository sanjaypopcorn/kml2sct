# Made by Sanjay Singh (github.com/sanjaypopcorn)

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
            
            if name_tag is not None and description_tag is not None:
                description = description_tag.text
                name_tag.text = "COLOR_"+description
                placemark.remove(description_tag)

        
        tree.write("output.kml", encoding="utf-8", xml_declaration=True)

    except ET.ParseError as e:
        print("System phat gaya: ", e)

def splitter(kml_file):
    try:
        tree = ET.parse(kml_file)
        root = tree.getroot()

        ns = {'ns0': 'http://www.opengis.net/kml/2.2'}  # Define the namespace prefix

        for folder_name in ["SCT Entries", "Regions"]:
            # Find the specific folder
            folder = root.find(".//ns0:Folder[ns0:name='{}']".format(folder_name), ns)

            if folder is not None:
                # Create a TXT file to store the contents
                txt_filename = "{}.txt".format(folder_name)
                with open(txt_filename, 'w') as txt_file:

                    # Write relevant information to the TXT file
                    for ICAO_folder in folder.findall('.//ns0:Folder', ns):
                        folder_name_element = ICAO_folder.find('ns0:name', ns)
                        if folder_name_element is not None:
                            folder_name1 = folder_name_element.text.strip()
                            if len(folder_name1) == 4 and folder_name1.startswith("V") and folder_name1 not in ["VECF", "VIDF", "VABF", "VOMF"]:

                                airport_code = folder_name1
                                txt_file.write(f"{airport_code}\n")
                                for placemark in ICAO_folder.findall('.//ns0:Placemark', ns):
                                    
                                    name_tag = placemark.find('ns0:name', ns)
                                    description_tag = placemark.find('ns0:description', ns)
                                    coordinates = placemark.find('.//ns0:coordinates', ns).text.strip()
                  
                                    if name_tag is not None:
                                        txt_file.write("Name: {}\n".format(name_tag.text.strip()))
                                    if description_tag is not None:
                                        txt_file.write("Description: {}\n".format(description_tag.text.strip()))
                                    if coordinates is not None:
                                        txt_file.write(f"Coordinates: {coordinates}")
                                    txt_file.write("\n")  # Separate entries with a blank line

                                #####print("Contents of '{}' folder written to '{}'".format(folder_name, txt_filename))
            else:
                print("Folder '{}' not found in the KML file.".format(folder_name))

    except Exception as e:
        print("System Phat gya: ", e)

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
    with open("FREETEXT/FREETEXT.txt", "w") as output_file:
        tree = ET.parse(kml_file)
        root = tree.getroot()

        # Define the namespace prefix
        ns = {'ns0': 'http://www.opengis.net/kml/2.2'}

        # Find all folders with a 4-letter name that starts with "V"
        for folder in root.findall('.//ns0:Folder', ns):
            folder_name_element = folder.find('ns0:name', ns)
            if folder_name_element is not None:
                if folder_name_element.text.strip() == "Labels":
                    for folder in folder.findall('.//ns0:Folder', ns):
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

def GEO_converter(txt_file, out_txt):
    with open(txt_file, "r") as raw_geo, open(out_txt, "w") as parsed_geo:
        icao_code = ""
        for line in raw_geo:
            line = line.strip()

            if len(line) == 4:
                icao_code = line
                parsed_geo.write("\n"+icao_code + " ")
            elif line.startswith("Name:"):
                color_name = line.split(": ")[1]
            elif line.startswith("Coordinates:"):
                coordinates = line.replace("Coordinates: ", "").split()
                lat1, lon1 = map(float, coordinates[0].split(",")[:2])
                for i in range(len(coordinates) - 1):
                    lat2, lon2 = map(float, coordinates[i + 1].split(',')[:2])
                    lat1_str = convert_to_degrees_minutes_seconds(lon1, lat1)
                    lon1_str = convert_to_degrees_minutes_seconds(lon2, lat2)
                    parsed_geo.write(f"{lat1_str.replace(":"," ")} {lon1_str.replace(":"," ")} {color_name}\n")
                    lat1, lon1 = lat2, lon2 


def main():
    try:
        kml_file = sys.argv[1]
    except IndexError:
        sys.exit("Skill issue")

    init()   #IT WORKS DONT FORGET TO UNCOMMENT
    dekachra(kml_file)
    splitter("output.kml")
    # GEO A(lat, long) B(lat, long)_Color_definition
    # B(let, long) C(lat, long)_Color_definition
    GEO_converter("SCT Entries.txt", "GEO/GEO.txt")
    # POLYGONS 
    #   REGIONNAME VEBD GroundLayout
    #   COLOR_Building     N026.40.42.734 E088.19.53.362
    #   N026.40.41.944 E088.19.53.444
    #
    # FRETEXT Done
    extract_coordinates("output.kml")


if __name__ == "__main__":
    main()