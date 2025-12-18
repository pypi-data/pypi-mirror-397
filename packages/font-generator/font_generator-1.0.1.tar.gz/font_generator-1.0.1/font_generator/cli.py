"""Command-line interface for font-generator."""

import argparse
import os
import sys

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Font Generator - Tools for font manipulation and conversion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
          # Convert TTF to SVG
          font-generator ttf-to-svg input.ttf output_dir/
        
          # Convert SVG to TTF
          font-generator svg-to-ttf svg_dir/ base.ttf output.ttf
        
          # Add handwritten effect to font
          font-generator handwritten input.ttf output.ttf --jitter 50 --smoothing 20
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # TTF to SVG command
    ttf_svg_parser = subparsers.add_parser(
        'ttf-to-svg',
        help='Convert TTF/OTF font to SVG files'
    )
    ttf_svg_parser.add_argument(
        'input_font',
        help='Path to input TTF/OTF font file'
    )
    ttf_svg_parser.add_argument(
        'output_dir',
        help='Output directory for SVG files'
    )

    # SVG to TTF command
    svg_ttf_parser = subparsers.add_parser(
        'svg-to-ttf',
        help='Convert SVG files to TTF font'
    )
    svg_ttf_parser.add_argument(
        'input_folder',
        help='Directory containing SVG files'
    )
    svg_ttf_parser.add_argument(
        'base_font',
        help='Path to base font file to use as template'
    )
    svg_ttf_parser.add_argument(
        'output_font',
        help='Path for output TTF font file'
    )
    svg_ttf_parser.add_argument(
        '--width',
        type=int,
        default=800,
        help='Default glyph width (default: 800)'
    )

    # Handwritten command
    handwritten_parser = subparsers.add_parser(
        'handwritten',
        help='Add handwritten effect to a font',
        description='Transform a standard font into a handwritten-style font by '
                    'applying algorithmic imperfections such as random jitter and '
                    'curve variation.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
              # Basic usage with defaults
              font-generator handwritten input.ttf output.ttf
            
              # High jitter, more smoothing
              font-generator handwritten input.ttf output.ttf --jitter 10 --smoothing 25
            
              # Reproducible output with seed
              font-generator handwritten input.ttf output.ttf --seed 42
            
              # Normal distribution jitter with high point density
              font-generator handwritten input.ttf output.ttf --jitter 8 --distribution normal --point-density 2.0
            
              # Maximum variation per glyph
              font-generator handwritten input.ttf output.ttf --jitter 6 --variation 0.5
            
              # Output as OTF format
              font-generator handwritten input.ttf output.otf --format otf
            
            For more information, see: https://github.com/GenXLabs-org/font-generator
        """
    )
    handwritten_parser.add_argument(
        'input_font',
        help='Path to input TTF/OTF font file'
    )
    handwritten_parser.add_argument(
        'output_font',
        help='Path for output font file (format inferred from extension)'
    )
    handwritten_parser.add_argument(
        '--jitter',
        type=float,
        default=5.0,
        metavar='AMOUNT',
        help='Range of random movement for points in font units. '
             'Higher values create more pronounced jitter. (default: 5.0)'
    )
    handwritten_parser.add_argument(
        '--smoothing',
        type=float,
        default=15.0,
        metavar='AMOUNT',
        help='How much to smooth the jagged lines back into curves. '
             'Higher values create smoother curves. Range typically 0-100. (default: 15.0)'
    )
    handwritten_parser.add_argument(
        '--seed',
        type=int,
        default=None,
        metavar='SEED',
        help='Random seed for reproducibility. If not specified, uses system time.'
    )
    handwritten_parser.add_argument(
        '--point-density',
        type=float,
        default=1.0,
        metavar='MULTIPLIER',
        help='Multiplier for point density before jittering. '
             'Values > 1.0 add more points along curves. Range: 0.1-5.0. (default: 1.0)'
    )
    handwritten_parser.add_argument(
        '--distribution',
        type=str,
        choices=['uniform', 'normal', 'gaussian'],
        default='uniform',
        help='Distribution type for jitter: uniform (default), normal/gaussian. '
             'Normal distribution creates more natural-looking variation.'
    )
    handwritten_parser.add_argument(
        '--variation',
        type=float,
        default=0.2,
        metavar='AMOUNT',
        help='Multiplier for per-glyph jitter variation. Each glyph gets a '
             'slightly different jitter amount. Range: 0.0-1.0. (default: 0.2)'
    )
    handwritten_parser.add_argument(
        '--no-preserve-metrics',
        action='store_true',
        help='Do not preserve original font metrics (advance width, sidebearings). '
             'By default, metrics are preserved.'
    )
    handwritten_parser.add_argument(
        '--format',
        type=str,
        choices=['ttf', 'otf', 'woff', 'woff2'],
        default=None,
        help='Output format. If not specified, inferred from output file extension.'
    )
    handwritten_parser.add_argument(
        '--suffix',
        type=str,
        default='Handwritten',
        help='Suffix to add to font names. (default: "Handwritten")'
    )
    handwritten_parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    handwritten_parser.add_argument(
        '--rotation',
        type=float,
        default=5.0,
        metavar='DEGREES',
        help='Maximum rotation angle in degrees for each glyph. '
             'Creates tilting effect. Default: 5.0'
    )
    handwritten_parser.add_argument(
        '--scale-variation',
        type=float,
        default=0.15,
        metavar='FRACTION',
        help='Random scale variation as fraction (0.15 = ±15%%). '
             'Creates inconsistent letter sizes. Range: 0.0-1.0. Default: 0.15'
    )
    handwritten_parser.add_argument(
        '--baseline-shift',
        type=float,
        default=60.0,
        metavar='UNITS',
        help='Maximum vertical shift in font units. '
             'Creates bouncy baseline effect. Default: 60.0'
    )

    # Spacing Chaos
    handwritten_parser.add_argument(
        '--bearing-jitter',
        type=float,
        default=45.0,
        metavar='UNITS',
        help='Random variation in left/right sidebearings. '
             'Creates spacing chaos. Only applies if --no-preserve-metrics. Default: 45.0'
    )

    # Slant/Skew
    handwritten_parser.add_argument(
        '--skew',
        type=float,
        default=12.0,
        metavar='DEGREES',
        help='Base slant angle in degrees. Positive = right (italic). Default: 12.0'
    )
    handwritten_parser.add_argument(
        '--skew-jitter',
        type=float,
        default=3.0,
        metavar='DEGREES',
        help='Per-glyph variation in slant angle. Default: 3.0'
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        try:
            if args.command == 'ttf-to-svg':
                from .ttf_to_svg import ttf_to_svg
                ttf_to_svg(args.input_font, args.output_dir)

            elif args.command == 'svg-to-ttf':
                from .svg_to_ttf import svg_to_ttf
                svg_to_ttf(args.input_folder, args.base_font, args.output_font, default_width=args.width)

            elif args.command == 'handwritten':
                from .handwritten import make_handwritten
                make_handwritten(
                    args.input_font,
                    args.output_font,
                    jitter_amount=args.jitter,
                    smoothing=args.smoothing,
                    random_seed=args.seed,
                    point_density=args.point_density,
                    jitter_distribution=args.distribution,
                    per_glyph_variation=args.variation,
                    preserve_metrics=not args.no_preserve_metrics,
                    output_format=args.format,
                    font_name_suffix=args.suffix,
                    verbose=not args.quiet,
                    max_rotation=args.rotation,
                    scale_variation=args.scale_variation,
                    baseline_shift=args.baseline_shift,
                    bearing_jitter=args.bearing_jitter,
                    skew_angle=args.skew,
                    skew_jitter=args.skew_jitter,
                )
        except ImportError:
            if args.command == 'ttf-to-svg':
                from font_generator.ttf_to_svg import ttf_to_svg
                ttf_to_svg(args.input_font, args.output_dir)

            elif args.command == 'svg-to-ttf':
                from font_generator.svg_to_ttf import svg_to_ttf
                svg_to_ttf(args.input_folder, args.base_font, args.output_font, default_width=args.width)

            elif args.command == 'handwritten':
                from font_generator.handwritten import make_handwritten
                make_handwritten(
                    args.input_font,
                    args.output_font,
                    jitter_amount=args.jitter,
                    smoothing=args.smoothing,
                    random_seed=args.seed,
                    point_density=args.point_density,
                    jitter_distribution=args.distribution,
                    per_glyph_variation=args.variation,
                    preserve_metrics=not args.no_preserve_metrics,
                    output_format=args.format,
                    font_name_suffix=args.suffix,
                    verbose=not args.quiet,
                    max_rotation=args.rotation,
                    scale_variation=args.scale_variation,
                    baseline_shift=args.baseline_shift,
                    bearing_jitter=args.bearing_jitter,
                    skew_angle=args.skew,
                    skew_jitter=args.skew_jitter,
                )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
