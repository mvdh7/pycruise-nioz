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
    """Convert longitude as a text string in various formats to
    a float of decimal degrees.
    """

    # Define all longitude formats
    lon_dmf = re.match("(\d+)°(\d+\.\d+)'([EW])", lon_text)
    lon_dmsf = re.match("(\d+)°(\d+)'(\d+)\"([EW])", lon_text)

    # Parse decimal minutes format --- longitude
    if lon_dmf:
        lon = float(lon_dmf.group(1)) + float(lon_dmf.group(2)) / 60
        if lon_dmf.group(3) == "W":
            lon *= -1

    # Parse degrees minutes seconds format --- longitude
    elif lon_dmsf:
        lon = (
            float(lon_dmsf.group(1))
            + float(lon_dmsf.group(2)) / 60
            + float(lon_dmsf.group(3)) / 3600
        )
        if lon_dmsf.group(4) == "W":
            lon *= -1

    # Parse decimal degrees format --- longitude
    else:
        lon = float(lon_text)

    return lon
