<p align="center">
  <img src="https://raw.githubusercontent.com/xdityagr/ProjectStarForge/main/starforge_banner.png" width="800">
</p>

# StarForge

**Generate beautiful, accurate astronomical star charts in Python.**


StarForge is a high-fidelity astronomical visualization engine that transforms real celestial mechanics into beautiful, publication-ready vector star charts.

**"_It is not a toy sky plotter._"**

### StarForge combines:

- Physically accurate astronomy (Skyfield, real ephemerides, Hipparcos catalog)

- Smart decluttering & perceptual filtering

- A fluent, composable API

- A professional SVG rendering pipeline

- CLI + library parity

All while remaining deterministic, scriptable, and design-grade.

## Features

- **Simple API** - One line to generate a beautiful star chart
- **Fluent Interface** - Chain methods for easy configuration
- **Accurate Astronomy** - Uses Skyfield for precise star positions
- **Fuzzy Location Search** - Type "New York" or "NYC" - it just works
- **Multiple Date Formats** - Supports "2024-12-25", "25/12/2024", etc.
- **Customizable** - Colors, sizes, labels, effects, and more
- **High Quality SVG** - Scalable vector output for any resolution

# Usage

StarForge can be used both as a **Python library** and as a **command-line tool**. The API is designed to be fluent, composable, and easy to read, while still allowing deep control over astronomical accuracy and visual styling.

---

## Installation

```bash
pip install py-starforge
```

> Python 3.9+ recommended

---

## Quick Start (Recommended)

Generate a star chart in a single line:

```python
from Starforge import StarForge

StarForge("Paris").render("paris_sky.svg")
```

This generates an **accurate SVG star chart** of the sky visible from Paris at the current time.

---

## Fluent API Usage

StarForge supports a fluent, chainable API for expressive configuration:

```python
from Starforge import StarForge

(
    StarForge("Tokyo")
        .at_date("2024-06-15 22:00")
        .with_fov(60)
        .with_magnitude_limit(5.0)
        .without_labels()
        .with_circular_mask()
        .render("tokyo_sky.svg")
)
```

---

## Setting Location

### Using a City Name

```python
StarForge("New York").render("nyc_sky.svg")
```

City names are resolved using fuzzy matching and population weighting.

### Using Coordinates

```python
StarForge("28.61, 77.20").render("delhi_sky.svg")
```

### Using Explicit Coordinates

```python
StarForge("Delhi").at_coordinates(28.61, 77.20).render("delhi_sky.svg")
```

---

## Setting Date & Time

### Using a String (Multiple Formats Supported)

```python
chart.at_date("2024-12-25")
chart.at_date("25/12/2024 22:30")
chart.at_date("2024-12-25 22:30")
```

### Using a datetime Object

```python
from datetime import datetime
import pytz

chart.at_datetime(datetime(2024, 12, 25, 22, 30, tzinfo=pytz.utc))
```

### Current Time

```python
chart.now()
```

---

## Field of View (Zoom)

```python
chart.with_fov(90)   # Full hemisphere (default)
chart.with_fov(60)   # Zoomed
chart.with_fov(30)   # Deep zoom near zenith
```

---

## Star Density Control

Limit faint background stars:

```python
chart.with_magnitude_limit(4.5)  # Bright stars only
chart.with_magnitude_limit(6.5)  # Dense sky
```

---

## Labels & Annotations

```python
chart.with_labels(True)
chart.without_labels()
```

---

## Chart Shape & Projection

### Circular Mask

```python
chart.with_circular_mask()
```

### Sphere / Globe Effect

```python
chart.with_sphere_effect(True, strength=0.6)
```

---

## Styling & Colors

```python
chart.with_colors(
    background="#050505",
    stars="#ffffff",
    lines="#ffffff",
    labels="#ffcc00",
)
```

---

## Size & Resolution

```python
chart.with_size(1000)        # Square
chart.with_size(1200, 800)   # Rectangular
```

SVG output is resolution-independent and print-ready.

---

## Advanced Styling

### Star Sizes

```python
chart.with_star_sizes(
    constellation=14.0,
    background=7.0
)
```

### Constellation Line Style

```python
chart.with_line_style(
    width=1.2,
    opacity=0.8
)
```

### Label Style

```python
chart.with_label_style(
    font_size="12px",
    font_family="Arial",
    opacity=0.9
)
```

---

## Procedural Background Stars

```python
chart.with_procedural_stars(enabled=True, count=300)
```

Useful for artistic or stylized charts.

---

## Custom Star Icons (SVG)

```python
chart.with_custom_icons(
    constellation_star_file="icons/star_main.svg",
    background_star_file="icons/star_bg.svg"
)
```

---

## Rendering & Saving

```python
chart.render("output.svg")
chart.save("output.svg")  # Alias
```

If the `.svg` extension is omitted, it is added automatically.

---

## Command-Line Interface (CLI)

StarForge includes a first-class CLI for automation and scripting.

### Basic Usage

```bash
starforge "Paris" paris.svg
```

### With Options

```bash
starforge "New York" nyc.svg \
  --date "2024-12-25 22:00" \
  --fov 60 \
  --magnitude 5.0 \
  --no-labels \
  --circular
```

### Quiet Mode

```bash
starforge "Tokyo" tokyo.svg --quiet
```

---

## Log Levels

Control console output verbosity:

```python
from starforge import StarForge, Log, LogLevel

Log.set_level(LogLevel.WARNING)  # Only warnings and errors
Log.set_level(LogLevel.SILENT)   # No output

StarForge("Paris").render("quiet.svg")
```
## Legacy API (Still Supported)

```python
from Starforge import create_starmap

create_starmap("Paris", "paris_sky.svg")
create_starmap("28.61, 77.20", "delhi_sky.svg")
```

---

## Typical Workflow

```python
(
    StarForge("London")
        .at_date("2024-10-01 21:00")
        .with_fov(45)
        .with_magnitude_limit(5.5)
        .with_circular_mask()
        .with_colors(background="#000000", stars="#ffffff")
        .render("london_sky.svg")
)
```

---

StarForge is designed to scale from **one-line scripts** to **production pipelines** without changing how you think about the sky.

## Configuration Options

| Method | Description |
|--------|-------------|
| `.at_date(date)` | Set observation date/time |
| `.with_fov(degrees)` | Field of view (default: 90) |
| `.with_magnitude_limit(mag)` | Star brightness filter (default: 6.0) |
| `.with_labels()` / `.without_labels()` | Toggle constellation labels |
| `.with_circular_mask()` | Clip to circular shape |
| `.with_sphere_effect(enabled, strength)` | 3D globe distortion |
| `.with_size(width, height)` | Chart dimensions in pixels |
| `.with_colors(...)` | Customize colors |
| `.with_star_sizes(...)` | Star icon sizes |
| `.with_line_style(...)` | Constellation line style |

## Examples 
See more examples in [examples.py](https://github.com/xdityagr/ProjectStarForge/tree/main/examples/examples.py) & their outputs in [outputs](https://github.com/xdityagr/ProjectStarForge/tree/main/examples/outputs/)

#### Run specific examples:
    python examples.py basic
    python examples.py dates
    python examples.py colors
    python examples.py all
## License

MIT License - see LICENSE file.

## Author

Developed by **Aditya Gaur** ([@xdityagr](https://github.com/xdityagr))

## Links

- [GitHub Repository](https://github.com/xdityagr/starforge)
- [PyPI Package](https://pypi.org/project/starforge/)
- [Report Issues](https://github.com/xdityagr/starforge/issues)
