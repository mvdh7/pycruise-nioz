import re

# Convert latitude ....
def parse_latitude_text(lat_text):
    """Convert latitude as a text string in various formats to
    a float of decimal degrees.
    """

    # Define all latitude formats
    lat_dmf = re.match("(\d+)°(\d+\.\d+)'([NS])", lat_text)
    lat_dmsf = re.match("(\d+)°(\d+)'(\d+)\"([NS])", lat_text)

    # Parse decimal minutes format --- latitude
    if lat_dmf:
        lat = float(lat_dmf.group(1)) + float(lat_dmf.group(2)) / 60
        if lat_dmf.group(3) == "S":
            lat *= -1

    # Parse degrees minutes seconds format --- latitude
    elif lat_dmsf:
        lat = (
            float(lat_dmsf.group(1))
            + float(lat_dmsf.group(2)) / 60
            + float(lat_dmsf.group(3)) / 3600
        )
        if lat_dmsf.group(4) == "S":
            lat *= -1

    # Parse decimal degrees format --- latitude
    else:
        lat = float(lat_text)
        
    return lat


def parse_longitude_text(lon_text):
    
    try:
        lon = float(lon_text)
    except:
        lon = None
        
    return lon
    
    
