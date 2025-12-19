"""
Starforge - A Python library for generating astronomical star charts.
- astronomy.py : 

Handles astronomical calculations using the Skyfield library.
Separates data loading from calculation to allow for better UI feedback.

Developed & maintained by Aditya Gaur (adityagaur.home@gmail.com) (@xdityagr)
Copyright Aditya Gaur, 2025. All rights reserved.
"""
from skyfield.api import load, Star, wgs84
from skyfield.data import hipparcos, stellarium
from skyfield.projections import build_stereographic_projection
import os

def load_astronomy_data(verbose=False):
    """
    Loads necessary astronomical files (Ephemeris, Catalogs).
    This handles downloading if files are missing.
    
    Args:
        verbose (bool): If False, we try to suppress Skyfield's progress bars.
                        (Note: Skyfield's load() function prints by default, 
                         so we can't fully silence it without redirecting stdout,
                         but we remove the invalid arg here to fix the crash.)
    
    Returns:
        tuple: (ts, eph, stars_df, constellations)
    """
    # 1. Timescale
    # builtin=True prevents downloading an updated Delta T file every run
    ts = load.timescale(builtin=True) 
    
    # 2. Planetary Ephemeris (de421.bsp)
    # The 'load' function does not accept 'verbose' as a direct argument in recent versions.
    # It prints progress bars if files are missing.
    eph = load('de421.bsp')
    
    # 3. Hipparcos Star Catalog
    with load.open(hipparcos.URL) as f:
        stars_df = hipparcos.load_dataframe(f)
        
    # 4. Constellation Lines
    url = ('https://raw.githubusercontent.com/Stellarium/stellarium/'
           'eb47095a9282cf6b981f6e37fe1ea3a3ae0fd167'
           '/skycultures/modern_st/constellationship.fab')
           
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
        
    return ts, eph, stars_df, constellations

def calculate_celestial_positions(lat_deg, lon_deg, dt_utc, magnitude_limit=6.0, data_cache=None):
    """
    Calculates star positions.
    
    Args:
        data_cache: Optional tuple of pre-loaded data (ts, eph, stars_df, constellations)
                    to avoid reloading/downloading inside this function.
    """
    # Unpack pre-loaded data or load it now (silently)
    if data_cache:
        ts, eph, stars_df, constellations = data_cache
    else:
        ts, eph, stars_df, constellations = load_astronomy_data(verbose=False)
    
    t = ts.from_datetime(dt_utc)
    earth = eph['earth']

    # Define the observer's location on Earth
    observer_location = earth + wgs84.latlon(latitude_degrees=lat_deg, longitude_degrees=lon_deg)
    observer = observer_location.at(t)

    # 4. Project *ALL* stars from the catalog
    all_stars = Star.from_dataframe(stars_df)
    astrometric = observer.observe(all_stars)
    alt, az, _ = astrometric.apparent().altaz()

    # 5. Define the projection (Zenith center)
    zenith_position = observer.from_altaz(alt_degrees=90, az_degrees=0)
    projection = build_stereographic_projection(zenith_position)

    # 6. Initial Pass: Get ALL visible stars and separate them
    # This prepares data for the filtering/decluttering phase
    star_hip_map = {} 
    constellation_stars_to_render = []
    background_stars_to_filter = []
    
    # Pre-calculate constellation HIP IDs for fast lookup
    constellation_star_ids = set()
    for _, lines in constellations:
        for start_hip, end_hip in lines:
            constellation_star_ids.add(start_hip)
            constellation_star_ids.add(end_hip)

    for i, star_alt in enumerate(alt.degrees):
        if star_alt > 0: # If visible above the horizon
            x, y = projection(astrometric[i])
            hip_id = stars_df.index[i]
            mag = stars_df['magnitude'].iloc[i]
            
            star_data = {
                'x': x, 'y': y, 'hip': hip_id, 'mag': mag,
            }
            
            if hip_id in constellation_star_ids:
                constellation_stars_to_render.append(star_data)
            else:
                background_stars_to_filter.append(star_data)

    # 7. Filter background stars by MAGNITUDE
    background_star_candidates = [
        s for s in background_stars_to_filter 
        if s['mag'] <= magnitude_limit
    ]
            
    # 8. Sort brightest first
    background_star_candidates.sort(key=lambda s: s['mag'])

    # 9. De-clutter background stars
    final_background_stars = []
    occupied_positions = [(s['x'], s['y']) for s in constellation_stars_to_render]
    min_dist_sq = 0.03**2 

    for candidate_star in background_star_candidates:
        x, y = candidate_star['x'], candidate_star['y']
        is_too_close = False
        
        for (occ_x, occ_y) in occupied_positions:
            dist_sq = (x - occ_x)**2 + (y - occ_y)**2
            if dist_sq < min_dist_sq:
                is_too_close = True
                break
        
        if not is_too_close:
            final_background_stars.append(candidate_star)
            occupied_positions.append((x, y))

    visible_stars = constellation_stars_to_render + final_background_stars
    
    return visible_stars, constellations