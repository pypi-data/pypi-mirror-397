"""
Starforge - A Python library for generating astronomical star charts.
- utils.py : 

Utility tools for StarForge

Developed & maintained by Aditya Gaur (adityagaur.home@gmail.com) (@xdityagr)
Copyright Aditya Gaur, 2025. All rights reserved.
"""
import geonamescache
import re
import sys
import time
import threading
import itertools
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class LogLevel:
    """Log level constants."""
    DEBUG = 0
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4
    SILENT = 5  # Suppress all logs


class Log:
    """
    Professional logging helper with configurable log levels.

    Usage:
        from Starforge.utils import Log, LogLevel

        # Set log level (default is INFO)
        Log.set_level(LogLevel.WARNING)  # Only show warnings and errors
        Log.set_level(LogLevel.DEBUG)    # Show everything
        Log.set_level(LogLevel.SILENT)   # Suppress all output

        # Log messages
        Log.debug("Detailed info")   # Only shown if level <= DEBUG
        Log.info("General info")     # Only shown if level <= INFO
        Log.success("Task done")     # Only shown if level <= SUCCESS
        Log.warning("Watch out")     # Only shown if level <= WARNING
        Log.error("Something broke") # Only shown if level <= ERROR
    """
    _level = LogLevel.INFO  # Default level

    @classmethod
    def set_level(cls, level: int):
        """Set the minimum log level to display."""
        cls._level = level

    @classmethod
    def get_level(cls) -> int:
        """Get the current log level."""
        return cls._level

    @classmethod
    def debug(cls, msg):
        """Debug message - verbose details for troubleshooting."""
        if cls._level <= LogLevel.DEBUG:
            print(f"{Fore.LIGHTBLACK_EX}[DEBUG]{Style.RESET_ALL} {msg}")

    @classmethod
    def info(cls, msg):
        """Info message - general progress information."""
        if cls._level <= LogLevel.INFO:
            print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {msg}")

    @classmethod
    def success(cls, msg):
        """Success message - task completed successfully."""
        if cls._level <= LogLevel.SUCCESS:
            print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {msg}")

    @classmethod
    def warning(cls, msg):
        """Warning message - something unexpected but not fatal."""
        if cls._level <= LogLevel.WARNING:
            print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")

    @classmethod
    def error(cls, msg):
        """Error message - something went wrong."""
        if cls._level <= LogLevel.ERROR:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

class Spinner:
    """
    A smooth, professional console spinner for long-running tasks.
    Uses braille patterns for a modern, flicker-free animation.
    """
    def __init__(self, message="Processing", delay=0.08, style="dots"):
        # Different spinner styles
        spinner_styles = {
            "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
            "line": ["─", "\\", "│", "/"],
            "circle": ["◐", "◓", "◑", "◒"],
            "bounce": ["⠁", "⠂", "⠄", "⠂"],
            "arc": ["◜", "◠", "◝", "◞", "◡", "◟"],
            "star": ["✶", "✸", "✹", "✺", "✹", "✸"],
            "moon": ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
            "pulse": ["█", "▓", "▒", "░", "▒", "▓"],
        }

        self.frames = spinner_styles.get(style, spinner_styles["dots"])
        self.spinner = itertools.cycle(self.frames)
        self.delay = delay
        self.message = message
        self.running = False
        self.thread = None
        self._last_length = 0

    def spin(self):
        # Hide cursor for cleaner animation
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

        while self.running:
            frame = next(self.spinner)
            output = f'\r{Fore.CYAN}{frame} {self.message}...{Style.RESET_ALL}'

            # Pad with spaces to overwrite any previous longer text
            padding = ' ' * max(0, self._last_length - len(output))
            full_output = output + padding

            sys.stdout.write(full_output)
            sys.stdout.flush()

            self._last_length = len(output)
            time.sleep(self.delay)

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.2)

        # Clear the spinner line completely
        clear_length = len(self.message) + 20
        sys.stdout.write('\r' + ' ' * clear_length + '\r')

        # Show cursor again
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

        if exc_type is not None:
            Log.error(f"{self.message} failed!")

def _normalize_string(s: str) -> str:
    """Normalize a string for comparison (lowercase, remove accents, strip)."""
    import unicodedata
    # Normalize unicode characters (decompose accents)
    normalized = unicodedata.normalize('NFD', s)
    # Remove accent marks (combining characters)
    without_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return without_accents.lower().strip()


def _string_similarity(s1: str, s2: str) -> float:
    """
    Calculate similarity between two strings using a combination of methods.
    Returns a score from 0.0 (no match) to 1.0 (exact match).
    """
    s1_norm = _normalize_string(s1)
    s2_norm = _normalize_string(s2)

    # Exact match after normalization
    if s1_norm == s2_norm:
        return 1.0

    # Check if one contains the other (partial match)
    if s1_norm in s2_norm or s2_norm in s1_norm:
        return 0.9

    # Check if query matches start of city name
    if s2_norm.startswith(s1_norm):
        return 0.85

    # Levenshtein-like similarity (simple implementation)
    # Calculate ratio of matching characters
    len1, len2 = len(s1_norm), len(s2_norm)
    if len1 == 0 or len2 == 0:
        return 0.0

    # Use longest common subsequence ratio
    lcs_len = _longest_common_subsequence_length(s1_norm, s2_norm)
    lcs_ratio = (2.0 * lcs_len) / (len1 + len2)

    # Also check character overlap
    set1, set2 = set(s1_norm), set(s2_norm)
    if len(set1 | set2) > 0:
        jaccard = len(set1 & set2) / len(set1 | set2)
    else:
        jaccard = 0.0

    # Combine metrics
    return max(lcs_ratio * 0.7 + jaccard * 0.3, 0.0)


def _longest_common_subsequence_length(s1: str, s2: str) -> int:
    """Calculate the length of the longest common subsequence."""
    m, n = len(s1), len(s2)
    # Use space-optimized DP
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(prev[j], curr[j-1])
        prev, curr = curr, [0] * (n + 1)

    return prev[n] if m > 0 else 0


def resolve_location(query: str):
    """
    Resolves a location query string into latitude, longitude, and a descriptive name.

    Supports:
    - Explicit coordinates: "lat, lon" or "lat lon"
    - City names with fuzzy matching (handles typos, missing accents, partial names)

    When multiple cities match, prefers the most populous one.
    """

    # 1. Try to parse as explicit coordinates "lat, lon" or "lat lon"
    coord_pattern = r'^(-?\d+(\.\d+)?)[,\s]+(-?\d+(\.\d+)?)$'
    match = re.match(coord_pattern, query.strip())

    if match:
        lat = float(match.group(1))
        lon = float(match.group(3))
        return lat, lon, f"Coordinates {lat}, {lon}"

    # 2. City Name Lookup using GeonamesCache with fuzzy matching
    gc = geonamescache.GeonamesCache()
    cities = gc.get_cities()

    query_normalized = _normalize_string(query)

    # Score all cities and find best matches
    candidates = []

    for _, city_data in cities.items():
        city_name = city_data['name']
        similarity = _string_similarity(query, city_name)

        # Only consider reasonable matches (similarity > 0.5)
        if similarity > 0.5:
            candidates.append({
                'data': city_data,
                'similarity': similarity,
                'population': city_data['population']
            })

    if not candidates:
        # Try even more lenient matching for very short queries
        for _, city_data in cities.items():
            city_name = city_data['name']
            if _normalize_string(city_name).startswith(query_normalized[:3]) if len(query_normalized) >= 3 else False:
                candidates.append({
                    'data': city_data,
                    'similarity': 0.4,
                    'population': city_data['population']
                })

    if candidates:
        # Sort by similarity first, then by population for ties
        candidates.sort(key=lambda x: (-x['similarity'], -x['population']))

        best = candidates[0]['data']
        similarity = candidates[0]['similarity']

        # If not an exact match, log info about the match
        if similarity < 1.0:
            Log.info(f"Matched '{query}' to '{best['name']}' (similarity: {similarity:.0%})")

        return best['latitude'], best['longitude'], f"{best['name']}, {best['countrycode']}"

    raise ValueError(f"Could not resolve location: '{query}'. Please check spelling or use coordinates.")