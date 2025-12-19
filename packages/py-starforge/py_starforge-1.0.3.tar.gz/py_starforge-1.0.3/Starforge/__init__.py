"""
Starforge - A Python library for generating astronomical star charts.

Usage (New - Recommended):
    from Starforge import StarForge

    # Simple usage
    StarForge("Paris").render("paris_sky.svg")

    # With fluent configuration
    (StarForge("Tokyo")
        .at_date("2024-06-15")
        .with_fov(60)
        .with_magnitude_limit(5.0)
        .without_labels()
        .render("tokyo_sky.svg"))

Usage (Legacy - Still Supported):
    from Starforge import create_starmap

    # Using a city name
    create_starmap("Paris", "paris_sky.svg")

    # Using coordinates
    create_starmap("28.61, 77.20", "delhi_sky.svg")


Developed & maintained by Aditya Gaur (adityagaur.home@gmail.com) (@xdityagr)
Copyright Aditya Gaur, 2025. All rights reserved.

"""

from datetime import datetime
import pytz, os
from .astronomy import calculate_celestial_positions, load_astronomy_data
from .renderer import render_svg_chart, Config
from .utils import resolve_location
from colorama import Fore, Back, Style
from .utils import resolve_location, Spinner, Log, LogLevel
from .core import StarForge

# Public API exports
__all__ = [
    'StarForge',       # New unified class (recommended)
    'create_starmap',  # Legacy function (backward compatible)
    'Config',          # Configuration dataclass
    'Log',             # Logging utility
    'LogLevel',        # Log level constants (DEBUG, INFO, WARNING, ERROR, SILENT)
    'Spinner',         # Progress spinner utility
]


# =========================
def print_banner(version="v1.0"):
    text = """
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⠤⢤⣀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠐⣿⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠴⠒⢋⣉⣀⣠⣄⣀⣈⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠄⠀⠀⠀⠀⠀⠀⠀⠀⣸⡆⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⣠⣴⣾⣯⠴⠚⠉⠉⠀⠀⠀⠀⣤⠏⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⣄⠀⠀⠀⠀⠀⠀⡿⡇⠁⠀⠀⠀⠀⠀⠀⠀⡀⠂⠀⠀⠀⠀⣠⣴⡿⠿⢛⠁⠁⣸⠀⠀⠀⠀⠀⣤⣾⠵⠚⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⢄⠀⠀⣠⠀⡇⢧⠀⠀⠀⠀⠀⠀⠖⠁⠀⠀⠀⣠⣴⠿⠋⠁⠀⠀⠀⠀⠘⣿⠀⣀⡠⠞⠛⠁⠂⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡈⣻⡦⣞⡿⣷⠸⣄⣠⢶⡟⠁⠀⠀⠀⣀⣴⠟⠋⠁⠀⠀⠀⠀⠐⠠⡤⣾⣙⣶⡶⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣂⡷⠰⣔⣾⣖⣾⡷⢿⣀⣀⣀⣤⢾⣋⠁⠀⠀⠀⣀⢀⣀⣀⣀⣀⠀⢀⢿⠑⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠠⡦⠴⠴⠤⠦⠤⠤⠤⠤⠤⠴⠶⢾⣽⣙⠒⢺⣿⣿⣿⣿⢾⠶⣧⡼⢏⠑⠚⠋⠉⠉⡉⡉⠉⠉⠹⠈⠁⠉⠀⠨⢾⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠀⠀⠀⠂⠐⠀⠀⠀⠈⣇⡿⢯⢻⣟⣇⣷⣞⡛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⣆⠀⠀⠀⠀⢠⡷⡛⣛⣼⣿⠟⢙⣧⠇⡄⠀⠀⠀⠀⠀⠀⠰⡆⠀⠀⠀⠀⢠⣾⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⢶⠏⠉⠀⠀⠀⠀⠀⠿⢠⣴⡟⡗⡾⡒⡿⠯⢏⡅⠀⠀⠀⠀⣀⢀⣠⣧⣀⣀⠀⠀⠀⠚⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣠⢴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⣠⣷⢿⣫⡽⡿⠿⠗⢷⠀⠀⠑⣗⡀⠀⠀⠀⠈⠙⣿⢭⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⡴⢏⡵⠛⠀⠀⠀⠀⠀⠀⠀⣀⣴⠞⠛⠀⠰⡟⣿⠀⡌⠀⠀⠀⠀⠀⠀⠁⠢⡀⠀⠀⠂⢿⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣀⣼⠛⣲⡏⠁⠀⠀⠀⠀⠀⢀⣠⡾⠋⠉⠀⠀⠀⠀⣧⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠣⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⡴⠟⠀⢰⡯⠄⠀⠀⠀⠀⣠⢴⠟⠉⠀⠀⠀⠀⠀⠀⠀⠘⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⡾⠁⠁⠀⠘⠧⠤⢤⣤⠶⠏⠙⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠘⣇⠂⢀⣀⣀⠤⠞⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

                ┏┓     ┏┓        
                ┗┓╋┏┓┏┓┣ ┏┓┏┓┏┓┏┓
                ┗┛┗┗┻┛ ┻ ┗┛┛ ┗┫┗ 
                              ┛  
    """

    subtitle = "         𝑃𝑜𝑤𝑒𝑟𝑒𝑑 𝑏𝑦 𝑇ℎ𝑒 𝑆𝑡𝑎𝑟𝐹𝑜𝑟𝑔𝑒 𝐸𝑛𝑔𝑖𝑛𝑒"

    # Simple gradient shades:
    gradient = [
        Fore.LIGHTWHITE_EX,
        Fore.LIGHTCYAN_EX,
        Fore.CYAN,
        Fore.BLUE,
    ]

    # Build gradient text
    colored_text = ""
    for i, ch in enumerate(text):
        colored_text += gradient[i % len(gradient)] + ch

    print("\n" + colored_text + Style.RESET_ALL)

    print(Fore.LIGHTGREEN_EX + subtitle + Style.RESET_ALL)
    print(Fore.LIGHTBLACK_EX + f"                 Version: {version}\n" + Style.RESET_ALL)
    print()


def create_starmap(
    location: str,
    output_filename: str,
    dt_utc = None, # Can be datetime OR str
    magnitude_limit: float = 6.0,
    fov_radius_deg: float = 90.0,
    show_labels: bool = True,
    style_config: Config = None
):
    """
    Generates a star chart SVG for a specific location and time.

    Args:
        location (str): City name (e.g., "Tokyo") or "Lat, Lon" string.
        output_filename (str): Output file path (e.g., "chart.svg").
        dt_utc (datetime, optional): Time of observation (UTC). Defaults to now.
        magnitude_limit (float): Faintest visible star magnitude. Lower = fewer stars.
        fov_radius_deg (float): Field of view radius. 90 = full hemisphere.
        show_labels (bool): Toggle constellation labels.
        style_config (Config, optional): Custom styling configuration.
    """
    
    # 1. Resolve Location
    try:
        with Spinner("Resolving location"):
            lat, lon, place_name = resolve_location(location)
        Log.info(f"Location resolved: {place_name} ({lat:.4f}, {lon:.4f})")
    except ValueError as e:
        Log.error(str(e))
        return

    # 2. Handle Defaults
    if dt_utc is None:
        dt_utc = datetime.now(pytz.utc)
    elif isinstance(dt_utc, str):
        dt_str = dt_utc.strip()
        parsed = False
        
        # Expanded list of formats to support DD/MM/YYYY, YY, dashes, slashes, etc.
        formats = [
            # Standard ISO-like
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            
            # Day-Month-Year (Dashes)
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y",
            "%d-%m-%y",       # Short year (e.g. 24-06-07)
            "%d-%m-%y %H:%M", 
            
            # Day/Month/Year (Slashes)
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%d/%m/%y",       # Short year (e.g. 24/06/07)
            "%d/%m/%y %H:%M",

            # Month/Day/Year (US style common fallback, though dangerous with ambiguous dates)
            "%m/%d/%Y",
            
            # Dot notation
            "%d.%m.%Y",
            "%d.%m.%y"
        ]
        
        for fmt in formats:
            try:
                dt_utc = datetime.strptime(dt_str, fmt)
                parsed = True
                # If we parsed a short year (e.g. '07'), Python might map 00-68 to 2000-2068
                # This is usually standard behavior, so we leave it.
                break
            except ValueError:
                continue
        
        if not parsed:
            Log.warning(f"Could not parse date string '{dt_utc}'. Using current time.")
            dt_utc = datetime.now(pytz.utc)

    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=pytz.utc)
    else:
        dt_utc = dt_utc.astimezone(pytz.utc)


    if style_config is None:
        # Default nice styling
        style_config = Config()
        style_config.star_color = "#FFFFFF"
        style_config.background_color = "#050505" # Deep black/grey
        style_config.constellation_line_color = "#FFFFFF"
        style_config.constellation_line_width = 1.0
        style_config.show_labels = show_labels
        style_config.fov_radius_deg = fov_radius_deg

    # 3. Load Data & Calculate
    # We remove the 'verbose' flag as it causes issues in some Skyfield versions
    data_exists = os.path.exists('de421.bsp')
    msg = "Verifying/Downloading astronomical data" if not data_exists else "Loading astronomical data"
    
    astronomy_data = None
    with Spinner(msg):
        astronomy_data = load_astronomy_data(verbose=False)
    
    Log.info(f"Computing sky for {dt_utc.strftime('%Y-%m-%d %H:%M UTC')}...")
    
    visible_stars = []
    constellations = []
    
    with Spinner("Calculating star positions"):
        visible_stars, constellations = calculate_celestial_positions(
            lat, lon, dt_utc, magnitude_limit, data_cache=astronomy_data
        )

    # 4. Render
    if not visible_stars:
        Log.warning("No stars found. Is the sky covered or magnitude too low?")
    else:
        Log.info(f"Visible stars: {len(visible_stars)} | Constellations: {len(constellations)}")
        
    Log.info(f"Rendering chart to {output_filename}...")
    render_svg_chart(visible_stars, constellations, output_filename, config=style_config)
    Log.success(f"Saved to {output_filename}")


print_banner(version="1.0.0")