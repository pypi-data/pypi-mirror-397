# Font Generator

A Python package for font manipulation and conversion. Convert TTF/OTF fonts to SVG format, convert SVG files back to
fonts, and add handwritten effects to fonts.

## Features

- **TTF to SVG Conversion**: Extract individual glyphs from TrueType/OpenType fonts as SVG files
- **SVG to TTF Conversion**: Combine SVG files back into a TTF font
- **Handwritten Effect**: Add a handwritten, jittery effect to fonts using
  FontForge ([see HANDWRITTEN.md](https://github.com/GenXLabs-org/font-generator/blob/main/HANDWRITTEN.md))
- **CLI Interface**: Easy-to-use command-line interface for all operations
- **Python API**: Use as a library in your Python projects

## Installation

### From PyPI

```bash
pip install font-generator
```

### From Source

```bash
git clone https://github.com/GenXLabs-org/font-generator.git
cd font-generator
pip install -e .
```

## Quick Start

### Running Without Installation

You can run the CLI directly without installing the package:

```bash
# From the project root directory
python -m font_generator.cli ttf-to-svg input/Allura-Regular.ttf output/
```

### Command Line Usage

#### Convert TTF to SVG

```bash
font-generator ttf-to-svg input/Allura-Regular.ttf output/
```

This will extract all glyphs from the font and save them as individual SVG files in the output directory, along with
a `_font_metadata.json` file containing font metrics.

#### Convert SVG to TTF

```bash
font-generator svg-to-ttf output/input_svgs/ input/Allura-Regular.ttf output/CustomFont.ttf --width 800
```

This will combine SVG files from the input directory into a new TTF font, using the base font as a template.

### Python API Usage

```python
from font_generator import ttf_to_svg, svg_to_ttf, make_handwritten

# Convert TTF to SVG
ttf_to_svg('input/Allura-Regular.ttf', 'output/')

# Convert SVG to TTF
svg_to_ttf('output/input_svgs/', 'input/Allura-Regular.ttf', 'output/CustomFont.ttf')

# Add handwritten effect
make_handwritten('input/Allura-Regular.ttf', 'output/Allura-Handwritten.ttf')
```

## Detailed Usage

### TTF to SVG Conversion

The `ttf-to-svg` command extracts all glyphs from a font file:

```bash
font-generator ttf-to-svg input/Allura-Regular.ttf output/
```

**Output:**

- Individual SVG files for each glyph (named with Unicode values)
- `_font_metadata.json` file containing:
    - Font metadata (name, family, version)
    - Font metrics (units per em, ascent, descent)
    - Glyph metrics (width, left bearing)
    - OpenType feature information (GSUB/GPOS)

### SVG to TTF Conversion

The `svg-to-ttf` command combines SVG files into a font:

```bash
font-generator svg-to-ttf output/input_svgs/ input/Allura-Regular.ttf output/CustomFont.ttf --width 800
```

**Parameters:**

- `svg_folder/`: Directory containing SVG files
- `base_font.ttf`: Template font file
- `output.ttf`: Output font file path
- `--width`: Default glyph width (default: 800)

**Note:** SVG files should be named to match glyph names (e.g., `A.svg`, `uni0041_A.svg`). The command uses a default
Unicode map for A-Z, but you can customize this in the Python API.

## Requirements

- Python >=3.7
- fonttools >= 4.0.0
- svgpathtools >= 1.4.0
- fontforge (optional, for handwritten feature)

## Examples

### Example 1: Extract Glyphs from a Font

```bash
font-generator ttf-to-svg input/Allura-Regular.ttf output/
```

This creates individual SVG files for each character in the font, saved in the `output/` directory.

### Example 2: Create Custom Font from SVGs

```bash
# First, extract glyphs
font-generator ttf-to-svg input/Arya-Regular.ttf output/input_svgs/

# Edit SVG files as needed...

# Then rebuild the font
font-generator svg-to-ttf output/input_svgs/ input/Arya-Regular.ttf output/CustomFont.ttf
```

## Troubleshooting

### Invalid Font File Error

Make sure you're using a valid TTF or OTF file. The tool validates font files by checking their headers.

### SVG Conversion Issues

- Ensure SVG files are properly formatted
- Check that glyph names match the Unicode map
- Verify the base font file is valid

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](https://github.com/GenXLabs-org/font-generator/blob/main/LICENSE)

## Author

[GenXLabs](https://genxlabs.org/)

## Support

For issues, questions, or contributions, please visit
the [GitHub repository](https://github.com/GenXLabs-org/font-generator).
