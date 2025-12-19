"""
Starforge - A Python library for generating astronomical star charts.
- renderer.py : 

Handles rendering in StarForge

Developed & maintained by Aditya Gaur (adityagaur.home@gmail.com) (@xdityagr)
Copyright Aditya Gaur, 2025. All rights reserved.
"""
import svgwrite
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
import random
from typing import *
import xml.etree.ElementTree as ET
import re
import math
from .utils import Log


@dataclass
class Config:
    """Configuration for chart styling and rendering."""
    width_px: int = 1000
    height_px: int = 1000
    
    # Colors & Style
    background_color: str = '#000000'
    star_color: str = 'white'
    border_color: str = 'white'
    border_width: int = 2
    
    # Stars
    background_star_size: float = 7.0
    constellation_star_size: float = 14.0
    procedural_bg_stars: bool = False
    num_procedural_stars: int = 300
    
    # Constellations
    constellation_line_color: str = 'white'
    constellation_line_width: float = 0.8
    constellation_line_opacity: float = 0.8
    circular_mask = False
    
    # Text
    show_labels: bool = True
    label_color: str = '#ffcc00'
    label_font_size: str = '12px'
    label_font_family: str = 'Arial, sans-serif'
    label_opacity: float = 0.9

    # Projection Physics
    fov_radius_deg: float = 90.0
    sphere_effect: bool = False
    sphere_distortion_strength: float = 0.6
    bend_strength: float = 0.02
    
    # Custom Icons (Optional)
    star_icon_main_file: Optional[str] = None
    star_icon_bg_file: Optional[str] = None
    
    # Defaults
    star_icon_main_svg: str = "M 5 0 L 6.18 3.82 L 10 3.82 L 6.91 6.18 L 8.09 10 L 5 7.64 L 1.91 10 L 3.09 6.18 L 0 3.82 L 3.82 3.82 Z"
    star_icon_bg_svg: str = "M 5 2 A 3 3 0 1 0 5 8 A 3 3 0 1 0 5 2"
    bounds: Optional[Tuple[int, int, int, int]] = None


def extract_svg_path_from_file(svg_file_path):
    import xml.etree.ElementTree as ET
    import re
    try:
        tree = ET.parse(svg_file_path)
        root = tree.getroot()
        for elem in root.iter():
            tag = elem.tag
            if isinstance(tag, str) and '}' in tag:
                tag = tag.split('}', 1)[1]  # strip namespace

            if tag.lower() == 'path' and 'd' in elem.attrib:
                d = elem.attrib['d']
                d = d.replace(',', ' ')
                d = re.sub(r'\s+', ' ', d.strip())
                return d

        print(f"Warning: No supported shape found in {svg_file_path}")
        return None
    except Exception as e:
        print(f"Error reading SVG file {svg_file_path}: {e}")
        return None
    
def get_viewbox(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()
    vb = root.attrib.get('viewBox')
    return vb if vb else "0 0 10 10"

def tangential_edge_bend(x, y, strength=0.05, edge_start=0.9):
    """
    Applies a slight tangential (sideways) bend near the map's circular edge.
    x, y are normalized projected coordinates.
    """
    r = math.hypot(x, y)
    if r < edge_start:
        return x, y  # Only bend near edge

    # How close to the border?
    t = (r - edge_start) / (1.0 - edge_start)
    t = min(max(t, 0.0), 1.0)

    # Compute the tangent direction (perpendicular to radius)
    nx, ny = -y, x
    tangent_len = math.hypot(nx, ny)
    if tangent_len == 0:
        return x, y  # Center case—no direction

    # Normalize tangent direction
    nx /= tangent_len
    ny /= tangent_len

    # Scale the tangential push by falloff and strength
    bend = strength * (t * t)  # quadratic easing-out for smoother pull
    return x + nx * bend, y + ny * bend


def simulate_globe_projection(x, y, strength=0.6):
    """
    Applies a 'Spherize' effect that blends between flat and spherical.
    strength: 0.0 (Flat) to 1.0 (Full Orthographic Sphere).
    """
    r = math.hypot(x, y)
    
    if r < 1e-6:
        return x, y
        
    # 1. Calculate the Orthographic 'Globe' Radius
    # We treat r=1.0 as 90 degrees. r_ortho = sin(r * pi/2)
    # This creates the heavy compression at the edges.
    theta = r * (math.pi / 2.0)
    r_ortho = math.sin(theta)
    
    # 2. Blend original radius (Linear) with Globe radius (Ortho)
    # This softens the effect so it doesn't look like a fisheye lens.
    r_blended = (r * (1 - strength)) + (r_ortho * strength)
    
    # 3. Calculate scale
    scale = r_blended / r
    
    return x * scale, y * scale


class SVGChart:
    """Generates an SVG star chart based on celestial data and a config."""
    
    def __init__(self, output_filename, visible_stars, constellations, config: Config):
        if not output_filename.lower().endswith('.svg'):
            output_filename += '.svg'
        self.output_filename = output_filename
        self.visible_stars = visible_stars
        self.constellations = constellations
        # self.constellation_labels = constellation_labels
        self.config = config


        # Scaling Factor Calculation 

        # Calculate the zoom/scale factor.
        # 90 degrees (full horizon) = scale 1.
        # 45 degrees = scale 2 (zoomed in).
        if self.config.fov_radius_deg <= 0:
            print(f"Warning: Invalid fov_radius_deg ({self.config.fov_radius_deg}). Defaulting to 90.")
            self.config.fov_radius_deg = 90.0
        self.scale_factor = 90.0 / self.config.fov_radius_deg 
        
        
        self.center_x = self.config.width_px / 2
        self.center_y = self.config.height_px / 2
        self.radius = (min(self.config.width_px, self.config.height_px) / 2) - self.config.border_width


        self.star_hip_map = {star['hip']: star for star in self.visible_stars}
        self.constellation_lines_map = {name: lines for name, lines in self.constellations}

        # Load external SVG icons if specified
        self._load_star_icons()
        
        self._setup_drawing()
        self._get_constellation_star_ids()
        # self._simplify_constellation_nodes()


    def _load_star_icons(self):
        """Load star icon path data and viewBox dimensions from external files."""
        
        def parse_vb(vb_str):
            """Helper to parse a viewBox string '0 0 10 10' into a tuple."""
            try:
                parts = vb_str.split(' ')
                # Return (min_x, min_y, width, height)
                return (float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]))
            except Exception:
                # Fallback
                return (0.0, 0.0, 10.0, 10.0)

        # Main constellation star
        if self.config.star_icon_main_file and Path(self.config.star_icon_main_file).exists():
            path_data = extract_svg_path_from_file(self.config.star_icon_main_file)
            vb_str = get_viewbox(self.config.star_icon_main_file)
            if path_data:
                self.star_main_path = path_data
                self.star_main_vb = parse_vb(vb_str) # <-- Store parsed viewBox
            else:
                self.star_main_path = self.config.star_icon_main_svg
                self.star_main_vb = parse_vb("0 0 10 10") # Fallback
        else:
            Log.warning("Background & Constellation Star Icons not found, Using Defaults.")
            self.star_main_path = self.config.star_icon_main_svg
            self.star_main_vb = parse_vb("0 0 10 10") # Fallback
        
        # Background star
        if self.config.star_icon_bg_file and Path(self.config.star_icon_bg_file).exists():
            path_data = extract_svg_path_from_file(self.config.star_icon_bg_file)
            vb_str = get_viewbox(self.config.star_icon_bg_file)
            if path_data:
                self.star_bg_path = path_data
                self.star_bg_vb = parse_vb(vb_str) # <-- Store parsed viewBox
            else:
                self.star_bg_path = self.config.star_icon_bg_svg
                self.star_bg_vb = parse_vb("0 0 10 10") # Fallback
        else:
            self.star_bg_path = self.config.star_icon_bg_svg
            self.star_bg_vb = parse_vb("0 0 10 10") # Fallback


    def _setup_drawing(self):
        """Initializes the SVG drawing object with background and border."""
        self.dwg = svgwrite.Drawing(self.output_filename,
            profile='full', 
            size=(f'{self.config.width_px}px', f'{self.config.height_px}px')
        )
        self.dwg.add(self.dwg.rect(
            insert=(0, 0), 
            size=('100%', '100%'), 
            fill=self.config.background_color
        ))
        # self.dwg.add(self.dwg.circle(
        #     center=(self.center_x, self.center_y), 
        #     r=self.radius, 
        #     stroke=self.config.border_color, 
        #     fill='none', 
        #     stroke_width=self.config.border_width
        # ))
        if self.config.circular_mask:
            clip_path = self.dwg.defs.add(self.dwg.clipPath(id='clipCircle'))
            clip_path.add(self.dwg.circle(
                center=(self.center_x, self.center_y),
                r=self.radius
            ))
            self.main_group = self.dwg.g(clip_path='url(#clipCircle)')
        else:
            self.main_group = self.dwg.g()  # No clipping

        self.dwg.add(self.main_group)

    # def _define_star_symbols(self):
    #     """Defines the SVG symbols for the custom star icons."""
    #     vb = get_viewbox(self.config.star_icon_main_file)
    #     main_star_symbol = self.dwg.symbol(id='starMain', viewBox=vb)
    #     # main_star_symbol = self.dwg.symbol(id='starMain', viewBox='0 0 10 10')
    #     main_star_symbol.add(self.dwg.path(d=self.star_main_path, fill=self.config.star_color))
    #     self.dwg.defs.add(main_star_symbol)

    #     vb2 = get_viewbox(self.config.star_icon_bg_file)
    #     bg_star_symbol = self.dwg.symbol(id='starBg', viewBox=vb2)
    #     bg_star_symbol.add(self.dwg.path(d=self.star_bg_path, fill=self.config.star_color))
    #     self.dwg.defs.add(bg_star_symbol)

    def _simplify_constellation_nodes(self, tolerance=0.012):
        """Reduces constellation star clutter by simplifying vertex list."""
        new_star_map = {}
        kept_hips = set()

        def rdp(points, hips):
            if len(points) < 3:
                return hips
            (x1, y1), (x2, y2) = points[0], points[-1]
            max_dist, idx = 0, 0
            for i, (x, y) in enumerate(points[1:-1], 1):
                num = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1)
                den = math.hypot(x2 - x1, y2 - y1)
                dist = num / den if den else 0
                if dist > max_dist:
                    max_dist, idx = dist, i
            if max_dist > tolerance:
                left = rdp(points[: idx + 1], hips[: idx + 1])
                right = rdp(points[idx:], hips[idx:])
                return left[:-1] + right
            return [hips[0], hips[-1]]

        for name, lines in self.constellations:
            hip_chain = [start for start, _ in lines]
            pts = []
            for hip in hip_chain:
                if hip in self.star_hip_map:
                    x = self.star_hip_map[hip]['x'] * self.scale_factor
                    y = -self.star_hip_map[hip]['y'] * self.scale_factor
                    pts.append((x, y))
            reduced = rdp(pts, hip_chain)
            kept_hips |= set(reduced)

        # Filter star_hip_map to only keep simplified constellation stars
        for hip, star in self.star_hip_map.items():
            if hip in kept_hips or hip not in self.constellation_star_ids:
                new_star_map[hip] = star

        self.star_hip_map = new_star_map
        self.visible_stars = [s for s in self.visible_stars if s['hip'] in new_star_map]



    def _get_constellation_star_ids(self):
        """Creates a set of HIP IDs for stars that are part of constellations."""
        self.constellation_star_ids = set()
        for _, lines in self.constellations:
            for start_hip, end_hip in lines:
                self.constellation_star_ids.add(start_hip)
                self.constellation_star_ids.add(end_hip)

        self.constellation_visible_star_ids = set()

    def _is_within_bounds(self, x, y):
        """Return True if (x, y) is inside the configured drawing bounds."""
        if not hasattr(self.config, 'bounds') or not self.config.bounds:
            return True  # No bounds defined, treat as globally visible

        x1, y1, x2, y2 = self.config.bounds  # Poster space bounds
        return x1 <= x <= x2 and y1 <= y <= y2


    def _draw_constellations(self):
        """Draw constellation lines with tangential bending, but only keep segments fully inside bounds."""
        lines_group = self.dwg.g(
            stroke=self.config.constellation_line_color,
            stroke_width=self.config.constellation_line_width,
            stroke_opacity=self.config.constellation_line_opacity,
            fill='none'
        )

        num_segments = 12  # more -> smoother curve

        # Track which constellation stars are actually visible (connected by drawn lines)
        self.constellation_visible_star_ids = set()

        for _, lines in self.constellations:
            for start_hip, end_hip in lines:
                s = self.star_hip_map.get(start_hip)
                e = self.star_hip_map.get(end_hip)
                if not (s and e):
                    continue

                # normalized (projected) coords in your internal space
                u1, v1 = s['x'] * self.scale_factor, -s['y'] * self.scale_factor
                u2, v2 = e['x'] * self.scale_factor, -e['y'] * self.scale_factor

                # sample along the segment, bend, then map to canvas
                pts_canvas = []
                for i in range(num_segments + 1):
                    t = i / num_segments
                    u = u1 + (u2 - u1) * t
                    v = v1 + (v2 - v1) * t

                    # u_b, v_b = tangential_edge_bend(u, v, strength=self.config.bend_strength)
                    
                    if self.config.sphere_effect:
                        u_b, v_b = simulate_globe_projection(u, v, strength=self.config.sphere_distortion_strength)
                    else:
                        u_b, v_b = tangential_edge_bend(u, v, strength=self.config.bend_strength)

                    x = (u_b * self.radius) + self.center_x
                    y = (v_b * self.radius) + self.center_y
                    pts_canvas.append((x, y))

                # CRITICAL: Only draw line AND mark stars as visible if line fits bounds
                if self._polyline_fits_bounds(pts_canvas):
                    lines_group.add(self.dwg.polyline(points=pts_canvas))
                    # Only add stars to visible set if their connecting line is drawn
                    self.constellation_visible_star_ids.add(start_hip)
                    self.constellation_visible_star_ids.add(end_hip)

        self.main_group.add(lines_group)


    def _point_in_bounds(self, x: float, y: float) -> bool:
        b = getattr(self.config, "bounds", None)
        if not b:  # no bounds -> everything allowed
            return True
        x1, y1, x2, y2 = b
        return (x1 <= x <= x2) and (y1 <= y <= y2)

    def _polyline_fits_bounds(self, pts) -> bool:
        # every bent+transformed point must be inside
        return all(self._point_in_bounds(x, y) for (x, y) in pts)



    def _draw_procedural_bg_stars(self):
        """Generate procedural stars *only inside visible FOV circle AND shape bounds*."""
        num = getattr(self.config, "num_procedural_stars", 300)
        color = self.config.star_color or "#000000"
        size_base = getattr(self.config, "procedural_star_size", 0.8)

        group = self.dwg.g(fill=color, fill_opacity=0.65)

        star_path = self.star_bg_path
        vb_min_x, vb_min_y, vb_width, vb_height = self.star_bg_vb
        if vb_width == 0:
            vb_width = 10.0

        # FOV circle radius in normalized coords
        visible_R = 1 / self.scale_factor  # e.g., FOV=45 => 0.5

        # SPEED: pre-calc shape bounds
        bx1, by1, bx2, by2 = self.config.bounds or (0,0,self.config.width_px,self.config.height_px)

        for _ in range(num):
            # Generate point strictly INSIDE visible FOV circle
            r = visible_R * math.sqrt(random.random())
            theta = random.random() * math.tau
            u = r * math.cos(theta)
            v = r * math.sin(theta)

            # apply bend
            u_b, v_b = tangential_edge_bend(u, v, strength=self.config.bend_strength * 0.25)

            # map to canvas
            cx = (u_b * self.radius) + self.center_x
            cy = (v_b * self.radius) + self.center_y

            # HARD FILTER — must be inside export shape area
            if not (bx1 <= cx <= bx2 and by1 <= cy <= by2):
                continue

            # size variation
            size = size_base * (0.7 + 0.6 * random.random())
            scale = size / vb_width

            native_center_x = vb_min_x + vb_width/2
            native_center_y = vb_min_y + vb_height/2

            star_g = self.dwg.g()
            star_g.attribs['transform'] = (
                f"translate({cx},{cy}) "
                f"scale({scale}) "
                f"translate({-native_center_x},{-native_center_y})"
            )
            star_g.add(self.dwg.path(d=star_path))
            group.add(star_g)

        self.main_group.add(group)

    def _draw_stars(self):
        """Draw stars with optional slight edge curvature."""
        stars_group = self.dwg.g(fill=self.config.star_color)

        for star in self.visible_stars:
            u = star['x'] * self.scale_factor
            v = -star['y'] * self.scale_factor

            # Subtle bend near edge
            if self.config.sphere_effect:
                # Apply the globe projection instead of the bend
                u, v = simulate_globe_projection(u, v, strength=self.config.sphere_distortion_strength)
            else:
                # Standard bend
                u, v = tangential_edge_bend(u, v, strength=self.config.bend_strength)
            # -------------------------------

            center_x = (u * self.radius) + self.center_x
            center_y = (v * self.radius) + self.center_y

            # CRITICAL FIX: Check constellation membership FIRST
            is_constellation_star = star['hip'] in self.constellation_star_ids
            is_visible_constellation_star = star['hip'] in self.constellation_visible_star_ids

            if is_constellation_star:
                # This star is part of a constellation
                if not is_visible_constellation_star:
                    # None of its connecting lines were drawn (all rejected by bounds)
                    # Skip drawing this star entirely
                    continue
                
                # If we get here, at least one of its lines was drawn
                # Check if the star itself is in bounds
                if self.config.bounds and not self._point_in_bounds(center_x, center_y):
                    # Star position is out of bounds, skip it
                    continue
                    
                # Draw constellation star
                star_size = self.config.constellation_star_size
                path_data = self.star_main_path
                vb = self.star_main_vb
                
            else:
                # Background star - just check if it's in bounds
                if self.config.bounds and not self._point_in_bounds(center_x, center_y):
                    continue
                    
                star_size = self.config.background_star_size
                path_data = self.star_bg_path
                vb = self.star_bg_vb

            # Draw the star
            vb_min_x, vb_min_y, vb_width, vb_height = vb
            if vb_width == 0: 
                vb_width = 10.0
            scale = star_size / vb_width

            native_center_x = vb_min_x + vb_width / 2.0
            native_center_y = vb_min_y + vb_height / 2.0

            star_g = self.dwg.g()
            star_g.attribs['transform'] = (
                f"translate({center_x}, {center_y}) "
                f"scale({scale}) "
                f"translate({-native_center_x}, {-native_center_y})"
            )
            star_g.add(self.dwg.path(d=path_data))
            stars_group.add(star_g)

        self.main_group.add(stars_group)


    def _draw_labels(self):
            """
            Calculates and draws constellation labels dynamically based on
            stars visible *within the current zoomed-in view*.
            """
            if not self.config.show_labels:
                return
                
            labels_group = self.dwg.g(
                fill=self.config.label_color,
                font_size=self.config.label_font_size,
                font_family=self.config.label_font_family,
                text_anchor='middle',
                opacity=self.config.label_opacity
            )

            # Pre-calculate squared radius for efficient distance checking
            radius_squared = self.radius**2

            # Iterate through constellations, not pre-calculated labels
            for name, lines in self.constellation_lines_map.items():
                if not lines:
                    continue

                # Store the *canvas coordinates* of visible stars for this constellation
                visible_star_canvas_positions = []
                
                # Get all unique stars for this constellation
                unique_hip_ids = set()
                for start_hip, end_hip in lines:
                    unique_hip_ids.add(start_hip)
                    unique_hip_ids.add(end_hip)

                for hip_id in unique_hip_ids:
                    star_data = self.star_hip_map.get(hip_id)
                    
                    # Check if this star is in our master list
                    if star_data:
                        # Calculate the star's zoomed canvas position
                        star_x_canvas = (star_data['x'] * self.scale_factor) * self.radius + self.center_x
                        star_y_canvas = (-star_data['y'] * self.scale_factor) * self.radius + self.center_y
                        
                        # Check if its distance from center is within the visible circle
                        dist_sq = (star_x_canvas - self.center_x)**2 + (star_y_canvas - self.center_y)**2
                        
                        if dist_sq <= radius_squared and hip_id in self.constellation_visible_star_ids:
                            visible_star_canvas_positions.append((star_x_canvas, star_y_canvas))

                        # # If it's visible, add its canvas coordinates for the centroid
                        # visible_star_canvas_positions.append((star_x_canvas, star_y_canvas))
            
                # If we found any visible stars, calculate the centroid of their *canvas positions*
                if visible_star_canvas_positions:
                    # Remove duplicates
                    unique_positions = list(set(visible_star_canvas_positions))
                    
                    avg_x = sum(pos[0] for pos in unique_positions) / len(unique_positions)
                    avg_y = sum(pos[1] for pos in unique_positions) / len(unique_positions)
                    
                    # Draw the label at this *newly calculated* centroid
                    labels_group.add(self.dwg.text(name, insert=(avg_x, avg_y)))

            self.main_group.add(labels_group)
            
    def render(self):
        """Generates the full SVG chart and saves it to a file."""
        # self._define_star_symbols()
        self._draw_constellations()
        self._draw_stars()
        self._draw_labels()

        if getattr(self.config, "procedural_bg_stars", False):
            self._draw_procedural_bg_stars()


        if self.config.circular_mask:
            self.dwg.add(self.dwg.circle(
                center=(self.center_x, self.center_y), 
                r=self.radius, 
                stroke=self.config.border_color, 
                fill='none', 
                stroke_width=self.config.border_width
            ))

        self.dwg.save()


def render_svg_chart(visible_stars, constellations, output_filename, config: Config = None):
    """High-level function to render the star chart."""
    if config is None:
        config = Config()
        config.star_icon_main_file = "vec2.svg"
        config.star_icon_bg_file = "vec1.svg"
        # config.star_color = "#000000"
        # config.background_color = 'white'
        # config.constellation_line_color = 'black'
        config.constellation_line_width = 0.8
        config.bend_strength = 0.02
        # config.fov_radius_deg = fov_radius_deg
        config.show_labels = True
        # config.border_color = 'black'
    
    chart = SVGChart(
        visible_stars=visible_stars, 
        constellations=constellations,
        # constellation_labels=constellation_labels,
        output_filename=output_filename,
        config=config
    )
    chart.render()