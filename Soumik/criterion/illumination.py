from skyfield.api import load, PlanetaryConstants
from datetime import datetime, timezone


def angular_difference_long(long1: float, long2: float) -> float:
    # Ensure longitudes are in the range [-180, 180]
    long1 = ((long1 + 180.0) % 360.0) - 180.0
    long2 = ((long2 + 180.0) % 360.0) - 180.0

    # Calculate the raw difference
    diff = abs(long1 - long2)

    # Adjust to get the smallest angular difference
    if diff > 180.0:
        diff = 360.0 - diff

    return diff


def angular_difference_lat(lat1: float, lat2: float) -> float:
    # Ensure latitudes are in the range [-90, 90]
    lat1 = max(min(lat1, 90.0), -90.0)
    lat2 = max(min(lat2, 90.0), -90.0)

    # Calculate the absolute difference
    diff = abs(lat1 - lat2)

    return diff


def get_subsolar_latitude_longitude(dt: datetime) -> tuple[float, float]:
    ts = load.timescale()

    # Load ephemeris data for the Sun and the Moon
    eph = load("de421.bsp")
    moon = eph["moon"]
    sun = eph["Sun"]

    pc = PlanetaryConstants()
    pc.read_text(load("moon_080317.tf"))
    pc.read_text(load("pck00008.tpc"))
    pc.read_binary(load("moon_pa_de421_1900-2050.bpc"))

    frame = pc.build_frame_named("MOON_ME_DE421")

    t = ts.utc(dt)
    p = moon.at(t).observe(sun).apparent()
    lat, long, distance = p.frame_latlon(frame)
    long_degrees = (long.degrees + 180.0) % 360.0 - 180.0

    return lat.degrees, long_degrees


def check_if_illuminated(lat: float, long: float, dt: datetime) -> bool:
    moon_lat, moon_long = get_subsolar_latitude_longitude(dt)

    if angular_difference_lat(moon_lat, lat) > 44.0:
        return False

    if angular_difference_long(moon_long, long) > 89.0:
        return False

    return True


if __name__ == "__main__":
    print(check_if_illuminated(1.0, 30.0, datetime.now(timezone.utc)))
