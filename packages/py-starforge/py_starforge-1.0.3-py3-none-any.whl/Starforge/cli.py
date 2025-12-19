"""
Starforge: A Command-Line Starmap Generator

This script provides a command-line interface to the Starforge library,
allowing users to generate SVG star charts from their terminal.
Developed & maintained by Aditya Gaur (adityagaur.home@gmail.com) (@xdityagr)

Usage:
    starforge "Paris" output.svg
    starforge "26.9124, 75.7873" jaipur.svg --date "2024-06-15" --fov 60
    starforge "New York" nyc.svg --magnitude 5.0 --no-labels --circular

Developed & maintained by Aditya Gaur (adityagaur.home@gmail.com) (@xdityagr)
Copyright Aditya Gaur, 2025. All rights reserved.
"""

import argparse
from datetime import datetime
import pytz

from Starforge.core import StarForge
from Starforge.utils import Log, LogLevel


def main():
    """Parses command-line arguments and generates a star chart."""
    parser = argparse.ArgumentParser(
        description="Generate a beautiful and accurate SVG star chart for a specific date, time, and location.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- Positional Arguments ---
    parser.add_argument(
        "location",
        type=str,
        help="Location: city name (e.g., 'Paris') or coordinates (e.g., '48.8566, 2.3522')"
    )
    parser.add_argument(
        "output",
        type=str,
        help="Output SVG file path (e.g., 'starmap.svg')"
    )

    # --- Optional Arguments ---
    parser.add_argument(
        "-d", "--date",
        type=str,
        default=None,
        help="Date/time for observation. Supports multiple formats:\n"
             "  '2024-12-25', '25/12/2024', '2024-12-25 22:00'\n"
             "Defaults to current time."
    )
    parser.add_argument(
        "-m", "--magnitude",
        type=float,
        default=6.0,
        help="Limiting magnitude for background stars (default: 6.0).\n"
             "Lower = fewer, brighter stars only."
    )
    parser.add_argument(
        "-f", "--fov",
        type=float,
        default=90.0,
        help="Field of view radius in degrees (default: 90).\n"
             "90 = full hemisphere, smaller = zoomed in."
    )
    parser.add_argument(
        "--no-labels",
        action="store_true",
        help="Disable constellation labels."
    )
    parser.add_argument(
        "--circular",
        action="store_true",
        help="Apply circular mask to the chart."
    )
    parser.add_argument(
        "--sphere",
        type=float,
        default=None,
        metavar="STRENGTH",
        help="Apply sphere effect with given strength (0.0-1.0)."
    )
    parser.add_argument(
        "--size",
        type=int,
        default=1000,
        help="Chart size in pixels (default: 1000)."
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress output messages."
    )
    parser.add_argument(
        "--bg-color",
        type=str,
        default="#050505",
        help="Background color (default: '#050505')."
    )
    parser.add_argument(
        "--star-color",
        type=str,
        default="#FFFFFF",
        help="Star color (default: '#FFFFFF')."
    )
    parser.add_argument(
        "--line-color",
        type=str,
        default="#FFFFFF",
        help="Constellation line color (default: '#FFFFFF')."
    )

    args = parser.parse_args()

    # Set log level
    if args.quiet:
        Log.set_level(LogLevel.SILENT)

    # Build the chart using fluent API
    chart = StarForge(args.location, verbose=not args.quiet)

    # Apply date if specified
    if args.date:
        chart.at_date(args.date)

    # Apply configuration
    chart.with_fov(args.fov)
    chart.with_magnitude_limit(args.magnitude)
    chart.with_size(args.size)
    chart.with_colors(
        background=args.bg_color,
        stars=args.star_color,
        lines=args.line_color
    )

    if args.no_labels:
        chart.without_labels()

    if args.circular:
        chart.with_circular_mask()

    if args.sphere is not None:
        chart.with_sphere_effect(True, args.sphere)

    # Render
    chart.render(args.output)

    if not args.quiet:
        print(f"\nStar chart saved to '{args.output}'")

if __name__ == "__main__":
    main()