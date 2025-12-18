"""Module for adding handwritten effects to fonts using FontForge.

This module provides functionality to transform standard fonts into handwritten-style
fonts by applying algorithmic imperfections such as random jitter, point variation,
and curve roughening.
"""

import os
import platform
import random
import math
from typing import Optional, Literal

try:
    import fontforge
except ImportError:
    fontforge = None


def _get_fontforge_install_instructions():
    """Get platform-specific FontForge installation instructions."""
    system = platform.system().lower()

    if system == "darwin":
        return """FontForge is required for handwritten font generation.

            Installation steps for macOS:
            1. Install FontForge using Homebrew:
               brew install fontforge
            
            2. Set up Python bindings in your virtual environment:
               Run: ./setup_fontforge_venv.sh
               
               Or manually create symlinks (check Python version first):
               ls -la $(brew --prefix fontforge)/lib/
               ln -sf $(brew --prefix fontforge)/lib/python3.14/site-packages/fontforge.so .venv/lib/python3.14/site-packages/
            
            Note: FontForge's Python bindings are NOT available via 'pip install fontforge'.
            They come with the system FontForge installation and need to be linked to your venv.
            
            If Homebrew is not installed, download from: https://fontforge.org/en-US/downloads/
            """

    elif system == "linux":
        return """FontForge is required for handwritten font generation.

            Installation steps for Linux:
            1. Install FontForge with Python bindings:
               Ubuntu/Debian: sudo apt-get install fontforge python3-fontforge
               Fedora: sudo dnf install fontforge python3-fontforge
               Arch: sudo pacman -S fontforge python-fontforge
            
            2. Python bindings are included with the system package.
               Test: python3 -c "import fontforge; print('OK')"
            
            Note: FontForge's Python bindings are NOT available via 'pip install fontforge'."""

    elif system == "windows":
        return """FontForge is required for handwritten font generation.

            Installation steps for Windows:
            1. Download and install FontForge from:
               https://fontforge.org/en-US/downloads/
            
            2. Python bindings are included with the FontForge installation.
               Test: python -c "import fontforge; print('OK')"
            
            Note: FontForge's Python bindings are NOT available via 'pip install fontforge'.
            You may need to add FontForge to your PATH."""

    else:
        return """FontForge is required for handwritten font generation.

            Please install FontForge for your system:
            1. Install FontForge: https://fontforge.org/en-US/downloads/
            2. Install Python bindings: pip install fontforge
            """


def make_handwritten(
        input_font_path: str,
        output_font_path: str,
        jitter_amount: float = 5.0,
        smoothing: float = 15.0,
        random_seed: Optional[int] = None,
        point_density: float = 1.0,
        jitter_distribution: Literal["uniform", "normal", "gaussian"] = "uniform",
        per_glyph_variation: float = 0.2,
        preserve_metrics: bool = True,
        output_format: Optional[str] = None,
        font_name_suffix: str = "Handwritten",
        verbose: bool = True,
        # Geometric Variations
        max_rotation: float = 5.0,
        scale_variation: float = 0.15,
        baseline_shift: float = 60.0,
        # Spacing Chaos
        bearing_jitter: float = 45.0,
        # Slant/Skew
        skew_angle: float = 12.0,
        skew_jitter: float = 3.0,
):
    """
    Add a handwritten effect to a font by adding random jitter to glyph points.

    This function applies algorithmic imperfections to transform a standard font
    into a handwritten-style font. It works by:
    1. Adding random jitter to control points
    2. Optionally subdividing curves for more detail
    3. Converting to on-curve points (polygonization)
    4. Smoothing the result back into curves

    Args:
        input_font_path (str): Path to the input TTF/OTF font file
        output_font_path (str): Path where the output font will be saved
        jitter_amount (float): Range of random movement for points in font units.
            Higher values create more pronounced jitter. Default: 5.0
        smoothing (float): How much to smooth the jagged lines back into curves.
            Higher values create smoother curves. Range typically 0-100. Default: 15.0
        random_seed (int, optional): Random seed for reproducibility. If None, uses
            system time. Default: None
        point_density (float): Multiplier for point density before jittering.
            Values > 1.0 add more points along curves. Default: 1.0
        jitter_distribution (str): Distribution type for jitter:
            - "uniform": Uniform distribution (default)
            - "normal": Normal/Gaussian distribution
            - "gaussian": Alias for "normal"
            Default: "uniform"
        per_glyph_variation (float): Multiplier for per-glyph jitter variation.
            Each glyph gets a slightly different jitter amount. Range 0.0-1.0.
            Default: 0.2
        preserve_metrics (bool): Whether to preserve original font metrics
            (advance width, sidebearings). Default: True
        output_format (str, optional): Output format ("ttf", "otf", "woff", "woff2").
            If None, inferred from output file extension. Default: None
        font_name_suffix (str): Suffix to add to font names. Default: "Handwritten"
        verbose (bool): Whether to print progress messages. Default: True
        max_rotation (float): Maximum rotation angle in degrees for each glyph.
            Creates tilting effect. Default: 5.0
        scale_variation (float): Random scale variation as a fraction (0.15 = ±15%).
            Creates inconsistent letter sizes. Default: 0.15
        baseline_shift (float): Maximum vertical shift in font units.
            Creates bouncy baseline effect. Default: 60.0
        bearing_jitter (float): Random variation in left/right sidebearings.
            Creates spacing chaos. Default: 45.0
        skew_angle (float): Base slant angle in degrees. Positive = right (italic).
            Default: 12.0
        skew_jitter (float): Per-glyph variation in slant angle. Default: 3.0

    Raises:
        ImportError: If fontforge is not installed
        FileNotFoundError: If input font file doesn't exist
        ValueError: If parameters are out of valid ranges

    Example:
        >>> make_handwritten(
        ...     "input.ttf",
        ...     "output.ttf",
        ...     jitter_amount=8.0,
        ...     smoothing=20.0,
        ...     random_seed=42
        ... )
    """
    if fontforge is None:
        instructions = _get_fontforge_install_instructions()
        raise ImportError(instructions)

    if not os.path.exists(input_font_path):
        raise FileNotFoundError(f"Input font file not found: {input_font_path}")

    if jitter_amount < 0:
        raise ValueError("jitter_amount must be >= 0")
    if smoothing < 0:
        raise ValueError("smoothing must be >= 0")
    if point_density < 0.1 or point_density > 5.0:
        raise ValueError("point_density must be between 0.1 and 5.0")
    if per_glyph_variation < 0.0 or per_glyph_variation > 1.0:
        raise ValueError("per_glyph_variation must be between 0.0 and 1.0")
    if jitter_distribution not in ["uniform", "normal", "gaussian"]:
        raise ValueError(
            f"jitter_distribution must be one of: uniform, normal, gaussian. "
            f"Got: {jitter_distribution}"
        )
    if max_rotation < 0:
        raise ValueError("max_rotation must be >= 0")
    if scale_variation < 0 or scale_variation > 1.0:
        raise ValueError("scale_variation must be between 0.0 and 1.0")
    if baseline_shift < 0:
        raise ValueError("baseline_shift must be >= 0")
    if bearing_jitter < 0:
        raise ValueError("bearing_jitter must be >= 0")
    if skew_jitter < 0:
        raise ValueError("skew_jitter must be >= 0")

    if random_seed is not None:
        random.seed(random_seed)

    if output_format is None:
        ext = os.path.splitext(output_font_path)[1].lower()
        format_map = {
            ".ttf": "ttf",
            ".otf": "otf",
            ".woff": "woff",
            ".woff2": "woff2",
        }
        output_format = format_map.get(ext, "ttf")

    if verbose:
        print(f"📖 Opening {input_font_path}...")

    font = fontforge.open(input_font_path)

    font.is_quadratic = True

    if font.fontname:
        font.fontname += font_name_suffix
    if font.familyname:
        font.familyname += f" {font_name_suffix}"
    if font.fullname:
        font.fullname += f" {font_name_suffix}"

    glyphs_list = list(font.glyphs())
    total_glyphs = len(glyphs_list)

    if verbose:
        print(f" Processing {total_glyphs} glyphs...")

    try:
        from tqdm import tqdm
        use_progress_bar = True
    except ImportError:
        use_progress_bar = False
        tqdm = None

    if verbose and use_progress_bar:
        progress_bar = tqdm(
            total=total_glyphs,
            desc="  Processing",
            unit="glyph",
            ncols=80,
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
            leave=False
        )
    else:
        progress_bar = None

    glyph_count = 0
    for glyph in glyphs_list:
        if glyph.foreground.isEmpty():
            continue

        glyph.unlinkRef()

        glyph_jitter = jitter_amount * (
                1.0 + random.uniform(-per_glyph_variation, per_glyph_variation)
        )

        layer = glyph.foreground
        new_layer = fontforge.layer()

        for contour in layer:
            new_contour = fontforge.contour()
            new_contour.closed = contour.closed

            points = list(contour)

            if point_density > 1.0:
                points = _subdivide_points(points, point_density)

            for point in points:
                if jitter_distribution == "uniform":
                    dx = random.uniform(-glyph_jitter, glyph_jitter)
                    dy = random.uniform(-glyph_jitter, glyph_jitter)
                else:
                    dx = random.gauss(0, glyph_jitter / 2.0)
                    dy = random.gauss(0, glyph_jitter / 2.0)
                    dx = max(-glyph_jitter * 2, min(glyph_jitter * 2, dx))
                    dy = max(-glyph_jitter * 2, min(glyph_jitter * 2, dy))

                new_point = fontforge.point(
                    point.x + dx,
                    point.y + dy,
                    True  # True = "On Curve" point
                )
                new_contour += new_point

            new_layer += new_contour

        glyph.foreground = new_layer

        if smoothing > 0:
            glyph.simplify(smoothing)

        # Apply geometric transformations
        # 1. Rotation
        if max_rotation > 0:
            rotation_angle = random.uniform(-max_rotation, max_rotation)
            if rotation_angle != 0:
                glyph.transform(fontforge.matrix(1, 0, 0, 1, 0, 0).rotate(rotation_angle))

        # 2. Scale variation
        if scale_variation > 0:
            scale_x = 1.0 + random.uniform(-scale_variation, scale_variation)
            scale_y = 1.0 + random.uniform(-scale_variation, scale_variation)
            if scale_x != 1.0 or scale_y != 1.0:
                glyph.transform(fontforge.matrix(scale_x, 0, 0, scale_y, 0, 0))

        # 3. Baseline shift (vertical translation)
        if baseline_shift > 0:
            vertical_shift = random.uniform(-baseline_shift, baseline_shift)
            if vertical_shift != 0:
                glyph.transform(fontforge.matrix(1, 0, 0, 1, 0, vertical_shift))

        # 4. Skew/Slant
        if skew_angle != 0 or skew_jitter > 0:
            glyph_skew = skew_angle + random.uniform(-skew_jitter, skew_jitter)
            if glyph_skew != 0:
                skew_rad = math.radians(glyph_skew)
                skew_value = math.tan(skew_rad)
                glyph.transform(fontforge.matrix(1, skew_value, 0, 1, 0, 0))

        # 5. Bearing jitter (spacing chaos)
        if bearing_jitter > 0 and not preserve_metrics:
            if hasattr(glyph, 'width') and glyph.width > 0:
                left_bearing_jitter = random.uniform(-bearing_jitter, bearing_jitter)
                right_bearing_jitter = random.uniform(-bearing_jitter, bearing_jitter)

                current_width = glyph.width
                new_left_bearing = glyph.left_side_bearing + left_bearing_jitter
                new_width = current_width + (left_bearing_jitter + right_bearing_jitter)

                if new_left_bearing < 0:
                    new_width += abs(new_left_bearing)
                    new_left_bearing = 0
                if new_width < 0:
                    new_width = abs(new_width)

                glyph.width = int(new_width)
                glyph.left_side_bearing = int(new_left_bearing)

        glyph_count += 1

        if progress_bar:
            progress_bar.update(1)
        elif verbose and glyph_count % 100 == 0:
            print(f"  Processed {glyph_count}/{total_glyphs} glyphs...")

    if progress_bar:
        progress_bar.close()

    if verbose:
        print(f"Generating {output_font_path} ({output_format.upper()})...")

    font.generate(output_font_path)

    if verbose:
        print(f"Successfully created handwritten font: {output_font_path}")


def _subdivide_points(points, density_multiplier):
    """Subdivide points along curves to increase density.

    Args:
        points: List of fontforge points
        density_multiplier: Multiplier for point density

    Returns:
        List of subdivided points
    """
    if density_multiplier <= 1.0:
        return points

    new_points = []
    num_points = len(points)

    for i in range(num_points):
        current = points[i]
        next_idx = (i + 1) % num_points
        next_point = points[next_idx]

        new_points.append(current)

        if density_multiplier > 1.0:
            num_subdivisions = int(density_multiplier)
            for j in range(1, num_subdivisions):
                t = j / num_subdivisions
                x = current.x + (next_point.x - current.x) * t
                y = current.y + (next_point.y - current.y) * t
                new_point = fontforge.point(x, y, True)
                new_points.append(new_point)

    return new_points
