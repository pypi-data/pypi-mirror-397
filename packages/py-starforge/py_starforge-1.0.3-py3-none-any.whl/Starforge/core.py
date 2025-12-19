"""
StarForge - Unified class for generating astronomical star charts.

This module provides a single, intuitive interface for creating star charts
by orchestrating location resolution, astronomical calculations, and SVG rendering.

Example:
    from Starforge import StarForge

    # Simple usage
    StarForge("Paris").render("paris_sky.svg")

    # With configuration
    (StarForge("Tokyo")
        .at_date("2024-06-15")
        .with_fov(60)
        .with_magnitude_limit(5.0)
        .without_labels()
        .render("tokyo_sky.svg"))

Developed & maintained by Aditya Gaur (adityagaur.home@gmail.com) (@xdityagr)
Copyright Aditya Gaur, 2025. All rights reserved.
"""

from datetime import datetime
from typing import Optional, Union, Tuple, List, Dict, Any
import pytz
import os

from .astronomy import calculate_celestial_positions, load_astronomy_data
from .renderer import SVGChart, Config
from .utils import resolve_location, Spinner, Log


class StarForge:
    """
    A unified interface for generating astronomical star charts.

    StarForge orchestrates all functionality needed to create beautiful,
    accurate star charts: location resolution, astronomical calculations,
    and SVG rendering.

    Attributes:
        location (str): The observation location (city name or "lat, lon").
        latitude (float): Resolved latitude in degrees.
        longitude (float): Resolved longitude in degrees.
        place_name (str): Human-readable location name.
        config (Config): Chart styling configuration.

    Example:
        # Basic usage
        chart = StarForge("New York")
        chart.render("nyc_sky.svg")

        # Fluent API
        (StarForge("London")
            .at_date("2024-12-25 23:00")
            .with_fov(45)
            .with_circular_mask()
            .render("london_christmas.svg"))
    """

    def __init__(self, location: str, verbose: bool = True):
        """
        Initialize StarForge with an observation location.

        Args:
            location: City name (e.g., "Paris") or coordinates as "lat, lon".
            verbose: If True, display progress messages. Default True.
        """
        self._location_query = location
        self._verbose = verbose

        # Location data (resolved lazily or immediately)
        self._latitude: Optional[float] = None
        self._longitude: Optional[float] = None
        self._place_name: Optional[str] = None
        self._location_resolved = False

        # Observation time
        self._datetime: Optional[datetime] = None

        # Astronomical data cache
        self._astronomy_data = None
        self._astronomy_loaded = False

        # Calculation results
        self._visible_stars: List[Dict] = []
        self._constellations: List[Tuple] = []
        self._calculated = False

        # Configuration
        self._config = Config()
        self._magnitude_limit = 6.0
        self._fov_radius_deg = 90.0
        self._show_labels = True

        # Resolve location immediately if verbose (shows spinner)
        if verbose:
            self._resolve_location()

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def location(self) -> str:
        """The original location query string."""
        return self._location_query

    @property
    def latitude(self) -> float:
        """Latitude in degrees. Resolves location if needed."""
        if not self._location_resolved:
            self._resolve_location()
        return self._latitude

    @property
    def longitude(self) -> float:
        """Longitude in degrees. Resolves location if needed."""
        if not self._location_resolved:
            self._resolve_location()
        return self._longitude

    @property
    def place_name(self) -> str:
        """Human-readable place name. Resolves location if needed."""
        if not self._location_resolved:
            self._resolve_location()
        return self._place_name

    @property
    def observation_time(self) -> datetime:
        """The observation datetime in UTC."""
        if self._datetime is None:
            return datetime.now(pytz.utc)
        return self._datetime

    @property
    def config(self) -> Config:
        """Access the chart configuration directly."""
        return self._config

    @property
    def visible_stars(self) -> List[Dict]:
        """List of visible stars after calculation."""
        return self._visible_stars

    @property
    def constellations(self) -> List[Tuple]:
        """List of constellation data after calculation."""
        return self._constellations

    # =========================================================================
    # Location Configuration
    # =========================================================================

    def at_location(self, location: str) -> 'StarForge':
        """
        Change the observation location.

        Args:
            location: City name or "lat, lon" coordinates.

        Returns:
            Self for method chaining.
        """
        self._location_query = location
        self._location_resolved = False
        self._calculated = False
        return self

    def at_coordinates(self, latitude: float, longitude: float, name: str = None) -> 'StarForge':
        """
        Set observation location using explicit coordinates.

        Args:
            latitude: Latitude in degrees (-90 to 90).
            longitude: Longitude in degrees (-180 to 180).
            name: Optional place name for display.

        Returns:
            Self for method chaining.
        """
        self._latitude = latitude
        self._longitude = longitude
        self._place_name = name or f"Coordinates {latitude:.4f}, {longitude:.4f}"
        self._location_resolved = True
        self._calculated = False
        return self

    # =========================================================================
    # Time Configuration
    # =========================================================================

    def at_date(self, dt: Union[str, datetime]) -> 'StarForge':
        """
        Set the observation date and time.

        Args:
            dt: Date as string (various formats supported) or datetime object.
                Supported formats: "YYYY-MM-DD", "DD/MM/YYYY", "DD-MM-YYYY",
                with optional time "HH:MM:SS" or "HH:MM".

        Returns:
            Self for method chaining.

        Example:
            chart.at_date("2024-06-15")
            chart.at_date("15/06/2024 22:30")
            chart.at_date(datetime(2024, 6, 15, 22, 30))
        """
        if isinstance(dt, datetime):
            self._datetime = self._ensure_utc(dt)
        else:
            self._datetime = self._parse_date_string(dt)
        self._calculated = False
        return self

    def at_datetime(self, dt: datetime) -> 'StarForge':
        """
        Set observation time using a datetime object.

        Args:
            dt: A datetime object (timezone-aware or naive UTC assumed).

        Returns:
            Self for method chaining.
        """
        self._datetime = self._ensure_utc(dt)
        self._calculated = False
        return self

    def now(self) -> 'StarForge':
        """
        Set observation time to the current moment.

        Returns:
            Self for method chaining.
        """
        self._datetime = datetime.now(pytz.utc)
        self._calculated = False
        return self

    # =========================================================================
    # Chart Configuration (Fluent API)
    # =========================================================================

    def with_fov(self, degrees: float) -> 'StarForge':
        """
        Set the field of view radius.

        Args:
            degrees: FOV radius in degrees. 90 = full hemisphere.
                    Smaller values zoom in on the zenith.

        Returns:
            Self for method chaining.
        """
        self._fov_radius_deg = degrees
        self._config.fov_radius_deg = degrees
        return self

    def with_magnitude_limit(self, magnitude: float) -> 'StarForge':
        """
        Set the magnitude limit for background stars.

        Args:
            magnitude: Limiting magnitude. Lower = fewer, brighter stars only.
                      Typical values: 4.0 (bright only) to 6.5 (many stars).

        Returns:
            Self for method chaining.
        """
        self._magnitude_limit = magnitude
        self._calculated = False
        return self

    def with_labels(self, show: bool = True) -> 'StarForge':
        """
        Enable or disable constellation labels.

        Args:
            show: True to show labels, False to hide.

        Returns:
            Self for method chaining.
        """
        self._show_labels = show
        self._config.show_labels = show
        return self

    def without_labels(self) -> 'StarForge':
        """
        Disable constellation labels.

        Returns:
            Self for method chaining.
        """
        return self.with_labels(False)

    def with_circular_mask(self, enabled: bool = True) -> 'StarForge':
        """
        Enable or disable circular masking of the chart.

        Args:
            enabled: True to clip chart to a circle, False for rectangular.

        Returns:
            Self for method chaining.
        """
        self._config.circular_mask = enabled
        return self

    def with_sphere_effect(self, enabled: bool = True, strength: float = 0.6) -> 'StarForge':
        """
        Enable globe/sphere projection effect.

        Args:
            enabled: True to enable sphere distortion.
            strength: Distortion strength (0.0 to 1.0).

        Returns:
            Self for method chaining.
        """
        self._config.sphere_effect = enabled
        self._config.sphere_distortion_strength = strength
        return self

    def with_size(self, width: int, height: int = None) -> 'StarForge':
        """
        Set the chart dimensions in pixels.

        Args:
            width: Width in pixels.
            height: Height in pixels. If None, uses width (square).

        Returns:
            Self for method chaining.
        """
        self._config.width_px = width
        self._config.height_px = height or width
        return self

    def with_colors(
        self,
        background: str = None,
        stars: str = None,
        lines: str = None,
        labels: str = None,
        border: str = None
    ) -> 'StarForge':
        """
        Configure chart colors.

        Args:
            background: Background color (e.g., "#000000" or "black").
            stars: Star fill color.
            lines: Constellation line color.
            labels: Label text color.
            border: Border stroke color.

        Returns:
            Self for method chaining.
        """
        if background is not None:
            self._config.background_color = background
        if stars is not None:
            self._config.star_color = stars
        if lines is not None:
            self._config.constellation_line_color = lines
        if labels is not None:
            self._config.label_color = labels
        if border is not None:
            self._config.border_color = border
        return self

    def with_star_sizes(
        self,
        constellation: float = None,
        background: float = None
    ) -> 'StarForge':
        """
        Configure star icon sizes.

        Args:
            constellation: Size of constellation stars (default 14.0).
            background: Size of background stars (default 7.0).

        Returns:
            Self for method chaining.
        """
        if constellation is not None:
            self._config.constellation_star_size = constellation
        if background is not None:
            self._config.background_star_size = background
        return self

    def with_line_style(
        self,
        width: float = None,
        opacity: float = None
    ) -> 'StarForge':
        """
        Configure constellation line appearance.

        Args:
            width: Line width in pixels.
            opacity: Line opacity (0.0 to 1.0).

        Returns:
            Self for method chaining.
        """
        if width is not None:
            self._config.constellation_line_width = width
        if opacity is not None:
            self._config.constellation_line_opacity = opacity
        return self

    def with_label_style(
        self,
        font_size: str = None,
        font_family: str = None,
        opacity: float = None
    ) -> 'StarForge':
        """
        Configure label text appearance.

        Args:
            font_size: CSS font size (e.g., "12px", "1em").
            font_family: CSS font family string.
            opacity: Text opacity (0.0 to 1.0).

        Returns:
            Self for method chaining.
        """
        if font_size is not None:
            self._config.label_font_size = font_size
        if font_family is not None:
            self._config.label_font_family = font_family
        if opacity is not None:
            self._config.label_opacity = opacity
        return self

    def with_bend_strength(self, strength: float) -> 'StarForge':
        """
        Set edge distortion strength.

        Args:
            strength: Bend strength near edges (0 disables, ~0.02 is subtle).

        Returns:
            Self for method chaining.
        """
        self._config.bend_strength = strength
        return self

    def with_procedural_stars(self, enabled: bool = True, count: int = 300) -> 'StarForge':
        """
        Enable procedural background star generation.

        Args:
            enabled: True to generate random background stars.
            count: Number of procedural stars to generate.

        Returns:
            Self for method chaining.
        """
        self._config.procedural_bg_stars = enabled
        self._config.num_procedural_stars = count
        return self

    def with_custom_icons(
        self,
        constellation_star_file: str = None,
        background_star_file: str = None
    ) -> 'StarForge':
        """
        Use custom SVG files for star icons.

        Args:
            constellation_star_file: Path to SVG for constellation stars.
            background_star_file: Path to SVG for background stars.

        Returns:
            Self for method chaining.
        """
        if constellation_star_file is not None:
            self._config.star_icon_main_file = constellation_star_file
        if background_star_file is not None:
            self._config.star_icon_bg_file = background_star_file
        return self

    def with_config(self, config: Config) -> 'StarForge':
        """
        Apply a complete Config object.

        Args:
            config: A Config instance with desired settings.

        Returns:
            Self for method chaining.
        """
        self._config = config
        self._fov_radius_deg = config.fov_radius_deg
        self._show_labels = config.show_labels
        return self

    def with_bounds(self, x1: int, y1: int, x2: int, y2: int) -> 'StarForge':
        """
        Set rendering bounds (for cropped/partial renders).

        Args:
            x1, y1: Top-left corner coordinates.
            x2, y2: Bottom-right corner coordinates.

        Returns:
            Self for method chaining.
        """
        self._config.bounds = (x1, y1, x2, y2)
        return self

    # =========================================================================
    # Core Operations
    # =========================================================================

    def calculate(self) -> 'StarForge':
        """
        Perform astronomical calculations for the configured location and time.

        This method loads astronomical data and calculates star positions.
        Called automatically by render() if not already done.

        Returns:
            Self for method chaining.
        """
        if not self._location_resolved:
            self._resolve_location()

        # Load astronomy data if needed
        if not self._astronomy_loaded:
            self._load_astronomy_data()

        # Calculate positions
        if self._verbose:
            Log.info(f"Computing sky for {self.observation_time.strftime('%Y-%m-%d %H:%M UTC')}...")

        with Spinner("Calculating star positions") if self._verbose else _NoOpContext():
            self._visible_stars, self._constellations = calculate_celestial_positions(
                self._latitude,
                self._longitude,
                self.observation_time,
                self._magnitude_limit,
                data_cache=self._astronomy_data
            )

        self._calculated = True

        if self._verbose:
            if not self._visible_stars:
                Log.warning("No stars found. Is the sky covered or magnitude too low?")
            else:
                Log.info(f"Visible stars: {len(self._visible_stars)} | Constellations: {len(self._constellations)}")

        return self

    def render(self, output_filename: str) -> 'StarForge':
        """
        Render the star chart to an SVG file.

        Args:
            output_filename: Path for the output SVG file.

        Returns:
            Self for method chaining.

        Example:
            StarForge("Paris").render("paris_sky.svg")
        """
        # Ensure calculations are done
        if not self._calculated:
            self.calculate()

        # Ensure .svg extension
        if not output_filename.lower().endswith('.svg'):
            output_filename += '.svg'

        if self._verbose:
            Log.info(f"Rendering chart to {output_filename}...")

        # Create and render the SVG chart
        chart = SVGChart(
            output_filename=output_filename,
            visible_stars=self._visible_stars,
            constellations=self._constellations,
            config=self._config
        )
        chart.render()

        if self._verbose:
            Log.success(f"Saved to {output_filename}")

        return self

    def save(self, output_filename: str) -> 'StarForge':
        """
        Alias for render(). Saves the star chart to an SVG file.

        Args:
            output_filename: Path for the output SVG file.

        Returns:
            Self for method chaining.
        """
        return self.render(output_filename)

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

    def _resolve_location(self) -> None:
        """Resolve location query to coordinates."""
        try:
            with Spinner("Resolving location") if self._verbose else _NoOpContext():
                self._latitude, self._longitude, self._place_name = resolve_location(
                    self._location_query
                )
            if self._verbose:
                Log.info(f"Location resolved: {self._place_name} ({self._latitude:.4f}, {self._longitude:.4f})")
            self._location_resolved = True
        except ValueError as e:
            Log.error(str(e))
            raise

    def _load_astronomy_data(self) -> None:
        """Load astronomical ephemeris and star catalogs."""
        data_exists = os.path.exists('de421.bsp')
        msg = "Verifying/Downloading astronomical data" if not data_exists else "Loading astronomical data"

        with Spinner(msg) if self._verbose else _NoOpContext():
            self._astronomy_data = load_astronomy_data(verbose=False)

        self._astronomy_loaded = True

    def _parse_date_string(self, dt_str: str) -> datetime:
        """Parse a date string in various formats."""
        dt_str = dt_str.strip()

        formats = [
            # Standard ISO-like
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
            # Day-Month-Year (Dashes)
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y",
            "%d-%m-%y",
            "%d-%m-%y %H:%M",
            # Day/Month/Year (Slashes)
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%d/%m/%y %H:%M",
            # Month/Day/Year (US style)
            "%m/%d/%Y",
            # Dot notation
            "%d.%m.%Y",
            "%d.%m.%y"
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                return self._ensure_utc(dt)
            except ValueError:
                continue

        if self._verbose:
            Log.warning(f"Could not parse date string '{dt_str}'. Using current time.")
        return datetime.now(pytz.utc)

    def _ensure_utc(self, dt: datetime) -> datetime:
        """Ensure datetime is timezone-aware and in UTC."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=pytz.utc)
        return dt.astimezone(pytz.utc)

    # =========================================================================
    # String Representation
    # =========================================================================

    def __repr__(self) -> str:
        location_str = self._place_name if self._location_resolved else self._location_query
        return f"StarForge(location='{location_str}')"

    def __str__(self) -> str:
        parts = [f"StarForge Chart"]
        if self._location_resolved:
            parts.append(f"  Location: {self._place_name}")
            parts.append(f"  Coordinates: ({self._latitude:.4f}, {self._longitude:.4f})")
        else:
            parts.append(f"  Location: {self._location_query} (not resolved)")
        parts.append(f"  Time: {self.observation_time.strftime('%Y-%m-%d %H:%M UTC')}")
        parts.append(f"  FOV: {self._fov_radius_deg}°")
        parts.append(f"  Magnitude limit: {self._magnitude_limit}")
        parts.append(f"  Labels: {'enabled' if self._show_labels else 'disabled'}")
        return "\n".join(parts)


class _NoOpContext:
    """A no-operation context manager for when verbose is False."""
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
